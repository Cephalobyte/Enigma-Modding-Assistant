from typing import NamedTuple#, TypedDict
import sys
sys.path.insert(0, sys.path.pop(0).removesuffix('\\modules')) #-----------------set root directory

from modules.filemanagement import SelectionSummary


#==== CLASSES ==========================================================================================================

class MenuInfo(NamedTuple):
	"""Tuple containing title, options & more when creating a menu

	title:
		title displayed in the green rectangle
	prompt:
		prompt displayed before the options
	primary_options:
		list of options that can be chosen by their index
	secondary_options:
		dictionary of options that can be chosen by their key
	default_value:
		option index or key chosen by default when prompt is skipped
	discriminators:
		dictionary of lists that excludes certain options (key) when
		the selection is empty or only contains listed discriminators
		(value)

	Usage::

	    MenuInfo(
	        'My menu',
	        'What do you want?',
	        [
	            'option 0 description'   #for anything but data
	            'option 1 description'   #for single selection only
	            'option 2 description'   #for multiple selection only
	            'option 3 description'   #chosen if user skips
	            'option 4 description'   #for planned features
	        ],
	        {
	            'a': 'description'   #for multiple or non-data sel.
	            'b': 'description'   #for compressed files only
	            'c': 'description'   #for decompressed files only
	            'd': 'description'   #always available
	        },
	        3,                       #default
	        {
	            0: ['data'],	 # disable if selection only has data
	            1: [2],			 # ^^ has multiple files
	            2: [1],          # ^^ has only one file
	                             # always enabled
	            4: [3],          # always disabled
	            'a': ['data', 0],# disable no file OR data only
	            'b': [True],     # ^^ has only compressed files
	            'c': [False],    # ^^ has only decompressed files
	        }
	    )
	"""
	title: str
	prompt: str
	primary_options: list[str]
	secondary_options: dict[str, str] = {}
	default_value: int|str|None = None
	discriminators: dict[int|str, list[str|bool]] = {}
	

	def getdisabledoptions(
			self,
			# selectiontypes:SelectionTypes,
			selsum:SelectionSummary,
		) ->list[int,str]:
		"""Return a list of the options that need to be disabled depending on
		the current selection's types, compressions and amount

		:param selsum: summary of a selection
		"""
		# :param selectiontypes: simplified information abount the selection
		disabled = []

		for opt, disc in self.discriminators.items():
			discN = [d for d in disc if type(d) is int]

			# if 3 in discN or selectiontypes.multiple in discN:
			if 3 in discN or selsum.multiple in discN:
				disabled.append(opt)
			if selsum.multiple == 0:
				continue

			discT = [d for d in disc if type(d) is str]
			discC = [d for d in disc if type(d) is bool]

			if (
				# all([t in discT for t in selectiontypes.types])
				all([t in discT for t in selsum.types])
				or all([c in discC for c in selsum.are_compressed])
			):
				disabled.append(opt)
		
		return disabled


	def setprimaryoptions(self, options:list=[]):
		"""Replace the list of primary options with another list"""
		self.primary_options.clear()
		self.primary_options.extend(options)

	# def addsupermenuoptions(self, master:bool=False):
	# 	"""Add selection (sel) & exit (done/quit) options"""
	# 	self.secondary_options.setdefault(
	# 		'sel',
	# 		(
	# 			'modify current selection',
	# 			'select multiple files to edit at once'
	# 		)[master]
	# 	)
	# 	self.secondary_options.setdefault(
	# 		(
	# 			'done',
	# 			'quit'
	# 		)[master],
	# 		(
	# 			'done for this batch?',
	# 			'done for now?'
	# 		)[master]
	# 	)
		
	def addnavigationoptions(self, prepend:bool=True, label:str='preview'):
		"""Add left/right (</>) navigation options to the menu"""
		if prepend:
			sOptions = self.secondary_options.copy()
			self.secondary_options.clear()
			
		self.secondary_options['<'] = 'see previous '+ label
		self.secondary_options['>'] = 'see next '+ label
		self.discriminators['>'] = self.discriminators['<'] = [1]
		
		if prepend:
			self.secondary_options.update(sOptions)

	
	def addbatchmanipoptions(self):
		"""Add reset (res) & confirm (ok) options to the menu"""
		self.secondary_options.setdefault('res', 'reset changes & return')
		self.secondary_options.setdefault('ok', 'apply changes & return')


#==== MENUS ============================================================================================================

