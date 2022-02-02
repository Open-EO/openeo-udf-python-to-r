from udf_lib import execute_udf, create_dummy_cube
import time

# Data Cube config
dims = ['x', 'y', 'b']
sizes = [1000, 1000, 3]

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

run("apply", "./udfs/apply.R", context = -1)

run("reduce_dimension", "./udfs/reduce.R", dimension = 'b', context = -1)

# Benchmark for 1000x1000x3:
# apply: 1.5 sec
# reduce_dimension: 11 sec
# old variant for reduce_dimension: 233 sec
#
# Benchmark for 74000x1000x3:
# apply: 31 sec
# reduce_dimension: several minutes (tbc)
# old variant for reduce_dimension: not tested