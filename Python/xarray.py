import time
import xarray as xr
import numpy as np
import rpy2.robjects as robjects

# Create example numpy and xarray data
npData = np.random.rand(5,4,3)
xrData = xr.DataArray(npData, dims = ['x', 'y', 'b'], coords = {'x': [1,2,3,4,5], 'y': [6,7,8,9], 'b': ['b1', 'b2', 'b3']})

# Read R Code
file = open('./R/vectors.R', mode = 'r')
rCode = file.read()
file.close()

# "Compile" R code once
rEnv = robjects.r(rCode)
reducerRFun = robjects.globalenv['reducer']
reducer = lambda data, axis: data.tolist()
context = -1

# Run R code
t1 = time.time() # Start benchmark
# groups = xrData.groupby(dim = 'b');
result = xrData.reduce(reducer, dim = 'b')
t2 = time.time() # End benchmark

# Print result and benchmark
print(result)
print("Time elapsed: %s" % (t2 - t1))
