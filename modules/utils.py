import os
import re


PATTERN_ESCAPESEQUENCE = r"\033\[.*?[A-z]"
PATTERN_NOTESCAPE = r"[^\033]*"


def terminalsize(axis:int|None=None)->tuple[int,int]|int:
	ts = os.get_terminal_size()
	match axis:
		case 0:
			return ts.columns
		case 1:
			return ts.lines
	
	return tuple(ts)


def invisiblen(txt:str):
	"""Find all escape sequences and return the sum of their lenght for
	screen-accurate adjusting, truncating, etc.
	"""
	return sum(list(map( #------------------------------------------------------sum of all lenghts of found invisible escape sequences
			len,
			re.findall(PATTERN_ESCAPESEQUENCE, txt)
		)))


def visiblen(txt:str):
	"""Find all escape sequences and return the lenght of the string minus the 
	sum of their lenght for screen-accurate justification, truncating, etc.
	"""
	return len(txt)-invisiblen(txt)


def truncatestringwidth(txt:str, maxlen:int, units:dict[str,int]):
	"""Truncate text based on font width"""
	tLen = 0

	for i, c in enumerate(txt):
		if (tLen := tLen + units.get(c, 1)) > maxlen:
			txt = txt[:i]
			return True
	return False


def micromapindexorder(width:int, height:int) ->list[int]:
	"""return a list of indexes to draw a proportional grid in ASCII using a
	single character to draw 2 tiles above eachother
	"""
	order = []

	for y in range(-(height // -2)): #------------------------------------------for each 2 rows,
		y *= 2
		for x in range(width): #------------------------------------------------for each columns,
			pair = (i := x*height + y), #---------------------------------------assign a tuple of one element (and remember its value)

			if y+1 < height: #--------------------------------------------------if not on the last row of an uneven grid height,
				pair += i+1, #--------------------------------------------------add the first value +1 to the pair

			order.append(pair)
	
	return order #--------------------------------------------------------------and peace to the galaxy


# def minimapindexorder(width:int, height:int):
# 	pass


def rowsfromlist(
		lst:list[str],
		cwidth:int = 14,
		csep:str = '║',
		cnumber:int = 2,
		rnumber:int = None,
		vertical:bool = False,
	) -> list[str] | tuple[list[str], list[int]]:
	"""Rearrange a list of strings into columns and return the rows for a more
	vertically compact display.  
	Takes escape sequences into account when calculating widths

	:param lst: the list of cells (must be 1D, strings only)
	:param cwidth: column width for strings to be justified & truncated. If 0 or
	less, justify by the maximum width of each column subtracted by this value
	:param csep: character to separate columns (not included in cwidth)
	of columns (ignores cnumber)
	:param cnumber: number of columns. determines number of rows if rnumber is None
	:param rnumber: number of rows. Set value to determine number of columns
	:param vertical: set to True to spread list from top to bottom first, as
	opposed to left to right first.
	"""

	if rnumber is None:
		rnumber = -(len(lst) // -cnumber) #-------------------------------------ceiling division
	else :
		cnumber = -(len(lst) // -rnumber)
	
	rows = []
	if (auto := cwidth < 1):
		maximums = [0]*cnumber

	for y in range(rnumber):
		line = ''

		for x in range(cnumber):
			i = (
				y*cnumber + x, #------------------------------------------------if list is spread from left to right
				x*rnumber + y #-------------------------------------------------if list is spread from top to bottom
			)[vertical]

			if x > 0:
				line += (csep,'\0')[auto] #-------------------------------------if we're past column 0, separate with character or leave empty to split later on if in automatic mode
			
			if i >= len(lst): #-------------------------------------------------if list is out of range, next 
				line += ' '*cwidth
				continue

			elem = lst[i]

			if auto: #========================================================== ▼▼▼ AUTO WIDTH MODE ▼▼▼ ===============
				line += elem
				maximums[x] = max(visiblen(elem), maximums[x])
				continue #====================================================== ▲▲▲ AUTO WIDTH MODE ▲▲▲ ===============


			matches = list(re.finditer( #---------------------------------------find all escape sequences
				rf"({PATTERN_NOTESCAPE})({PATTERN_ESCAPESEQUENCE}|$)",
				elem
			))

			if not matches[0].group(2): #---------------------------------------if no escape sequences were found, justify & trim normally
				line += elem.ljust(cwidth)[:cwidth]
				continue

			truewidth = cwidth #------------------------------------------------store desired column width
			elem = ''
			l1 = 0

			for match in matches:
				truewidth += len(match.group(2))

				if (l2 := l1 + len(match.group(1))) >= cwidth:
					elem += match.group(1)[:cwidth-l1] + match.group(2)
					continue

				l1 = l2
				elem += match.group(1) + match.group(2)
			
			line += elem.ljust(truewidth)

		rows.append(line)

	if auto: #================================================================== ▼▼▼ AUTO WIDTH MODE ▼▼▼ ===============
		rows = [
			csep.join([
				col.ljust(maximums[x] + invisiblen(col) - cwidth) #----------justify by the maximum, plus the hidden length, plus the column width offset
				for x, col in enumerate(row.split('\0'))
			])
			for row in rows
		] #===================================================================== ▲▲▲ AUTO WIDTH MODE ▲▲▲ ===============
	
	return rows


def getnestedvalue(dct:dict|list, keys:list, defau=None):
	"""Get the value from a nested dictionary from a path consisted of a list of
	keys

	:param dct: The dictionary
	:param keys: The keys to search within the nested dictionary
	:param defau: default value to return if one key doesn't exist
	"""

	for k in keys:
		try:
			dct = dct[k]
		except KeyError|ValueError|IndexError: #--------------------------------if key not found or index invalid or out of range, return default value
			return defau
	
	return dct


def setnestedvalue(dct:dict|list, keys:list, value, default=None):
	"""Set the value of a nested key in a dictionary from a path consisted of a
	list of keys if path is valid
	
	:param dct: The dictionary/list
	:param keys: The keys to search within the nested dictionary
	:param value: the value to set at the last key
	:param defau: value to assign to keys out of range of a list
	"""
	#Inspired from https://stackoverflow.com/a/13688108
	for k in keys[:-1]:
		try:
			dct = dct[k]
		except KeyError:
			dct.setdefault(k, {})
		except IndexError:
			if type(k) is int:
				while k >= len(dct): #------------------------------------------as long as the key is out of range, fill with default values
					dct.append(default)
				dct = dct[k]
			else:
				return

	dct[keys[-1]] = value


#============ Sorting ==================================================================================================

def sortdictbypriority(dct:dict, prior:list[str|list[str]]=[]): #old method
	"""Orders dictionary by key in case-insensitive alphabetic order.
	It will sort every key from the first row of :prior:, then the second, etc.

	:param dct: 
	:param prior:
	
	example:

	    [
	        ['x', 'y'],
	        'width',
	        'height',
	    ]
	"""
	items = dct.items()

	if len(prior) == 0:	#if there are no priorities,
		return dict(sorted(items, key=lambda k:k[0].swapcase()))	#sort dictionary alphabetically, ignore case

	def sor(key):
		k = key[0]
		i = len(items)	#default order is last

		for pi, pn in enumerate(prior):
			if k == pn or k in pn: i = pi	#if key is or is in the priority name/names, set the order to the priority index
		
		return (i, k.swapcase())	#return the order as key, content as value

	return dict(sorted(items, key=sor))


def sortdictbylist(dct:dict, order:list=[])->dict:
	"""Orders dictionary by given list of keys, then puts the rest after

	:param dct: original dictionary
	:param order: list of key names (if not present, skips)
	"""
	dico = {k: dct[k] for k in order if k in dct} #create a new dictionary based off the old, but following the given list's order
	dico.update(dct.items()) #put the rest of the items after
	return dico


#============ Readability ==============================================================================================

def dec2bin(num:int) ->str:
	return bin(num).removeprefix('0b')


def splittile():
	pass


def decbgr2rgb(col:int) ->list[int]:
	col = col%16777216
	r = col%256
	g = col//256%256
	b = col//(256**2)
	return [r,g,b]