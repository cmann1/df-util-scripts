import os
from math import atan2
from pathlib import Path
from typing import List

import svg
from bs4 import BeautifulSoup, Tag

# POTRACE: http://potrace.sourceforge.net/
from svg.path import parse_path, Close, Move, Line

PROCESSED_SPRITES = Path('processed_sprites')
OUTPUT_FOLDER = Path('generated_outlines')
OPTIMISED_OUTPUT = Path('optimised_outlines')

INPUT_SCALE = 0.1
INPUT_TRANSLATE_X = 0.25
INPUT_TRANSLATE_Y = 0.25
ANGLE_TOLERANCE = 0.15


class Main:
	
	def __init__(self):
		OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
		OPTIMISED_OUTPUT.mkdir(parents=True, exist_ok=True)
		
		for sprite_file in PROCESSED_SPRITES.iterdir():
			output = OUTPUT_FOLDER / (sprite_file.stem + '.svg')
			cmd = f'potrace -s -a 0 -u 10 --flat -o "{output}" "{sprite_file}"'
			print(cmd)
			os.system(cmd)
			self.optimise(output)
			pass
	
	@staticmethod
	def optimise(svg_file: Path):
		with svg_file.open('r', encoding='utf-8') as f:
			soup = BeautifulSoup(f.read(), 'xml')
		
		height = float(soup.svg['viewBox'].split(' ')[-1])
		path_element = soup.svg.path
		old_path = parse_path(path_element['d'])
		start_point = None
		new_path = svg.path.Path()
		points = None
		
		for path_item in old_path:
			if isinstance(path_item, Close):
				continue
			
			if isinstance(path_item, Move):
				if points is not None and len(points) > 0:
					Main.clean(points, new_path, height)
				
				start_point = None
				points = []
				pass
			
			point = (path_item.end.real, -path_item.end.imag)
			
			if start_point is None:
				start_point = point
			elif point == start_point:
				continue
			
			points.append(point)
			pass
		
		if points is not None and len(points) > 0:
			Main.clean(points, new_path, height)
		
		ouput = OPTIMISED_OUTPUT / (svg_file.stem + '.d')
		with ouput.open('w', encoding='utf-8') as f:
			f.write(new_path.d())
	
	@staticmethod
	def clean(points: List, new_path: svg.path.Path, height):
		count = len(points)
		i = 0
		
		while i < count:
			x1, y1 = points[i]
			
			while count >= 3:
				x2, y2 = points[(i + 1) % count]
				x3, y3 = points[(i + 2) % count]
				
				a = atan2(y2 - y1, x2 - x1)
				b = atan2(y3 - y2, x3 - x2)
				test = abs(a - b) <= ANGLE_TOLERANCE
				if not test:
					break
				
				points.pop((i + 1) % count)
				if i + 1 >= count:
					i -= 1
				
				count -= 1
			
			i += 1
		
		prev_point = complex(points[0][0] * INPUT_SCALE + INPUT_TRANSLATE_X, points[0][1] * INPUT_SCALE + INPUT_TRANSLATE_Y + height)
		start_point = prev_point
		new_path.append(Move(to=prev_point))
		
		for point in points[1:]:
			new_point = complex(point[0] * INPUT_SCALE + INPUT_TRANSLATE_X, point[1] * INPUT_SCALE + INPUT_TRANSLATE_Y + height)
			new_path.append(Line(start=prev_point, end=new_point))
			prev_point = new_point
			pass
		
		new_path.append(Close(start=prev_point, end=start_point))
		pass


if __name__ == '__main__':
	Main()
	pass
