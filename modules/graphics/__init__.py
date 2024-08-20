from time import sleep

from modules.utils import terminalsize


#============ FUNCTIONS ================================================================================================


def flushprint(*msg): #---------------------------------------------------------
	"""Print messages and output immediately"""	
	print(*msg, sep='', end='', flush=True)


def drawgraphic(graphic, centered:bool=True, transpace:bool=False):
	"""Print a ascii art graphic
	:param graphic:
		list of strings
	:param centered:
		will write the graphic at the terminal center
	:param transpace:
		will skip space characters to not overwrite characters below
	"""

	if centered:
		tw, th = terminalsize() #-----------------------------------------------terminal width & height
		if (voffset := max(0, th - len(graphic)) // 2) > 0: #-------------------if there is a need for a vertical offset
			flushprint(f'\33[{voffset}B')

	for line in graphic:
		if centered:
			hoffset = max(0, tw - len(line)) // 2
			line = f'\33[{hoffset}G{line}' #------------------------------------place cursor where the line would be centered
		if transpace:
			line = line.replace(' ','\33[C') #----------------------------------skip space characters and move the cursor forward 
		
		flushprint(line,'\33[B')


def fadegraphic(
		graphic:list[str], colors:list[int]=[], delay:float=.125,
		centered:bool=True, transpace:bool=False
	):
	"""fade one graphic with a list of colors
		save the cursor position beforehand with escape code \\33[s for correct replacement
	"""
	
	for color in colors:
		flushprint(f'\33[u\33[{color}m') #--------------------------------------reset cursor position and apply color in list
		drawgraphic(graphic, centered, transpace) #-----------------------------draw graphic on screen
		sleep(delay) #----------------------------------------------------------wait until drawing next frame


def fadegraphics(
		*graphicswithgradient:tuple[list[str], list[str]],
		delay:float=.125,
		centered:bool=True,
		transpace:bool=False
	):
	"""fade multiple graphics simultaneously with an associated list of colors
	save the cursor position beforehand with escape code \\33[s for correct replacement
	"""

	for color in range(len(graphicswithgradient[0][1])): #----------------------for the number of colors in the first gradient

		for gwg in graphicswithgradient: #--------------------------------------for each group of graphic
			flushprint(f'\33[u\33[{gwg[1][color]}m') #----------------------=---reset cursor position and apply color in list
			drawgraphic(gwg[0], centered, transpace) #--------------------------draw graphic on screen

		sleep(delay) #----------------------------------------------------------wait until drawing next frame