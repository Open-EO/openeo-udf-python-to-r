from udf_lib import execute_udf, create_dummy_cube
import time
import numpy as np
from joblib import Parallel, delayed
import dask
from dask import delayed as dask_delayed
import xarray as xr

# Data Cube config
dims = ['x', 'y', 't', 'b']
sizes = [740, 1000, 10, 3]
labels = {
    # x and y get generated automatically for now (todo: get from actual data)
    'x': None,
    'y': None,
    't': ['2020-01-01T00:00:00Z', '2020-01-02T00:00:00Z', '2020-01-03T00:00:00Z', '2020-01-04T00:00:00Z', '2020-01-05T00:00:00Z', '2020-01-06T00:00:00Z', '2020-01-07T00:00:00Z', '2020-01-08T00:00:00Z', '2020-01-09T00:00:00Z', '2020-01-10T00:00:00Z'],
    'b': ['b1', 'b2', 'b3']
}

data = create_dummy_cube(dims, sizes, labels)

chunk_size_x = 100
chunk_size_y = 100

data_size_x = len(data.x)
data_size_y = len(data.y)

chunks_list = []
for i in range(int(np.ceil(data_size_x/chunk_size_x))):
    x_end_index = chunk_size_x*(i+1)-1
    if x_end_index > data_size_x: x_end_index = data_size_x-1
    for j in range(int(np.ceil(data_size_y/chunk_size_y))):
        y_end_index = chunk_size_y*(j+1)-1
        if y_end_index > data_size_y: y_end_index = data_size_y-1
        # print(i*chunk_size_x,chunk_size_x*(i+1))
        # print(j*chunk_size_y,chunk_size_y*(j+1))            
        chunk = data.loc[dict(x=slice(data.x[i*chunk_size_x],data.x[x_end_index]),y=slice(data.y[j*chunk_size_y],data.y[y_end_index]))]
        chunks_list.append(chunk)

def chunked_data_processing(data):
    return data.mean(dim='b')

results_list = list(Parallel(n_jobs=4)(delayed(chunked_data_processing)(chunks_list[i]) for i in range(len(chunks_list))))

result0 = xr.combine_by_coords(data_objects=results_list, compat='no_conflicts', data_vars='all', coords='different', join='outer', combine_attrs='no_conflicts', datasets=None)

result1 = data.mean(dim='b')

print((result0 == result1).all())

# Dask parallel processing

dask_calls_list = []
for chunk in chunks_list:
    dask_calls_list.append(dask_delayed(chunked_data_processing)(chunk))
    
results_list_dask = dask.compute(*dask_calls_list)

result2 = xr.combine_by_coords(data_objects=results_list_dask, compat='no_conflicts', data_vars='all', coords='different', join='outer', combine_attrs='no_conflicts', datasets=None)

print((result2 == result1).all())