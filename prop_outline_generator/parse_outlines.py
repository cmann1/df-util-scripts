import os
from pathlib import Path
from typing import Dict, List

from _common import config
from _common import props
from bs4 import BeautifulSoup, Tag
from svg.path import parse_path, Close, Move

INPUT_FOLDER = Path('final_outlines')

# Determining which path compenents are holes could be done automatically, but it turns
# out that these props are the only props with mulitple separate components that are not holes
PROPS_NO_HOLES = {
	# Stains
	(2, 5, 17): True,
	(2, 5, 18): True,
	# Mushrooms
	(2, 5, 20): True,
	(2, 5, 21): True,
	(2, 5, 24): True,
	# Virtual NPC
	(5, 24, 1): True
}


class Main:
	sets_data: List
	prop_names: Dict
	soup: BeautifulSoup
	root: Tag
	
	def __init__(self):
		self.sets_data = [[] for _ in range(6)]
		self.prop_names = dict()
		
		for svg_file in INPUT_FOLDER.iterdir():
			# print(svg_file)
			with svg_file.open('r', encoding='utf-8') as f:
				self.soup = BeautifulSoup(f.read(), 'xml')
			
			self.root = self.soup.svg
			
			prop_elements = self.root.find_all('g')
			
			for prop_element in prop_elements:
				# print(prop_element['id'])
				prop_set, prop_group, prop_index = map(int, prop_element['id'].split('_')[1:])
				
				path_elements = prop_element.find_all('path')
				rect_element = prop_element.rect
				prop_key = (prop_set, prop_group, prop_index)
				self.prop_names[prop_key] = f'{prop_set}.{prop_group}.{prop_index} - {prop_element.title.string.strip()}'
				
				if len(path_elements) == 0:
					continue
					
				offset_x, offset_y = float(rect_element['x'] if rect_element.has_attr('x') else 0), float(rect_element['y'] if rect_element.has_attr('y') else 0)
				# print(offset_x, offset_y)
				
				groups_data = self.sets_data[prop_set - 1]
				if len(groups_data) <= prop_group:
					for i in range(len(groups_data), prop_group + 1):
						groups_data.append([])
				
				props_data = groups_data[prop_group]
				
				if len(props_data) < prop_index:
					for i in range(len(props_data), prop_index):
						props_data.append('')
				
				# print(prop_set, prop_group, prop_index)
				# path_components = [f'{offset_x},{offset_y}']
				path_components = []
				components_types = ['false']
				has_holes = prop_key not in PROPS_NO_HOLES
				
				for path_element in path_elements:
					path_data = parse_path(path_element['d'])
					component_start_index = -1
					path_output = []
					
					for path_item in path_data:
						if isinstance(path_item, Close):
							continue
						
						if isinstance(path_item, Move):
							if component_start_index != -1:
								path_output.append('},{')
								components_types.append('true' if has_holes else 'false')
							component_start_index = len(path_output)
						
						x, y = path_item.end.real, path_item.end.imag
						path_output.append(x + offset_x - 1)
						path_output.append(y + offset_y - 1)
					
					path_components.append(','.join(map(str, path_output)))
				
				path_string = '{' + ','.join(path_components).replace(',},{,', '},{') + '}'
				holes_string = ','.join(components_types).replace(',},{,', '},{')
				props_data[prop_index - 1] = (path_string, holes_string)
				pass
		
		output_file = config.LIB / 'props/outlines.cpp'
		output_file.parent.mkdir(parents=True, exist_ok=True)
		
		output_outline_data = f'const array<array<array<array<array<float>>>>> PROP_OUTLINES = {{\n'
		output_hole_data = '/// Bool values corresponding to each outline component. Path components that are holes are set to `true`.\n'
		output_hole_data += f'const array<array<array<array<bool>>>> PROP_OUTLINES_HOLES_INFO = {{\n'
		
		for set_index, set_list in enumerate(self.sets_data):
			set_start_text = f'\t{{ // Set {set_index + 1}\n'
			output_outline_data += set_start_text
			output_hole_data += set_start_text
			
			first_group = False
			first_empty_group = True
			
			for group_index, group_list in enumerate(set_list):
				if len(group_list) == 0:
					if first_empty_group:
						indent_text = '\t\t'
						output_outline_data += indent_text
						output_hole_data += indent_text
						
						first_empty_group = False
					
					empty_group_text = '{}, '
					output_outline_data += empty_group_text
					output_hole_data += empty_group_text
					first_group = True
					continue
				
				if first_group:
					output_outline_data += '\n'
					output_hole_data += '\n'
					first_group = False
				
				first_empty_group = True
				group_start_text = f'\t\t{{ // Group {group_index} - {props.GROUP_NAMES[group_index]}\n'
				output_outline_data += group_start_text
				output_hole_data += group_start_text
				# print(group_list)
				
				for prop_index, (prop_list, holes_list) in enumerate(group_list):
					# outfile.write(f'\t\t\t\t/*  */ {{{prop_list}}},\n')
					prop_output_prefix = f'\t\t\t/* {self.prop_names[(set_index + 1, group_index, prop_index + 1)]} */ '
					output_outline_data += f'{prop_output_prefix}{{{prop_list}}},\n'
					output_hole_data += f'{prop_output_prefix}{{{holes_list}}},\n'
					pass
				
				group_end_text = '\t\t},\n'
				output_outline_data += group_end_text
				output_hole_data += group_end_text
			
			set_end_text = '\t},\n'
			output_outline_data += set_end_text
			output_hole_data += set_end_text
		
		output_outline_data += '};'
		output_hole_data += '};'
		
		with output_file.open('w') as outfile:
			outfile.write('/// Auto generated by .scripts/prop_outline_generator/. Do not edit.\n\n')
			outfile.write(output_outline_data)
			outfile.write('\n\n')
			outfile.write(output_hole_data)
	
	pass


if __name__ == '__main__':
	Main()
	pass
