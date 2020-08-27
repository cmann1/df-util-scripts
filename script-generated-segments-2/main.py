import os

from .Chunk import Chunk
from dustmaker import *

LOCATION = os.getenv('APPDATA') + '/Dustforce/user/level_src/'
FILE_NAME = 'downhill'

TPL_PATH = 'templates'
CHUNK_TPL_FILE = 'chunk_tpl.cpp'

# =======================================================================
# =======================================================================


def main():
	os.makedirs('output', 0o777, True)

	with open(os.path.join(LOCATION, FILE_NAME), 'rb') as f:
		df_map = read_map(f.read())

	with open(os.path.join(TPL_PATH, CHUNK_TPL_FILE), 'r') as f:
		chunk_tpl = f.read()

	# Entities
	for (id, (x, y, entity)) in list(df_map.entities.items()):
		Chunk.get(x, y).add_entity(id, x, y, entity)

	# Props
	for id, value in df_map.props.items():
		layer, x, y, prop = value
		Chunk.get(x, y).add_prop(layer, x, y, prop)

	# Entities
	for id, tile in df_map.tiles.items():
		layer, x, y = id
		Chunk.get(x, y).add_tile(layer, x, y, tile)


if __name__ == "__main__":
	main()
