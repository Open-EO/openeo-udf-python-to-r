from openeo_r_udf.udf_lib import prepare_udf, execute_udf, create_dummy_cube
import time
import tempfile
import xarray as xr

# Data Cube config
dims = ['x', 'y', 't', 'b']
sizes = [2000, 1000, 30, 3]
labels = {
    # x and y get generated automatically for now (todo: get from actual data)
    'x': None,
    'y': None,
    't': ['2020-01-01T00:00:00Z', '2020-01-02T00:00:00Z', '2020-01-03T00:00:00Z', '2020-01-04T00:00:00Z', '2020-01-05T00:00:00Z', '2020-01-06T00:00:00Z', '2020-01-07T00:00:00Z', '2020-01-08T00:00:00Z', '2020-01-09T00:00:00Z', '2020-01-10T00:00:00Z', '2020-01-11T00:00:00Z', '2020-01-12T00:00:00Z', '2020-01-13T00:00:00Z', '2020-01-14T00:00:00Z', '2020-01-15T00:00:00Z', '2020-01-16T00:00:00Z', '2020-01-17T00:00:00Z', '2020-01-18T00:00:00Z', '2020-01-19T00:00:00Z', '2020-01-20T00:00:00Z', '2020-01-21T00:00:00Z', '2020-01-22T00:00:00Z', '2020-01-23T00:00:00Z', '2020-01-24T00:00:00Z', '2020-01-25T00:00:00Z', '2020-01-26T00:00:00Z', '2020-01-27T00:00:00Z', '2020-01-28T00:00:00Z', '2020-01-29T00:00:00Z', '2020-01-30T00:00:00Z'],
    'b': ['r', 'g', 'b']
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
    # print(result)


def run_native(dimension = None):
    t1 = time.time() # Start benchmark
    result = data * -1
    t2 = time.time() # End benchmark

    # Print result and benchmark
    print('  Time elapsed: %s' % (t2 - t1))
    # print(result)

def measure_r(process, udf, udf_folder, dimension = None, context = None):
    udf_path = prepare_udf(udf, udf_folder)
    result = execute_udf(process, udf_path, data, dimension = dimension, context = context)
    # print(result)

with tempfile.TemporaryDirectory() as folder:
    # print('Native Python')
    # run_native()
    
    # print('UDF')
    run('apply', './tests/udfs/apply.R', folder)

    # print('Native R')
    # measure_r('apply', './tests/udfs/apply_timer.R', folder)


