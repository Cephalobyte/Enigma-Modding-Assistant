import string

from modules.menus import MenuInfo
from modules.dialog import (
	header,
	breadcrumbtrail,
	progress,
	# woops,
	pageinfo,
	pe2c,
	# listdialog,
	menudialog,
)
from modules.filemanagement import (
	SelectionInfo,
	mpselectedpreview
)
from modules.utils import (
	terminalsize,
	visiblen,
	rowsfromlist,
)


DATAPATHS = {
	'title': {
		'room': '[0]["GENERAL"]["name"]',
		'world': '[0]["name"]',
		'save': '[0]["ENIGMA"]["world_name"]'
	},
	'identifier': {
		'room': '[0]["GENERAL"]["designer"]',
		'world': '[0]["name_full"]',
		'save': None
	}
}

#!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~▯
def fontcharwidth(fontwidths:list[str]) ->dict[str,int]:
	chars = string.ascii_uppercase + string.digits + string.punctuation + ' '
	widths = {}

	for c in chars: #-----------------------------------------------------------check every character
		for w, fw in enumerate(fontwidths): #-----------------------------------compare to lists of widths
			if c in fw:
				widths[c] = w+2 #-----------------------------------------------+1 because index 0 is width 1, +1 for kerning

	return widths

FONTMAGO_CHARWIDTHS = fontcharwidth([
		'I!\',.:;|~',
		'()[]`',
		'CEFJLTVXYZ0123456789"+-/<=>?\\^{}',
		'ABDGHKOPQRSU $_',
		'MNW#%&*@',
	])


def batchrenamer(
		mInfo: MenuInfo,
		selection: SelectionInfo,
		basecrumbs: list[str] = [],
		goal: str = 'title'
	):
	mInfo.addbatchmanipoptions()
	
	datas = selection.getdatas()
	sSumm = selection.getsummary()
	fTypes = [ft.type for ft in selection.file_types]

	while True:
		message = (
			breadcrumbtrail(basecrumbs),
			shownames(selection, datas, goal),
		)
		header(mInfo.title, True)
		print(*message, sep='\n')
		print('\n'+' CURRENT SCRIPT NOT FUNCTIONAL, PREVIEW ONLY '.center(80,'='))
		return pe2c()

		# match (choice := menudialog(
		# 		mInfo,
		# 		sSumm,
		# 		True,
		# 		message,
		# 		30
		# 	)):
			
		# 	case 'res':
		# 		datas = selection.getdatas()
		# 		progress(goal.capitalize()+" names reverted", True)
		# 		break

		# 	case 'ok':
		# 		progress(f"Saving {goal.capitalize()} names")
		# 		selection.setdatas(datas)
		# 		progress(goal.capitalize()+" names saved!", True)
		# 		break

		# 	case 0:
		# 		datas = {
		# 			k: newname(d, (fTypes[k], goal))
		# 			for k, d in datas.items()
		# 		}
		# 	case 1|2|3:
		# 		datas = editname(datas, goal, fTypes, choice)


def shownames(
		selection:SelectionInfo,
		datas:dict[int, list[dict]],
		goal:str
	) ->str:
	shortFNames, names, cells = [],[],[]

	for k, data in datas.items():
		if (dp := DATAPATHS[goal][selection.file_types[k].type]) is None: #-----if unsupported, ignore
			continue
		
		shortFNames.append(mpselectedpreview(selection, k))
		names.append(eval('data'+dp))
	
	cwidth = visiblen(max(shortFNames + names, key=visiblen)) #-----------------measure longest name
	cnumber = terminalsize(0) // cwidth #---------------------------------------floor division to count # of columns
	rnumber = -(len(shortFNames) // -cnumber) #---------------------------------ceil division to count # of rows

	while (nCells := len(shortFNames)):
		cRange = min(rnumber, nCells)
		spacer = '─'*cwidth

		for i in range(cRange):
			cells.append(shortFNames.pop(0))
			cells.append(names.pop(0))
			if i == rnumber-1: #------------------------------------------------if on last row, don't add
				continue
			cells.append(spacer)
		
	preview = '\n'.join(rowsfromlist(
			cells,
			cwidth,
			' │ ',
			rnumber=rnumber*3 - 1,
			vertical=True
		))
		
	return preview


def newname(data:list[dict], goal:tuple[str,str]) ->list[dict]:
	# name = eval('data'+ DATAPATHS[goal[1]][goal[0]])
	name = input()

	match goal[0]:
		case 'room':
			data[0]["GENERAL"]["name"] = name
		case 'world':
			data[0]["name"]

	# data[0]
	
	return data


def editname(
		datas:dict[int,list[dict]],
		goal:tuple[str,str]
	) ->dict[int,list[dict]]:
	pass