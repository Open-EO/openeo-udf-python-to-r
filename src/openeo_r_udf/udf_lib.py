import xarray as xr
import numpy as np
import rpy2.robjects as robjects
from rpy2.robjects import numpy2ri
import requests
import json
import os
import pkg_resources
from typing import Any, Optional

numpy2ri.activate()

def execute_udf(process: str, udf_path: str, data: xr.DataArray, dimension: Optional[str] = None, context: Any = None):
    rFunc = compile_udf_executor()

    # Prepare data cube metadata
    input_dims = list(data.dims)
    output_dims = list(data.dims)
    if dimension is not None:
        output_dims.remove(dimension)
    kwargs_default = {'process': process, 'dimension': dimension, 'context': json.dumps(context), 'file': udf_path, 'dimensions': list(),  'labels': list()}

    def call_r(data, dimensions, labels, file, process, dimension, context):
        if dimension is None and context is None:
            vector = rFunc(data, dimensions, labels, file, process)
        if context is None:
            vector = rFunc(data, dimensions, labels, file, process, dimension = dimension)
        elif dimension is None:
            vector = rFunc(data, dimensions, labels, file, process, context = context)
        else:
            vector = rFunc(data, dimensions, labels, file, process, dimension = dimension, context = context)
        return vector

    if process == 'apply' or process == 'reduce_dimension':
        def runnable(data): 
            kwargs = kwargs_default.copy()
            kwargs['dimensions'] = list(data.dims)
            kwargs['labels'] = get_labels(data)
            return xr.apply_ufunc(
                call_r, data, kwargs = kwargs,
                input_core_dims = [input_dims], output_core_dims = [output_dims],
                vectorize = True
                # exclude_dims could be useful for apply_dimension?
            )

        return runnable(data)
    else:
        raise Exception("Not implemented yet for Python")

def get_labels(data):
    labels = []
    for k in data.dims:
        labels.append(data.coords[k].data)
    return labels

def create_dummy_cube(dims, sizes, labels) -> xr.DataArray:
    npData = np.random.rand(*sizes)
    if (labels['x'] is None):
        labels['x'] = np.arange(npData.shape[0])
    if (labels['y'] is None):
        labels['y'] = np.arange(npData.shape[1])
    xrData = xr.DataArray(npData, dims = dims, coords = labels)
    return xrData

def combine_cubes(data):
    return xr.combine_by_coords(
        data_objects = data,
        compat = 'no_conflicts',
        data_vars = 'all',
        coords = 'different',
        join = 'outer',
        combine_attrs = 'no_conflicts',
        datasets = None)

def chunk_cube(data, dimension = None, size = 1000):
    # todo: generalize to work on all dimensions except the one given in `dimension`
    chunks = []
    data_size = dict(data.sizes)
    num_chunks_x = int(np.ceil(data_size['x']/size))
    num_chunks_y = int(np.ceil(data_size['y']/size))
    for i in range(num_chunks_x):
        x1 = i * size
        x2 = min(x1 + size, data_size['x']) - 1
        for j in range(num_chunks_y):
            y1 = j * size
            y2 = min(y1 + size, data_size['y']) - 1
            chunk = data.loc[dict(
                x = slice(data.x[x1], data.x[x2]),
                y = slice(data.y[y1], data.y[y2])
            )]
            chunks.append(chunk)


    return chunks

def prepare_udf(udf, udf_folder = None):
    if isinstance(udf, str) == False :
        raise "Invalid UDF specified"

    if udf.startswith("http://") or udf.startswith("https://"): # uri
        r = requests.get(udf)
        if r.status_code != 200:
            raise Exception("Provided URL for UDF can't be accessed")
        return write_udf(r.text, udf_folder)
    elif "\n" in udf or "\r" in udf: # code
        return write_udf(udf, udf_folder)
    else: # file path
        return udf

def write_udf(data, udf_folder):
    success = False
    path = os.path.join(udf_folder, 'udf.R')
    file = open(path, 'w')
    try:
        file.write(data)
        success = True
    finally:
        file.close()
    
    if success == True:
        return path
    else:
        raise Exception("Can't write UDF file to " + path)

# Compile R Code once
def compile_udf_executor():
    executor_R_path = pkg_resources.resource_filename(__name__, 'executor.R')
    file = open(executor_R_path, mode = 'r')
    rCode = file.read()
    file.close()
    rEnv = robjects.r(rCode)
    return robjects.globalenv['main']
