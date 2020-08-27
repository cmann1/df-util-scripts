class Chunk
{

	array<int> tiles;
	array<float> props;
	array<dictionary> entities;

	Chunk(array<int> tiles, array<float> props, array<dictionary> entities)
	{
		this.tiles = tiles;
		this.props = props;
		this.entities = entities;
	}

}

class EntityData
{

	string type;
	int id;
	float x;
	float y;
	int rotation;
	int face;
	array<VarData> vars;

	EntityData(string type, int id, float x float y, int rotation, int face, array<VarData> vars)
	{
		this.type = type;
		this.id = id;
		this.x = x;
		this.y = y;
		this.rotation = rotation;
		this.face = face;
		this.vars = vars;
	}

}

class VarData
{

	string name;
	int type;
	? value;

	VarData(string name, int type, ? value)
	{
		this.name = name;
		this.type = type;
		this.value = value;
	}

}
