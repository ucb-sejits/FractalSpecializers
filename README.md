# FractalSpecializers
Specializers for rendering fractals

The mandelbrot set is a mathematical structure which utilizes complex numbers to generate  recursive images. This software uses SEJITS to express the basic mandelbrot algorithm in python but still achieve practical render times.

Dependencies: 
PILLOW (for writing image files)
get with 
$ pip install Pillow

Running:
python mandelspecial.py -d[image resolution 1 side square image]
e.g
$ python mandelspecial.py -d1000 
will create a 1000x1000 pixel image called mandelbrot1000.png in the same directory as this code


Coming soon:
Julia Sets
Generation using arbitrary input equation
Zooming
