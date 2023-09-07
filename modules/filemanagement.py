from typing import NamedTuple
import os
from os import path as osp
import json, zlib
import re
from glob import glob
import sys

sys.path.insert(0, sys.path.pop(0).removesuffix('\\modules')) #-----------------set root directory

from modules.utils import (
	visiblen,
	invisiblen
)
#to prevent circular dependency with dialog.py, importing functions from the
#module is done in each function that requires it

#============ CLASSES ==================================================================================================

class MPFileType(NamedTuple):
	"""Tuple for classification of the file type depending on its extension or
	its prefix
	
	type:
	- `room`
	- `world`
	- `save`
	- `data`
	- `palette`

	is_compressed:
	- `True` if extension starts with `.mp_` and ends with file type
	- `False` if extension is `.json` and file name starts with file type
	"""
	type: str = ''
	is_compressed: bool = True


class SelectionSummary(NamedTuple):
	"""Summary of a selection's content

	multiple:
		0 if selection is empty, 1 if one, 2 if multiple
	types:
		every unique type (including compression) present in selection
	are_compressed:
		every matching compression state of the types list
	"""
	multiple: int = 0
	types: list[str] = []
	are_compressed: list[bool] = []


class SelectionInfo(NamedTuple):
	"""Tuple containing precalculated selection information when passing selection
	to a submodule

	file_paths:
		list of all file paths in selection
	file_types:
		list of MPFileType respective to each path 
	selection_types:
		SelectionTypes, or summary of the selection's content
	discriminators:
		list of clues to filter the selection's items when getting or setting datas
	"""
	file_paths: list[str] = []
	file_types: list[MPFileType] = []
	discriminators: list[str|int|bool] = []


	def _getvalidtypes(self) ->list[MPFileType]:
		disc = self.discriminators
		discC = [c for c in disc if type(c) is bool] #--------------------------discriminators for compression
		
		return [ #--------------------------------------------------------------list of MPFileType not discriminated
			mpft for mpft in self.file_types
			if mpft.type not in disc
			and mpft.is_compressed not in discC
		]

	
	def getsummary(self) ->SelectionSummary:
		"""Obtain a simplified summary of the valid contents of the selection"""
		# disc = self.discriminators
		# discC = [c for c in disc if type(c) is bool] #--------------------------discriminators for compression
		
		# validtypes = [ #--------------------------------------------------------list of MPFileType not discriminated
		# 	mpft for mpft in self.file_types
		# 	if mpft.type not in disc
		# 	and mpft.is_compressed not in discC
		# ]
		validtypes = self._getvalidtypes()
		uniquetypes = list(set(validtypes)) #-----------------------------------list of unique valid MPFileType

		#stolen from https://stackoverflow.com/a/8081580
		if (sTypes := tuple(map(list, zip(*uniquetypes)))): #-------------------unpack tuple of lists from list of tuples
			types = sTypes[0]
			arecompressed = sTypes[1]
		else:
			types, arecompressed = [], [] #-------------------------------------if tuple was empty, store 2 empty lists, not 1

		return SelectionSummary(
			min(len(validtypes), 2), #------------------------------------------remember simplified amount
			types,
			arecompressed
		)


	def getdatas(self) ->dict[int, list[dict]]:
		"""Get a dictionary with indexed datas (a list of 1/2 dictionaries)
		limited by the discriminators
		"""
		datas = {}
		# fTypes = self.file_types
		fPaths = self.file_paths
		# discs = self.discriminators

		for i, ft in enumerate(self._getvalidtypes()):
			if ft.is_compressed:
				data = mptodict(fPaths[i])
			else:
				data = jsontodict(fPaths[i])
			
			if data is None:
				continue

			datas[i] = data

		# for i, fp in enumerate(self.file_paths):
		# 	if (
		# 		fTypes[i].type not in discs and
		# 		fTypes[i].is_compressed not in discs
		# 	):
		# 		if fTypes[i].is_compressed:
		# 			data = mptodict(fp)
		# 		else:
		# 			data = jsontodict(fp)

		# 		if data is None:
		# 			continue

		# 		datas[i] = data


		return datas
	

	def setdatas(self, datas:dict[int, list[dict]]):
		fPaths = self.file_paths
		fTypes = self.file_types
		discs = self.discriminators

		for i, d in datas.items():
			if (
				fTypes[i].type not in discs and
				fTypes[i].is_compressed not in discs
			):
				if fTypes[i].is_compressed:
					dicttomp(d, fPaths[i])
				else:
					dicttojson(d, fPaths[i])

	
	def send(
			self,
			option:int|str,
			menudiscriminators:dict[int|str,list[str|bool]]={},
		):
		"""Update the selection's discriminators from the chosen menu option for
		disabling the correct submenu options when sending it"""
		self.discriminators.extend(
			menudiscriminators.get(option, [])
		)
	

	def reclaim(self, discriminators:list[str|int|bool]=[]):
		"""Update the selection's discriminators for disabling the correct menu
		options when reclaiming it"""
		self.discriminators.clear()
		self.discriminators.extend(discriminators)


