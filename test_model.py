from udf_lib import execute_udf, create_dummy_cube
#import pandas as pd
import time

# Data Cube config
dims = ['x', 'y', 'b']
sizes = [10, 10, 4]
labels = {
    # x and y get generated automatically for now (todo: get from actual data)
    'x': None,
    'y': None,
    'b': ['B02', 'B03', 'B04', 'B08']
}
parallelize = False
chunk_size = 2000

def run(process, udf, dimension = None, context = None):
    # Prepare data
    data = create_dummy_cube(dims, sizes, labels)

    # Run UDF executor
    t1 = time.time() # Start benchmark
    result = execute_udf(process, udf, data, dimension = dimension, context = context, parallelize = parallelize, chunk_size = chunk_size)
    t2 = time.time() # End benchmark

    # Print result and benchmark
    print('  Time elapsed: %s' % (t2 - t1))
    print(result)


print('apply model')
run('apply', './udfs/apply_models.R')