from dustmaker import *


class Chunk:
	chuck_size = 24
	chunks = {}

	@staticmethod
	def get(x, y):
		chunk_x = math.floor(x / Chunk.chuck_size)
		chunk_y = math.floor(y / Chunk.chuck_size)
		chunk_key = (chunk_x, chunk_y)

		if chunk_key in Chunk.chunks:
			return Chunk.chunks[chunk_key]

		chunk = Chunk(chunk_x, chunk_y)
		Chunk.chunks[chunk_key] = chunk
		return chunk

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

	def write(self, tpl, df_map):
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
