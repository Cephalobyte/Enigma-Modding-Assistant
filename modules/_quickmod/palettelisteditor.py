from itertools import chain

from modules.menus import MenuInfo
from modules.dialog import (
	breadcrumbtrail,
	progress,
	woops,
	painttext,
	pageinfo,
	listdialog,
	menudialog,
)
from modules.filemanagement import (
	SelectionInfo,
	mpselectedpreview
)
from modules.utils import (
	rowsfromlist,
	terminalsize
)


ENIGMATILES_INVISIBLE = [0, 98, 99, 103, 104, 208, 209, 210]

ENIGMACOLORS_RGB = [
	#0				1				2				3				4				5				6				7				8				9				10				11				12				13			14				15
	(34,34,34),		(37,24,140),	(0,0,170),		(67,0,157),		(143,0,118),	(168,0,17),		(164,0,0),		(125,8,0),		(63,44,1),		(1,68,1),		(1,80,1),		(0,61,20),		(24,60,92),		(0,0,0),	(23,39,10),		(0,0,0),
	#16				17				18				19				20				21				22				23				24				25				26				27				28				29			30				31
	(75,75,75),		(0,116,237),	(36,58,240),	(133,0,242),	(190,1,191),	(228,0,89),		(219,44,1),		(202,80,15),	(135,112,0),	(1,151,2),		(0,169,2),		(0,147,59),		(0,133,137),	(0,0,0),	(92,25,141),	(79,21,9),
	#32				33				34				35				36				37				38				39				40				41				42				43				44				45			46				47
	(188,188,188),	(63,191,255),	(94,152,252),	(205,136,253),	(245,120,250),	(252,116,180),	(251,116,97),	(252,152,56),	(242,191,63),	(128,208,15),	(74,221,71),	(88,248,152),	(0,232,218),	(0,0,0),	(165,40,176),	(173,77,26),
	#48				49				50				51				52				53				54				55				56				57				58				59				60				61			62				63
	(255,255,255),	(170,227,255),	(197,213,249),	(211,201,251),	(254,199,220),	(250,197,217),	(251,190,172),	(250,216,170),	(252,227,161),	(223,252,159),	(168,241,188),	(178,251,205),	(156,252,240),	(0,0,0),	(0,0,0),		(253,232,55),
	#64				65	
	(0,0,0),		(127,127,127)
]
ENIGMACOLORS_CHARS = {
							14:'■',	15:'■',
					29:'■',	30:'■',	31:'■',
					45:'■',	46:'■',	47:'■',
					61:'■',	62:'■',	63:'■',
	64:'■',	65:'▒'
}

MPPalette = dict[str, int|list[list[int]]]

def newpalette(frames:list[list[int]]=[], anim:bool=False)->MPPalette:
	if not frames:
		frames = [[48]*3]
		if anim:
			frames *= 2

	return {
		"s": (0, 3)[len(frames) > 1],
		"f": frames
	}

ENIGMAPALETTES_LEGAL = chain(range(15), range(20,25))
ENIGMAPALETTES_DEFAULTSHADES = [
	newpalette([[16,32,48]]),
	newpalette([[28,18,34]]),
	newpalette([[23,22,40]]),
	newpalette([[4,22,21]]),
	newpalette([[22,27,54]]),
	newpalette([[19,20,33]]),
	newpalette([[21,19,60]]),
	newpalette([[27,25,40]]),
	newpalette([[25,2,40]]),
	newpalette([[4,22,53]]),
	newpalette([[10,24,40]]),
	newpalette([[12,26,57]]),
	newpalette([[17,44,60]]),
	newpalette([[1,28,59]]),
	newpalette([[4,38,56]])
] + [newpalette()]*5 + [newpalette(anim=True)]*8 + [newpalette()]*3 + [
	# newpalette(),
	# newpalette(),
	# newpalette(),
	# newpalette(),
	# newpalette(),
	# newpalette(anim=True),
	# newpalette(anim=True),
	# newpalette(anim=True),
	# newpalette(anim=True),
	# newpalette(anim=True),
	# newpalette(anim=True),
	# newpalette(anim=True),
	# newpalette(anim=True),
	# newpalette(),
	# newpalette(),
	# newpalette(),
	newpalette([[0,16,32]]),
]

