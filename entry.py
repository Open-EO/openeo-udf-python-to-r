from udf_lib import execute_udf, create_dummy_cube
import time

# Data Cube config
dims = ['x', 'y', 'b']
sizes = [10000, 10000, 3]

def run(process, process_args, udf):
    # Prepare data
    data = create_dummy_cube(dims, sizes)

    # Run UDF executor
    t1 = time.time() # Start benchmark
    execute_udf(data, process, process_args, udf)
    t2 = time.time() # End benchmark

    # Print result and benchmark
    print(result)
    print("Time elapsed: %s" % (t2 - t1))


run("reduce_dimension", {'dimension': 'b', 'context': -1}, "./udfs/reduce.R")

run("apply", {'context': -1}, "./udfs/apply.R")