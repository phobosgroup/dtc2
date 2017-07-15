#!/usr/bin/env python3
import argparse
import enum
import logging
import os
import select
import shlex
import signal
import socket
import ssl
import struct
import sys
import threading


def counter(start=1, end=0xffffffff):
    for i in range(start, end):
        yield i


def human(size):
    """
    :param int size: The integer to represent as human-readable bytes
    :return: A human-readable-string representation of the argument
    :rtype: str
    """
    suffixes = ['B', 'K', 'M', 'G', 'T', 'P']
    for i in range(len(suffixes)):
        if size < 1024:
            return '{}{}'.format(size, suffixes[i])
        size //= 1024
    return '{}{}'.format(size * 1024, suffixes[-1])


class MessageType(enum.Enum):
    Control = 0
    Data = 1
    OpenChannel = 2
    CloseChannel = 3


class Message(object):
    """
    This is a container class for messages sent across the tunnel

    A message consists of:
      +-+--+----+=====...======+
      |T|Id|Size| message body |
      +-+--+----+=====...======+
      T    - The message type (see class MessageType)
      Id   - The Channel ID (value 0-65535)
      Size - The number of bytes in the Message body
      body - The Message body, variable bytes

    Note that it is important that a single thread should be in charge of reading/writing Messages, or you'll run
    into situations where Messages are interleaved!
    """
    HDR_STRUCT = b'!BHI'
    HDR_SIZE = struct.calcsize(HDR_STRUCT)

    def __init__(self, body, channel_id, msg_type=MessageType.Data):
        """
        :param bytes body:
        :param int channel_id:
        :param MessageType msg_type:
        """
        self.body = body
        self._channel_id = channel_id
        self.msg_type = msg_type
        self.logger = logging.getLogger('message')

    def __repr__(self):
        return '<Message type={} channel={} len={}>'.format(self.msg_type.name, self.channel_id, len(self.body))

    @property
    def channel_id(self):
        """
        Public accessor for Channel ID associated with a message
        :return: The Message's channel ID
        :rtype: int
        """
        return self._channel_id

    @classmethod
    def parse_hdr(cls, data):
        """
        Parse a Message header into the primary tuple of elements
        :param data: The data containing a Message header
        :return: A tuple of elements constituting the Message header
        :rtype: (MessageType, int, int)
        :raises TypeError: When parsing a header that contains an unknown MessageType
        :raises struct.error: If passed too few bytes to parse a full Message header
        """
        msg_type, channel_id, length = struct.unpack(cls.HDR_STRUCT, data[:struct.calcsize(cls.HDR_STRUCT)])
        try:
            msg_type = MessageType(msg_type)
        except TypeError:
            raise TypeError('Parsing a message with an invalid message type: 0x{:02x}'.format(msg_type))
        return msg_type, channel_id, length

    @classmethod
    def parse(cls, data):
        """
        Create a Message from a blob of data, which should contain a full header an body
        :param bytes data: The data to parse
        :return: An unserialized Message object
        :rtype: Message
        :raises ValueError: When an invalid message is parsed, if header parsing fails or Message body is bad length
        """
        if len(data) < cls.HDR_SIZE:
            raise ValueError('Invalid message, received incomplete header')
        msg_type, channel_id, length = cls.parse_hdr(data[:cls.HDR_SIZE])
        data = data[cls.HDR_SIZE:]
        if length != len(data):
            raise ValueError('Invalid message, received {} bytes and expected {}'.format(len(data), length))
        try:
            msg_type = MessageType(msg_type)
        except ValueError:
            raise ValueError('Invalid message type: 0x{:02x}'.format(msg_type))
        return Message(data, channel_id, msg_type=MessageType(msg_type))

    def serialize(self):
        """
        Serializes a Message object into a stream of bytes
        :return: A Message formatted as a stream of bytes
        :rtype: bytes
        """
        return struct.pack(self.HDR_STRUCT, self.msg_type.value, self.channel_id, len(self.body)) + self.body