#============ CONSTANTS ================================================================================================

FILETYPES_VALIDCOLORS = {
	'room':		'6', #cyan
	'world':	'4', #blue
	'save':		'2', #green
	'data':		'3', #yellow
	'palette':	'5', #purple
}

ROOTDIR = osp.dirname(osp.abspath(__file__)).removesuffix('\\modules')

#============ GENERIC ==================================================================================================

def listfilesindir(dir:str, ext:str|None=None) ->list[str]:
	"""Return a list of every file in the specified directory
	filtered by its extension (if given)
	"""
	fileList = []
	for de in os.scandir(dir):
		if de.is_file():
			if ext is not None and de.name.endswith(ext): #---------------------if is a file and ends with the extension
				fileList.append(de[-len(ext):])
			else:
				fileList.append(de)
	return fileList


def getshortname(path:str, typ:str|None=None) ->str:
	"""get the name part of a filepath without its extension"""
	shortname = osp.splitext(osp.split(path)[1])[0]
	if typ is None:
		return shortname
	return shortname.removeprefix(typ+'.')
	

#------ 1.27g decoding -------------------------------------------------------------------------------------------------

# def unsalt():
# 	pass


# def salt():
# 	pass


#------ Importing ------------------------------------------------------------------------------------------------------

def opentxt(path:str) ->str:
	with open(path) as file:
		return file.read()


def openjson(path:str) ->dict:
	with open(path) as file:
		return json.loads(file.read())	#store file content in string


#------ Exporting ------------------------------------------------------------------------------------------------------

def writetxt(path:str, text:str, openFile:bool=False):
	with open(path, 'wb') as file:
		file.write(text.encode())	#-------------------------------------------write string into new text file
	if openFile: os.system('notepad.exe '+ path)


def writejson(path:str, obj:dict, ind:int=4):
	with open(path, 'wt') as file:
		file.write(json.dumps(obj, indent=ind))	#-------------------------------write json string to a new text file


#============ PLANETS ==================================================================================================

def mpfiletypefrompath(fPath:str) ->MPFileType:
	"""Identify the file type and compression state of a file path
	"""
	
	fName, fExt = osp.splitext(osp.split(fPath)[1])

	if fExt == '.json': #-------------------------------------------------------if uncompressed (decrypted) into a json
		fType = fName.split('.')[0] #-------------------------------------------find prefix
		return MPFileType(fType, False)
	
	fType = fExt.removeprefix('.mp_') #-----------------------------------------clean from prefix
	return MPFileType(fType, True)


