import importlib.util
from os import system
import subprocess #-------------------------------------------------------------run commands from command line
import sys #--------------------------------------------------------------------sys.executable ensures that the pip command runs on the currently running Python interpreter
import importlib
from types import ModuleType

import importlib._bootstrap

sys.path.insert(0, sys.path.pop(0).removesuffix('\\modules')) #-----------------set root directory (if ran as main)

from modules.dialog import (
	optiondialog,
	yesnodialog,
	progress,
	boolinfo,
	woops,
	pe2c,
)


#============ CONSTANTS ================================================================================================

EXTERNALMODULESEXPLANATION = {
	"keyboard": "This module enables some keyboard shortcuts. Ease of use only"
}

REASONWHYTHISPROMPTEXISTS = """\
Enimga Modding Assistant was made to speed up the process of modifying json data
for Metroid Planets. As new features got implemented, the project needed to be
as clear and simple as it could, otherwise documentation would become necessary.

Since I've never been a fan of plugins, I've been working on these tools with
vanilla Python 3.11, which also avoided the user to install anything else than
EMA and python. But some QoL features such as keyboard shortcuts aren't possible
without external modules.

So I decided to make a submodule that automatically installs a module if not
found on the computer, which is controlled by the user, who can also decide to
uninstall it from the main menu.
"""


#============ FUNCTIONS ================================================================================================

def importexternalmodule(modulename:str)->ModuleType|None:
	try: #----------------------------------------------------------------------attempt returning external module
		return importlib.import_module(modulename)
	
	except ImportError: #-------------------------------------------------------if import failed, warn
		woops(f'failed to import "{modulename}"')

	moduleinstalled = False
	userknowswhy = False
	userknowswhat = False

	def explainwhy():
		print(REASONWHYTHISPROMPTEXISTS)
		return True

	def explainwhat():
		if (explanation := EXTERNALMODULESEXPLANATION.get(modulename)) is None:
			woops(f'module "{modulename}" is missing an explanation')
			print('Just tag GUMMY with a screenshot of this message')
			return True
		
		print(explanation)
		return True
	
	while True: #---------------------------------------------------------------Start loop until broken
		match optiondialog( #---------------------------------------------------ask permission for installing external module
			f'Install the "{modulename}" module?',
			[],
			{
				'y': 'yes (can be uninstalled from the main menu)',
				'n': 'no',
				'wy': 'why are you asking me this?',
				'wa': f'what does "{modulename}" do?'
			},
			defau='wa',
		):
			case 'y': #---------------------------------------------------------if user accepts, install
				moduleinstalled = installmodule(modulename) #-------------------try to install module
				
				if moduleinstalled: break #-------------------------------------if module installed, exti loop
				if yesnodialog( #-----------------------------------------------if user abandons,
						'Abandon installation?',
						defau=False
					):
					woops(f'module "{modulename}" won\'t be installed')
					break #-----------------------------------------------------exit loop

			case 'n': #---------------------------------------------------------if user declines,
				if not userknowswhy and yesnodialog( #--------------------------if user doesn't know why and wants to know why,
					"Don't want to know why I'm asking you this?",
					defau=False
				):
					userknowswhy = explainwhy() #-------------------------------explain why the prompt exists
					continue #--------------------------------------------------restart loop

				if not userknowswhat and yesnodialog( #-------------------------if user doesn't know what and wants to know what,
					"Don't want to know what the module does?",
					defau=False
				):
					userknowswhat = explainwhat() #-----------------------------explain what it does
					continue #--------------------------------------------------restart loop
				
				woops(f'module "{modulename}" won\'t be installed')
				break #---------------------------------------------------------exit loop

			case 'wy': #--------------------------------------------------------if user asks why
				userknowswhy = explainwhy()
			case _: #-----------------------------------------------------------default result (what does it do)
				userknowswhat = explainwhat()
		#-----------------------------------------------------------------------end of loop

	if moduleinstalled: #-------------------------------------------------------if module was indeed installed
		return importlib.import_module(modulename) #----------------------------return it
	
	return None


def installmodule(modulename:str)->bool:
	try:
		progress('Installing module from pip')
		subprocess.check_call([sys.executable, "-m", "pip", "install", modulename])
		progress(f'module "{modulename}" installed', True)
		return True
	
	except subprocess.CalledProcessError as e:
		woops(f'failed to install "{modulename}" module')
		print('return code :', e.returncode)
		# if e.returncode == 5:
			# print('It appears the error was raised due to a denied access')
			# print('If you can\'t install this module on your machine')
		# 	return False
		# print('It is possible that "pip" can\'t be found')

		# print("To install pip, follow these instructions:")
		# print("1. Download get-pip.py from https://bootstrap.pypa.io/get-pip.py.")
		# print("2. Run the script using Python: python get-pip.py")
	
	except subprocess.TimeoutExpired:
		woops('timeout expired before completion of the command')
		print('Make sure that your internet connection is adequate')
	
	return False


def uninstallmodule(modulename:str):
	try:
		progress('Uninstalling module from pip')
		subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", modulename])
		progress(f'module "{modulename}" uninstalled', True)
		return False
	
	except subprocess.CalledProcessError as e:
		woops(f'failed to uninstall "{modulename}" module')
		print('return code :', e.returncode)
		return None


def checkinstalledmodules(dump:bool=True):
	modulesinstalled = {}

	for mod in EXTERNALMODULESEXPLANATION.keys():
		location = importlib.util.find_spec(mod) #------------------------------check if module is found
		installed = location is not None

		if installed:
			location = location.origin.removesuffix('\\__init__.py') #----------set location to the origin of the ModuleSpec 
		
		modulesinstalled[mod] = location
		
		if dump:
			print(
				boolinfo(installed, mod),
				('', location)[installed],
				sep='\t'
			)
	
	return modulesinstalled


if __name__ == '__main__':	#---------------------------------------------------if this script was run on its own,
	system('cls')	#-----------------------------------------------------------clear terminal to allow ANSI escape sequences (such as fancy colors)

	checkinstalledmodules()
	# importexternalmodule('ababa')
	keyboard = importexternalmodule("keyboard")

	# installmodule('keyboard')
	# uninstallmodule('keyboard')

	checkinstalledmodules()

	# def on_up_arrow():
	# 	print("\nUp arrow pressed",end='')
	# 	checkinstalledmodules()

	# if keyboard:
	# 	keyboard.add_hotkey('up', on_up_arrow)
	# else:
	# 	print("Failed to import module.")

	pe2c()
	uninstallmodule('keyboard')
	# installmodule('keyboard')
	
	checkinstalledmodules()
	pe2c()