class Channel(object):
    """
    A Channel object is an iterface between a Tunnel and client software. It is implemented as a pair of connected
    Unix domain sockets; the Tunnel reads/writes from/to one end, and the client software reads/writes from/to the
    other end.

    All methods below should be used by client software, except for tunnel_interface, which is intended for use
    by the Tunnel to which the Channel belongs.
    """
    def __init__(self, channel_id):
        """
        :param int channel_id: The Channel ID of this channel
        :type self._client_end: socket.socket
        :type self._tunnel_end: socket.socket
        """
        self._channel_id = channel_id
        self._client_end, self._tunnel_end = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        self.logger = logging.getLogger('channel')
        self.tx = 0
        self.rx = 0

    def __repr__(self):
        return '<Channel id={} bytes_tx={} bytes_rx={}>'.format(self.channel_id, human(self.tx), human(self.rx))

    @property
    def tunnel_interface(self):
        """
        You can assume this supports the socket.socket stream interface. DO NOT USE THIS IN A CLIENT APPLICATION!
        :return: something for the tunnel to interact with
        :rtype: socket.socket
        """
        return self._tunnel_end

    @property
    def client_interface(self):
        """
        You can assume this supports the socket.socket stream interface.
        :return: something for the client software to interact with
        :rtype: socket.socket
        """
        return self._client_end

    @property
    def channel_id(self):
        """
        :return: The ID of this channel
        :rtype: int
        """
        return self._channel_id

    def fileno(self):
        """
        Needed for calls to select.select from client software
        :return:
        """
        return self._client_end.fileno()

    def close(self):
        """
        Closes the Channel
        """
        self._client_end.close()

    def send(self, data, flags=0):
        """
        Send data associated with this Channel across the Tunnel
        :param bytes data: Data to send
        :param int flags: Flags that are passed through to the underlying socket
        :raises BrokenPipeError: If the socket is no longer connected
        """
        self._client_end.sendall(data, flags)
        self.tx += len(data)

    def recv(self, length):
        """
        Receive data associated with this Channel from the associated tunnel.
        :param int length: The number of bytes to receive
        :return: Data from the tunnel
        :rtype: bytes
        :raises EOFError: When the remote endpoint is closed
        """
        try:
            data = self._client_end.recv(length)
        except Exception as e:
            self.logger.debug('Error sending through channel: {}'.format(e))
            data = b''
        else:
            self.rx += len(data)
        return data


