import json
import math
import os
from pathlib import Path

from _common import config
from typing import Dict
from bs4 import BeautifulSoup, Tag
from rectpack import newPacker

BIN_SIZE = 1200
PADDING = 5
PADDING_2 = PADDING * 2

OUTLINES_INPUT = Path('optimised_outlines')
OUTPUT_FOLDER = Path('generated_templates')


class Main:
	data: Dict
	soup: BeautifulSoup
	root: Tag
	
	def __init__(self):
		with (config.COMMON / 'sprite-data.json').open('r') as fp:
			self.data = json.load(fp)
		
		OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
		
		for prop_set in self.data:
			self.soup = BeautifulSoup('<svg></svg>', 'xml')
			self.root = self.soup.svg
			self.root['xmlns'] = 'http://www.w3.org/2000/svg'
			self.root['xmlns:xlink'] = 'http://www.w3.org/1999/xlink'
			
			prop_elements = []
			packer = newPacker(rotation=False)
			packer.add_bin(BIN_SIZE, BIN_SIZE, count=float('inf'))
			count = 0
			
			prop_set_data = self.data[prop_set]
			# set_element = self.soup.new_tag('g', id='prop_set_' + prop_set)
			# self.root.append(set_element)
			
			for prop_group in prop_set_data:
				prop_group_data = prop_set_data[prop_group]
				prop_group_name = prop_group_data['name']
				# group_element = self.soup.new_tag('g', id='prop_group_' + prop_group)
				# set_element.append(group_element)
				
				for prop_index in prop_group_data['sprites']:
					prop_data = prop_group_data['sprites'][prop_index]
					prop_element = self.soup.new_tag('g', id=f'prop_{prop_set}_{prop_group}_{prop_index}')
					rect = prop_data['palettes'][0][0]['rect']
					prop_element.append(self.soup.new_tag('rect', stroke='none', fill='none', style='display:none', x=rect[0], y=rect[1], width=rect[2], height=rect[3]))
					
					title_element = self.soup.new_tag('title', style='display:none')
					title_element.string = prop_data['name_nice']
					prop_element.append(title_element)
					prop_filename = f"{prop_group_name}_{prop_set}_{prop_group}_{prop_index}_{prop_data['name']}"
					image_filename = str(os.path.relpath(config.PROP_SPRITES / f'{prop_filename}.png', OUTPUT_FOLDER)).replace('\\', '/')
					image_element = self.soup.new_tag('image', width=rect[2], height=rect[3])
					image_element['xlink:href'] = image_filename
					image_element['xmlns:xlink'] = 'http://www.w3.org/1999/xlink'
					prop_element.append(image_element)
					
					with (OUTLINES_INPUT / f'{prop_filename}.d').open('r') as file:
						path = self.soup.new_tag('path', d=file.read(), stroke='#ff0000', fill='none')
						path['stroke-width'] = 0.5
						prop_element.append(path)
					
					# if count < 20:
					packer.add_rect(rect[2] + PADDING_2, rect[3] + PADDING_2, count)
					self.root.append(prop_element)
					prop_elements.append(prop_element)
					
					count += 1
			
			packer.pack()
			all_rects = packer.rect_list()
			num_bins = len(packer)
			num_columns = int(math.ceil(math.sqrt(num_bins)))
			num_rows = int(math.ceil(num_bins / num_columns))
			self.root['viewBox'] = f'0 0 {num_columns * BIN_SIZE} {num_rows * BIN_SIZE}'
			
			for rect in all_rects:
				b, x, y, w, h, rid = rect
				bin_row = int(b / num_columns)
				bin_column = b - bin_row * num_columns
				bin_x = bin_column * BIN_SIZE
				bin_y = bin_row * BIN_SIZE
				prop_element = prop_elements[rid]
				prop_element['transform'] = f'translate({bin_x + x + PADDING}, {bin_y + y + PADDING})'
			
			template_file = OUTPUT_FOLDER / f'{prop_set}.svg'
			
			with template_file.open('w') as fp:
				fp.write(self.soup.prettify())
			
		pass
	

if __name__ == '__main__':
	Main()
	pass
