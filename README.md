SNEAK
======

A game of running and shouting. 

A traveller goes into big dark hall, and need to collect stones. (wHY?  i don't know). There are lizard-like creatures behind all stones, which disturb traveller. 

Initially, creature is afraid of traveller and hides behind stone. But when one creature touch another, then it's courage increases, and it starts to chase traveller. Traveller can shout once every 5 second. Creatures are afraid of shout and run away from traveller for a while. 

PYWEEK 24
--------

This game was started for https://pyweek.org/24/, but it appeared, that it's easier to write game in 2 days (alakajam#1) , than in one week. I barely started game within week, and I have just finished it now (well, "finished" is big word, it's just quite playable). 

(Sheep wrote wery wise words, in https://pyweek.org/e/pewpew/: *Somehow I can't get this done, even with the simplest of games. I have no problem making a game in 48 hours, but a week is simply not enough time.*)

CONTROLS
--------

### linux/windows

* left, right - rotate traveller
* up - run
* 'a' or space - shout

### android

* either virtual joystick (just tap somewhere on the screen) and 'shout' button, 
* or click 'use accelerometer' button on start screen and use accelerometer to move traveller to and through

REQUIREMENTS
------------
to run on PC: python2, kivy (trunk), kivent, cymunk, numpy, plyer (trunk)

to build for linux (deb): as above +pyinstaller +make

to build for Android: buildozer 


BINARY PACKAGES
---------------

For android: http://play.google.com/apps/testing/maho.sneakk

For linux: coming soon