class Tunnel(object):
    def __init__(self, sock, open_channel_callback=None, close_channel_callback=None):
        """
        :param socket.socket sock: Connected socket to use for transport
        :param callable open_channel_callback: A function to call when remote end opens a channel
        :param callable close_channel_callback: A function to call when remote end closes a channel
        :type self.channels: list[(Channel, int)]
        :type self.transport: socket.socket
        """
        self.logger = logging.getLogger('tunnel')
        self.transport = sock
        self.transport_lock = threading.Lock()
        self.channels = []
        self.closed_channels = {}

        # Set up callbacks for remotely opened/closed Channels
        if open_channel_callback is None:
            self.open_channel_callback = lambda x: None
        else:
            self.open_channel_callback = open_channel_callback  # type: callable

        if close_channel_callback is None:
            self.close_channel_callback = lambda x: None
        else:
            self.close_channel_callback = close_channel_callback  # type: callable

        # CTRL-C ends Tunnel, CTRL-\ prints Tunnel stats
        signal.signal(signal.SIGINT, self.sigint_handler)
        signal.signal(signal.SIGQUIT, self.sigquit_handler)

        # Monitors Tunnel activity
        self.monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self.monitor_thread.start()

    def __repr__(self):
        msg = '<Tunnel OpenChannels={} ClosedChannels={} BytesTX={} BytesRX={}>'
        return msg.format(
            len(self.channels),
            len(self.closed_channels),
            human(sum([c.tx for c, _ in self.channels] + [c.tx for _, c in self.closed_channels.items()])),
            human(sum([c.rx for c, _ in self.channels] + [c.rx for _, c in self.closed_channels.items()])),
        )

    def sigquit_handler(self, signum, frame):
        self.logger.debug('Caught SIGQUIT (if you want to exit, use CTRL-C!!)')

        def print_options():
            print('.: AROX Options :.')
            print('?...:  Show this menu')
            print('s...:  Show Tunnel statistics')
            print('k...:  Kill a Channel')
            print('V...:  Increase logging verbosity')
            print('v...:  Decrease logging verbosity')
            print('')
            return

        def print_stats():
            print('################################# Stats For Nerds #################################')
            print(self)
            for channel, _ in self.channels:
                print('`-> {}'.format(channel))
            print('###################################################################################')
            print('')
            return

        try:
            choice = input('AROX> ').strip()
        except EOFError:
            print('')
            self.logger.warn('Unable to use the AROX commandline (did you pipe args in on stdin?) Here are some stats.')
            print_stats()
            return
        else:
            print('')

        if choice == '?' or choice == 'h':
            print_options()
        elif choice == 's':
            print_stats()
        elif choice == 'k':
            try:
                cid = int(input('ChannelID? '))
                self.close_channel(cid, close_remote=True, exc=True)
            except:
                print('ERROR: illegal channel provided')
            print('')
        elif choice == 'v':
            level = logging.getLogger().getEffectiveLevel()
            if level == logging.ERROR:
                level = logging.CRITICAL
            elif level == logging.WARNING:
                level = logging.ERROR
            elif level == logging.INFO:
                level = logging.WARNING
            elif level == logging.DEBUG:
                level = logging.INFO
            print('[+] Logging verbosity decreased to {}'.format(logging._levelToName[level]))
            logging.getLogger().setLevel(level)
        elif choice == 'V':
            level = logging.getLogger().getEffectiveLevel()
            if level == logging.CRITICAL:
                level = logging.ERROR
            elif level == logging.ERROR:
                level = logging.WARNING
            elif level == logging.WARNING:
                level = logging.INFO
            elif level == logging.INFO:
                level = logging.DEBUG
            print('[+] Logging verbosity increased to {}'.format(logging._levelToName[level]))
            logging.getLogger().setLevel(level)
        else:
            print('\nIllegal option "{}"\n'.format(choice))
        return

    def sigint_handler(self, signum, frame):
        self.close_tunnel()
        sys.exit(0)

    def wait(self):
        """
        Useful for client software that has nothing to do but handle callbacks from remote Channel opens
        :return:
        """
        self.monitor_thread.join()

    @property
    def channel_id_map(self):
        """
        :return: A mapping of open channels to their channel ID's
        :rtype: dict[Channel: int]
        """
        return {x: y for x, y in self.channels}

    @property
    def id_channel_map(self):
        """
        :return: A mapping of open channel ID's to their Channels
        :rtype: dict[int: Channel]
        """
        return {y: x for x, y in self.channels}

    def _close_channel_remote(self, channel_id):
        """
        Sends a command across the Tunnel to close a given Channel
        :param int channel_id: The ID of the channel to close
        :rtype: None
        """
        message = Message(b'', channel_id, msg_type=MessageType.CloseChannel)
        self.logger.debug('Sending request to close remote channel: {}'.format(message))
        self.transport_lock.acquire()
        self.transport.sendall(message.serialize())
        self.transport_lock.release()

    def close_channel(self, channel_id, close_remote=False, exc=False):
        """
        Closes a Channel associated with this Tunnel
        :param int channel_id: The ID of the Channel to close
        :param bool close_remote: Whether to also close the Channel on the remote end
        :param bool exc: Whether to raise an Exception if the Channel could not be closed
        :return:
        """
        if channel_id in self.closed_channels:
            if close_remote:
                self._close_channel_remote(channel_id)
            return

        if channel_id not in self.id_channel_map:
            if exc:
                raise ValueError('Attempted to close channel that is not open')
            else:
                self.logger.debug('Attempted to close channel that is not open : {}'.format(channel_id))
                return
        channel = self.id_channel_map[channel_id]
        self.channels.remove((channel, channel_id))
        channel.close()
        channel.tunnel_interface.close()
        if close_remote:
            self._close_channel_remote(channel_id)
        self.close_channel_callback(channel)
        self.closed_channels[channel_id] = channel
        self.logger.debug('Closed a channel: {}'.format(channel))

    def close_tunnel(self):
        """
        Shuts down the entire Tunnel, by first closing all Channels locally/remotely then exiting with status=0
        """
        self.logger.info('Closing Tunnel: {}'.format(self))
        for channel, channel_id in self.channels:
            self.close_channel(channel_id, close_remote=True)
        self.transport.close()

    def _open_channel_remote(self, channel_id):
        """
        Sends a Message to the remote endpoint to open a new Channel
        :param int channel_id: The ID of the Channel to open remotely
        """
        message = Message(b'', channel_id, MessageType.OpenChannel)
        self.logger.debug('Sending request to open remote channel: {}'.format(message))
        self.transport_lock.acquire()
        self.transport.sendall(message.serialize())
        self.transport_lock.release()

    def open_channel(self, channel_id, open_remote=False, exc=False):
        """
        Opens a Channel associated with this tunnel locally
        :param channel_id: The ID of the Channel to open
        :param open_remote: Whether to open the Channel on the remote endpoint as well
        :param exc: Whether to raise an exception if the Channel could not be opened
        :return: The newly opened Channel associated with this tunnel
        :rtype: Channel
        """
        if channel_id in self.id_channel_map:
            self.logger.warn('Attempted to open an already open channel : {}'.format(self.id_channel_map[channel_id]))
            if exc:
                raise ValueError('Channel already opened')
            else:
                return self.id_channel_map[channel_id]
        channel = Channel(channel_id)
        self.channels.append((channel, channel_id))
        if open_remote:
            self._open_channel_remote(channel_id)
        self.open_channel_callback(channel)
        self.logger.debug('Opened a channel: {}'.format(channel))
        return channel

    def recv_message(self):
        """
        :raises ValueError: When we fail to receive a complete Message header or body
        :return: A complete message received across the tunnel
        :rtype: Message
        """
        # Receive a full Message header
        data = b''
        while len(data) < Message.HDR_SIZE:
            _data = self.transport.recv(Message.HDR_SIZE - len(data))
            if not _data:
                break
            data += _data
        if len(data) != Message.HDR_SIZE:
            raise ValueError('Error encountered while receiving Message header')
        msg_type, channel_id, length = Message.parse_hdr(data)

        # Block until we've received the full Message body
        chunks = []  # This is an optimization to avoid reallocating strings while we receive large Message bodies
        received = 0
        while received < length:
            _data = self.transport.recv(length - received)
            if not _data:
                break
            chunks.append(_data)
            received += len(_data)
        if received != length:
            raise ValueError('Error encountered while receiving Message body')
        return Message(b''.join(chunks), channel_id, msg_type)

    def _monitor(self):
        """
        The main thread target that monitors the Tunnel
        :return:
        """
        while True:
            ignored_channels = []  # channels that were closed in this iteration

            read_fds = [channel.tunnel_interface for channel, channel_id in self.channels] + [self.transport]

            # Select for read on transport and on channels
            try:
                r, _, _ = select.select(read_fds, [], [], 1)
            except Exception as e:
                self.logger.debug('Error encountered while selecting on channels and transport: {}'.format(e))
                continue

            if not r:
                continue

            # If tunnel is ready, read a message and send to appropriate channels
            if self.transport in r:
                # Receive a message
                try:
                    message = self.recv_message()
                except ValueError as e:
                    self.logger.critical('Error encountered while reading from transport: {}'.format(e))
                    os.kill(os.getpid(), signal.SIGINT)  # Trigger tunnel teardown
                    sys.exit(1)

                self.logger.debug('Received a message: {}'.format(message))

                # Check if it's a ChannelClose message
                if message.msg_type == MessageType.CloseChannel:
                    self.close_channel(message.channel_id)
                    ignored_channels.append(message.channel_id)

                # Check if it's a ChannelOpen message
                elif message.msg_type == MessageType.OpenChannel:
                    self.open_channel(message.channel_id)

                # Check if it's a Data message
                elif message.msg_type == MessageType.Data:
                    channel = self.id_channel_map.get(message.channel_id)
                    if channel is None:
                        self.logger.debug('Received a message for an unknown channel, closing remote')
                        self.close_channel(message.channel_id, close_remote=True)
                    else:
                        try:
                            channel.tunnel_interface.sendall(message.body)
                        except OSError as e:
                            self.logger.debug('Error sending to transport, closing channel {} ({})'.format(channel, e))
                            self.close_channel(channel_id=message.channel_id, close_remote=True)

                # Not implemented channel type
                else:
                    self.logger.warn('Non-implemented MessageType received: {}'.format(message.msg_type))

            # If channels ready, then read data, encapsulate in Message, and send over transport
            else:
                tiface_channel_map = {channel.tunnel_interface: channel for (channel, channel_id) in self.channels}

                for tunnel_iface in r:
                    if tunnel_iface == self.transport:
                        continue  # We already did transport work in the previous block

                    channel = tiface_channel_map.get(tunnel_iface)
                    if channel is None or channel.channel_id in ignored_channels:
                        continue  # Channel was closed or does not exist

                    try:
                        data = tunnel_iface.recv(4096)
                    except Exception as e:
                        self.logger.debug('Error encountered while receiving from {}: {}'.format(channel, e))
                        self.close_channel(channel.channel_id, close_remote=True)
                        continue
                    if not data:
                        self.logger.debug('Received EOF from {}, closing channel remotely'.format(channel))
                        self.close_channel(channel.channel_id, close_remote=True)
                        continue

                    message = Message(data, channel.channel_id, MessageType.Data)

                    try:
                        self.transport_lock.acquire()
                        self.transport.sendall(message.serialize())
                        self.transport_lock.release()
                    except:
                        self.logger.critical('Problem sending data over transport, tearing it down!')
                        os.kill(os.getpid(), signal.SIGINT)
                        return
        return

    def proxy_sock_channel(self, sock, channel, logger):
        """
        A convenience function to proxy data between a TCP socket and channel. Intended to be used by Tunnel clients,
        i.e. uses the client interface of the Channel rather than the tunnel interface
        :param socket.socket sock:
        :param Channel channel:
        :param logging.Logger logger:
        :rtype: None
        """

        def close_both():
            self.close_channel(channel.channel_id, close_remote=True)
            sock.close()

        logger.debug('Proxying data between socket and {}'.format(channel))

        while True:
            # Check if we should even still be running
            if (channel, channel.channel_id) not in self.channels:
                self.logger.debug('Cleaning up thread that handles {}'.format(channel))
                return

            # See if the channel / socket are ready to be read
            readfds = [channel, sock]
            try:
                r, _, _ = select.select(readfds, [], [], 1)
            except Exception as e:
                logger.debug('Error encountered while selecting on sockets: {}'.format(e))
                return
            if not r:
                continue

            # Handle reads from channel + writes to socket
            if channel in r:
                try:
                    data = channel.recv(4096)
                except Exception as e:
                    logger.debug('Error receiving data from channel: {}'.format(e))
                    close_both()
                    return
                else:
                    if not data:
                        logger.debug('Received EOF from channel')
                        close_both()
                        return

                try:
                    sock.sendall(data)
                except Exception as e:
                    logger.debug('Error encountered while sending data to remote socket: {}'.format(e))
                    close_both()
                    return

            # Handle reads from socket + writes to channel
            if sock in r:
                try:
                    data = sock.recv(4096)
                except Exception as e:
                    logger.debug('Error encountered while reading data from remote socket: {}'.format(e))
                    close_both()
                    return
                else:
                    if not data:
                        logger.debug('Received EOF from remote socket')
                        close_both()
                        return

                try:
                    channel.send(data)
                except Exception as e:
                    logger.debug('Error sending to channel: {}'.format(e))
                    close_both()
                    return


