from openeo_r_udf.udf_lib import prepare_udf, execute_udf, chunk_cube, combine_cubes, create_dummy_cube
from joblib import Parallel, delayed as joblibDelayed
import time
import tempfile

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

# Parallelization config
chunk_size = 1000
num_jobs = -1

# Prepare data
data = create_dummy_cube(dims, sizes, labels)

def run(process, udf, udf_folder, dimension = None, context = None):
    udf_path = prepare_udf(udf, udf_folder)

    # Define callback function
    def compute_udf(data):
        return execute_udf(process, udf_path, data.compute(), dimension = dimension, context = context)
    
    t1 = time.time() # Start benchmark

    # Run UDF executor in parallel
    input_data_chunked = chunk_cube(data, size=chunk_size)
    results = Parallel(n_jobs=num_jobs, verbose=51)(joblibDelayed(compute_udf)(data) for data in input_data_chunked)
    result = combine_cubes(results)

    t2 = time.time() # End benchmark

    # Print result and benchmark
    print('  Time elapsed: %s' % (t2 - t1))
    print(result)

with tempfile.TemporaryDirectory() as folder:
    print('apply')
    run('apply', './tests/udfs/apply.R', folder, context = -1)

    print('reduce_dimension vectorized')
    run('reduce_dimension', './tests/udfs/reduce.R', folder, dimension = 'b', context = -1)
