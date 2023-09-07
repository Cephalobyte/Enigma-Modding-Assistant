from modules.menus import MenuInfo
from modules.dialog import (
	breadcrumbtrail,
	steptodo,
	protip,
	progress,
	boolinfo,
	pageinfo,
	polymenudialog,
)
from modules.filemanagement import (
	SelectionInfo,
	mpselectedpreview
)
from modules.utils import rowsfromlist


AMMOLABELS = {
	7:	'e-tanks',
	15:	'power bombs',
	16:	'missiles',
	17:	'super missiles'
}
AMMOPICKUPS_NORMAL = {
	7:	100,
	15:	1,
	16:	5,
	17:	2
}
AMMOPICKUPS_HARD = {
	7:	100,
	15:	1,
	16:	2,
	17:	1
}


def inventory(
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

	while True: #---------------------------------------------------------------for each answer,
		
		message = (
			breadcrumbtrail(basecrumbs),
			showinventory(datas, page),
			pageinfo(
				page,
				maxpage,
				mpselectedpreview(selection, indexes[page])
			),
		)

		for request in polymenudialog( #----------------------------------------for each request,
			mInfo,
			sSumm,
			True,
			message,
			30,
			True
		):
			match request:
				
				case '>':
					page = (page + 1) % maxpage
				case '<':
					page = (page - 1) % maxpage

				case 'res':
					datas = selection.getdatas()
					progress("Inventories reverted", True)
					break

				case 'ok':
					progress("Saving inventories")
					selection.setdatas(datas)
					progress("Inventories saved", True)
					break

				case 'all'|_:
					datas = editinventory(datas, request)
		
		else: continue #--------------------------------------------------------if for loop wasn't broken, continue
		break #-----------------------------------------------------------------otherwise, break while loop


def showinventory(datas:dict[int, list[dict]], page:int=0):#, fPaths:list[str]):
	data = [d for d in datas.values()][page]
	samus = data[0]["SAMUS"]
	invSize = len(samus["inventory"])

	def itemcolor(rId, amount, equipped) ->str:
		match rId:
			case 7|15|16|17:
				amount = str(amount).rjust(3)
			case _:
				amount = boolinfo(amount).rjust(13)
		rId = boolinfo(equipped, '', rId).rjust(13)

		return f'{rId} :{amount}'
	
	def capacityinfo(label:str, amount:int) ->str:
		return label.rjust(14) +' : '+ str(amount).ljust(4)

	inv = [
		itemcolor(*tup)
		for tup in list(zip(
			[i for i in range(invSize)],
			samus["inventory"],
			samus["equipped"]
		))
	]

	ammos = [
		capacityinfo('energy', samus["energy_capacity"])
	]+[
		capacityinfo(l, samus["ammo_capacity"][i-1])
		for i, l in enumerate(AMMOLABELS.values())
		if i > 0
	]

	preview = '\n'.join(
		rowsfromlist(
			rowsfromlist(
				inv,
				0,
				' | ',
				rnumber=10,
				vertical=True
			) + ammos,
			0,
			' ║ ',
			rnumber=10,
			vertical=True
		)
	)

	return preview


def editinventory(datas:dict[int,list[dict]], rId:int):
	allids = range(max([
				len(d[0]["SAMUS"]["inventory"])
				for d in datas.values()
			]))

	if rId == 'all':
		amount = min(sum( #-----------------------------------------------------minimum value of every upgrade (flattened) of every data
				[
					d[0]["SAMUS"]["inventory"]
					for d in datas.values()
				],
				[]
			))
	else:
		amount = min([#---------------------------------------------------------minimum value of the desired upgrade of every data
				d[0]["SAMUS"]["inventory"][rId]
				for d in datas.values()
			])

	activate = int(amount < 1) #------------------------------------------------if we should activate/deactivate every data's specific upgrade
	amount = activate #---------------------------------------------------------the new amount will be equal to the activation state, (until possibly adjusted later)


	def askammoamount(rId:int) ->int|None:
		steptodo(f'how many {AMMOLABELS[rId]}?')
		protip('enter number (without decimals)')

		if (answer := input()).isdecimal():
			return int(answer)
		
		progress(f'Keeping {AMMOLABELS[rId]} amount')
		return None

	def editupgrade(rId:int, amount:int|None):
		if amount is None: #----------------------------------------------------if no 
			return

		for k in datas:
			datas[k][0]["SAMUS"]["inventory"][rId] = amount * activate
			datas[k][0]["SAMUS"]["equipped"][rId] = activate

		if rId in AMMOLABELS:
			editammo(rId, amount)

	def editammo(rId:int, amount:int):
		if rId != 7:
			aId = { #-----------------------------------------------------------precompute ammunition id in the ammo_capacity list from the request id
				k: i-1 for i, k in enumerate(AMMOLABELS.keys()) #---------------rId #15 is 0, #16 is 1, #17 is 2
			}[rId]

		for k in datas:
			d = datas[k][0]
			pSizes = (
				AMMOPICKUPS_NORMAL,
				AMMOPICKUPS_HARD
			)[d["GAME"]["difficulty"]]

			ammo = pSizes[rId] * amount

			if rId == 7:
				datas[k][0]["SAMUS"]["energy_capacity"] = ammo + 99
				continue

			datas[k][0]["SAMUS"]["ammo_capacity"][aId] = ammo
					

	match rId:
		case 'all':
			for rId in allids: #------------------------------------------------for all upgrades,
				if activate and rId in AMMOLABELS: #----------------------------if upgrade needs to be activated and upgrade has ammunition,
					editupgrade(rId, askammoamount(rId)) #----------------------ask for amount
					continue

				editupgrade(rId, amount) #--------------------------------------otherwise, set it normally
			return datas #------------------------------------------------------and return when loop is done
		
		case 7|15|16|17:
			if activate:
				amount = askammoamount(rId) #-----------------------------------update amount desired
		
		case _:
			if rId not in allids: #---------------------------------------------if request id is not present in inventory, ignore request
				return datas #failsafe
	
	editupgrade(rId, amount)
	return datas