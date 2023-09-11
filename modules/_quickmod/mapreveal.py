from modules.menus import MenuInfo
from modules.dialog import (
	breadcrumbtrail,
	progress,
	woops,
	pageinfo,
	polymenudialog,
)
from modules.filemanagement import (
	SelectionInfo,
	mpselectedpreview
)


def mapreveal(
		mInfo: MenuInfo,
		selection: SelectionInfo,
		basecrumbs: list[str] = []
	):
	
	mInfo.addnavigationoptions()
	mInfo.addbatchmanipoptions()

	datas = selection.getdatas()
	sSumm = selection.getsummary()
	indexes = [k for k in datas]
	page = 0
	maxpage = len(indexes)

	while True:
		message = (
			breadcrumbtrail(basecrumbs),
			showmapreveal(datas, page),
			pageinfo(
				page,
				maxpage,
				mpselectedpreview(selection, indexes[page])
			),
		)

		for request in polymenudialog(
			mInfo,
			sSumm,
			True,
			message,
			30,
		):
			match request:
				
				case '>':
					page = (page + 1) % maxpage
				case '<':
					page = (page - 1) % maxpage

				case 'res':
					datas = selection.getdatas()
					progress("Map reveal reverted", True)
					break

				case 'ok':
					progress("Saving map reveal")
					selection.setdatas(datas, True)
					progress("Map reveal saved!", True)
					break

				case 'ar'|'av'|'ae' :
					params = (
						request == 'ar',
						request == 'av',
						request == 'ae',
					)
					datas = {
						k: editmapreveal(d, *params)
						for k, d in datas.items()
					}

				case _ :
					woops('not implemented')
		
		else: continue #--------------------------------------------------------if for loop wasn't broken, continue
		break #-----------------------------------------------------------------otherwise, break while loop


def showmapreveal(datas:dict[int, list[dict]], page:int=0):
	data = [d for d in datas.values()][page]
	mapdata = data[0]["MAP"]
	mWidth = len(mapdata)
	mHeight = len(mapdata[0])
	mScreens = sum(mapdata, []) #--------------------------------------------------1D array of all screens
	preview = ''

	def screencolor(mScreen, bg:bool=False) -> str:
		if type(mScreen) is int:
			return ('30','40')[bg]

		col = 10 * (
			(3, 9)[mScreen["revealed"]] + #-------------------------------------if revealed, lighter
			(0, 1)[bg] #--------------------------------------------------------if applied to bg, 40|100 instead of 30|90
		) + (
			(0, 4)[mScreen["visited"]] + #--------------------------------------if visited, bluer
			(0, 2)[mScreen["elevator"]] #---------------------------------------if elevator revealed, greener
		)
		return str(col)

	for y in range(-(mHeight // -2)):
		y *= 2
		
		for x in range(mWidth):
			i1 = x*mHeight + y
			i2 = i1 + 1
			col = screencolor(mScreens[i1])

			if y+1 < mHeight:
				col += ';'+ screencolor(mScreens[i2], True)
			
			preview += f'\033[{col}m▀' #----------------------------------------set color of screens

		preview += '\033[39;49m\n' #--------------------------------------------reset fore/background color at end of line

	return preview


def editmapreveal(data, reveal:bool=False, visit:bool=False, elevator:bool=False):
	for i in data[0]["MAP"]:
		for j in i:
			j["revealed"] = max(int(reveal), j["revealed"])
			j["visited"] = max(int(visit), j["visited"])
			j["elevator"] = max(int(elevator), j["elevator"])
	
	return data