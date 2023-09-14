from os import system#, path as osp #--------------------------------------------will allow to use colored text
import sys

sys.path.insert(0, sys.path.pop(0).removesuffix('\\modules')) #-----------------set root directory

from modules.menus import ENCRYPT_MENUS
from modules.dialog import (
	header,
	breadcrumbtrail,
	progress,
	seeyounextmission,
	boolinfo,
	yesnodialog,
	filepathdialog,
	menudialog,
)
from modules.filemanagement import (
	SelectionInfo,
	ROOTDIR,
	getshortname,
	mpfileselection,
	mpselectionpreview,
	dicttomp,
)
from modules.utils import rowsfromlist


def encrypter(
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
	
	while True: #=============================================================== ENCRYPTER =============================
		mInfo = ENCRYPT_MENUS['info']
		breadcrumbs = []
		message = (
			trail(),
			showparameters(),
			mpselectionpreview(selection),
		)

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
				encrypt(selection, outputdir, renamebytitle, overwrite)

			case 'done':
				return selection


def encrypt(
		selection:SelectionInfo,
		outputdir:str,
		renamebytitle:bool,
		overwrite:bool
	):
	progress('Encrypting files')
	
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
			
		progress(f'Exporting {fType}')

		if dicttomp(data, outputdir+f'\\{fName}.mp_{fType}', overwrite): #------write to file and verify if successful

			progress(f'{fType.capitalize()} "{fName}" exported!', True)
			continue
		
		progress('Export cancelled')


if __name__ == '__main__':	#---------------------------------------------------if this script (encrypt.py) was run, (to prevent clearing a non empty terminal)
	system('cls')	#-----------------------------------------------------------clear terminal to allow ANSI escape sequences (such as fancy colors)

	encrypter(SelectionInfo(discriminators=[True]))
	
	seeyounextmission()