def mpfileselection(
		discriminators: list[str|int|bool] = [],
		mandatory: bool = False
	) -> SelectionInfo:
	"""Automatically fill a SelectionInfo from user input
	
	:param discriminators: list of indicators to ignore items selected
	:param mandatory: simple progress message change
	"""
	from modules.dialog import listdialog, progress
	
	for fp in (fPaths := listdialog(
			'Enter the filepaths to use',
			[
				'Drag & drop your files here one by one',
				'Use .\ for paths relative to '+ROOTDIR,
				'Use *, **, ?, [a-z], etc. as glob pattern wildcards'
			],
			file=True
		)):
		fName = osp.split(fp)[1]

		if fPaths.count(fp) > 1:
			progress(f'{fName} already selected')
			fPaths.remove(fp)
			continue

		print('current path is :',fp)

		if any(fp.count(char) for char in '*?['): #-----------------------------if glob wildcards are present in the path,
			if (newpaths := glob(fp, root_dir=ROOTDIR, recursive=True)): #------if a glob search returns results,
				ifp = fPaths.index(fp)
				fPaths = fPaths[:ifp] + newpaths + fPaths[ifp:] #---------------insert new paths in selection
				fPaths.remove(fp) #---------------------------------------------remove glob pattern from path list
				continue
		
		if not osp.isfile(fp):
			progress(f"{fName} can't be found")
			fPaths.remove(fp)
	
	# print(*fPaths, sep='\n')
	# progress('Cleaning up')
	
	fPaths = [ #----------------------------------------------------------------filter valid file types from fPaths
		fp for fp in fPaths
		if any(
			fp.endswith('.mp_'+ext) or (
				fp.endswith('.json') and
				osp.split(fp)[1].startswith(ext+'.')
			)
			for ext in FILETYPES_VALIDCOLORS
		)
	]
	
	if not fPaths: #------------------------------------------------------------if fPaths is empty, return empty selection
		progress((
			'Selection cleared',
			'Operation cancelled'
		)[mandatory], True)
		return SelectionInfo()

	fTypes = [mpfiletypefrompath(fp) for fp in fPaths] #------------------------MPFileTypes of each path (type & compression state)

	progress('Selection updated!', True)
	return SelectionInfo(
		fPaths,
		fTypes,
		discriminators
	)


def mpselectionpreview(selection:SelectionInfo) ->str:
	"""Generate and return 2 lines that shows a preview of the currently selected
	files
	"""
	if not selection.file_paths:
		return 'no current selection'

	line1 = f'current selection ({len(selection.file_paths)}):' #---------------prepare 1st line
	
	# discT = [t for t in selection.discriminators if type(t) is str]
	discC = [c for c in selection.discriminators if type(c) is bool]
	fTypeColors = {
		t: col
		for t, col in FILETYPES_VALIDCOLORS.items()
		if t not in selection.discriminators
	}

	legend = []
	for typ, col in fTypeColors.items():
		el = '\33['
		if True not in discC:
			el += f'9{col}m■\33['
		if False not in discC:
			el += f'4;3{col}m■\33[24;'
		el += f'39m: {typ} '

		legend.append(el)
	
	legend = ' '.join(legend)
	
	selectionPreview = ''
	i = 0

	while i < len(selection.file_paths):
		fType = selection.file_types[i] #---------------------------------------get file type from path's index
		esc = '\33[' + ('4;3','9')[fType.is_compressed] #----------------------prepare escape sequence (bright if compressed)
		if fType.is_compressed in discC:
			esc += '1m'
		else:
			esc += fTypeColors.get(fType.type, '1') + 'm' #---------------------identify the file's type and assign a color (red if unsupported)
		
		shortname = getshortname(selection.file_paths[i], fType.type) #---------get the file name and strip its extension...
		shortname = esc + shortname + '\33[24;39m' #------------------=---------add escape coloring to the short file name

		if len(prediction := selectionPreview + shortname) - \
		visiblen(prediction) > 90 : #-------------------------------------------if the list would become too long
			selectionPreview += ' ...' #----------------------------------------add "..." instead
			break #-------------------------------------------------------------and stop

		if i > 0 : selectionPreview += ', ' #-----------------------------------add comma separators after the first item
		selectionPreview += shortname #-----------------------------------------add name to preview
		i += 1
	
	justify = 80 + invisiblen(legend) - visiblen(line1)
	line1 += legend.rjust(justify) +'\n'

	return line1 + selectionPreview


def mpselectedpreview(selection:SelectionInfo, index:int) ->str:
	from modules.dialog import mpfiletypeinfo
	
	fPath = selection.file_paths[index]
	fType = selection.file_types[index]
	shortname = getshortname(fPath, fType.type)
	
	return mpfiletypeinfo(fType, shortname)


#------ Importing ------------------------------------------------------------------------------------------------------