class Server(object):
    def __init__(self, tunnel_port, socks_port, certfile=None, keyfile=None):
        """
        If an SSL certificate or key is not provided, the Server will fallback to using an unencrypted Tunnel.
        :param int tunnel_port: The port to listen for Relays on
        :param int socks_port: The port to listen for SOCKS clients to connect on
        :param str certfile: An SSL certificate file (required for SSL connections)
        :param str keyfile: An SSL key file (required for SSL connections)
        :type self.tunnel: Tunnel
        """
        self.logger = logging.getLogger('server')

        # Create the tunnel server
        if ':' in tunnel_port:
            host, port = tunnel_port.split(':')
        else:
            host, port = '0.0.0.0', tunnel_port
        self.tunnel_port = int(port)
        self.tunnel_host = host
        self.tunnel_server = socket.socket()
        self.tunnel_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tunnel_server.bind((self.tunnel_host, self.tunnel_port))
        self.tunnel_server.listen(1)

        # Create the SOCKS server
        self.socks_port = socks_port
        self.socks_server = socket.socket()
        self.socks_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socks_server.bind(('', socks_port))
        self.socks_server.listen(100)

        self.tunnel = None
        self.channel_counter = counter(0)

        # Set up SSL if desired
        if certfile is not None:
            certfile = os.path.abspath(certfile)
        if keyfile is not None:
            keyfile = os.path.abspath(keyfile)
        if keyfile is None or certfile is None:
            self.logger.warn('A Certificate and/or Key was not given. Proceeding without SSL!')
        else:
            try:
                self.tunnel_server = ssl.wrap_socket(self.tunnel_server,
                                                     server_side=True,
                                                     certfile=certfile,
                                                     keyfile=keyfile)
            except ssl.SSLError as e:
                self.logger.error('Error setting up SSL, bailing: {}'.format(e))
                sys.exit(-1)

    def _handle_channel(self, sock):
        """
        Create a channel in the Tunnel to accommodate new SOCKS client, and proxy data to/from the SOCKS client
        through the tunnel.
        :param socket.socket sock: A newly connect SOCKS client
        """
        host, port = sock.getpeername()[:2]
        try:
            channel = self.tunnel.open_channel(self.channel_counter.__next__(), open_remote=True, exc=True)
        except ValueError as e:
            self.logger.error('Error occurred while opening channel: {}'.format(e))
            sock.close()
            return

        self.tunnel.proxy_sock_channel(sock, channel, self.logger)
        self.logger.info('Terminating thread that handled {} <--> {}:{}'.format(channel, host, port))

    def run(self):
        """
        Waits for Relay to connect, then handles SOCKS clients as they connect. A thread is spawned to handle each
        SOCKS client.
        """
        self.logger.info('Listening for relay connections on {}:{}'.format(self.tunnel_host, self.tunnel_port))
        client, addr = self.tunnel_server.accept()
        self.logger.info('Accepted relay client connection from: {}:{}'.format(*addr))
        self.tunnel = Tunnel(client)
        while True:
            socks_client, addr = self.socks_server.accept()
            self.logger.info('Accepted SOCKS client connection from {}:{}'.format(*addr))
            t = threading.Thread(target=self._handle_channel, args=(socks_client,), daemon=True)
            t.start()


