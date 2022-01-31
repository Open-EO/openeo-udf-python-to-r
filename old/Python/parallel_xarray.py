import time
import xarray as xr
import numpy as np
import rpy2.robjects as robjects
from array import array
from dask.distributed import Scheduler, Worker, Client, LocalCluster
import dask

if __name__ == '__main__':
    ## Create a xArray.DataArray with and without chunks
    npData = np.random.rand(1000,100,3)
    xrData = xr.DataArray(npData, dims = ['x', 'y', 'b'], coords = {'x': np.arange(npData.shape[0]), 'y': np.arange(npData.shape[1]), 'b': ['b1', 'b2', 'b3']})
    xrData_chunked = xrData.chunk({'x':100,'y':100,'b':-1})
        
    print("Input data has shape: ", xrData.shape)
    # Read R Code
    file = open('../R/vectors.R', mode = 'r')
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

    print("Input chunked data: ",xrData_chunked)

    # Print result and benchmark
    print("CASE 1: Feed the whole block of data to R:\n Time elapsed: {}".format(t2 - t1))

    # Run R code parallelized with DASK
    with LocalCluster(n_workers=2, threads_per_worker=1, processes=True,memory_limit='1GB') as cluster:
        with Client(cluster) as client:
            t1 = time.time() # Start benchmark
            result = xr.apply_ufunc(ufunc, xrData_chunked,
                                    vectorize = True,
                                    input_core_dims = [['b']],
                                    dask="parallelized",
                                   output_dtypes=[float],
                                   dask_gufunc_kwargs={'allow_rechunk':False}).compute()

    # Print result and benchmark
    t2 = time.time() # End benchmark
    print("CASE 2: Parallelize the calls with Dask using the chunk size we have set.\nUsing 2 CPUs:\nTime elapsed: {}".format(t2 - t1))

    with LocalCluster(n_workers=4, threads_per_worker=1, processes=True,memory_limit='1GB') as cluster:
        with Client(cluster) as client:
            # Run R code parallelized with DASK
            t1 = time.time() # Start benchmark
            result = xr.apply_ufunc(ufunc, xrData_chunked,
                                    vectorize = True,
                                    input_core_dims = [['b']],
                                    dask="parallelized",
                                   output_dtypes=[float],
                                   dask_gufunc_kwargs={'allow_rechunk':False}).compute()

    # Print result and benchmark
    t2 = time.time() # End benchmark
    print("CASE 2: Parallelize the calls with Dask using the chunk size we have set.\nUsing 4 CPUs:\nTime elapsed: {}".format(t2 - t1))

    with LocalCluster(n_workers=8, threads_per_worker=1, processes=True,memory_limit='1GB') as cluster:
        with Client(cluster) as client:
            # Run R code parallelized with DASK
            t1 = time.time() # Start benchmark
            result = xr.apply_ufunc(ufunc, xrData_chunked,
                                    vectorize = True,
                                    input_core_dims = [['b']],
                                    dask="parallelized",
                                   output_dtypes=[float],
                                   dask_gufunc_kwargs={'allow_rechunk':False}).compute()

    # Print result and benchmark
    t2 = time.time() # End benchmark
    print("CASE 2: Parallelize the calls with Dask using the chunk size we have set.\nUsing 8 CPUs:\nTime elapsed: {}".format(t2 - t1))