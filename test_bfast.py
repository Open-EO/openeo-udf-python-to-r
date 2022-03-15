from udf_lib import execute_udf, create_dummy_cube
import pandas as pd
import time

# Data Cube config
dims = ['x', 'y', 't', 'b']
dates = pd.date_range(start = '1-1-2018', periods = 4*365).tolist()
for i in range(0, len(dates)):
    dates[i] = dates[i].strftime("%Y-%m-%dT%H:%M:%SZ")
sizes = [10, 10, len(dates), 3]
labels = {
    # x and y get generated automatically for now (todo: get from actual data)
    'x': None,
    'y': None,
    't': dates,
    'b': ['b1', 'b2', 'b3']
}
parallelize = True
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


print('reduce_dimension bfast')
run('reduce_dimension', './udfs/reduce_bfast.R', dimension = 't', context = {'start_monitor': 2018})