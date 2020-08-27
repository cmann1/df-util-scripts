import os
from pathlib import Path

COMMON = Path(__file__).parent
PROP_SPRITES = COMMON.joinpath('prop_sprites')

SCRIPT_SRC = Path(os.getenv('APPDATA')).resolve().joinpath('Dustforce/user/script_src/')
LIB = SCRIPT_SRC.joinpath('lib/')
