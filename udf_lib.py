import xarray as xr
import numpy as np
import rpy2.robjects as robjects
from rpy2.robjects import numpy2ri
import requests

numpy2ri.activate()

CHUNK_LIMIT = 100

def execute_udf(process, udf, data, dimension = None, context = None):
    # Prepare UDF code
    udf_filename = prepare_udf(udf)
    rFunc = compile_udf_executor()

    # Prepare data cube metadata
    input_dims = list(data.dims)
    output_dims = list(data.dims)
    if dimension is not None:
        output_dims.remove(dimension)
    labels = get_labels(data)

    kwargs = {'process': process, 'dimension': dimension, 'context': context, 'file': udf_filename, 'dimensions': list(data.dims),  'labels': labels}

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
        return xr.apply_ufunc(call_r, data, input_core_dims = [input_dims], output_core_dims = [output_dims], kwargs = kwargs, vectorize = True, dask = "parallelized")
        #chunks = chunk_cube(data, dimension = dimension)
        #return chunks.map_blocks(call_r, data, kwargs = kwargs).compute()
    else:
        raise Exception("Not implemented yet for Python")

def get_labels(data):
    labels = []
    for k in data.coords:
        labels.append(data.coords[k].data)
    return labels

def chunk_cube(data, dimension = None):
    # Determin chunk sizes
    chunks = dict(data.sizes)
    for k,v in chunks.items():
        if k != dimension and v > CHUNK_LIMIT:
            chunks[k] = CHUNK_LIMIT

    # Chunk data
    return data.chunk(chunks = chunks)

def unchunk_cube(data):
    return xr.combine_by_coords(data_objects = data, compat = 'no_conflicts', data_vars = 'all', coords = 'different', join = 'outer', combine_attrs = 'no_conflicts', datasets = None)
        
def create_dummy_cube(dims, sizes):
    npData = np.random.rand(*sizes)
    xrData = xr.DataArray(npData, dims = dims, coords = {'x': np.arange(npData.shape[0]), 'y': np.arange(npData.shape[1]), 'b': ['b1', 'b2', 'b3']}) # todo
    return xrData

def generate_filename():
    return "./udfs/temp.R"

def prepare_udf(udf):
    if isinstance(udf, str) == False :
        raise "Invalid UDF specified"

    if udf.startswith("http://") or udf.startswith("https://"): # uri
        r = requests.get(udf)
        if r.status_code != 200:
            raise Exception("Provided URL for UDF can't be accessed")
        
        return write_udf(r.content)
    elif "\n" in udf or "\r" in udf: # code
        return write_udf(udf)
    else: # file path
        return udf

def write_udf(data):
    filename = generate_filename()
    success = False
    file = open(filename, 'w')
    try:
        file.write(data)
        success = True
    finally:
        file.close()
    
    if success == True:
        return filename
    else:
        raise Exception("Can't write UDF file")

# Compile R Code once
def compile_udf_executor():
    file = open('./main.R', mode = 'r')
    rCode = file.read()
    file.close()

    rEnv = robjects.r(rCode)
    return robjects.globalenv['main']