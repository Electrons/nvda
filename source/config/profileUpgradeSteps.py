# -*- coding: UTF-8 -*-
#A part of NonVisual Desktop Access (NVDA)
#Copyright (C) 2016 NV Access Limited
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

from logHandler import log

def upgradeConfigFrom_0_to_1(profile):
	# Schema has been modified to set a new minimum blink rate
	# The blink rate could previously be set to zero to disable blinking (while still 
	# having a cursor)
	try:
		blinkRate = int(profile["braille"]["cursorBlinkRate"])
	except KeyError as e:
		# Setting does not exist, no need for upgrade of this setting
		log.info("No cursorBlinkRate, no action taken.")
		pass
	else:
		newMinBlinkRate = 200
		if blinkRate < newMinBlinkRate :
			profile["braille"]["cursorBlinkRate"] = newMinBlinkRate
			if blinkRate < 1 :
				profile["braille"]["cursorBlink"] = False