import math

from dustmaker import *
import os

location = os.getenv('APPDATA') + '/Dustforce/user/level_src/'
name = 'fp-dragon'

tpl_path = os.getenv('APPDATA') + '/Dustforce/user/script_src/'
tpl_file = 'spawn_trigger_tpl.cpp'
tpl_file_out = '__spawn_triggers.cpp'

CHUNK_SIZE = 24
chunks = {}


class Chunk:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.entities = []
		self.tiles = []
		self.props = []

	def add_entity(self, id, x, y, entity):
		result = True

		# if entity.type == 'camera_node':
		# 	result = False
		# elif entity.type == 'kill_box':
		# 	#width,height
		# 	result = True
		# elif entity.type == 'ambience_trigger':
		# 	#width,height
		# 	result = True

		if result:
			self.entities.append((id, x, y, entity))

		return result

	def add_tile(self, layer, x, y, tile):
		self.tiles.append((layer, x, y, tile))
		pass

	def add_prop(self, layer, x, y, prop):
		self.props.append((layer, x, y, prop))
		pass

	def export_var_value(self, name, var):
		type = var.type
		value = var.value

		if type == VarType.BOOL:
			return 'true' if value else 'false'
		if type == VarType.UINT or type == VarType.INT or type == VarType.FLOAT:
			return str(value)
		if type == VarType.STRING:
			return "'{}'".format(value)
		if type == VarType.VEC2:
			return "array<float>={{{},{}}}".format(value[0], value[1])
		if type == VarType.ARRAY:
			return "dictionary={{{{'t',{}}},{{'v',array<{}>={{{}}}}}}}".format(value[0], self.get_var_type(var), ','.join([self.export_var_value('', v) for v in value[1]]))

		return "''"

	def get_var_type(self, var):
		type = var if isinstance(var, VarType) else var.type

		if type == VarType.BOOL:
			return 'bool'
		if type == VarType.UINT:
			return 'int'
		if type == VarType.INT:
			return 'int'
		if type == VarType.FLOAT:
			return 'float'
		if type == VarType.STRING:
			return 'string'
		if type == VarType.VEC2:
			return 'array<float>'
		if type == VarType.ARRAY:
			return '{}'.format(self.get_var_type(var.value[0]))

		return 'int'

	def write(self, tpl, map):
		tiles_out = ''
		for (layer, x, y, tile) in self.tiles:
			tiles_out += ','.join(str(str_val) for str_val in [
				layer, x, y, int(tile.shape),
				self.get_edge(tile, TileSide.TOP),
				self.get_edge(tile, TileSide.BOTTOM),
				self.get_edge(tile, TileSide.LEFT),
				self.get_edge(tile, TileSide.RIGHT),
				int(tile.sprite_set()), tile.sprite_tile(), tile.sprite_palette(),
				self.get_filth(tile, TileSide.TOP), self.get_filth(tile, TileSide.BOTTOM), self.get_filth(tile, TileSide.LEFT), self.get_filth(tile, TileSide.RIGHT)
			]) + ','
			pass

		props_out = ''
		for (layer, x, y, prop) in self.props:
			props_out += ','.join(str(str_val) for str_val in [
				layer, prop.layer_sub, x * 48, y * 48,
				prop.rotation, prop.scale,
			    1 if prop.flip_x else 0, 1 if prop.flip_y else 0,
			    prop.prop_set, prop.prop_group, prop.prop_index,
			    prop.palette
			]) + ','
			pass

		entities_out = ''
		for (id, x, y, entity) in self.entities:
			var_data = []
			for name, var in entity.vars.items():
				var_data.append("{{{{'n','{}'}},{{'t',{}}},{{'v',{}}}}}".format(name, var.type, self.export_var_value(name, var)))
			entities_out += ("{{"
			                 "{{'type','{}'}},"
			                 "{{'vars',array<dictionary>={{{}}}}},"
			                 "{{'i',array<float>={{{},{},{},{},{},{}}}}}"
			                 "}},").format(entity.type, ','.join(var_data), id, entity.layer, x * 48, y * 48, entity.rotation,
			                               '1' if entity.flipX else '0',
			                               '1' if entity.flipY else '0',
			                               '1' if entity.visible else '0')

			pass

		tpl = tpl.replace('__TILES__', tiles_out)
		tpl = tpl.replace('__ENTITIES__', entities_out)
		tpl = tpl.replace('__PROPS__', props_out)

		return tpl

	@staticmethod
	def get_filth(tile, side):
		sprite_set, spikes = tile.edge_filth_sprite(side)
		value = sprite_set.value

		if value > 0 and spikes:
			value += 8

		return value

	@staticmethod
	def get_edge(tile, side):
		# 1111
		bits = tile.edge_bits(side)

		edge_priority = bits & 1
		collision = (bits & 2) >> 1
		cap_tl = (bits & 4) >> 2
		cap_br = (bits & 8) >> 3

		out_bits = 0
		out_bits |= edge_priority
		out_bits |= cap_tl << 1
		out_bits |= cap_br << 2
		out_bits |= collision << 3

		return out_bits


