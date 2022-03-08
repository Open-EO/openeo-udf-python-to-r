from udf_lib import execute_udf, load_data, save_result
import time

# Config
parallelize = True
chunk_size = 2000
load_file = ""
save_file = ""

# Prepare data
data = load_data(load_file)

def run(process, udf, dimension = None, context = None):
    # Run UDF executor
    t1 = time.time() # Start benchmark
    result = execute_udf(process, udf, data, dimension = dimension, context = context, parallelize = parallelize, chunk_size = chunk_size)
    t2 = time.time() # End benchmark

    # Print result and benchmark
    print('  Time elapsed: %s' % (t2 - t1))
    save_result(result, save_file)

print('apply')
run('apply', './udfs/apply.R', context = -1)

#print('reduce_dimension bfast')
#run('reduce_dimension', './udfs/reduce_bfast.R', dimension = 't', context = {'start_monitor': 2021})