MAIN_MENUS = { #================================================================ MAIN MENU
	'info': MenuInfo(
		'Main menu',
		'What would you like to do?',
		[
			'Decrypt a Metroid Planets file to JSON',				#0 compressed
			'Encrypt a JSON file for Metroid Planets',				#1 decompressed
			'"quick mod" to edit simple data without converting',	#2
			# '"quick fix" to correct common problems when modding'	#3
		],
		{
			'sel':'select multiple files to edit at once',
			# 'pf':'Manage your preferences',
			'mem':'Manage external python modules',
			'quit':'Done for now?'
		},
		None,
		{
			0: [False],
			1: [True],
			2: ['data','stamp'],
			3: ['save','data','palette','stamp'],
			'pf': [3],
		}
	)
}


DECRYPT_MENUS = {
	'info': MenuInfo( #========================================================= DECRYPT MENU
		'Decrypt',
		'Decompress .mp_ files to indented .json',
		[
			'proceed'	#0
		],
		{
			'out': 'edit output parameters',
			'sel': 'modify the current selection',
			'done': 'done for this batch?'
		},
		0,
		{
			0:[0]
		}
	)
}

ENCRYPT_MENUS = {
	'info': MenuInfo( #========================================================= DECRYPT MENU
		'Encrypt',
		'Recompress .json files into .mp_ files',
		[
			'proceed'	#0
		],
		{
			'out': 'edit output parameters',
			'sel': 'modify the current selection',
			'done': 'done for this batch?'
		},
		0,
		{
			0:[0]
		}
	)
}


QUICKMOD_MENUS:dict[str|int, MenuInfo|dict] = {
	'info': MenuInfo( #========================================================= QUICK MOD MENU
		'Quick mod',
		'What would you like to mod?',
		[
			'name of the room / world',	#0	(room,world,save)
			'designer / full name',		#1	(room,world)
			# 'date of creation (id)',	#2	(room,world,save)
		],
		{
			# 'ed': "rooms' last modified date", #(room)
			'pal': "rooms' palette list", #(room)
			# 'tl': "rooms' tag list", #(room)
			# 'al': "rooms' area & custom area list", #(room)
			# 'area': "worlds' areas and their data", #(world)
			'map': "saves' map reveal",	#(save)
			'inv': "saves' starting inventory",
			'sel': 'modify the current selection',
			'done': 'done for this batch?'
		},
		'done',
		{
			0: [0,'palette'],
			1: [0,'save','palette'],
			2: [0,'palette'],
			'ed': [0,'world','save','palette'],
			'pal': [0,'world','save'],
			'tl': [0,'world','save','palette'],
			'al': [0,'world','save','palette'],
			'area': [0,'room','save','palette'],
			'map': [0,'room','world','palette'],
			'inv': [0,'room','world','palette']
		}
	),

	0: { #====================================================================== RENAME TITLE SUBMENU
		'info': MenuInfo(
			'Rename title',
			'By which method?',
			[
				'rewrite',		#0	(singular)
				'add prefix',	#1
				'add suffix',	#2
				'replace'		#3
			],
			{},
			3,
			{
				0: [2],
			}
		),
	},
	1: { #====================================================================== RENAME IDENTIFIER SUBMENU
		'info': MenuInfo(
			'Rename identifier',
			'By which method?',
			[
				'rewrite',		#0	(singular)
				'add prefix',	#1
				'add suffix',	#2
				'replace'		#3
			],
			{},
			3,
			{
				0: [2],
			}
		)
	},
	2: { #====================================================================== EDIT ID SUBMENU
		'info': MenuInfo(
			'Edit ID',
			'By which method?',
			[
				'rewrite',				#0	(singular)
				'match current date',	#1	(singular)
				'update old room'		#2	(multiple)
			],
			{},
			0,
			{
				0: [2],
				1: [2],
				2: [1],
			}
		)
	},
	'ed': { #=================================================================== EDIT MODIFICATION DATE SUBMENU
		'info': MenuInfo(
			'Edit modification date',
			'By which method?',
			[
				'rewrite',				#0	(singular)
				'match current date',	#1	(singular)
			],
			{},
			0,
			{
				0: [2],
				1: [2],
			}
		)
	},
	'pal': { #================================================================== EDIT PALETTE ORDER SUBMENU
		'info': MenuInfo(
			'Palette list editor',
			'What do you want to edit?',
			[
				'manual reorder',		#0
				# 'reorder by color id',	#1
				# 'reorder by most used'	#2
			],
			{
				'a2s': 'strip fake static palettes',
				'ssx': "strip static palettes' extra frames"
				# 'mrg': 'merge palettes'
			},
			0,
			{
				1: [3],
				2: ['palette', 3]
			}
		)
	},
	'tl': { #=================================================================== EDIT TAG LIST SUBMENU
		'info': MenuInfo(
			'Tag list editor',
			'What do you want to edit?',
			[
				'enter new list',				#0
				'add to list',					#1
				'find & replace',				#2
				'remove',						#3
			],
			{},
			0,
		)
	},
	'al': { #=================================================================== EDIT AREA LIST SUBMENU
		'info': MenuInfo(
			'Area list editor',
			'What do you want to edit?',
			[
				'enter new list',	#0
				'add to list',		#1
				'find & replace',	#2
				'remove',			#3
			],
			{},
			0,
		)
	},
	'area': { #================================================================= EDIT AREA DATA SUBMENU
		'info': MenuInfo(
			'Edit area data',
			'Which data?',
			[
				'name',				#0
				'color',			#1
				'background music'	#2
			],
			{
				'done': 'done with areas?'
			},
		),
		0: { #================================================================== EDIT AREA NAMES SUBSUBMENU
			'info': MenuInfo(
				'Edit area names',
				'By which method?',
				[
					'replace by name'	#0
					'replace by color',	#1
					'replace by music',	#2
				],
				{},
				0,
			)
		},
		1: { #================================================================== EDIT AREA COLORS SUBSUBMENU
			'info': MenuInfo(
				'Edit area colors',
				'By which method?',
				[
					'replace by name'	#0
					'replace by color',	#1
					'replace by music',	#2
				],
				{},
				1,
			)
		},
		2: { #================================================================== EDIT AREA MUSIC SUBSUBMENU
			'info': MenuInfo(
				'Edit area Music',
				'By which method?',
				[
					'replace by name'	#0
					'replace by color',	#1
					'replace by music',	#2
				],
				{},
				2,
			)
		}
	},
	'map': { #================================================================== REVEAL MAP DATA SUBMENU
		'info': MenuInfo(
			'Reveal map data',
			'Which region?',
			[
				# 'Crateria',
				# 'Brinstar',
				# 'Norfair',
				# 'Wrecked Ship',
				# 'Kraid',
				# 'Ridley',
				# 'Tourian',
			],
			{
				'ar': 'reveal all screens',
				'av': 'visit all screens',
				'ae': 'reveal all elevators',
			},
			'ar ae',
		),
	},
	'inv': {
		'info': MenuInfo(
			'Edit starting inventory',
			'Which upgrade?',
			[],
			{
				'all': 'obtain every upgrade',
			},
			'all',
			{
				# 0: [3],
				# '26': [3]
				# 28: [3],
				# 29: [3],
			}
		)
	}
}


