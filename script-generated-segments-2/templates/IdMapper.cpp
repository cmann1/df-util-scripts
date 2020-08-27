class IdMapper
{

	scene@ g;
	array<int> id_list;
	array<varvalue@> id_val_list;
	dictionary entity_id_map;
	dictionary pending;

	IdMapper()
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
