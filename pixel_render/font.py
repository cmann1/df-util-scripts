import sys
import os.path
import math
import re
import png


class RenderFont(object):
	def __init__(self):
		self.charMap = {}
		self.lineHeight = 0
		self.base = 0
		
		f = open("cube.fnt")
		data = f.readlines()
		f.close()
		
		# line height and base
		sizes = re.split(r'[\t ]+', data[1].rstrip('\t \n\r'))
		self.lineHeight = int(sizes[0])
		self.base = int(sizes[1])
		
		reader = png.Reader('cube.png')
		w, h, fontPixelData, metadata = reader.read()
		fontPixels = list(fontPixelData)
		
		for lineIndex in range(3, len(data)):
			
			id, x, y, width, height, xoffset, yoffset, xadvance = [int(n) for n in re.split(r'[\t ]+', data[lineIndex].rstrip('\t \n\r'))]
			
			char = {}
			pixels = []
			
			for py in range(height):
				for px in range(width):
					pixels.append(fontPixels[y + py][x + px])
				#
			#
			
			char['id'] = id
			char['x'] = x
			char['y'] = y
			char['width'] = width
			char['height'] = height
			char['xoffset'] = xoffset
			char['yoffset'] = yoffset
			char['xadvance'] = xadvance
			char['pixels'] = pixels
			
			self.charMap[id] = char
		#
		
	# END init
	
	def getCharData(self, char):
		charId = ord(char)
			
		# Replace unknown chars with a space
		if charId not in self.charMap:
			charId = 32
		#
		
		return self.charMap[charId]
	#
		
	def render(self, text, filename):
		minX = sys.maxsize
		minY = sys.maxsize
		maxX = -sys.maxsize
		maxY = -sys.maxsize
		x = 0
		y = 0
		
		# Measure
		for char in text:
			charData = self.getCharData(char)
			
			minX = min(minX, x + charData['xoffset'])
			minY = min(minY, y + charData['yoffset'])
			
			maxX = max(maxX, x + charData['xoffset'] + charData['width'])
			maxY = max(maxY, y + charData['yoffset'] + charData['height'])
			
			x += charData['xadvance']
		#
		
		sizeX = maxX - minX
		sizeY = maxY - minY
		
		w, h = sizeX * 4, sizeY;
		output = [[0 for x in range(w)] for y in range(h)]
		
		# Render
		x = 0
		y = 0
		
		for char in text:
			charData = self.getCharData(char)
			
			width = charData['width']
			height = charData['height']
			xoffset = charData['xoffset']
			yoffset = charData['yoffset']
			pixels = charData['pixels']
			
			for charY in range(height):
				outY = y + yoffset + charY
				if outY < 0 or outY >= sizeY:
					continue
				#
			
				charYIndex = charY * width
				outputRow = output[outY]
				for charX in range(width):
					outX = x + xoffset + charX
					if outX < 0 or outX >= sizeX:
						continue
					#
					
					outX *= 4
					outputRow[outX + 0] = pixels[charYIndex + charX]
					outputRow[outX + 1] = pixels[charYIndex + charX]
					outputRow[outX + 2] = pixels[charYIndex + charX]
					outputRow[outX + 3] = 255
				#
			#
			
			x += charData['xadvance']
		#
		
		png.from_array(output, 'RGBA').save(filename)
		
	# END render
# END class RenderFont
