QUICKFIX_MENUS:dict[str|int, MenuInfo|dict] = { #=============================== QUICK FIX MENU
	'info': MenuInfo(
		'Quick fix',
		'What would you like to fix?',
		[
			'world statistics',			#0
			'self connecting rooms',	#1
		],
		{
			'auto': 'toggle autocompression & set directory',
			'sel': 'modify the current selection',
			'done': 'done for this batch?'
		},
		'done'
	),

	0: { #====================================================================== WORLD STATS SUBMENU
		'info': MenuInfo(
			'World statistics',
			'Which of them?',
			[
				'dimensions (world_w, world_h)',	#0
				'area, room & screen count',		#1
				'enemy & boss count',				#2
				'item & object count',				#3
				'block count',						#4
				'door count',						#5
			],
			{
				'all': 'all of the above',
				'h': 'only header statistics',
				'g': 'only "GENERAL" statistics'
			},
			'all',
		),
	},
	# 1: { #====================================================================== SELF CONNECTING DOORS ROOMS
	# 	'info': MenuInfo(
	# 		'Self connecting doors'
	# 	)
	# }
}


MANAGEEXTERNALMODULES_MENUS:dict[str|int, MenuInfo|dict] = { #================== MANAGE EXTERNAL MODULES MENU
	'info': MenuInfo(
		'Manage external modules',
		'type module index then select operation',
		[],
		{
			'_ i': 'install',
			'_ o': 'uninstall',
			'_ d': 'describe',
			'done': 'go back to Main Menu'
		},
		None,
		{
			'_ i':[3],
			'_ o':[3],
			'_ d':[3]
		}
	)
}