def palettelisteditor(
		mInfo: MenuInfo,
		selection: SelectionInfo,
		basecrumbs: list[str] = []
	):
	
	mInfo.addnavigationoptions(False)
	mInfo.addbatchmanipoptions()

	datas = selection.getdatas()
	sSumm = selection.getsummary()
	indexes = [k for k in datas]
	page = 0
	maxpage = len(indexes)

	while True:
		message = (
			breadcrumbtrail(basecrumbs),
			showpalettes(datas, page),
			pageinfo(
				page,
				maxpage,
				mpselectedpreview(selection, indexes[page])
			),
		)

		match menudialog(mInfo, sSumm, True, message, 30):
			
			case '>':
				page = (page + 1) % maxpage
			case '<':
				page = (page - 1) % maxpage

			case 'res':
				datas = selection.getdatas()
				progress("Palette order reverted", True)
				break

			case 'ok':
				progress("Saving palette order")
				selection.setdatas(datas, True)
				progress("Palette order saved!", True)
				break

			case 'a2s':
				datas = {
					k: animated2static(d)
					for k, d in datas.items()
				}
			
			case 'ssx':
				datas = {
					k: stripstaticframes(d)
					for k, d in datas.items()
				}

			case 0:
				datas = manualpaletteorder(datas, page)

			case _ :
				woops('not implemented')


# def showsummary(datas:dict[int, list[dict]]):
# 	pass


def showpalettes(datas:dict[int, list[dict]], page:int=0) ->str:
	data = [d for d in datas.values()][page]
	palettes:list[MPPalette] = data[0]["PALETTES"]
	
	# screens:list[dict[str]] = data[0].get("SCREENS", None)

	def shadecolor(cId:int, big:bool=True) ->str:
		esc = painttext(*ENIGMACOLORS_RGB[cId])
		char = ENIGMACOLORS_CHARS.get(cId, '█') * (big+1)
		return esc+char

	# pShades = {}
	sShades = []
	aShades = []

	for i, pal in enumerate(palettes):
		frames = [f[::-1] for f in pal['f']] #----------------------------------lighter shades first
		static = i < 20
		single = len(frames) < 2

		esc = '\33['+ ('3','9')[i in ENIGMAPALETTES_LEGAL]
		esc += ('7','3')[static and not single] +'m\0\33[39m'
		# stats = list(map(str, [i, pal['s']]))
		stats = [esc.replace('\0', str(s)) for s in [i, pal['s']]]

		colors = [
			shadecolor(col, static and single)
			for col in sum(frames, [])
		]
		shades = rowsfromlist(
			colors,
			0,
			'',
			rnumber=3,
			vertical=True
		)

		# if screens:
		# 	pShades[i] = (
		# 		painttext(*ENIGMACOLORS_RGB[frames[0][0]]),
		# 		painttext(*ENIGMACOLORS_RGB[frames[0][1]], True),
		# 		painttext(*ENIGMACOLORS_RGB[frames[0][2]]),
		# 	)
		
		if static:
			sShades.extend(stats+shades)
			continue
		aShades.extend(stats+shades)

	preview = '\n'.join(
		rowsfromlist(
			rowsfromlist(
				sShades,
				0,
				'\033[39m ',
				rnumber=5,
				vertical=True
			) +
			rowsfromlist(
				aShades,
				0,
				'\033[39m ',
				rnumber=5,
				vertical=True
			),
			0,
			' | ',
			vertical=True
		)
	)+'\33[39m'

	if (newwidth := len(preview[0])) > terminalsize(0):
		progress('Adjusting window width to fit all info')
		print(f'\33[8;{newwidth}t', end='')

	# if screens:
	# 	showroomcolors(
	# 		screens,
	# 		pShades
	# 	)
	
	return preview


