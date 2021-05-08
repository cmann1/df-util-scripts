from dustmaker import *
from dustmaker.Entity import Trigger, FogTrigger, Apple
import sys
import os.path
import math
import re
import png
from font import RenderFont

parallaxOffset = (0, 0) # A global offset for all parallax layers
parallaxLayersOffset = { # Offsets for individual layers
	6: (0, 0),
	7: (0, 0),
	8: (0, 0),
	9: (0, 0),
	10: (0, 0),
	11: (0, 0)
}
forceFogTrigger = 0
renderEntities = True
padding = 4
tiles = {}
entitySprites = {}
layerList = []


def getTileName(tile):
	return "tiles/%s/tile%d_%d_0001.png" % (
        tile.sprite_set().name, tile.sprite_tile(), tile.sprite_palette() + 1)


def int2rgb(int):
	return [
		(int >> 16) & 255,
		(int >> 8) & 255,
		(int >> 0) & 255
	]


class LayersImage(object):
	def __init__(self, index):
		self.index = index
		self.realMinX = 0
		self.realMinY = 0
		self.minX = sys.maxsize
		self.minY = sys.maxsize
		self.maxX = - sys.maxsize
		self.maxY = - sys.maxsize
		self.sizeX = 0
		self.sizeY = 0
		self.tiles = []
		self.entities = []
		self.colour = [0, 0, 0]
		self.blend = 0
	
	def update(self):
		self.sizeX = self.maxX - self.minX + 1
		self.sizeY = self.maxY - self.minY + 1
		
	def updateOffsets(self, maxSizeX, maxSizeY):
		self.realMinX = self.minX
		self.realMinY = self.minY
		
		self.minX -= padding
		self.minY -= padding
		
		if self.index > 11 and self.index != 19:
			self.minX = layerList[19].minX
			self.minY = layerList[19].minY
		#
		else:
			if self.index >= 6 and self.index < 12:
				layerOffsets = parallaxLayersOffset[self.index]
				self.minX -= parallaxOffset[0] + layerOffsets[0]
				self.minY -= parallaxOffset[1] + layerOffsets[1]
			#
			if maxSizeX > self.sizeX:
				self.minX -= math.floor((maxSizeX - self.sizeX) / 2)
			#
			if maxSizeY > self.sizeY:
				self.minY -= math.floor((maxSizeY - self.sizeY) / 2)
			#
		#
# END class LayersImage


