from sys import exc_info, exit
from os import path as osp
from time import sleep
import re
import sys

sys.path.insert(0, sys.path.pop(0).removesuffix('\\modules')) #-----------------set root directory

from modules.menus import MenuInfo
from modules.filemanagement import (
	SelectionSummary,
	MPFileType,
	FILETYPES_VALIDCOLORS,

	openasciiart
)
from modules.utils import (
	rowsfromlist,
	terminalsize,
	# visiblen
)
from modules.graphics import (
	GWG,

	flushprint,
	fadegraphic,
	fadegraphics
)


#------ Info / Debugging -------------------------------------------------------

def header(title:str, big:bool=False, size:int=80):
	"""Print a header for clear navigation"""
	headr = []
	speed = size//10
	size -=2 #------------------------------------------------------------------to simplify the procedural ascii header
	frame = 1/60

	if big: #-------------------------------------------------------------------if big, give vertical padding to the borders
		headr.append('█'+ ('▀'*size) +'█')
		headr.append(f'█{title.center(size)}█')
		headr.append('█'+ ('▄'*size) +'█')
	else:
		headr.append(' '+ ('▄'*size) +' ')
		headr.append(f' █{title.center(size-2)}█ ')
		headr.append(' '+ ('▀'*size) +' ')

	size = (size+2) // speed #--------------------------------------------------get back to the original size and divide it by the speed
	bar = '▒'*(speed-1)+'█' #---------------------------------------------------build a "whoosh" effect to print as the header appears
	
	flushprint('\n\n\n\33[32m')#------------------------------------------------feed newlines to scroll up (if at bottom of screen)and activate the green coloration

	for i in range(size):
		j = i*speed
		k = j + speed
		if i == size-1: #-------------------------------------------------------if it's the last step, don't put a whoosh
			bar = ''

		flushprint(f'\33[2A\33[{j+1}G', headr[0][j:k], bar) #-------------------go up 2 lines, set the horizontal position and print the segment of characters in the 1st row of the header plus the whoosh bar
		flushprint(f'\33[B\33[{j+1}G', headr[1][j:k], bar) #--------------------go down 1 line, set the horizontal position and print the segment of characters in the 2nd row of the header plus the whoosh bar
		flushprint(f'\33[B\33[{j+1}G', headr[2][j:k], bar) #--------------------go down 1 line, set the horizontal position and print the segment of characters in the 3rd row of the header plus the whoosh bar
		sleep(frame)
		
	flushprint('\n\033[39m') #--------------------------------------------------feed a newline and set the text color to the original


def breadcrumbtrail(breadcrumbs:list[str]) ->str:
	return '\033[92m> '+' > '.join(map(str, breadcrumbs)) +'\033[39m\n'


def steptodo(step:str, newline:bool=False):
	"""Instruct the user on what to do"""
	print(('','\n')[newline] + f' {step} '.center(80,'='))


def protip(tip:str, defau=False):
	"""Print useful info

	:param defau: highlight this tip for describing a default value for example
	"""
	col = ('94','96')[defau]
	print(f'\033[{col}m(i) '+ tip +'\033[0m')


def optiontip(
		id,
		tip:str,
		margin:int = 3,
		defau:bool = False,
		dis:bool = False
	) -> str:
	"""Print an option with a description

	:param id: option identifier
	:param tip: option description
	:param margin: margin length to separate the columns evenly
	:param defau: true appears cyan instead of blue
	:param dis: true appears darker
	:param ret: true returns result, otherwise print directly
	"""
	esc = ('','\033[90m')[dis]
	opt = str(id).rjust(margin)
	col = ('9','3')[dis] + ('4','6')[defau]
	tip = f' : \033[{col}m{tip}\033[0m'
	
	return esc + opt + tip


def progress(prog:str, done=False):
	"""Report the step progression"""
	if not done: prog += '...'
	print('\033[95m'+f' {prog} '.center(80,'▒') +'\033[0m')