def showroomcolors(screens, palettesshades:dict[tuple[str,str,str]]) ->str:

	def autofilllayer(layer:list[list[int]]) ->list[list[int]]:
		if not layer:
			return [[0]*15]*20
		
		for column in layer:
			if not column:
				column = [0]*15
		return layer
	
	def colortile(t1 = 0, t0 = 0, t2 = 0, tl = 0):
		# if t2%4096 not in ENIGMATILES_INVISIBLE:
		# 	pId = t2//4096%32
		if t1%4096 not in ENIGMATILES_INVISIBLE:
			pId = t1//4096%32
		elif t0%4096 not in ENIGMATILES_INVISIBLE:
			pId = t0//4096%32
		else:
		# if t1 in ENIGMATILES_INVISIBLE:
			return '  '
		# pId = t1//4096%32
		
		shades = palettesshades.get(pId, ('','',''))

		return shades[0]+shades[1]+'▀'+shades[2]+'▄\33[0m'
	
		
	rSizeX, rSizeY = (
		max(((xposs := [s["x"] for s in screens]))) - (xOff := min(xposs)) + 1,
		max(((yposs := [s["y"] for s in screens]))) - (yOff := min(yposs)) + 1,
	)
	del xposs, yposs
	
	rTiles:list[list[list[str]]] = [
		[['  '*20]*15]*rSizeY
		for _ in range(rSizeX)
	]

	for screen in screens:
		sX, sY = screen["x"]-xOff, screen["y"]-yOff
		tiles:list[list[list[int]]] = screen["TILES"].copy()
		tiles[0] = autofilllayer(tiles[0])
		tiles[2] = autofilllayer(tiles[2])

		rTiles[sX][sY] = rowsfromlist(
			list(map(
					colortile,
					sum(tiles[1], []),
					# sum(tiles[1], []),
					sum(tiles[0], []),
					# sum(tiles[2], [])
				)),
			2,
			'',
			20,
			vertical=True
		)
		# ),sep='\n')
		
	# print(*rTiles, sep='\nSCREENS\n')
	# print(*sum(rTiles,[]), sep='\n')
	# print(*sum(sum(rTiles,[]),[]), sep='\n')
	print(*rowsfromlist(
		rowsfromlist(
			sum(sum(rTiles, []), []),
			0,
			'',
			rSizeX,
			# rnumber=15,
			vertical=True
		),
		0,
		# '',
		# cnumber=rSizeX,
		rnumber=15*rSizeY,
		# vertical=True
		),
		sep='\n'
	)


def animated2static(data:list[dict]) ->list[dict]:
	for pal in data[0]["PALETTES"]:
		if len((frames := pal["f"])) < 2 or any(f != frames[0] for f in frames):#ignore static palettes & animated palettes with unique frames
			continue

		pal = stripframes(pal)
	return data


def stripstaticframes(data:list[dict]) ->list[dict]:
	for pId, pal in enumerate(data[0]["PALETTES"]):
		if pId > 20 or len(pal["f"]) < 2: #-------------------------------------ignore palette with ids over 20 and less than 2 frames
			continue
		
		data[0]["PALETTES"][pId] = stripframes(pal)
	return data


def stripframes(palette:dict[str,int|list[int]]) -> dict[str,int|list[int]]:
	palette["s"] = 0 #----------------------------------------------------------set speed to 0
	palette["f"] = palette["f"][:1] #-------------------------------------------limit frames to first
	return palette


def manualpaletteorder(datas:dict[int,list[dict]], page:int):
	mainkey = [k for k in datas][page]
	mainpalettes = datas[mainkey][0]["PALETTES"].copy()
	
	requests = []
	for r in listdialog(
		'Enter reorder requests',
		[
			'a request goes as follows: [#][palette id]-[slot to insert]',
			'add a "#" to make a hard change, leave no prefix to make an auto change',
			'"hard" changes move each palette by id to the desired slot',
			'"auto" changes move each palette corresponding to the previewed palette id to the desired slot, if available',
			'example : 7-2 8-4 #9-7',
		]
	):
		try:
			request = list(map(int, r.lstrip('#-').split('-')[:2])) #-----------limit list to 2 items & attempt to parse to integer
			if any(i > 31 for i in request): #----------------------------------if any of the values is over 31, ignore request
				raise ValueError
		except ValueError:
			progress(f'{r} removed')
			continue

		request += [r.startswith('#')] #----------------------------------------3rd parameter determines if change should be "hard"
		requests.append(request)
	
	if not requests:
		progress("Operation cancelled",True)
		return datas
	
	requests.sort()
	# progress('Requests :', *requests, sep='\n')
	
	changes = getchanges(fillunsetorders(*getorders(requests)))
	# print(*changes.items(), sep='\t')

	if len(datas) > 1:
		orders, softs = getorders(
			requests,
			False,
			mainpalettes# + ENIGMAPALETTES_DEFAULTSHADES[28:]
		)
	
	for k in datas:
		if k == mainkey: #------------------------------------------------------do the main first, others after
			palettes = mainpalettes
		else:
			palettes:list[MPPalette] = datas[k][0]["PALETTES"].copy()
			changes = getchanges(fillunsetorders(*getorders(
						None,
						True,
						palettes,
						orders,
						softs
					)))
			
		# print(*changes.items(), sep='\t')
		# pLength = len(datas[k][0]["PALETTES"])
		palettes += ENIGMAPALETTES_DEFAULTSHADES[28:]

		updatepalettelist(datas[k], changes, palettes)
		
		try:
			datas[k] = updatetilespalette(datas[k], changes)
		except KeyError: #------------------------------------------------------if not room (palette)
			continue

	return datas


