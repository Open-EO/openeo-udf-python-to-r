import time
import xarray as xr
import numpy as np
import rpy2.robjects as robjects
from rpy2.robjects import numpy2ri
from array import array

numpy2ri.activate()

# Create example numpy and xarray data
npData = np.random.rand(100,100,3)
xrData = xr.DataArray(npData, dims = ['x', 'y', 'b'], coords = {'b': ['b1', 'b2', 'b3']})

# Read R Code
file = open('./R/vectors.R', mode = 'r')
rCode = file.read()
file.close()

# "Compile" R code once
rEnv = robjects.r(rCode)
reducer = robjects.globalenv['reducer']
def ufunc(data): # data ia a numpy.ndarray
	global t4
	vector = reducer(data, context)
	return vector[0]

context = -1

# Run R code
t1 = time.time() # Start benchmark
result = xr.apply_ufunc(ufunc, xrData, vectorize = True, input_core_dims = [['b']])
t2 = time.time() # End benchmark

# Print result and benchmark
print(result)
print("Time elapsed: %s" % (t2 - t1))
