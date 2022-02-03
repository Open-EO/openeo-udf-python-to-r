from udf_lib import execute_udf, create_dummy_cube
import time

# Data Cube config
dims = ['x', 'y', 't', 'b']
sizes = [7400, 1000, 10, 3]
labels = {
    # x and y get generated automatically for now (todo: get from actual data)
    'x': None,
    'y': None,
    't': ['2020-01-01T00:00:00Z', '2020-01-02T00:00:00Z', '2020-01-03T00:00:00Z', '2020-01-04T00:00:00Z', '2020-01-05T00:00:00Z', '2020-01-06T00:00:00Z', '2020-01-07T00:00:00Z', '2020-01-08T00:00:00Z', '2020-01-09T00:00:00Z', '2020-01-10T00:00:00Z'],
    'b': ['b1', 'b2', 'b3']
}

def run(process, udf, dimension = None, context = None):
    # Prepare data
    data = create_dummy_cube(dims, sizes, labels)

    # Run UDF executor
    t1 = time.time() # Start benchmark
    result = execute_udf(process, udf, data, dimension = dimension, context = context)
    t2 = time.time() # End benchmark

    # Print result and benchmark
    print("Time elapsed: %s" % (t2 - t1))
    print(result)

print("apply")
run("apply", "./udfs/apply.R", context = -1)

print("reduce_dimension")
run("reduce_dimension", "./udfs/reduce.R", dimension = 'b', context = -1)

# Benchmark for 100x100x10x3:
# apply: 1.5 sec
# reduce_dimension: 0.3 sec
# old variant for reduce_dimension: 233 sec
#
# Benchmark for 7400x1000x10x3:
# apply: ~ 20 sec
# reduce_dimension: ~ 25 sec