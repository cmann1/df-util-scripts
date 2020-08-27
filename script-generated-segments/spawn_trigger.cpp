#include '__spawn_triggers.cpp'

class script
{
	
	IdRemapper remapper;
	IdRemapper remapper_checkpoint;
	
	void checkpoint_save()
	{
		remapper_checkpoint = remapper;
	}
	void checkpoint_load()
	{
		remapper = remapper_checkpoint;
	}
	
}

class IdRemapper
{
	
	scene@ g;
	array<int> id_list;
	array<varvalue@> id_val_list;
	dictionary entity_id_map;
	dictionary pending;
	
	IdRemapper()
	{
		@g = get_scene();
	}
	
	void add(int id, varvalue@ varval)
	{
		id_list.insertLast(id);
		id_val_list.insertLast(varval);
		
		varvalue@ val = cast<varvalue>(pending[id+'']);
		if(@val != null)
		{
			entity@ e = cast<entity>(entity_id_map[val.get_int32()+'']);
			if(@e != null)
			{
				val.set_int32(e.id());
				pending.delete(id+'');
			}
		}
	}
	
	void add_entity(int old_id, entity@ e)
	{
		entity_id_map.set(old_id+'', @e);
	}
	
	void remap()
	{
		for(uint i = 0, count = id_list.length(); i < count; i++)
		{
			varvalue@ val = id_val_list[i];
			entity@ e = cast<entity>(entity_id_map[val.get_int32()+'']);
			if(e is null)
			{
				pending.set(val.get_int32()+'', @val);
				continue;
			}
			
			val.set_int32(e.id());
		}
	}
	
}

class _SpawnTrigger : trigger_base
{
	
	int CHUNK_SIZE = 16;
	
	scene@ g;
	script@ script;
	scripttrigger @self;
	[hidden] bool active = false;
	
	_SpawnTrigger()
	{
		@g = get_scene();
	}
	
	void init(script@ s, scripttrigger@ self)
	{
		@script = s;
		@this.self = self;
	}
	
	void step()
	{
		active = true;
		if(active)
		{
			place_chunk();
			g.remove_entity(self.as_entity());
		}
	}
	
	void activate(controllable @e)
	{
		active = true;
	}
	
	void draw(float sub_frame)
	{
		const float x = self.x();
		const float y = self.y();
		g.draw_rectangle_world(17, 17, x - CHUNK_SIZE * 24, y - CHUNK_SIZE * 24, x + CHUNK_SIZE * 24, y + CHUNK_SIZE * 24, 0, 0x55FF0000);
	}
	
	array<int> get_tiles()
	{
		return array<int> = {};
	}
	
	array<float> get_props()
	{
		return array<float> = {};
	}
	
	array<dictionary> get_entities()
	{
		return array<dictionary> = {{}};
	}
	
