# Step 1
Run the provided Photoshop action (prop_outline_generator.atn) on _`common/prop_sprites`, saving the results to `generated_outlines`.  
The action:
- Fills the image with black (preserving alpha)
- Flattens it, creating a greyscale image
- Adjusts the levels, setting the input black from 0 to 128
- Saves the file as `.pbm` which is required by potrace

# Step 2
Run `generate_outlines.py` to convert the black and white images to outlines.

# Step 3
Run `generate_templates.py`. An svg file will be created for each prop set.  
These can be opened in Illustrator or Inkscape for manual cleaning.

# Step 3
Copy the cleaned files to `final_outlines` and run `parse_outlines.py`.  
`outlines.cpp` will be created in `<SCRIPT_SRC>lib/props/`.
