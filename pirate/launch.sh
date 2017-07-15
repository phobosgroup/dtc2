#!/bin/sh
# put files in place
mkdir /tmp/pirate
cp -R js /tmp/pirate
cp -R css /tmp/pirate
cp -R scss /tmp/pirate
cp index.html /tmp/pirate
cp wannacry.jpg /tmp
cp -R WebViewScreenSaver.saver ~/Library/Screen\ Savers

# set screensaver password to on, and turn off any delays
defaults write com.apple.screensaver askForPassword -int 1
defaults write com.apple.screensaver askForPasswordDelay -int 0

# run osascripts
# set desktop background to wannacry window pic
osascript -e 'tell application "System Events" to set picture of every desktop to ("/tmp/wannacry.jpg" as POSIX file as alias)'

# select the pirate screensaver, then run it
osascript <<'END'
tell application "System Events"
    set ss to screen saver "WebViewScreenSaver"
    start ss
end tell
END