	void place_chunk()
	{
		array<int> tiles = get_tiles();
		array<float> props = get_props();
		array<dictionary> entities = get_entities();
		
		const uint num_tiles = tiles.length();
		const uint num_props = props.length();
		const uint num_entities = entities.length();
		
		tileinfo@ tile = create_tileinfo();
		tilefilth@ filth = create_tilefilth();
		tile.solid(true);
		for(uint i = 0; i < num_tiles; i += 15)
		{
			const int layer = tiles[i];
			const int tx = tiles[i + 1];
			const int ty = tiles[i + 2];
			tile.type(tiles[i + 3]);
			
			tile.edge_top(tiles[i + 4]);
			tile.edge_bottom(tiles[i + 5]);
			tile.edge_left(tiles[i + 6]);
			tile.edge_right(tiles[i + 7]);
			
			tile.sprite_set(tiles[i + 8]);
			tile.sprite_tile(tiles[i + 9]);
			tile.sprite_palette(tiles[i + 10]);
			
			g.set_tile(tx, ty, layer, tile, false);
			
			const int filth_top = tiles[i + 11];
			const int filth_bottom = tiles[i + 12];
			const int filth_left = tiles[i + 13];
			const int filth_right = tiles[i + 14];
			if(filth_top != 0 || filth_bottom != 0 || filth_left != 0 || filth_right != 0)
			{
				filth.top(filth_top);
				filth.bottom(filth_bottom);
				filth.left(filth_left);
				filth.right(filth_right);
				g.set_tile_filth(tx, ty, filth);
			}
		}
		
		for(uint i = 0; i < num_props; i += 12)
		{
			prop@ p = create_prop();
			p.layer(int(props[i]));
			p.sub_layer(int(props[i + 1]));
			p.x(props[i + 2]);
			p.y(props[i + 3]);
			p.rotation(props[i + 4]);
			const float scale = props[i + 5];
			p.scale_x((props[i + 6] == 1 ? 1 : -1) * scale);
			p.scale_y((props[i + 7] == 1 ? 1 : -1) * scale);
			p.prop_set(int(props[i + 8]));
			p.prop_group(int(props[i + 9]));
			p.prop_index(int(props[i + 10]));
			p.palette(int(props[i + 11]));
			g.add_prop(p);
		}
		
		IdRemapper@ id_remapper = @script.remapper;

		for(uint i = 0; i < num_entities; i++)
		{
			dictionary@ entity_data = entities[i];
			array<float>@ idata = cast<array<float>>(entity_data['i']);
			const string type = string(entity_data['type']);
			
			entity@ e = create_entity(type);
			const int id = int(idata[0]);
			e.layer(int(idata[1]));
			e.x(idata[2]);
			e.y(idata[3]);
			e.rotation((idata[4] / 0x10000) * 360);
			e.face(idata[5] == 1 ? -1 : 1);
			
			varstruct@ evars = e.vars();
			
			array<dictionary>@ vars = cast<array<dictionary>>(entity_data['vars']);
			const uint num_vars = vars.length();
			for(uint j = 0; j < num_vars; j++)
			{
				dictionary@ var = cast<dictionary>(vars[j]);
				const string name = string(var['n']);
				
				varvalue@ varval = evars.get_var(name);
				
				if(name == 'dm_scale')
				{
					controllable@ c = e.as_controllable();
					if(@c != null)
						c.scale(float(var['v']));
					continue;
				}
				
				if(varval is null) continue;
				
				if(name == 'puppet_id')
				{
					id_remapper.add(id, varval);
				}
				
				write_var(var, name, varval, id_remapper);
			}
			
			g.add_entity(e, true);
			id_remapper.add_entity(id, @e);
			
		}
		
		id_remapper.remap();
	}
	
	void write_var(dictionary@ var, string name, varvalue@ varval, IdRemapper@ id_remapper)
	{
		const uint type = uint(var['t']);
		
		switch(type)
		{
			case 1: // BOOL
				varval.set_bool(bool(var['v']));
			break;
			case 2: // INT
			case 3: // UINT
				varval.set_int32(int(var['v']));
			break;
			case 4: // FLOAT
				varval.set_float(float(var['v']));
			break;
			case 5: // STRING
				varval.set_string(string(var['v']));
			break;
			case 10: // VEC2
			{
				array<float>@ vec2 = cast<array<float>>(var['v']);
				varval.set_vec2(vec2[0], vec2[1]);
			}
			break;
			case 15: // ARRAY
			{
				dictionary@ array_data = cast<dictionary>(var['v']);
				const int array_type = int(array_data['t']);
				vararray@ varray = varval.get_array();
				
				switch(array_type)
				{
					case 1: // BOOL
					{
						array<bool>@ arr = cast<array<bool>>(array_data['v']);
						const uint arr_length = arr.length();
						varray.resize(arr_length);
						for(uint i = 0; i < arr_length; i++)
							varray.at(i).set_bool(arr[i]);
					}
					break;
					case 2: // INT
					case 3: // UINT
					{
						array<int>@ arr = cast<array<int>>(array_data['v']);
						const uint arr_length = arr.length();
						varray.resize(arr_length);
						for(uint i = 0; i < arr_length; i++)
						{
							varvalue@ v = varray.at(i);
							v.set_int32(arr[i]);
							if(name == 'c_node_ids')
								id_remapper.add(arr[i], v);
						}
					}
					break;
					case 4: // FLOAT
					{
						array<float>@ arr = cast<array<float>>(array_data['v']);
						const uint arr_length = arr.length();
						varray.resize(arr_length);
						for(uint i = 0; i < arr_length; i++)
							varray.at(i).set_float(arr[i]);
					}
					break;
					case 5: // STRING
					{
						array<string>@ arr = cast<array<string>>(array_data['v']);
						const uint arr_length = arr.length();
						varray.resize(arr_length);
						for(uint i = 0; i < arr_length; i++)
							varray.at(i).set_string(arr[i]);
					}
					break;
					case 10: // VEC2
					{
						array<array<float>>@ arr = cast<array<array<float>>>(array_data['v']);
						const uint arr_length = arr.length();
						varray.resize(arr_length);
						for(uint i = 0; i < arr_length; i++)
							varray.at(i).set_vec2(arr[i][0], arr[i][1]);
					}
					break;
				}
				
			}
			break;
		}
	}
	
}