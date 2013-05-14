import os, sys, msvcrt, time, random, math

#helpers
def Clamp(i, a, b):
	if i < a: i = a
	if i > b: i = b
	return i
def RadiusCoordinates(Radius):
	ret = []
	for x in xrange(-Radius-1, Radius+2):
		for y in xrange(-Radius-1, Radius+2):
			if math.sqrt(x**2 + y**2) <= Radius:
				ret.append((x, y))
	return ret
def Line((x,y), (x2,y2)):#Brensenhams line algorithm:
	#Copied from someplace on the internet long ago
	steep = 0
	coords = []
	dx = abs(x2 - x)
	if (x2 - x) > 0:
		sx = 1
	else:
		sx = -1
	dy = abs(y2 - y)
	if (y2 - y) > 0:
		sy = 1
	else:
		sy = -1
	if dy > dx:
		steep = 1
		x,y = y,x
		dx,dy = dy,dx
		sx,sy = sy,sx
	d = (2 * dy) - dx
	for i in range(0,dx):
		if steep:
			coords.append((y,x))
		else:
			coords.append((x,y))
		while d >= 0:
			y = y + sy
			d = d - (2 * dx)
		x = x + sx
		d = d + (2 * dy)
	coords.append((x2,y2))
	return coords

#le game classes:
class terminal:
	def __init__(self):
		os.system("mode 120,46")#should be 45, but shit's niggertastic
		#os.system("Le RPG - by pbsds")
		os.system("clear")
		
		self.updated = False
		
		#self.buffer = [[" " for i in xrange(120)] for i in xrange(45)]
		self.buffer = [" " for i in xrange(120*45)]
		self.rectangle((1, 1), (80, 35))
		self.rectangle((1, 35), (118, 10))
		self.rectangle((80, 1), (39, 18))
		self.rectangle((80, 18), (39, 18))
	def rectangle(self, pos, size, char="#", filled = False):
		if filled:
			for x in xrange(pos[0], pos[0]+size[0]):
				for y in xrange(pos[1]*120, (pos[1]+size[1])*120, 120):
					self.buffer[x + y] = char
		else:
			x1, x2 = pos[0], pos[0]+size[0]-1
			y1, y2 = pos[1]*120, (pos[1]+size[1]-1)*120
			for i in xrange(pos[0], pos[0]+size[0]):
				self.buffer[i + y1] = char
				self.buffer[i + y2] = char
			for i in xrange(pos[1], pos[1]+size[1]):
				self.buffer[x1 + i*120] = char
				self.buffer[x2 + i*120] = char
		self.updated = True
	def blit(self, spr, pos):#spr is a list where each item is a string. the list represents the y axis
		w = len(spr[0])
		h = len(spr)
		
		for x in xrange(w):
			for y in xrange(h):
				#self.buffer[x][y] = 
				spr[y][x]
				self.buffer[pos[0] + x + (pos[1]+y)*120]
				self.buffer[pos[0] + x + (pos[1]+y)*120] = spr[y][x]
		self.updated = True
	def set(self, char, (x, y)):
		self.buffer[x + y*120] = char
		self.updated = True
	def render(self):
		if self.updated:
			#sys.stdout.seek(0)
			os.system("cls")
			sys.stdout.write("".join(self.buffer))
			#sys.stdout.flush()
			self.updated = False

class cmd:
	def __init__(self):
		self.pos = (3, 36)
		self.size = (114, 8)
		self.lines = []
		
		self.updated = False
	def Print(self, string):
		self.lines.append(string[:self.size[0]] + " "*(self.size[0]-min((len(string),self.size[0]))))
		if len(self.lines) > self.size[1]: self.lines.pop(0)
		self.updated = True
	def render(self):
		if self.updated:
			if self.lines:
				terminal.blit(self.lines, self.pos)
			self.updated = False