def woops(warn:str, stop:bool=False):
	"""Print a warning

	:param stop: will pause the program until user presses enter
	"""
	print('\033[4;33m/!\\'+ warn.center(74,'_') +'/!\\\033[0m')

	if stop:
		pe2c()
	else:
		sleep(.5)


def ohno(err:str, stop:bool=True, out:bool=True):
	""""Print an error

	:param stop: will pause the program until user presses enter
	:param out: will kill the program after the optional user interaction
	"""
	#stolen from https://stackoverflow.com/questions/1278705/when-i-catch-an-exception-how-do-i-get-the-type-file-and-line-number
	exc_type, exc_obj, exc_tb = exc_info()
	del exc_obj
	fname = osp.split(exc_tb.tb_frame.f_code.co_filename)[1]
	print('\033[4;91m[!]'+f' {err} '.center(94,'_')+'[!]', end='\n\033[0;0m')
	print(str(exc_type))
	print(fname+f' line {exc_tb.tb_lineno}')

	if not stop or not out:
		sleep(1)
	if stop:
		pe2c()
	if out:
		exit()


def painttext(r:int, g:int=0, b:int=0, bg:bool=False) ->str:
	"""Return a colored escape sequence from r, g and b values (give at least red value)
	
	:param bg: true to affect the background
	"""
	esc = ('38','48')[bg]
	return f'\033[{esc};2;{r};{g};{b}m'


def welcome():
	logo = openasciiart("logo")
	title = openasciiart("title")
	blues = [30,34,94,36]
	greys = [30,90,37,97]
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
		GWG(logo, list(reversed(blues[1:]))),
		GWG(title, list(reversed(greys[1:]))),
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


#------ Type info --------------------------------------------------------------

def boolinfo(value:bool|int, label:str='', look:str|None=None) ->str:
	if look is None:
		look = value
	
	esc = '\033['+ ('91','92')[value] +'m'
	look = f'{look}\033[39m'
	if label:
		label += ' : '
	
	return label + esc + look


def pageinfo(value:int, maximum:int=2, label:str='Preview') ->str:
	value += 1
	if label:
		label += ' : '
	return f'< {label}{value}/{maximum} >'


def mpfiletypeinfo(value:MPFileType, look:str|None=None) ->str:
	if look is None:
		look = value.type
	
	esc = '\033[' + ('4;3','9')[value.is_compressed]
	color = FILETYPES_VALIDCOLORS.get(value.type, '1')
	esc += color + 'm'
	
	return esc + look + f"\033[{('24;','')[value.is_compressed]}39m"


#------ Dialog -----------------------------------------------------------------

def pe2c():
	"""'Press Enter to continue' Pause the script until user interaction"""
	input('\033[4mPress Enter to continue...\033[24m')


def yesnodialog(question:str, tips:list=[], defau:bool|None=None) ->bool:
	"""Get a boolean from a "yes or no" dialog input

	:param question: the question to ask
	:param tips: optional list of strings to provide details
	:param defaut: optional default value (bool). If set to None, will ask the
	question again if the user doesn't type a string starting with "y" or "n"
	(ignore case)
	"""

	if defau is not None:
		prompt = ('y/\033[96mn\033[0m', '\033[96my\033[0m/n')[defau]
		prompt = f'({prompt}):'
	else:
		prompt = '(y/n): '

	def readyn():
		if not (yn := input(prompt)): #-----------------------------------------if question is skipped, return default answer
			return defau
		if yn.casefold().startswith('y'):
			return True
		if yn.casefold().startswith('n'):
			return False
		return None	#if invalid
	
	steptodo(question, True)
	for tip in tips:
		protip(tip)

	while (answer := readyn()) is None:	#---------------------------------------if the answer is invalid, ask again
		woops("I'll need you to type either y or n")
		steptodo(question)
	
	return answer


