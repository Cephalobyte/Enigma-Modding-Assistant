from os import system #---------------------------------------------------------will allow to use colored text
import sys

sys.path.insert(0, sys.path.pop(0).removesuffix('\\modules')) #-----------------set root directory

from modules.menus import DECRYPT_MENUS
from modules.dialog import (
	header,
	breadcrumbtrail,
	progress,
	seeyounextmission,
	boolinfo,
	filepathdialog,
	yesnodialog,
	menudialog,
)
from modules.filemanagement import (
	SelectionInfo,
	ROOTDIR,
	mpfileselection,
	mpselectionpreview,
	dicttojson,
	getshortname,
)
from modules.utils import (
	sortdictbypriority,
	rowsfromlist
)


def decrypter(
		selection: SelectionInfo = SelectionInfo(),
		basecrumbs: list[str] = []
	) -> None|SelectionInfo:
	
	if not selection.file_paths: #----------------------------------------------if the selection is empty, ask one
		selection = mpfileselection(selection.discriminators, True) #-----------keep the discriminators

		if not selection.file_paths: #------------------------------------------if the selection is still empty
			return
	
	sSumm = selection.getsummary()
	outputdir = ROOTDIR+'\\converted'
	renamebytitle = True
	overwrite = False
	
	
	def trail(bc=None) -> str: #------------------------------------------------simplification of the breadcrumbtrail() function
		if bc is None:
			return breadcrumbtrail(basecrumbs + breadcrumbs)
		print(breadcrumbtrail(basecrumbs + bc))

	def showparameters() -> str:
		msg = '\n'.join(rowsfromlist(
			[
				'Export directory',
				f'\033[4m{outputdir}\033[24m',
				'Rename by title',
				boolinfo(renamebytitle),
				'Overwrite',
				boolinfo(not overwrite, '', str(overwrite)),
			],
			0,
			' : '
		))
		return msg +'\n'
	
	while True: #=============================================================== DECRYPTER =============================
		mInfo = DECRYPT_MENUS['info']
		breadcrumbs = []
		message = (
			trail(),
			showparameters(),
			mpselectionpreview(selection)
		)
		
		print(
			'sDis :', *selection.discriminators,
			'mDis :', *mInfo.discriminators.items(),
			sep='\n'
		)
		print('sSum :', *sSumm)

		match (choice := menudialog(mInfo, sSumm, True, message)):
			
			case 'sel':
				header('Selection')
				trail([choice])

				selection = mpfileselection(selection.discriminators)
				sSumm = selection.getsummary()
			
			case 'out':
				header('Encryption directory')
				trail([choice])

				outputdir = filepathdialog(
					defau=outputdir,
					acceptdir=True,
					acceptfile=False
				)
				renamebytitle = yesnodialog(
					'Rename files by their title if it exists?',
					[
						'y to rename rooms & worlds by their title',
						'n to keep original file names'
					],
					renamebytitle
				)
				overwrite = yesnodialog(
					'Overwrite files with no warning?',
					[
						'y to overwrite without warning',
						'n to ask each time',
					],
					overwrite
				)
			
			case 0:
				decrypt(selection, outputdir, renamebytitle, overwrite)

			case 'done':
				return selection


def decrypt(
		selection:SelectionInfo,
		outputdir:str,
		renamebytitle:bool,
		overwrite:bool
	):
	progress('Decrypting files')
	
	for k, data in selection.getdatas().items():
		fPath:str = selection.file_paths[k]
		fType:str = selection.file_types[k].type

		if renamebytitle and fType in ['room','world']:
			match fType:
				case 'room':
					fName = data[0]['GENERAL']['name']
				case 'world':
					fName = data[0]['name_full']
		else:
			fName = getshortname(fPath)

		match fType:
			case 'room':
				progress(f"Sorting {(fName)}'s mess")
				data[0] = sortroom(data[0])
			case 'world':
				progress(f"Sorting {(fName)}'s mess")
				data = sortworld(*data)

		progress('Merging & exporting json')

		if dicttojson(data, outputdir+f'\\{fType}.{fName}.json', overwrite): #--write to file and verify if successful
			
			progress(f'{fType.capitalize()} "{fName}" decrypted!', True)
			continue
		
		progress('Export cancelled')