class inventory:
	def __init__(self):
		self.bag = {"Coins":250, "Potion of Health": 5, "Potion of Mana":5, "Town Blinkwing":2}
		self.page = 0
		
		self.bagupdate = True
		self.statsupdate = True
		self.facingupdate = True
		
		terminal.blit(["Character stats:"], (82, 20))
		
		self.keys = "123456789xz"
		
		self.worldinfo=(("== Town ==", "You fully heal when coming here", "You can sell your items by", "selecting them with the 1-9 key."),
						("== Stone ==", "It's in your way.", "You can hack it down with SPACE.", "Each stone gives 1 rubble."),
						("== Dungeon / Cave entrance ==", "A nasty place crawling with monsters", "and loot. Do you dare step foot", "within and loot it?", "Enter with SPACE."),
						("== A Tree ==", "Sells for 5 Coins", "You get 5 wood for each tree", "Used to make campfires", "Chop down with SPACE"),
						("== Gold ore ==", "Valuable resource", "One ore gives around 10 gold ingots", "Used for crafting and sells for a", "good price.", "Mine it with SPACE."),
						("== Diamond ==", "An exeptionally rare find!", "Sells for a high price and it's one", "of the strongest materials you can", "find.", "Mine it with SPACE."))
		self.mobinfo = (("== Goblin ==", "Has a lot of health and can take", "a hit. Drops 10 coins."),
						("== Imp ==", "Has little health, but powerfull", "attacks! Drops 15 coins."),
						("== Bat ==", "Annoying little flying brats.", "A simple slay, but it only drops 10", "coins."))
	def add(self, item, count=1):
		if item in self.bag:
			self.bag[item] += count
		else:
			self.bag[item] = count
		cmd.Print("Got %i %s!" % (count, item))
		self.bagupdate = True
	def take(self, item, count):
		if item not in self.bag:
			return False
		if self.bag[item] >= count:
			return False
		
		self.bag[item] -= count
		if self.bag[item] == 0:
			del self.bag[item]
		self.bagupdate = True
		return True
	def Keypress(self, key):
		if key.isdigit():
			if int(key)-1+9*self.page < len(self.bag):
				self.UseItem(key)
			else:
				cmd.Print("You don't have any items in slot %s!" % key)
			world.doStep = True
		elif key in "xz":
			if key == "x":
				self.page += 1
				if self.page >= (len(self.bag)+8)/9:
					self.page = 0
			else:
				self.page -= 1
				if self.page < 0:
					self.page = (len(self.bag)+8)/9-1
			self.bagupdate = True
	def UseItem(self, key):
		list = self.bag.keys()
		list.sort()
		item = list[int(key)-1+9*self.page]
		
		if item == "Coins" and world.facing[0] == 1:
			cmd.Print("There is nothing here to buy!")
		elif item == "Town Blinkwing":
			self.take("Town blinkwing", 1)
			cmd.Print("teleported back to town! 1 Town Blinkwing consumed.")
			
			
			world.you[0] = [world.townpos[0], world.townpos[1] + 1]
			world.orientation = "s"
			world.UpdateFacing()
			self.statsupdate = True
		#elif item == "":
		#	pass
		else:
			cmd.Print("You can't use that at the moment...")
		
		#self.bagupdate = True
		pass
	def render(self):
		if self.bagupdate:
			self.bagupdate = False
			
			#clean area:
			terminal.rectangle((82, 24), (36, 10), " ", True)
			
			terminal.blit(["Page %i of %i of inventory:" % (self.page+1, (len(self.bag)+8)/9)], (82, 24))
			lst = self.bag.keys()
			lst.sort()
			for i, item in enumerate(lst[self.page*9:self.page*9+9]):
				a = "%i - %s:" % (i+1, item)
				b = str(self.bag[item])
				terminal.blit(["%s%s%s" % (a, " "*(33-len(a)-len(b)), b)], (83, 25+i))
		
		if self.statsupdate:
			self.statsupdate = False
			
			#clean area:
			terminal.rectangle((82, 21), (35, 2), " ", True)
			
			hp = "%s/%s" % (world.you[2], world.you[3])
			mp = "%s/%s" % (world.you[4], world.you[5])
			at = str(world.you[1])
			dir = {None:"", "w":"Up", "s":"Down", "a":"Left", "d":"Right"}[world.orientation]
			terminal.blit(["Health:%s%s  Mana:%s%s" % (" "*(8-len(hp)), hp, " "*(11-len(mp)), mp)], (83, 21))
			terminal.blit(["Attack:%s%s  Direction:%s%s" % (" "*(8-len(at)), at, " "*(6-len(dir)), dir)], (83, 22))
		
		if self.facingupdate:
			self.facingupdate = False
			
			#clean area:
			terminal.rectangle((82, 3), (36, 14), " ", True)
			
			if world.facing[0]:#world blocks:
				for i, line in enumerate(self.worldinfo[world.facing[0]-1]):
					if line: terminal.blit([line], (82, 3+i))
			elif world.facing[1] >= 0:#entities:
				pos, type, lv, items, at, hp, mp = world.entities[world.facing[1]]
				
				for i, line in enumerate(self.mobinfo[type]):
					if line: terminal.blit([line], (82, 3+i))
				
				terminal.blit(["Health:%s%i  Mana:%s%i" % (" "*(8-len(str(hp))), hp, " "*(11-len(str(mp))), mp)], (82, 15))
				terminal.blit(["Attack:%s%i  Level:%s%i" % (" "*(8-len(str(at))), at, " "*(10-len(str(lv))), lv)], (82, 16))
				

