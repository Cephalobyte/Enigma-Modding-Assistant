from . import (
	sleep,

	flushprint,
	fadegraphic,
	fadegraphics,
)
from modules.filemanagement import openasciiart
from modules.utils import terminalsize


#------ animations -------------------------------------------------------------

def welcome():
	logo = openasciiart("logo")
	title = openasciiart("title")
	blues = [34,94,36]
	greys = [90,37,97]
	tw, th = terminalsize() #---------------------------------------------------terminal width & height

	th = max(len(logo), len(title), th)
	tw = max(*(len(s) for s in title), tw)
	flushprint(f'\33[8;{th};{tw}t') #-------------------------------------------resize window
	
	flushprint('\33[2J\33[0;0H\33[s') #-----------------------------------------erase display and save cursor position at top of screen
	fadegraphic(logo, blues) #--------------------------------------------------
	sleep(.25)
	
	fadegraphic(title, greys, transpace=True)
	sleep(1)

	fadegraphics(
		(logo, list(reversed(blues[1:]))),
		(title, list(reversed(greys[1:]))),
		transpace=True
	)

	flushprint('\33[2J\33[u') #-------------------------------------------------erase display and reset cursor position


def seeyounextmission():
	tw, th = terminalsize()
	message = 'See you next mission'
	msgl = len(message)
	speed = 2
	frame = 1/60

	message = [message[i:i+speed] for i in range(0, msgl, speed)] #-------------split every n character
	htw = (tw+1)//2
	hth = (th+1)//2
	clearcolsL = ('\33[1K│\33[1B\33[1D'*th)
	clearcolsR = ('\33[0K│\33[1A\33[1D'*th)
	clearrowsT = '\33[1J'
	clearrowsB = '\33[J'
	vbar = f'\33[2J\33[;{htw}H'+('│\33[1B\33[1D')*th #--------------------------vertical bar

	for x in range(1, htw, speed):
		start = f'\33[;{x}H'
		jump = tw-x*2
		switchside = f'\33[{jump}C'
		flushprint(start, clearcolsL, switchside, clearcolsR)
		sleep(frame)

	flushprint(vbar)
	sleep(frame)

	for y in range(1, hth, speed//2):
		start = f'\33[{y};{htw}H'
		jump = th-y*2
		switchside = f'\33[{jump}B'
		flushprint(start, clearrowsT, switchside, clearrowsB)
		sleep(frame)

	flushprint(f'\33[2J\33[{hth};{htw - (msgl//2)}H')

	for i in message:
		flushprint(i)
		sleep(frame)

	sleep(1)

	for i in range(0, th, speed):
		flushprint(f'\33[8;{th-i};{tw}t')
		sleep(frame)

