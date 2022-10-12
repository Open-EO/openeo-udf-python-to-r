from openeo_r_udf.udf_lib import prepare_udf, execute_udf, create_dummy_cube
import time
import tempfile

# Data Cube config
dims = ['x', 'y', 't']
sizes = [10, 10, 12]
labels = {
    # x and y get generated automatically for now (todo: get from actual data)
    'x': None,
    'y': None,
    't': ['2020-01-01T00:00:00Z', '2020-01-02T00:00:00Z', '2020-01-03T00:00:00Z', '2020-01-04T00:00:00Z', '2020-01-05T00:00:00Z', '2020-01-06T00:00:00Z', '2020-01-07T00:00:00Z', '2020-01-08T00:00:00Z', '2020-01-09T00:00:00Z', '2020-01-10T00:00:00Z', '2020-01-11T00:00:00Z', '2020-01-12T00:00:00Z']
}

# Prepare data
data = create_dummy_cube(dims, sizes, labels)

def run(process, udf, udf_folder, dimension = None, context = None):
    udf_path = prepare_udf(udf, udf_folder)
    # Run UDF executor
    t1 = time.time() # Start benchmark
    result = execute_udf(process, udf_path, data, dimension = dimension, context = context)
    t2 = time.time() # End benchmark

    # Print result and benchmark
    print('  Time elapsed: %s' % (t2 - t1))
    print(result)

with tempfile.TemporaryDirectory() as folder:
    print('apply_dimension')
    run('apply_dimension', './tests/udfs/apply_dimension.R', folder, dimension = "t", context = 2)

