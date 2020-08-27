Requires python, and the dustmaker and pypng libraries

Place all maps to be rendered in `maps/`
A png of the entire map will be created along with a name tag for every map file.
The images will be saved in `output`

At the top of render.py there are a few simple settings that can be used to control some of the rendering

Fonts can be generated using BMFont (http://www.angelcode.com/products/bmfont/)
The font descriptor will require some editing to be compatible - see the cube.fnt file to see what it should look like

DF.atn is a collection of photoshop actions for my own use.
The pixelate-tiles/entities actions were used to create the pngs needed to render tiles.
The rest were helper functions used when adding the name tag, cropping and enlarging the final image.
