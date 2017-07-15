#!/bin/bash

# If you just want to piratevirus someone

cd /tmp
git clone https://github.com/phobosgroup/dtc2.git
cd dtc2
mv pirate ../piratefiles
cd ../
rm -rf dtc2
cd piratefiles
sh launch.sh