class Socks5Proxy(object):
    @staticmethod
    def _remote_connect(remote_host, remote_port, sock, af=socket.AF_INET):
        """
        Connect to the final destination
        :param str remote_host: The host to connect to
        :param int remote_port: The port to connect on
        :param socket.socket sock: The tunnel from the SOCKS server that will be proxied to remote_host
        :param int af: Address family. Use either socket.AF_INET or socket.AF_INET6
        :return: The socket connected to the remote endpoint. An unconnected socket if connection fails
        :rtype: socket.socket
        """
        remote_socket = socket.socket(af, socket.SOCK_STREAM)

        # Get RFC1928 address type (minus domain)
        if af == socket.AF_INET:
            atyp = 1
            local_addr = ('0.0.0.0', 0)

        else:
            atyp = 4
            local_addr = ('::', 0)

        # Connect to the remote server
        try:
            remote_socket.connect((remote_host, remote_port))
        except Exception:
            # Connection failed
            reply = struct.pack('BBBB', 0x05, 0x05, 0x00, atyp)  # "SOCKSv5 | Connection refused"
        else:
            # Get the local socket and build the success reply message
            local_addr = remote_socket.getsockname()[:2]
            reply = struct.pack('BBBB', 0x05, 0x00, 0x00, atyp)  # "SOCKSv5 | succeeded"

        # Add local (proxy) address to SOCKSv5 reply message
        reply += socket.inet_pton(af, local_addr[0]) + struct.pack('!H', local_addr[1])
        sock.send(reply)

        return remote_socket

    @classmethod
    def new_connect(cls, sock):
        # Wait for authentication request from SOCKS client, reply with "no auth needed"
        sock.recv(4096)
        sock.sendall(struct.pack('BB', 0x05, 0x00))  # "SOCKSv5 | no authentication needed"

        # Wait for CONNECT request from client
        request_data = sock.recv(4096)
        if len(request_data) >= 10:
            ver, cmd, rsv, atyp = struct.unpack('BBBB', request_data[:4])
            if ver != 0x05 or cmd != 0x01:
                # Bad request; not SOCKSv5 or not CONNECT request
                sock.sendall(struct.pack('BBBB', 0x05, 0x01, 0x00, 0x00))
                sock.close()
                raise ValueError('Received invalid SOCKSv5 version or non-CONNECT message')
        else:
            # Partial CONNECT request received
            sock.sendall(struct.pack('BBBB', 0x05, 0x01, 0x00, 0x00))
            sock.close()
            raise ValueError('Received incomplete CONNECT request')

        # Parse the CONNECT request
        if atyp == 1:  # IPv4
            addr_type = socket.AF_INET
            addr = socket.inet_ntop(socket.AF_INET, request_data[4:8])
            port, = struct.unpack('!H', request_data[8:10])
        elif atyp == 3:  # Domain name, will be resolved by socket.connect API
            addr_type = socket.AF_INET
            length, = struct.unpack('B', request_data[4:5])
            addr = request_data[5:5 + length].decode()
            port, = struct.unpack('!H', request_data[length + 5:length + 5 + 2])
        elif atyp == 4:  # IPv6
            addr_type = socket.AF_INET6
            addr = socket.inet_ntop(socket.AF_INET6, request_data[4:20])
            port, = struct.unpack('!H', request_data[20:22])
        else:
            # Received unknown address type
            sock.sendall(struct.pack('BBBB', 0x05, 0x08, 0x00, 0x00))
            sock.close()
            raise ValueError('Received unknown address type')

        # Connect to the remote endpoint
        host = (addr, port)
        remote_sock = cls._remote_connect(addr, port, sock, af=addr_type)
        return remote_sock, host


