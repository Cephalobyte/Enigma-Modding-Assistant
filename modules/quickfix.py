from os import system, path as osp #--------------------------------------------system will allow to use colored text
import sys

sys.path.insert(0, sys.path.pop(0).removesuffix('\\modules')) #-----------------set root directory

from modules.menus import QUICKFIX_MENUS
from modules.dialog import (
	header,
	breadcrumbtrail,
	seeyounextmission,
	boolinfo,
	filepathdialog,
	menudialog,
)
from modules.filemanagement import (
	SelectionInfo,
	ROOTDIR,
	mpfileselection,
	mpselectionpreview,
)

def quickfix(
		selection:SelectionInfo=SelectionInfo(),
		basecrumbs:list[str]=[]
	) -> None|SelectionInfo:

	if not selection.file_paths: #----------------------------------------------if the selection is empty, ask one
		selection = mpfileselection(selection.discriminators, True) #-----------keep the discriminators

		if not selection.file_paths: #------------------------------------------if the selection is still empty
			return
		
	sSumm = selection.getsummary()


	def trail(bc=None) -> str: #------------------------------------------------simplification of the breadcrumbtrail() function
		if bc is None:
			return breadcrumbtrail(basecrumbs + breadcrumbs)
		print(breadcrumbtrail(basecrumbs + bc))
	
	def showautozip() -> str:
		msg = boolinfo(autozip, 'Autocompression') +'\n'

		if autozip:
			msg += f'folder : {autozipdir}\n'
		
		return msg
	
	autozip = False
	autozipdir = ROOTDIR+'\\converted'
	
	while True: #=============================================================== QUICK FIX =============================
		mInfo = QUICKFIX_MENUS['info']
		breadcrumbs = []
		message = trail(), showautozip(), mpselectionpreview(selection)

		match (choice := menudialog(mInfo, sSumm, True, message)):

			case 'auto':
				autozip = not autozip

				if autozip:
					header('Autocompression directory')
					trail([choice])
					print(showautozip())

					autozipdir = filepathdialog(
						defau=autozipdir,
						acceptdir=True,
						acceptfile=False
					)

			case 'sel':
				header('Selection')
				trail([choice])

				selection = mpfileselection(selection.discriminators)

			case 'done': #====================================================== DONE
				return selection
			
			case 0: #=========================================================== WORLD STATS
				pass
			
			case 1: #=========================================================== SELF CONNECTING ROOMS
				pass


if __name__ == '__main__':	#---------------------------------------------------if this script (encrypt.py) was run, (to prevent clearing a non empty terminal)
	system('cls')	#-----------------------------------------------------------clear terminal to allow ANSI escape sequences (such as fancy colors)

	quickfix()

	seeyounextmission()