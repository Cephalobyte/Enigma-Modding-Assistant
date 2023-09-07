from os import system #---------------------------------------------------------system will allow to use colored text
import sys

sys.path.insert(0, sys.path.pop(0).removesuffix('\\modules')) #-----------------set root directory

from modules.menus import QUICKMOD_MENUS
from modules.dialog import (
	breadcrumbtrail,
	menudialog,
	header,
	seeyounextmission
)
from modules.filemanagement import (
	SelectionInfo,
	mpfileselection,
	mpselectionpreview
)


def quickmod(
		selection: SelectionInfo = SelectionInfo(),
		basecrumbs: list[str] = []
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

	while True: #=============================================================== QUICK MOD =============================
		mInfo = QUICKMOD_MENUS['info']
		sDis = selection.discriminators.copy()
		breadcrumbs = []
		message = trail(), mpselectionpreview(selection)
		
		print(
			'sDis :', *selection.discriminators,
			'mDis :', *mInfo.discriminators.items(),
			sep='\n'
		)
		print('sSum :', *sSumm)

		match (choice := menudialog(mInfo, sSumm, True, message)):

			case 'sel': #======================================================= SELECTION
				header('Selection')
				trail([choice])

				selection = mpfileselection(selection.discriminators)
				sSumm = selection.getsummary()

			case 'done': #====================================================== DONE
				return selection

			case 0: #=========================================================== RENAME TITLE
				from modules._quickmod import batchrenamer

				selection.send(choice, mInfo.discriminators) #------------------prevent certain items in selection from being affected by unsupoorted operation
				
				breadcrumbs.append(choice)
				batchrenamer(
					QUICKMOD_MENUS[choice]['info'],
					selection,
					basecrumbs+breadcrumbs,
					'title'
				)
				selection.reclaim(sDis)

			case 1: #=========================================================== RENAME IDENTIFIER
				from modules._quickmod import batchrenamer

				selection.send(choice, mInfo.discriminators) #------------------prevent certain items in selection from being affected by unsupoorted operation
				
				breadcrumbs.append(choice)
				batchrenamer(
					QUICKMOD_MENUS[choice]['info'],
					selection,
					basecrumbs+breadcrumbs,
					'identifier'
				)

				selection.reclaim(sDis)
			
			case 2: #=========================================================== EDIT ID
				pass
			
			case 'ed': #===================================================== EDIT MODIFICATION DATE
				pass

			case 'pal': #======================================================= PALETTE OPTIMIZATION
				from modules._quickmod import palettelisteditor

				selection.send(choice, mInfo.discriminators) #------------------prevent certain items in selection from being affected by unsupoorted operation
				
				breadcrumbs.append(choice)
				palettelisteditor(
					QUICKMOD_MENUS[choice]['info'],
					selection,
					basecrumbs+breadcrumbs
				)

				selection.reclaim(sDis)

			case 'tl': #======================================================== EDIT TAG LIST
				pass

			case 'al': #======================================================== EDIT AREA LIST
				pass

			case 'area': #====================================================== EDIT AREA DATA
				pass

			case 'map': #======================================================= REVEAL MAP DATA
				from modules._quickmod import mapreveal

				selection.send(choice, mInfo.discriminators) #------------------prevent certain items in selection from being affected by unsupoorted operation
				
				breadcrumbs.append(choice)
				mapreveal(
					QUICKMOD_MENUS[choice]['info'],
					selection,
					basecrumbs+breadcrumbs
				)

				selection.reclaim(sDis)

			case 'inv': #======================================================= EDIT STARTING INVENTORY MODE
				from modules._quickmod import inventory

				selection.send(choice, mInfo.discriminators) #------------------prevent certain items in selection from being affected by unsupoorted operation

				breadcrumbs.append(choice)
				inventory(
					QUICKMOD_MENUS['inv']['info'],
					selection,
					basecrumbs+breadcrumbs
				)
				
				selection.reclaim(sDis)


if __name__ == '__main__':	#---------------------------------------------------if this script (encrypt.py) was run, (to prevent clearing a non empty terminal)
	system('cls')	#-----------------------------------------------------------clear terminal to allow ANSI escape sequences (such as fancy colors)

	quickmod(SelectionInfo(discriminators=['data']))
	
	seeyounextmission()