class Relay(object):
    def __init__(self, connect_host, connect_port, no_ssl=False):
        """
        :param str connect_host: The Server host to connect to
        :param int connect_port: The Server port to connect to
        :param bool no_ssl: Flag to control whether to SSL-wrap the Tunnel transport
        :type self.tunnel: Tunnel
        """
        self.logger = logging.getLogger('relay')
        self.no_ssl = no_ssl
        self.connect_server = (connect_host, connect_port)
        self.tunnel = None
        self.tunnel_sock = socket.socket()
        if not no_ssl:
            self.logger.info('SSL-wrapping client socket')
            try:
                self.tunnel_sock = ssl.wrap_socket(self.tunnel_sock)
            except ssl.SSLError as e:
                self.logger.critical('Problem SSL-wrapping socket, bailing!: {}'.format(e))
                sys.exit(-1)
        else:
            self.logger.warning('The proxy transport will not be encrypted!!')

    def _handle_channel(self, channel):
        """
        Handle initial SOCKS protocol, and proxy data between remote endpoint and tunnel
        :param tunnel.Channel channel: The Channel to proxy data with
        """
        sock = None

        # Handle SOCKS setup protocol
        try:
            sock, addr = Socks5Proxy.new_connect(channel.client_interface)
        except ValueError as e:
            self.logger.debug('Error connecting to remote host: {}'.format(e))
            self.tunnel.close_channel(channel.channel_id, close_remote=True)
            return
        except Exception as e:
            self.logger.debug('Error encountered while processing SOCKS protocol: {}'.format(e))
            self.tunnel.close_channel(channel.channel_id, close_remote=True)
            try:
                if isinstance(sock, socket.socket):
                    sock.close()
            except:
                pass
            return

        self.logger.info('Connected {} <--> {}:{}'.format(channel, *addr))
        self.tunnel.proxy_sock_channel(sock, channel, self.logger)
        self.logger.info('Terminating thread that handled {} <--> {}:{}'.format(channel, *addr))

    def open_channel_callback(self, channel):
        """
        Channel was opened remotely. Start a new thread to handle SOCKS protocol and proxy data between remote host and
        tunnel.
        :param Channel channel: The Channel opened by the Server
        """
        self.logger.debug('Spawning a thread to handle {}'.format(channel))
        t = threading.Thread(target=self._handle_channel, args=(channel,), daemon=True)
        t.start()

    def run(self):
        """
        Connect to the Server and wait on the Tunnel. All functionality from here will be started from the remote
        Channel open callback function.
        """
        try:
            self.tunnel_sock.connect(self.connect_server)
        except Exception as e:
            self.logger.critical('Error connecting to server, bailing! [{}]'.format(e))
            return

        self.logger.info('Connected to server at {}:{}'.format(*self.tunnel_sock.getpeername()[:2]))
        self.tunnel = Tunnel(self.tunnel_sock, open_channel_callback=self.open_channel_callback)
        self.tunnel.wait()


