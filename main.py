from os import system

from modules.menus import MAIN_MENUS
from modules.dialog import (
	welcome,
	seeyounextmission,
	breadcrumbtrail,
	menudialog,
	header,
	woops
)
from modules.filemanagement import (
	SelectionInfo,
	mpfileselection,
	mpselectionpreview
)


def main():
	selection = SelectionInfo() #-----------------------------------------------selection to perform actions on


	def trail(bc=None) -> str: #------------------------------------------------simplification of the breadcrumbtrail() function
		if bc is None:
			return breadcrumbtrail(breadcrumbs)
		print(breadcrumbtrail(bc))
	
	while True:
		mInfo = MAIN_MENUS['info']
		sSumm = selection.getsummary()
		breadcrumbs = []
		message = trail(), mpselectionpreview(selection)

		match (choice := menudialog(mInfo, sSumm, True, message)):

			case 'sel': #======================================================= SELECT ================================
				header('Selection')
				trail([choice])
				
				selection = mpfileselection()

			case 'pf': #======================================================== PREFERENCES ===========================
				woops('feature not implemented yet')

			case 'mem': #======================================================= MANAGE EXTERNAL MODULES ===============
				from modules.externaldependecies import manageexternalmodules

				manageexternalmodules([choice])

			case 'quit':
				break

			case 0: #=========================================================== DECRYPT ===============================
				from modules.decrypter import decrypter
				
				selection.send(choice, mInfo.discriminators) #------------------prevent certain items in selection from being affected by unsupoorted operation
				
				if (newsel := decrypter(selection, [choice])): #----------------run module, but if selection was changed, save it
					selection = newsel
				
				selection.reclaim()
				
			case 1: #=========================================================== ENCRYPT ===============================
				from modules.encrypter import encrypter
				
				selection.send(choice, mInfo.discriminators) #------------------prevent certain items in selection from being affected by unsupoorted operation

				if (newsel := encrypter(selection, [choice])): #----------------run module, but if selection was changed, save it
					selection = newsel
				
				selection.reclaim()
			
			case 2: #=========================================================== QUICK MOD =============================
				from modules.quickmod import quickmod
				
				selection.send(choice, mInfo.discriminators) #------------------prevent certain items in selection from being affected by unsupoorted operation
				
				if (newsel := quickmod(selection, [choice])): #-----------------run module, but if selection was changed, save it
					selection = newsel
				
				selection.reclaim()

			case 3: #=========================================================== QUICK FIX =============================
				from modules.quickfix import quickfix

				selection.send(choice, mInfo.discriminators) #------------------prevent certain items in selection from being affected by unsupoorted operation

				if (newsel := quickfix(selection, [choice])): #-----------------run module, but if selection was changed, save it
					selection = newsel
				
				selection.reclaim()


if __name__ == '__main__':
	system('cls') #-------------------------------------------------------------allows ANSI escape sequences
	
	welcome()

	main()	#-------------------------------------------------------------------run program

	seeyounextmission()