def getorders(
		requests:list[int|bool]|None,
		main:bool = True,
		palettes:list[dict] = [],
		orders:list[None|int] = [],
		softs:list[int] = [],
	) -> tuple[list[int|None|dict], list[int|None]]:

	if requests is None: #------------------------------------------------------if requests have already been parsed,
		for slot, pId in enumerate(orders): #-----------------------------------iterate through orders
			if type(pId) is not dict:
				continue
			try:
				if (pId := palettes.index(pId)) in orders: #--------------------find and assign matching palette except if it's already taken
					raise ValueError
				orders[slot] = pId
				softs.remove(pId) #---------------------------------------------this id is no longer soft
			except ValueError: #------------------------------------------------if requested palette is not found, mark available for replacement
				orders[slot] = None
		
		return orders, softs
	
	orders = [None]*32
	softs = list(range(32))
	
	if main: #------------------------------------------------------------------when all orders should be hard changes,
		for pId, slot, hard in requests: #--------------------------------------parse requests...
			orders[slot] = pId #------------------------------------------------new change
			softs.remove(pId) #-------------------------------------------------this id is no longer soft

		return orders, softs
	
	for pId, slot, hard in requests: #------------------------------------------parse requests...
		if hard: #--------------------------------------------------------------if request demands hard change
			orders[slot] = pId #------------------------------------------------new change
			softs.remove(pId) #-------------------------------------------------this id is no longer soft
			continue
		try:
			orders[slot] = palettes[pId] #--------------------------------------remember palette to assign id later
		except IndexError:
			orders[slot] = pId

	return orders, softs


def fillunsetorders(orders:list[None|int], softs:list[int]) ->list[int]:
	for slot in [s for s, p in enumerate(orders) if p is None]: #---------------for all unset slots, fill with remaining soft slots
		orders[slot] = softs.pop(0)
	return orders


def getchanges(orders:list[int]) ->dict[int,int]:
	return {s: p for s, p in enumerate(orders) if s != p}


def updatepalettelist(
		data:list[dict],
		changes:dict[int,int],
		palettes:list[MPPalette]
	) ->list[dict]:
	for slot, pId in changes.items():
		try:
			data[0]["PALETTES"][slot] = palettes[pId]
		except IndexError:
			progress("can't put palette %i in slot %i"%(pId, slot))
	return data


def updatetilespalette(data:list[dict], changes:dict[int,int]) ->list[dict]:
	changes = {p:(s-p)*4096 for s, p in changes.items()} #----------------------precalculate difference of tile data
	stats = 0
	# print(*changes.items(), sep='\t\t')

	for screen in data[0]["SCREENS"]:
		for l, layer in enumerate(screen["TILES"]):
			if l > 2: #---------------------------------------------------------if liquid, end loop
				break

			for column in layer:
				for t, tile in enumerate(column):
					if tile%4096 in ENIGMATILES_INVISIBLE: #--------------------ignore tiles with no palette
						continue

					if (pId := tile//4096%32) in changes.keys(): #--------------if tile needs to change,
						print(tile, '>', tile+changes[pId], end=' | ')
						column[t] += changes[pId] #-----------------------------add the appropriate amount to the tile
						stats += 1
	print('')
	progress(f'Updated {stats} tiles', True)
	return data

# def autopaletteorder(datas, mode) ->dict[list[dict]]:
# 	match mode:
# 		case 1:
# 			pass
# 		case _:
# 			pass
	
# 	return datas