def numberdialog(
		question:str,
		tips:list = [],
		defau:int|float|None = None,
		acceptdecimals:bool = False
	) ->int|float:
	"""Get an integer or a float from a dialog input"""

	def readnum():
		if defau is not None:
			print(f'\033[s\033[90m{defau}\033[u\033[39m', end='')
		
		if not (num := input()): #----------------------------------------------if question is skipped, return default answer
			return defau
		try:
			return int(num)
		except ValueError:
			if acceptdecimals:
				try:
					return float(num)
				except ValueError:
					pass
		return None

	steptodo(question, True)
	for tip in tips:
		protip(tip)
	
	while (answer := readnum()) is None: #--------------------------------------if the answer is invalid, ask again
		woops("I'll need you to type a valid number")
		steptodo(question)
	
	return answer


def textdialog(
	question:str = '',
	tips:list = [],
	defau:str|None = None,
	maxlen:int|None = None,
	units:dict[str,int] = {},
):
	"""Get a string within limits if given, measured by units (all chars default
	to 1)
	
	Usage::

	    textdialog(
	        "What's your name?',
	        [
	            'answer honestly',
	            'last, first'
	        ],
	        'Doe, John',
	        25,
	        {
	            'i':1
	            'a':2
	            'w':3
	        }
	    )
	"""
	uName = ' chars' if not units else 'px'
	if defau is not None:
		tips = tips.copy() + ['Leave empty to keep current string'] #-----------copy "tips" to prevent reference and constantly adding the same tip if asked again
	if maxlen is not None:
		tips += [f"String length should be under {maxlen}{uName}"]
	
	def readtext():
		if defau is not None:
			print(f'\033[s\033[90m{defau}\033[u\033[39m', end='')
		
		if not (text := input()): #---------------------------------------------if question is skipped, return default answer
			return defau
		
		if maxlen is not None:
			if units is not None:
				tLen = 0
				for i, c in enumerate(text):
					print(i, c, tLen, maxlen, sep='\t')
					if (tLen := tLen + units.get(c, 1)) > maxlen:
						text = text[:i]
						progress(f'String length over maximum ({tLen}{uName})')
						progress('Truncated to '+text, True)
						break

			else:
				text = text[:maxlen]
		
		return text

	steptodo(question, True)
	for tip in tips:
		protip(tip)
	
	while (answer := readtext()) is None:
		woops(f"I'll need you to type something")
		steptodo(question)

	return answer


def filepathdialog(
		question:str = '',
		tips:list = ['You can drag & drop your file here'],
		defau:str|None = None,
		acceptdir:bool = False,
		acceptfile:bool = True,
	) ->str:
	"""Get a file or directory path from a dialog input"""

	accepted = []
	if acceptfile:
		accepted.append('file')
	if acceptdir:
		accepted.append('directory')
	accepted = ' or '.join(accepted)

	if not question:
		question = f'Enter the {accepted} path'
	
	if defau is not None:
		tips = tips.copy() + ['Leave empty to keep current path'] #-------------copy "tips" to prevent reference and constantly adding the same tip if asked again

	def readpath():
		if defau is not None:
			print(f'\033[s\033[90m{defau}\033[u\033[39m', end='')
		
		if not (path := input().strip('"\'& ').rstrip('\\/')): #----------------strip drag n drop characters (' and & is for vscode's terminal) & directory trailing slashes
			return defau #------------------------------------------------------if question is skipped, return default answer
		if acceptdir and osp.isdir(path):
			return path
		if acceptfile and osp.isfile(path):
			return path
		return None

	steptodo(question, True)
	for tip in tips:
		protip(tip)
	
	while (answer := readpath()) is None: #-------------------------------------if the answer is invalid, ask again
		woops(f"I'll need you to type a valid {accepted} path")
		steptodo(question)
	
	return answer