class world:
	def __init__(self):
		self.pos = (2, 2)
		#self.size = (26*3, 33)
		self.size = (26, 33)#the width gets multiplied by 3
		#self.buffer = [["   " for _ in xrange(self.size[0]/3)] for _ in xrange(self.size[1])]#[y][x]
		playerpos = self.GenWorld((250, 250))
		
		#the sprites the world is made of:
		self.spr = ("   ",#nothing
					"TWN",#town
					"###",#blockade
					"/ \\",#entrance
					'"Y"',#Tree
					"HHH",#gold ore
					"#*#")#diamond
		
		self.you = [playerpos, 3, 100, 100, 5, 5]#[pos, attack, health, max health, mana, max mana]
		self.facing = [0, -1, [playerpos[0], playerpos[1]+1]]#[block, entity index, facingpos]
		self.orientation = "s"#the last pressed movement button
		self.sprYou = "\\o/"
		
		self.creatures  =  (("GOB", "Goblin", 10, 1, 0, 2, 0.5, 0, {}, 0, {"Coins":10, "Potion of Health":0.5}, 10),#(spr, name, base health, base attack, base mana, healthgain, attackgain, managain, item dictionary, item use chance %, drop dictionary, walk chance)
							("IMP", "Imp", 10, 2, 0, 1, 1, 0, {}, 0, {"Coins":15, "Potion of Mana":0.5}, 18),
							("~o~", "Bat", 5, 1, 0, 0.5, 0.5, 0, {}, 0, {"Coins":5}, 80))
		self.entities = []#[x] = [pos, type, lv, items, attack, health, mana]
		self.deathnote = []#indexes with those entities which shall die
		
		#spawn the entities:
		worst = (0, 0)
		spawnrange = RadiusCoordinates(4)
		for i in xrange(self.worldsize[0]/25*self.worldsize[1]/25):#for each 20*2 square block the world has, spawn:
			#up to 8 bats, or up to 5 goblins or up to 6 imps
			while 1:
				x = random.randrange(0, self.worldsize[0])
				y = random.randrange(0, self.worldsize[1])
				
				if not self.CheckOpen((x, y)): continue
				
				type, quantity = random.choice(((0, 5), (1, 6), (2, 8)))
				dist = math.sqrt((x-self.townpos[0])**2 + (y-self.townpos[1])**2)
				lv =  int(dist / 60) + 1*(random.randrange(0, 11) == 10)# + 1
				
				bHP, bAT, bMP,  HPg, ATg, MPg, items = self.creatures[type][2:9]
				
				self.entities.append([[x, y], type, lv+1, items, bAT+int(ATg*lv), bHP+int(HPg*lv), bMP+int(MPg*lv)])
				if lv > worst[0] or (lv == worst[0] and int(dist) < worst[1]): worst = (lv, int(dist))
				
				for _ in xrange(quantity-1):
					x2, y2 = random.choice(spawnrange)
					x2 += x
					y2 += y
					if self.CheckOpen((x2, y2)):
						dist = math.sqrt((x2-self.townpos[0])**2 + (y2-self.townpos[1])**2)
						lv =  int(dist / 60) + 1*(random.randrange(0, 11) == 10)# + 1
						
						self.entities.append([[x2, y2], type, lv+1, items, bAT+int(ATg*lv), bHP+int(HPg*lv), bMP+int(MPg*lv)])
						if lv > worst[0] or (lv == worst[0] and int(dist) < worst[1]): worst = (lv, int(dist))
				
				break
			
			#self.spawn(random.choice((0, 0, 1, 2, 2)))
			pass
		if worst[0]: cmd.Print("The highest leveled monster on this map is LV%i and is currently %i blocks away from you" % worst)
		
		self.doStep = False
		self.keys = "wasd "
		
		self.render()
	def GenWorld(self, size=(150, 150)):
		self.worldsize = size
		self.world = [[None for _ in xrange(size[0])] for _ in xrange(size[1])]#[x][y]
		
		
		self.townpos = (random.randrange(10, size[0]-10), random.randrange(10, size[1]-10))
		playerpos = [self.townpos[0], self.townpos[1]+2]
		
		#the town is preset, the rest is generated:
		for x in xrange(-8,9):
			for y in xrange(-8, 9):
				if math.sqrt(x*x + y*y) <= 8:
					self.world[self.townpos[0]+x][self.townpos[1]+y] = 0
		
		self.world[self.townpos[0]][self.townpos[1]] = 1#town
		
		self.world[self.townpos[0]-1][self.townpos[1]-3] = 2#wall
		self.world[self.townpos[0]  ][self.townpos[1]-3] = 2
		self.world[self.townpos[0]+1][self.townpos[1]-3] = 2
		self.world[self.townpos[0]-2][self.townpos[1]-2] = 2
		self.world[self.townpos[0]-1][self.townpos[1]-2] = 2
		self.world[self.townpos[0]  ][self.townpos[1]-2] = 2
		self.world[self.townpos[0]+1][self.townpos[1]-2] = 2
		self.world[self.townpos[0]+2][self.townpos[1]-2] = 2
		self.world[self.townpos[0]+2][self.townpos[1]-1] = 2
		self.world[self.townpos[0]+2][self.townpos[1]  ] = 2
		self.world[self.townpos[0]+2][self.townpos[1]+1] = 2
		self.world[self.townpos[0]+2][self.townpos[1]+2] = 2
		self.world[self.townpos[0]-2][self.townpos[1]-1] = 2
		self.world[self.townpos[0]-2][self.townpos[1]  ] = 2
		self.world[self.townpos[0]-2][self.townpos[1]+1] = 2
		self.world[self.townpos[0]-2][self.townpos[1]+2] = 2
		self.world[self.townpos[0]-1][self.townpos[1]+3] = 2
		self.world[self.townpos[0]+1][self.townpos[1]+3] = 2
		
		queue = []
		for i in xrange(size[0]/20*size[1]/20):
			x = random.randrange(0, size[0])
			y = random.randrange(0, size[1])
			if self.world[x][y] <> None: continue
			
			self.world[x][y] = 2#wall
			queue.append((x, y))
		
		
		
		#Create the land structures:
		caves = []
		while queue:
			x, y = queue.pop(random.randrange(0,len(queue)))
			
			for x2, y2 in ((x-1, y-1), (x, y-1), (x+1, y-1), (x+1, y), (x+1, y+1), (x, y+1), (x-1, y+1), (x-1, y)):#For each neightbor:
				if 0 <= x2 < size[0] and 0 <= y2 < size[1]:#If within the map:
					if self.world[x2][y2] == None:#If neighboring pixel isn't set yet:
						#if current pixel is ground, set neightboring pixels to ground.
						#if it's walls, set the neightboring pixel to either walls or ground chosen randomly
						if self.world[x][y] == 0:
							self.world[x2][y2] = 0#water
						else:
							if random.randrange(0,101) < 93:
								self.world[x2][y2] = 2#wall
							else:
								self.world[x2][y2] = 0#ground
								if x2==x and y2-y==1:
									caves.append((x, y))
						queue.append((x2,y2))
		
		#plant trees:
		for _ in xrange(size[0]/15*size[1]/15*2):
			x = random.randrange(0, size[0])
			y = random.randrange(0, size[1])
			
			if self.world[x][y] == 0:
				self.world[x][y] = 4#tree
		
		#spawn ores:
		diamonds = 0
		for _ in xrange(size[0]/20*size[1]/20):
			while 1:
				x = random.randrange(0, size[0])
				y = random.randrange(0, size[1])
				
				for x2 in xrange(x-1, x+2):
					for y2 in xrange(y-1, y+2):
						if 0 <= x2 < size[0] and 0 <= y2 < size[1]:
							if self.world[x2][y2] == 2:
								continue
						break
					else:
						continue
					break
				else:
					type = random.choice((5, 5, 5, 5, 5, 5, 6))
					self.world[x][y] = type
					if type == 6: diamonds += 1
					if random.randrange(0, 101) > 40*(type-4):
						x2 = random.choice((x-1, x, x+1))
						y2 = random.choice((y-1, y, y+1))
						self.world[x2][y2] = type
						if type == 6: diamonds += 1
						if random.randrange(0, 101) > 40*(type-4):#A second iteration perhaps?
							x2 = random.choice((x-1, x, x+1))
							y2 = random.choice((y-1, y, y+1))
							self.world[x2][y2] = type
							if type == 6: diamonds += 1
					break
		
		#check for valid cave positions and make them:
		toMake = size[0]/60*size[1]/60
		cavesMade = 0
		while toMake and caves:
			x, y = caves.pop(random.randrange(0,len(caves)))
			for x2, y2 in ((x-1, y), (x, y), (x+1, y), (x-1, y-1), (x, y-1), (x+1, y-1)):
				if 0 <= x2 < size[0] and 0 <= y2 < size[1]:#If within the map:
					if self.world[x2][y2] == 2:
						continue
				break
			else:
				#for x2, y2 in ((x-1, y+1), (x, y+1), (x+1, y+1), (x, y+2)):
				for x2, y2 in ((x, y+1), (x, y+2)):
					if 0 <= x2 < size[0] and 0 <= y2 < size[1]:#If within the map:
						if self.world[x2][y2] == 0:
							continue
					break
				else:
					toMake -= 1
					cavesMade += 1
					self.world[x][y] = 3#entrance
		
		cmd.Print("This world is newly generated, and it's %ix%i squares big!" % size)
		if cavesMade:
			cmd.Print("There are %i cave entrances hidden around the map, good luck looting them!" % cavesMade)
		if diamonds:
			cmd.Print("There are %i diamonds in this world." % diamonds)
		
		return playerpos
	def step(self):
		if self.doStep:
			self.doStep = False
			
			#step entities:
			for i, ((x, y), type, lv, items, at, hp, mp) in enumerate(self.entities):
				if i in self.deathnote: continue
				dist = math.sqrt((x-self.you[0][0])**2 + (y-self.you[0][1])**2)
				if dist <= 7:#if close enought:
					for x2, y2 in Line((x, y), self.you[0]):
						if self.world[x2][y2]:
							break
					else:#if player in sight:
						if dist > 1:#aproach player:
							dir = math.atan2(y - self.you[0][1], self.you[0][0] - x) / math.pi * 180
							x2, y2 = x, y
							if -45 < dir <= 45:
								x2 += 1
							elif -135 < dir <= -45:
								y2 += 1
							elif 45 < dir <= 135:
								y2 -= 1
							else:
								x2 -= 1
							
							if self.CheckOpen((x2, y2)):
								self.entities[i][0][0] = x2
								self.entities[i][0][1] = y2
								continue
							else:
								x2, y2 = x, y
								if -45 < dir <= 45:
									if dir >= 0:
										y2 -= 1
									else:
										y2 += 1
								elif -135 < dir <= -45:
									if dir >= -90:
										x2 += 1
									else:
										x2 -= 1
								elif 45 < dir <= 135:
									if dir >= 90:
										x2 -= 1
									else:
										x2 += 1
								else:
									if dir >= 0:
										y2 += 1
									else:
										y2 -= 1
								
								if self.CheckOpen((x2, y2)):
									self.entities[i][0][0] = x2
									self.entities[i][0][1] = y2
									continue
						else:#Attack:
							pass
							continue
				
				#step around carelessly:
				if random.randrange(1, 101) <= self.creatures[type][11]:
					x2, y2 = random.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
					if self.CheckOpen((x+x2, y+y2)):
						self.entities[i][0][0] += x2
						self.entities[i][0][1] += y2
				
			if self.deathnote:
				self.deathnote.sort()
				for i in self.deathnote[::-1]:
					del self.entities[i]
				self.deathnote = []
			
			self.UpdateFacing()
			
			self.render()
	def CheckOpen(self, (x, y), entities = True):#pos on map
		if not 0 <= x < self.worldsize[0]:
			return False
		if not 0 <= y < self.worldsize[1]:
			return False
		if self.world[x][y]:
			return False
		if entities:
			if self.you[0][0] == x and self.you[0][1] == y:
				return False
			for i in self.entities:
				if x == i[0][0] and y == i[0][1]:
					return False
		return True
	def Keypress(self, key):
		if key in "ws":#move up/down
			x, y = self.you[0]
			if key == "w":
				if self.CheckOpen((x, y-1)):
					self.you[0][1] -= 1
			else:
				if self.CheckOpen((x, y+1)):
					self.you[0][1] += 1
			if self.orientation <> key:
				inventory.statsupdate = True
				self.orientation = key
			self.doStep = True
		elif key in "ad":#move left/right
			x, y = self.you[0]
			if key == "a":
				if self.CheckOpen((x-1, y)):
					self.you[0][0] -= 1
			else:
				if self.CheckOpen((x+1, y)):
					self.you[0][0] += 1
			if self.orientation <> key:
				inventory.statsupdate = True
				self.orientation = key
			self.doStep = True
		elif key == " ":#action
			x, y = self.facing[2]
			if self.facing[0] == 2:#walls
				self.world[x][y] = 0
				inventory.add("Rubble")
			elif self.facing[0] == 4:#tree
				self.world[x][y] = 0
				inventory.add("Wood", 5)
			elif self.facing[0] == 5:#gold ore
				self.world[x][y] = 2
				inventory.add("Gold", random.choice((9, 10, 10, 10, 11)))
			elif self.facing[0] == 6:#diamond:
				self.world[x][y] = 2
				inventory.add("Diamond")
			elif self.facing[0] == 0 and self.facing[1] >= 0:#emptyspace, do entities:
				for i, entity in enumerate(self.entities):
					if x == entity[0][0] and y == entity[0][1]:
						dmg = random.choice((0, int(self.you[1]/2), self.you[1], self.you[1], self.you[1], self.you[1], self.you[1], self.you[1], self.you[1], self.you[1], int(self.you[1]*1.3), int(self.you[1]*1.6), self.you[1]*2))
						if dmg:
							cmd.Print("You attacked %s, did %i damage." % (self.creatures[entity[1]][1], dmg))
							self.entities[i][5] -= dmg
							if self.entities[i][5] <= 0:
								cmd.Print("%s was defeated." % self.creatures[entity[1]][1])
								#del self.entities[i]
								self.deathnote.append(i)
								luck = int(random.randrange(3, 12)/5)
								for item, n in self.creatures[entity[1]][10].items():#loot:
									if int(n*luck): inventory.add(item, int(n*luck))
						else:
							cmd.Print("You attacked %s, but it missed..." % self.creatures[entity[1]][1])
						break
						
			self.doStep = True
	def UpdateFacing(self):
		x, y = self.you[0]
		if self.orientation == "w":
			y -= 1
		elif self.orientation == "s":
			y += 1
		elif self.orientation == "a":
			x -= 1
		elif self.orientation == "d":
			x += 1
		
		prev = self.facing[:]
		
		if 0 <= x < self.worldsize[0] and 0 <= y < self.worldsize[1]:#If within the map:
			self.facing[0] = self.world[x][y]
			
			if self.facing[0]:
				self.facing[1] = -1
			else:
				for i, entity in enumerate(self.entities):
					if x == entity[0][0] and y == entity[0][1]:
						self.facing[1] = i
						break
				else:
					self.facing[1] = -1
		else:
			self.facing[0] = 0
			self.facing[1] = -1
		self.facing[2] = [x, y]
		
		if self.facing <> prev or self.facing[1] >= 0: inventory.facingupdate = True
	def render(self):
		render = []
		camx = Clamp(self.you[0][0]-self.size[0]/2, 0, self.worldsize[0]-self.size[0])
		camy = Clamp(self.you[0][1]-self.size[1]/2, 0, self.worldsize[1]-self.size[1])
		
		entities = []
		for i in self.entities:
			if camx <= i[0][0] < camx+self.size[0] and camy <= i[0][1] < camy+self.size[1]:
				entities.append(i)
		
		for y in xrange(camy, camy+self.size[1]):
			line = []
			for x in xrange(camx, camx+self.size[0]):
				if x == self.you[0][0] and y == self.you[0][1]:
					line.append(self.sprYou)
					continue
				if self.world[x][y]:
					line.append(self.spr[self.world[x][y]])
					continue
				for i in entities:
					if i[0][0] == x and i[0][1] == y:
						line.append(self.creatures[i[1]][0])
						break
				else:
					line.append(self.spr[0])
			render.append("".join(line))
		terminal.blit(render, self.pos)

#run game:		
terminal = terminal()
cmd = cmd()
cmd.Print("Welcome to CMDRPG!")
inventory = inventory()
print "Generating the world..."
world = world()


while 1:
	#15 fps
	time.sleep(1./15.)
	
	while msvcrt.kbhit():
		# cmd.keypress(msvcrt.getch())
		key = msvcrt.getch().lower()
		if key in inventory.keys: inventory.Keypress(key)
		if key in world.keys: world.Keypress(key)
	
	world.step()
	
	cmd.render()
	inventory.render()
	
	terminal.render()