def renderLevel(levelName):
	global layerList
	global entitySprites
	
	with open("maps/" + levelName, "rb") as f:
		map = read_map(f.read())
	#
	
	print("Rendering: " + levelName + ' [' + map.name() + ']')

	bgColour = [0, 0, 0, 255]
	layerList = [LayersImage(x) for x in range(23)]
	
	entityLayer = layerList[18]
	collisionLayer = layerList[19]
	fogTriggerCount = -1

	# Get fog colours
	for (id, (x, y, entity)) in list(map.entities.items()):
		if isinstance(entity, FogTrigger):
			# log.write(str(entity.vars) + "\n")
			# for name, var in entity.vars.items():
				# log.write(str(name) + ': ' + str(var) + "\n")
			#
			
			fogTriggerCount += 1
			
			if fogTriggerCount != forceFogTrigger:
				continue
			#
			
			vars = entity.vars
			gradient_middle = vars['gradient_middle'].value
			gradient = vars['gradient'].value[1]
			fog_per = vars['fog_per'].value[1]
			fog_colour = vars['fog_colour'].value[1]
			
			# log.write(str(gradient_middle) + "\n")
			# log.write(str(gradient) + "\n")
			# log.write(str(fog_per) + "\n")
			# log.write(str(fog_colour) + "\n")
			
			g1 = int2rgb(gradient[0].value)
			g2 = int2rgb(gradient[1].value)
			g3 = int2rgb(gradient[2].value)
			
			bgColour[0] = round((g1[0] + g2[0] + g3[0]) / 3)
			bgColour[1] = round((g1[1] + g2[1] + g3[1]) / 3)
			bgColour[2] = round((g1[2] + g2[2] + g3[2]) / 3)
			
			for i in range(21):
				layerList[i].colour = int2rgb(fog_colour[i].value)
				layerList[i].blend = fog_per[i].value
			#
			
			log.write(str(bgColour) + '\n')
		#
		elif renderEntities and (isinstance(entity, Enemy) or isinstance(entity, Apple)):
			spritePath = 'sprites/'
			sprite = entity.type
			if isinstance(entity, Apple):
				spritePath += 'entity/'
			#
			else:
				spritePath += 'enemy/'
				sprite = re.sub(r"^enemy_", r"", sprite)
			#
			spritePath += sprite + '.png'
			
			if not os.path.isfile(spritePath):
				log.write("Cannot find sprite [" + spritePath + "]\n")
				continue
			#
			
			if spritePath not in entitySprites:
				reader = png.Reader(spritePath)
				w, h, pixels, metadata = reader.read()
				pixels = list(pixels)
				# width, height, offsetX, offsetY, pixels
				entitySprites[spritePath] = (w, h, math.floor(w/2), h, pixels)
			#
			
			entityLayer.entities.append([x, y, spritePath])
			# log.write(str(spritePath) + "\n")
		#
	#

	# Calculate sizes
	for id, tile in map.tiles.items():
		layer, x, y = id
		
		layerData = layerList[layer]
		
		layerData.tiles.append((layer, x, y, getTileName(tile)))
		layerData.minX = min(layerData.minX, x)
		layerData.minY = min(layerData.minY, y)
		layerData.maxX = max(layerData.maxX, x)
		layerData.maxY = max(layerData.maxY, y)
	#

	maxSizeX = 0
	maxSizeY = 0
	for layerData in layerList:
		layerData.update()
		maxSizeX = max(maxSizeX, layerData.sizeX)
		maxSizeY = max(maxSizeY, layerData.sizeY)
	#
	layerList[19].updateOffsets(maxSizeX, maxSizeY)	
	for layerData in layerList:
		if layerData.index != 19:
			layerData.updateOffsets(maxSizeX, maxSizeY)
		#
	#

	maxSizeX += padding * 2
	maxSizeY += padding * 2
	w, h = maxSizeX * 4, maxSizeY;
	pixels = [[bgColour[x % 4] for x in range(w)] for y in range(h)]

	# Write to pixels array
	for layerData in layerList:
		# log.write("----\n")
		minX = layerData.minX
		minY = layerData.minY
		layerColour = layerData.colour
		layerBlend = layerData.blend
		
		for tileData in layerData.tiles:
			layer, x, y, sprite = tileData
			
			# if layer == 17:
				# continue
			# if layer != 6 and layer != 8:
				# continue
			#
			
			if sprite not in tiles:
				alt_sprite = ''
				if not os.path.isfile(sprite):
					base = os.path.basename(sprite)
					alt_sprite = sprite
					sprite = os.path.dirname(sprite) + '/' + re.sub(r"^tile(\d+)_(\d+)_0001\.png$", r"tile\1_1_0001.png", base)
					# log.write(base + ' - ' + re.sub(r"^tile(\d+)_(\d+)_0001\.png$", r"tile\1_1_0001.png", base) + "\n")
					# log.write(alt_sprite + ' - ' + sprite + "\n")
				#
				reader = png.Reader(sprite)
				w, h, tilePixels, metadata = reader.read()
				rgb = list(tilePixels)[0]
				tiles[sprite] = [rgb[0], rgb[1], rgb[2], rgb[3]]
				
				if alt_sprite != '':
					tiles[alt_sprite] = tiles[sprite]
				#
			#
			
			r, g, b, a = tiles[sprite]
			a /= 255
			
			px = x - minX
			py = y - minY
			
			if px < 0 or py < 0 or px >= maxSizeX or py >= maxSizeY:
				continue
			#
			
			if layerData.blend > 0:
				r = r + (layerColour[0] - r) * layerBlend
				g = g + (layerColour[1] - g) * layerBlend
				b = b + (layerColour[2] - b) * layerBlend
			#
			
			pi = px * 4;
			dstr = pixels[py][pi + 0]
			dstg = pixels[py][pi + 1]
			dstb = pixels[py][pi + 2]
			pixels[py][pi + 0] = round(dstr + (r - dstr) * a)
			pixels[py][pi + 1] = round(dstg + (g - dstg) * a)
			pixels[py][pi + 2] = round(dstb + (b - dstb) * a)
			# pixels[py][pi + 1] = 0
			# pixels[py][pi + 2] = 0
			# pixels[py][pi + 3] = 255
			
			# if pixels[py][pi + 0] > 255 or pixels[py][pi + 1] > 255 or pixels[py][pi + 2] > 255:
				# log.write(str(dstg) + ', ' + str(g) + ', ' + str(a) + ', ' + "\n")
				# log.write(' - ' + str(layerData.colour[0]) + ', ' + str(layerData.colour[1]) + ', ' + str(layerData.colour[2]) + ', ' + "\n")
		# END for tiles
		
		if renderEntities:
			for ex, ey, spritePath in layerData.entities:
				width, height, offsetX, offsetY, entityPixels = entitySprites[spritePath]
				
				for y in range(height):
					pixRow = entityPixels[y]
					for x in range(width):
						spritei = x * 4
						r = pixRow[spritei + 0]
						g = pixRow[spritei + 1]
						b = pixRow[spritei + 2]
						
						# px = round(ex) + x - offsetX
						# py = round(ey) + y - offsetY
						px = round(ex) - collisionLayer.minX + x - offsetX
						py = round(ey) - collisionLayer.minY + y - offsetY
						
						if px < 0 or py < 0 or px >= maxSizeX or py >= maxSizeY:
							continue
						#

						if layerData.blend > 0:
							r = r + (layerColour[0] - r) * layerBlend
							g = g + (layerColour[1] - g) * layerBlend
							b = b + (layerColour[2] - b) * layerBlend
						#
						
						pi = px * 4;
						pixels[py][pi + 0] = round(r)
						pixels[py][pi + 1] = round(g)
						pixels[py][pi + 2] = round(b)
						
					# END for x
				# END for y
			#
		# END for entities
	# END for layerList
		
	# Write the png
	# log.write(str(pixels) + "\n")
	png.from_array(pixels, 'RGBA').save('output/' + levelName + ".png")
	
	return map.name()
# END renderMap


log = open("log.txt", "w")
# levels = ["zetta", "kilo"]
levels = os.listdir('maps')

font = RenderFont()

for levelName in levels:
	name = renderLevel(levelName)
	font.render(name, 'output/' + levelName + '-name.png')
#

log.close() 
