def server_main(args):
    """
    Target function for Server functionality
    """
    server = Server(args.tunnel_port, args.socks_port, args.cert, args.key)
    server.run()
    return


def relay_main(args):
    """
    Target functionality for Relay mode.
    """
    host, port = args.connect.split(':')
    relay = Relay(host, int(port), no_ssl=args.no_ssl)
    relay.run()
    return


def main():
    # Main parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='Specify `server` mode or `relay` mode')

    # Server parser
    server_parser = subparsers.add_parser('server', description='Options for running in Server mode')
    server_parser.add_argument('-d', '--debug', default=False, action='store_true', help='Enable debug mode')
    server_parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Enable verbose mode')
    server_parser.add_argument('-s', '--socks-port', type=int, default=1080,
                               help='The port to bind for the SOCKS server')
    server_parser.add_argument('-t', '--tunnel-port', default='10000',
                               help='The port to bind for the tunnel callback')
    server_parser.add_argument('--cert', default=None, help='The path to the SSL certificate file')
    server_parser.add_argument('--key', default=None, help='The path to the SSL key file')
    server_parser.set_defaults(main_function=server_main)

    # Relay parser
    relay_parser = subparsers.add_parser('relay', description='Options for running in Relay mode')
    relay_parser.add_argument('-d', '--debug', default=False, action='store_true', help='Enable debug mode')
    relay_parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Enable verbose mode')
    relay_parser.add_argument('--connect', default=None, required=True,
                              help='The socksychains server to connect to (i.e. host:port).')
    relay_parser.add_argument('--no-ssl', dest='no_ssl', default=False, action='store_true',
                              help='Disable SSL on tunnel to the server')
    relay_parser.set_defaults(main_function=relay_main)

    # Parse the arguments. There's also a hack to provide the ability to send cmdline arguments on stdin at startup
    if len(sys.argv) == 1:
        sys.stderr.write('[-] Checking for options on stdin...\n')
        r, _, _ = select.select([sys.stdin], [], [], 0)
        if not r:
            sys.stderr.write('[!] Options not detected on stdin, bailing!\n')
            sys.exit(-1)
        else:
            cmdline = sys.stdin.read(4096)
            sys.stderr.write('[+] Options received\n')
        args = parser.parse_args(shlex.split(cmdline))
    else:
        args = parser.parse_args()

    # Set logging level
    log_level = logging.WARNING
    if args.verbose:
        log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG

    logging.basicConfig(
        format='[%(asctime)s] %(levelname)8s %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=log_level
    )

    # Run the desired functionality
    args.main_function(args)


if __name__ == '__main__':
    main()
