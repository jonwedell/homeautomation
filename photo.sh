#!/bin/sh

# Hide the cursor
unclutter -display :0 -noevents -grab &

DISPLAY=:0 xset s off
DISPLAY=:0 xset -dpms
DISPLAY=:0 xset s noblank
DISPLAY=:0 ./photo_display.py "$1"
DISPLAY=:0 xset s on
DISPLAY=:0 xset +dpms
DISPLAY=:0 xset s blank

killall unclutter
