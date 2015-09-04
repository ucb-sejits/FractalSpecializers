import numpy as np
import ctree
from ctree.nodes import Project
from ctree.jit import LazySpecializedFunction, ConcreteSpecializedFunction
from ctree.transformations import PyBasicConversions
import ast
import ctypes
from ctree.c.nodes import *
from PIL import Image
#install above with pip install Pillow
import argparse
import time


#Generates a mandelbrot set
#for explanation of theory, see
#https://en.wikipedia.org/wiki/Mandelbrot_set
def mandelbrot(dimsquare, dim):
    arr = np.zeros(dimsquare)
    
    #mandelbrot space
    x_low=-1.5
    x_high=.8 
    y_low=-1.0
    y_high=1.0
    xlen = x_high - x_low
    ylen = y_high - y_low

    maxiter = 1000 
    iteration = 0 
    for yi in range(0, dim):
        for xi in range(0, dim):
            x = 0.0
            y = 0.0
            cx = x_low + 1.0*xi*xlen/dim
            cy = y_low + 1.0*yi*ylen/dim
            iteration = 0
            while (x*x + y*y < 4.0 and iteration<maxiter):
                xtemp = x*x - y*y + cx
                y = 2*x*y + cy
                x = xtemp 
                iteration+=1
            arr[yi*dim+xi] = iteration
    return arr



class CSF(ConcreteSpecializedFunction):
    def finalize(self, entry_point_name, project_node, entry_point_typesig):
        #print("SmoothCFunction Finalize", entry_point_name)
        self._c_function = self._compile(entry_point_name, project_node, entry_point_typesig)
        self.entry_point_name = entry_point_name
        return self

    def __call__(self, arg, arg1):
        output = np.zeros(arg, dtype=np.int32)
        self._c_function(arg, arg1, output)
        return output

class ReturnDeleter(ast.NodeTransformer):
    def visit_Return(self, node):
        return None

class LSF(LazySpecializedFunction):
    def args_to_subconfig(self, args):
        return args[0]
    
    def transform(self, tree, program_config):
        args_subconfig, tuning_config = program_config
        function = tree.body[0]
        c_func = PyBasicConversions().visit(function)
        #print(c_func)
        c_func.defn = c_func.defn[1:]
        #print(c_func)
        c_func.params[0].type = ctree.types.get_ctype(args_subconfig)
        c_func.params[1].type =c_func.params[0].type
        c_func.params.append(SymbolRef('arr', ctypes.POINTER(ctypes.c_int32)()))
        #print(c_func)
        return CFile(body=[c_func])
    

    def finalize(self, transform_result, program_config):
        c_file = transform_result[0]
        proj = Project(transform_result)
        entry_point_name = 'mandelbrot'
        entry_point_typesig = ctypes.CFUNCTYPE(None, ctypes.c_long, ctypes.c_long, np.ctypeslib.ndpointer(np.int32, 1, (program_config[0],)))
        fn = CSF()
        return fn.finalize(entry_point_name, proj, entry_point_typesig)
        
parser = argparse.ArgumentParser(description='Mandelbrot set specializer')
parser.add_argument('-dimension','-d', nargs='?', help='resolution of 1 dimension of square image', const=1, type=int, default = 100)
args = parser.parse_args()
if args.dimension:
    xRes = args.dimension
yRes = xRes






py_ast = ctree.frontend.get_ast(mandelbrot)
R = ReturnDeleter()
R.visit(py_ast)
func = LSF(py_ast=py_ast)






print "start rendering"
start = time.time()
m = func(xRes*yRes, xRes)
end = time.time()
imagelist = []
print "render time: ", end-start, "s"
print "begin post processing"
for i in range(0, xRes):
    for j in range(0,yRes):
        imagelist.append(int(m[j*xRes+i]))   

img = Image.new('RGB', (xRes, yRes))
img.putdata(imagelist)
name = "mandelbrot"+str(xRes)+".png"
print "saving image:", name
img.save(name)

