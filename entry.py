from udf_lib import execute_udf, create_dummy_cube
import time

# Data Cube config
dims = ['x', 'y', 'b']
sizes = [100, 100, 3]

def run(process, udf, dimension = None, context = None):
    # Prepare data
    data = create_dummy_cube(dims, sizes)

    # Run UDF executor
    t1 = time.time() # Start benchmark
    result = execute_udf(process, udf, data, dimension = dimension, context = context)
    t2 = time.time() # End benchmark

    # Print result and benchmark
    print(result)
    print("Time elapsed: %s" % (t2 - t1))

run("reduce_dimension", "./udfs/reduce.R", dimension = 'b', context = -1)

run("apply", "./udfs/apply.R", context = -1)