def sortroom(roomDict:dict):

	roomDict = sortdictbypriority( #sort 1st level (properties)
		roomDict,
		[
			'META','GENERAL',
			'HAZARD',
			'PATHING'
		]
	)

	for data in [ #sort 2nd level (objects)
		["META", [
			'id','last_save','last_patch',
			'playable','gunship','boss',
		]],
		["GENERAL", [ #singular values first, lists second
			'name','designer',
			'focus','areas',
			'tags'
		]],
		["HAZARD", [
			'set',
			'style','color',
			'tanks',
		]]
	]:
		roomDict[data[0]] = sortdictbypriority(
			roomDict[data[0]],
			data[1]
		)
	
	for data in [ #sort 2nd level (lists of objects)
		["PATHING", [
			'a','b'
		]],
		["PALETTES", [
			's'
		]]
	]:
		propList = roomDict.get(data[0])
		if propList is None: continue #prevent searching for a non-existent property, eg: PATHING doesn't exist in worlds

		for stuff in propList:
			stuf2 = stuff.copy()
			stuff.clear()
			stuff.update(sortdictbypriority(stuf2, data[1]))
	
	for screen in roomDict["SCREENS"]: #sort 2nd level list of screens
		scren = screen.copy()
		screen.clear()
		screen.update(sortscreen(scren))
	
	return roomDict


def sortscreen(screen):
	screen = sortdictbypriority( #sort 1st level (properties)
		screen,
		[
			['room_id','x','y'],
			['world_x','world_y'],
			'area','bgm',
			'boss',
			'MAP',
			'ENEMIES','OBJECTS','DOORS','ELEVATORS',
			'SCROLLS',
			'BLOCKS'
		]
	)

	screen["MAP"] = sortdictbypriority( #sort 2nd level (objects properties)
		screen["MAP"],
		[
			'area','base'
			'elevator',
			'icons',
			'walls','doors',
		]
	)

	for data in [
		("ENEMIES", [
			'W_id','id',
			'x','y','rot','dir',
			'type','level','lock'
		])
	]:
		propList = screen.get(data[0])
		if propList is None: continue #prevent searching for a non-existent property

		for stuff in propList:
			stuf2 = stuff.copy()
			stuff.clear()
			stuff.update(sortdictbypriority(stuf2, data[1]))
	
	return screen


def sortworld(header:dict, worldDict:dict):
	header = sortdictbypriority(
		header,
		[
			'id',
			'name',
			'name_full',
		]
	)

	header["stats"] = sortdictbypriority( #replicating the in-game world data order
		header["stats"],
		[
			'size','world_w','world_h',
			'screens','rooms',
			'style','items',
			'areas','bosses'
		]
	)

	worldDict = dict(sorted(worldDict.items())) #alphabetical order: GENERAL, MAP_ELEVATORS, ROOMS

	for data in [
		["GENERAL", [ #singular values first, lists second
			'world_w','world_h',
			'total_enemies','total_objects','total_doors','total_blocks',
			'escape_length',
			'gate_bosses',
			'areas',
			'spawns'
		]],
	]:
		worldDict[data[0]] = sortdictbypriority(
			worldDict[data[0]],
			data[1]
		)

	for data in [
		['["GENERAL"]["areas"]', [
			'name','color','bgm'
		]],
		['["GENERAL"]["spawns"]', [
			'world_x','world_y','x','y',
			'name','area',
			'room','screen_n'
		]]
	]:
		propList = eval(f'worldDict{data[0]}')	#get property by name
		if propList is None: continue	#prevent searching for a non-existent property

		for stuff in propList:
			stuf2 = stuff.copy()
			stuff.clear()
			stuff.update(sortdictbypriority(stuf2, data[1]))
	
	worldDict["ROOMS"] = [sortroom(room) for room in worldDict["ROOMS"]]

	return [header, worldDict]


if __name__ == '__main__':	#---------------------------------------------------if this script (decrypt.py) was run, (to prevent clearing a non empty terminal)
	system('cls')	#-----------------------------------------------------------clear terminal to allow ANSI escape sequences (such as fancy colors)

	decrypter(SelectionInfo(discriminators=[False]))
	
	seeyounextmission()