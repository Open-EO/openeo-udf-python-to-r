import time
import xarray as xr
import numpy as np
import rpy2.robjects as robjects
from array import array

## Create a xArray.DataArray with and without chunks
npData = np.random.rand(50,50,3)
xrData = xr.DataArray(npData, dims = ['x', 'y', 'b'], coords = {'x': np.arange(len(npData[0])), 'y': np.arange(len(npData[1])), 'b': ['b1', 'b2', 'b3']})
xrData_chunked = xrData.chunk({'x':50,'y':10,'b':-1})

# Read R Code
file = open('./R/vectors.R', mode = 'r')
rCode = file.read()
file.close()

# "Compile" R code once
rEnv = robjects.r(rCode)
reducer = robjects.globalenv['reducer']
context = -1
def ufunc(data):
    vector = reducer(array('f', data), context)
    return vector[0]
    
# Run R code with non-chunked data, classic way
t1 = time.time() # Start benchmark
result = xr.apply_ufunc(ufunc, xrData, vectorize = True, input_core_dims = [['b']])
t2 = time.time() # End benchmark

# Print result and benchmark
print(result)
print("Time elapsed: %s" % (t2 - t1))

# Run R code parallelized with DASK
t1 = time.time() # Start benchmark
result = xr.apply_ufunc(ufunc, xrData_chunked,
                        vectorize = True,
                        input_core_dims = [['b']],
                        dask="parallelized",
                       output_dtypes=[float],
                       dask_gufunc_kwargs={'allow_rechunk':False,}).compute()

t2 = time.time() # End benchmark

# Print result and benchmark
print(result)
print("Time elapsed: %s" % (t2 - t1))