def listdialog(
		question:str,
		tips:list[str]=[],
		separator:str=' ',
		file:bool=False
	) ->list[str]:
	"""Get a list of entries from one input

	:param question: the question to ask
	:param tips: optional list of strings to provide details
	:param separator: the string to split the input
	:param file: looks for file paths with drive at the beginning of the path
	"""
	steptodo(question, True)
	for tip in tips:
		protip(tip)

	answer = input()
	
	if not file:
		#---- regular mode ------
		return answer.split(separator)

	#----- file mode --------
	# pat = r"[A-z]:.*?(?:(?=[A-z]:)|$)"
	pat = r"(?:[A-z]:|\.+[\\\/])[^:<>|]*?(?:(?=[A-z]:)|(?=\.+[\\\/])|$)" #------either (?: a drive letter [A-z]: or a relative path \.+[\\\/] ) followed by any valid path character [^:<>|]*? until either (?: a drive letter or a relative path or end of string $ )
	
	fPaths = [f.strip('\'" &') for f in re.findall(pat, answer)] #--------------make a list of found paths stripped of quotes, spaces and drag n drop symbols

	return fPaths


def optiondialog(
		question:str,
		options:list[str],
		others:dict[str,str] = {},
		defau:int|str|None=None,
		disabled:list[int|str]=[],
		cnumber:int=0
	) ->int|str:
	"""Get an integer or other value from a list of choices

	:param question: the question to ask
	:param options: numbered options, usually common and not very restrictive
	:param others: keyed options, usually more specific or present in many dialogs
	:param defau: default value. If set to None, will require the user to choose
	an option
	:param disabled: disable options in list from being valid & render them darker
	:param cnumber: amount of columns to separate options
	"""
	margin = 3
	if others: #----------------------------------------------------------------if there are extra options, set margin to the maximum between the maximum key length and 3
		margin = max(len(max(others.keys(), key=len))+1, 3)

	# cwidth = visiblen(max(options+list(others.values()), key=visiblen))+margin+3 #-----------maximum option description width + margin width + 3 (' : ')

	def formatoptiontip(i, tip) ->str:
		return optiontip(i, tip, margin, i==defau, i in disabled)
	
	def printoptions(optioniterator):
		if cnumber < 1: #======================================================= Vertical list
			for i, tip in optioniterator:
				print(formatoptiontip(i, tip))
			return
		#======================================================================= Rows of columns
		rows = rowsfromlist(
				[
					formatoptiontip(i, tip)
					for i, tip in optioniterator
				],
				-1,
				'',
				cnumber,
				vertical=True,
			)
		
		print(*rows, sep='\n')

	def readoption(): #---------------------------------------------------------interpret user input
		if not (opt := input()): #----------------------------------------------if question is skipped, return default value
			return defau
		if (other := [ #--------------------------------------------------------make a list of other options that match user input
				k for k in others.keys()
				if opt.casefold() == k.casefold()
			]): #---------------------------------------------------------------if there is a match, return first match
			return other[0]
		if opt.isdecimal() and (opt := int(opt)) in range(len(options)): #--------if option is a number and is in the option list,
			return opt
		return None	#-----------------------------------------------------------if invalid

	def verifyenabled():
		if (answer := readoption()) in disabled: #------------------------------if chosen option is disabled, return as invalid
			return None
		return answer

	steptodo(question, True)
	printoptions(enumerate(options))
	printoptions(others.items())

	while (answer := verifyenabled()) is None:	#-------------------------------if the answer is invalid, ask again
		woops("I'll need you to type one of the valid options")
		steptodo(question)

	return answer


