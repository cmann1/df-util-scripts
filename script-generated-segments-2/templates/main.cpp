#include "IdMapper.cpp"
#include "Chunk.cpp"

class script
{

	IdMapper id_mapper;
	IdMapper id_mapper_checkpoint;

	void checkpoint_save()
	{
		id_mapper_checkpoint = id_mapper;
	}

	void checkpoint_load()
	{
		id_mapper = id_mapper_checkpoint;
	}

}
