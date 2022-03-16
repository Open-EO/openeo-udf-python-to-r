from udf_lib import execute_udf, save_result
import time
import xarray as xr

# Config
parallelize = True
chunk_size = 2000
load_file = "r4openeo_uc2_ndvi_mskd_smaller.nc"
save_file = "result_bfast_udf_small.nc"

# Prepare data
dataset = xr.load_dataset(load_file)
dataset = dataset.drop('transverse_mercator') # ('crs')
data = dataset.to_array(dim = 'var')
data = data.squeeze('var')
data = data.drop('var')
data['t'] = data.t.astype('str')

def run(process, udf, dimension = None, context = None):
    # Run UDF executor
    t1 = time.time() # Start benchmark
    print('start: ', udf) #t1
    result = execute_udf(process, udf, data, dimension = dimension, context = context, parallelize = parallelize, chunk_size = chunk_size)
    t2 = time.time() # End benchmark
    print('end: ', udf) #t2

    # Print result and benchmark
    print('  Time elapsed: %s' % (t2 - t1))
    save_result(result, save_file)

#print('apply')
#run('apply', './udfs/apply.R', context = -1)

print('reduce_dimension bfast')
run('reduce_dimension', './udfs/reduce_bfast.R', dimension = 't', context = {'start_monitor': 2018})