def mptodict(fPath:str) ->list[dict]|None:
	"""Read a Metroid Planets file and returns it as a list of dict
	"""
	with open(fPath, "rb") as file: #-------------------------------------------read the file
		red = file.read()
	
	try:
		decompressedData = zlib.decompress(red).decode() #----------------------decode bytes text to string
		jsonData = decompressedData.split('\x00') #-----------------------------separate the string every NUL char and store it as a list
		jsonData = [json.loads(obj) for obj in jsonData[:-1]] #-----------------This is a cool line. Basically, you apply a function to every item of a list except the last item with [:-1] (since it's always empty). In that case, the json module translates a string into a python dictionary (equivalent to a javascript object)
	
	except Exception as e:
		from modules.dialog import ohno

		ohno(e, out=True)
		return None

	return jsonData


def jsontodict(fPath:str) ->list[dict]|None:
	"""Read a JSON of a decrypted Metroid Planets file and returns it as a list of dict
	"""
	with open(fPath, 'rt') as file: #-------------------------------------------read the file
		jsonText = file.read()
		
	from modules.dialog import ohno, pe2c

	try:
		jsonData = jsonText.split('\\x00') #------------------------------------separate the text each time there's a fake NUL char and put the items in a list
		jsonData = [json.loads(obj) for obj in jsonData] #----------------------convert every string of the list into a python dictionary
	
	except json.decoder.JSONDecodeError as e: #---------------------------------print error and snippet of the wrong part
		ohno(e, False, False)
		print(e.doc[max(e.pos-100, 0) : e.pos],
			'\33[41;97m',
			e.doc[e.pos : min(e.pos+100, len(e.doc))],
			'\33[0m',
			sep=''
		)
		pe2c()
		return None

	except Exception as e: #----------------------------------------------------...If something went wrong, print the error (without closing the terminal)
		ohno(e, out=False)
		return None

	return jsonData


#------ Exporting ------------------------------------------------------------------------------------------------------

def getvalidfilename(fName:str, substitute:str='_') ->str:
	"""Replace every invalid character from path by a valid substitute"""
	invalidchars = '\\\/:*?"<>|'
	pattern = rf'[{invalidchars}]'
	if substitute in invalidchars:
		substitute = '_'

	return re.sub(pattern, substitute, fName)


def dicttomp(jsondata:list[dict], fPath:str, overwrite:bool=False) ->bool:
	"""Write a Metroid Planets file from a list of dicts
	"""
	
	if not overwrite and osp.exists(fPath):
		from modules.dialog import yesnodialog, woops
		
		woops(f'File {osp.split(fPath)[1]} already exists')
		if not yesnodialog(
			'Overwrite file?',
			defau=False
		):
			return False
	
	try:
		decompressedData = [json.dumps(dico) for dico in jsondata] #------------make every dictionary of the list a string again, but with a compact and optimized format
		decompressedData = '\x00'.join(decompressedData)+'\x00' #---------------put every json object back together, separated with a NUL char and a NUL at the end
		compressedData = zlib.compress(decompressedData.encode()) #-------------encode into a bytes string and compress with zlib
		
		with open(fPath, 'wb') as file: #---------------------------------------write the new file based on its name
			file.write(compressedData)
		
		return True
	
	except OSError:
		from modules.dialog import ohno
		
		ohno('The file path contains invalid characters', out=False)
		print(fPath)

	except Exception as e:
		from modules.dialog import ohno

		ohno(e, out=False)


def dicttojson(jsondata:list[dict], fPath:str, overwrite:bool=False) ->bool:
	"""Write a json file from a list of dicts.
	Return true if successful
	"""
	if not overwrite and osp.exists(fPath):
		from modules.dialog import yesnodialog, woops

		woops(f'File {osp.split(fPath)[1]} already exists')
		if not yesnodialog(
			'Overwrite file?',
			defau=False
		):
			return False
	
	try:
		jsonText = [json.dumps(dico, indent=4) for dico in jsondata] #----------make every dictionary of the list a string again, but with a pretty and readable format 
		jsonText = '\n\\x00\n'.join(jsonText) #---------------------------------put every json object back together, separated with a newline, a fake NUL char, and another newline

		with open(fPath, 'wt') as file: #---------------------------------------save file with name in the folder
			file.write(jsonText)
		
		return True
		
	except Exception as e:
		from modules.dialog import ohno

		ohno(e)