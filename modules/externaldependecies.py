import subprocess #-------------------------------------------------------------run commands from command line
import sys #--------------------------------------------------------------------sys.executable ensures that the pip command runs on the currently running Python interpreter
import importlib
import importlib.util
from pathlib import Path

sys.path.insert(0, sys.path.pop(0).removesuffix('\\modules')) #-----------------set root directory (if ran as main)

from modules.menus import MANAGEEXTERNALMODULES_MENUS
from modules.dialog import (
	menudialog,
	breadcrumbtrail,
	optiondialog,
	yesnodialog,
	progress,
	woops,
)


#============ CLASSES ==================================================================================================

class ExternalModule:
	"""Essential information about external module used for EMA (read only, use
	methods to update data)

	name:
		name of the module
	explanation:
		what does the module add to EMA
	location:
		string of the absolute path, None if uninstalled
	usable:
		True if loaded in current session (if true but location is None, will be\
		unusable next session)
	"""

	def __init__(self, name:str, explanation:str):
		self._name = name
		self._explanation = explanation
		self.updatelocation()
	
	def __str__(self):
		installed = self.location is not None
		esccol = (1,3,2)
		esc = '\33[3%im%s\33[39m'
		label = esc%(
			esccol[installed + self.usable],
			self.name
		)

		preview = label +'\n    ╟── '
		preview += self.explanation +'\n    ╙── '
		preview += self.location if installed else '\33[31m<uninstalled>\33[39m'
		
		return preview
	
	@property
	def name(self)->str:
		return self._name
	
	@property
	def explanation(self)->str:
		return self._explanation
	
	@property
	def location(self)->str|None:
		return self._location
	
	@property
	def usable(self)->bool:
		return self._modulespec() is not None
	
	def _modulespec(self):
		return importlib.util.find_spec(self._name)

	def updatelocation(self, location:None|str = None):
		"""sets location

		:param location:
		- if None, autodetect
		- if empty string, unset
		- if string, set new path
		"""
		match location:
			case None: #--------------------------------------------------------autodetect if None
				if (spec := self._modulespec()) is not None:
					location = str(Path(spec.origin).parent) #------------------set location to the origin of the ModuleSpec
			case _:
				location = None if location == '' else location #---------------set to None if empty string
		
		self._location = location #---------------------------------------------set self location to either str if installed or None otherwise

	def askeytuple(self):
		return (self.name, self)
	
	def importtype(self):
		"""return module if installed"""
		return importlib.import_module(self.name)
	
	def install(self, silent:bool=False):
		output = subprocess.DEVNULL if silent else None #-----------------------if silent, discard subprocess' standard output and error output
		
		try:
			progress('Installing module from pip')
			subprocess.check_call(
				[sys.executable, "-m", "pip", "install", self.name],
				stdout=output,
				stderr=output
			)
			progress(f'module "{self.name}" installed', True)
			self.updatelocation()
		
		except subprocess.CalledProcessError as e:
			woops(f'failed to install "{self.name}" module')
			print('return code :', e.returncode)
			# if e.returncode == 5:
				# print('It appears the error was raised due to a denied access')
				# print('If you can\'t install this module on your machine')
			# print('It is possible that "pip" can\'t be found')

			# print("To install pip, follow these instructions:")
			# print("1. Download get-pip.py from https://bootstrap.pypa.io/get-pip.py.")
			# print("2. Run the script using Python: python get-pip.py")
		
		except subprocess.TimeoutExpired:
			woops('timeout expired before completion of the command')
			print('Make sure that your internet connection is adequate')
	

	def uninstall(self, silent:bool=False):
		output = subprocess.DEVNULL if silent else None #-----------------------if silent, discard subprocess' standard output and error output

		try:
			progress('Uninstalling module from pip')
			subprocess.check_call(
				[sys.executable, "-m", "pip", "uninstall", "-y", self.name],
				stdout=output, stderr=output
			)
			progress(f'module "{self.name}" uninstalled', True)
			self.updatelocation('')
		
		except subprocess.CalledProcessError as e:
			woops(f'failed to uninstall "{self.name}" module')
			print('return code :', e.returncode)


#============ CONSTANTS ================================================================================================

EXTERNALMODULES:dict[str,ExternalModule] = dict([
	ExternalModule("keyboard",
		"Enables some keyboard shortcuts. Ease of use only").askeytuple(),
	# ExternalModule("numpy",
	# 	"Just an example, it doesn't change anything").askeytuple()
])

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

def manageexternalmodules(
		basecrumbs: list[str] = []
	):

	modulenames = [mn for mn in EXTERNALMODULES.keys()]
	
	while True:
		mInfo = MANAGEEXTERNALMODULES_MENUS['info']
		mInfo.setprimaryoptions(modulenames) #----------------------------------set the list of available external modules as the primary options
		message = (
			breadcrumbtrail(basecrumbs),
			showinstalledmodules()
		)

		choice = menudialog(
			mInfo,
			None, #-------------------------------------------------------------send no selection
			True,
			message
		)
		if choice == 'done': return #-------------------------------------------if user is done, exit the external module manager
		
		externalmodule = EXTERNALMODULES[modulenames[choice]] #-----------------if anything choose 
		
		if externalmodule.location is None:
			externalmodule.install()
		else:
			externalmodule.uninstall()


def showinstalledmodules()->str:
	return '\n'.join([str(mod) for mod in EXTERNALMODULES.values()])


def importexternalmodule(modulename:str, autoinstall:bool=False):
	"""
	Safely returns an external python module and autoinstall if user allows it

	:param modulename:
		name of the module to import/install
	:param autoinstall:
		warn if module not installed and prompts the user to install it
		automatically with pip
	"""
	module = EXTERNALMODULES[modulename]
	if module.usable:
		return module.importtype()
	if not autoinstall:
		return None
	
	woops(f'Module "{modulename}" is unavailable')
	print(module)

	userknowswhy = False

	def explainwhy():
		print(REASONWHYTHISPROMPTEXISTS)
		return True
	
	while True: #---------------------------------------------------------------loop until broken
		match optiondialog( #---------------------------------------------------ask permission for installing external module
			f'Install the "{modulename}" module?',
			[],
			{
				'y': 'yes (can be uninstalled from the main menu)',
				'n': 'no',
				'w': 'why are you asking me this?',
			},
			defau='w',
		):
			case 'y': #---------------------------------------------------------if user accepts, install
				module.install() #----------------------------------------------try to install module
				
				if module.location is not None: break #-------------------------if module is isntalled, exit loop
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
				
				woops(f'module "{modulename}" won\'t be installed')
				break #---------------------------------------------------------exit loop

			case _: #-----------------------------------------------------------if user asks why
				userknowswhy = explainwhy()
		#-----------------------------------------------------------------------end of loop

	if module.location is not None:
		return module.importtype() #--------------------------------------------return it
	
	return None



from os import system

if __name__ == '__main__':	#---------------------------------------------------if this script was run on its own,
	system('cls')	#-----------------------------------------------------------clear terminal to allow ANSI escape sequences (such as fancy colors)

	print('0')
	EXTERNALMODULES['keyboard'].uninstall()
	print('1')
	keyboard = importexternalmodule('keyboard', True)
	print('2')
	input("end")

	# def on_up_arrow():
	# 	print("\nUp arrow pressed",end='')

	# if keyboard:
	# 	keyboard.add_hotkey('up', on_up_arrow)
	# else:
	# 	print("Failed to import module.")