def get_chunk(x, y):
	chunk_x = math.floor(x / CHUNK_SIZE)
	chunk_y = math.floor(y / CHUNK_SIZE)
	chunk_key = (chunk_x, chunk_y)

	if chunk_key in chunks:
		return chunks[chunk_key]

	chunk = Chunk(chunk_x, chunk_y)
	chunks[chunk_key] = chunk
	return chunk

with open(tpl_path + tpl_file, 'r') as f:
	trigger_tpl = f.read()

with open(location + name, 'rb') as f:
	map = read_map(f.read())

bounds1 = map.start_position(None, 3)
bounds2 = map.start_position(None, 4)
min_x = min(bounds1[0], bounds2[0])
min_y = min(bounds1[1], bounds2[1])
max_x = max(bounds1[0], bounds2[0])
max_y = max(bounds1[1], bounds2[1])

# ENTITIES
entities_del = []
for (id, (x, y, entity)) in list(map.entities.items()):
	if min_x <= x <= max_x and min_y <= y <= max_y:
		print(entity)
		if get_chunk(x, y).add_entity(id, x, y, entity):
			entities_del.append(id)

# PROPS
props_del = []
for id, value in map.props.items():
	layer, x, y, prop = value
	if min_x <= x <= max_x and min_y <= y <= max_y:
		get_chunk(x, y).add_prop(layer, x, y, prop)
		props_del.append(id)

# TILES
tiles_del = []
for id, tile in map.tiles.items():
	layer, x, y = id
	if min_x <= x <= max_x and min_y <= y <= max_y:
		get_chunk(x, y).add_tile(layer, x, y, tile)
		tiles_del.append(id)

chunk_index = 0
out = ''
for key, chunk in chunks.items():
	out += chunk.write(trigger_tpl.replace('__INDEX__', str(chunk_index)), map)

	vars = dict(
		is_square=Var(VarType.BOOL, False),
		script_name=Var(VarType.STRING, 'spawn_trigger.cpp'),
		type_name=Var(VarType.STRING, '_SpawnTrigger%d' % chunk_index),
		var_names=Var(VarType.ARRAY, (VarType.STRING, [])),
		var_values=Var(VarType.ARRAY, (VarType.STRING, [])),
		width=Var(VarType.INT, 50),
	)
	map.add_entity(chunk.x * CHUNK_SIZE + CHUNK_SIZE / 2, chunk.y * CHUNK_SIZE + CHUNK_SIZE / 2, Entity._from_raw(
		'z_script_trigger', vars, 0, 22,
		0, 0, 1))

	chunk_index += 1
	pass

for id in entities_del:
	map.remove_entity(id)
for id in tiles_del:
	del map.tiles[id]
for id in props_del:
	del map.props[id]

# with open(tpl_path + tpl_file_out, 'w') as text_file:
# 	text_file.write(out)

# Write out the final version.
# map.name(name + '-2')
# with open(location + name + '-2', 'wb') as f:
# 	f.write(write_map(map))