def menudialog(
		menuinfo: MenuInfo,
		selsum: SelectionSummary,
		bigheader: bool = False,
		message: tuple[str, ...] = (),
		columnwidth: int = 0,
	):
	"""Return option from an option dialog with a menu aesthetic

	:param menuinfo: the menu information containing title, options, etc.
	:param selsum: summary of a selection
	:param bigheader: whether or not the header should appear big
	:param message: the message(s) that appear below the header
	:param columnwidth: set how many columns of options would fit in the terminal
	with given width. set to 0 to display options in a simple vertical list.
	"""
	# :param selectiontypes: the simplified information about the selection
	header(menuinfo.title, bigheader)

	if message:
		print(*message, sep='\n')
	
	cnumber = 0
	if columnwidth > 0:
		cnumber = terminalsize(0) // columnwidth

	return optiondialog(
		menuinfo.prompt,
		menuinfo.primary_options,
		menuinfo.secondary_options,
		menuinfo.default_value,
		menuinfo.getdisabledoptions(selsum),
		cnumber
	)


def polymenudialog(
		menuinfo: MenuInfo,
		selsum: SelectionSummary,
		bigheader: bool = False,
		message: tuple[str, ...] = (),
		columnwidth: int = 0,
		strict: bool = False
	) -> list[int|str]:
	"""Return a list of requests from the given options with a menu aesthetic

	:param menuinfo: the menu information containing title, options, etc.
	:param selectiontypes: the simplified information about the selection
	:param bigheader: whether or not the header should appear big
	:param message: the message(s) that appear below the header
	:param columnwidth: set how many columns of options would fit in the terminal
	with given width. Set to 0 to display options in a simple vertical list.
	:param strict: filter user requests down to the given options
	"""
	# disabled = menuinfo.getdisabledoptions(selectiontypes)
	disabled = menuinfo.getdisabledoptions(selsum)
	primaries = menuinfo.primary_options
	secondaries = menuinfo.secondary_options

	margin = 3
	if secondaries:
		margin = max([
			len(max(secondaries.keys(), key=len))+1,
			margin
		])
	
	# cwidth = visiblen(max(options+others, key=visiblen)) + mrgn + 3 #-----------maximum option description width + margin width + 3 (' : ')
	
	if strict:
		# options = list(map(str, range(len(menuinfo.primary_options))))
		validoptions = list(range(len(primaries)))
		validoptions += list(secondaries.keys())
		# disabled = list(map(str, disabled))
	
	def formatoptiontip(i, tip) ->str:
		return optiontip(
			i,
			tip,
			margin,
			i in menuinfo.default_value.split(' '),
			i in disabled
		)

	def printoptions(optioniterator):
		if columnwidth < 1: #=================================================== Vertical list
			for i, tip in optioniterator:
				print(formatoptiontip(i, tip))
			return
		#======================================================================= Rows of columns
		cnumber = terminalsize(0) // columnwidth #------------------------------division by 0 avoided with by guarding column width

		print(
			*rowsfromlist(
				[
					formatoptiontip(i, tip)
					for i, tip in optioniterator
				],
				-1,
				'',
				cnumber,
				vertical=True
			),
			sep='\n'
		)
	
	header(menuinfo.title, bigheader)
	
	if message:
		print(*message, sep='\n')

	steptodo(menuinfo.prompt, True)
	protip('you can tweak multiple values by separating options with a space')
	printoptions(enumerate(primaries))
	printoptions(secondaries.items())

	while True: #---------------------------------------------------------------start a loop
		if not (answer := input()): #-------------------------------------------if the user inputs nothing, return default value
			requests = menuinfo.default_value.split(' ')
			break
		
		requests = answer.split(' ')
		for i, r in enumerate(requests): #--------------------------------------for each request in answer,
			if r.isdecimal():
				requests[i] = r = int(r) #--------------------------------------convert to digit

			if r in disabled or ( #---------------------------------------------if the request is a disabled option...
				strict and r not in validoptions #------------------------------------or is not in the options when the menu is strict,
			):
				requests[i] = None #--------------------------------------------mark request for deletion
				progress(f"{r} removed")
			
		if (requests := [r for r in requests if r is not None]): #--------------filter invalid requests
			break #-------------------------------------------------------------if some requests are left, break the loop to return them

		woops('No valid requests were found, try again') #----------------------if not, start the loop over
	
	progress('Requests : '+', '.join([str(r) for r in requests]), True)
	return requests