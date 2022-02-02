import xarray as xr
import numpy as np
import rpy2.robjects as robjects
from rpy2.robjects import numpy2ri
import requests

numpy2ri.activate()

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
        # print("r called")
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
        # todo: chunking/parallelization doesn't work
        # data = chunk_cube(data, dimension = dimension, size = 500)
        return xr.apply_ufunc(
            call_r, data, kwargs = kwargs,
            input_core_dims = [input_dims], output_core_dims = [output_dims],
            vectorize = True,
            dask = "parallelized"#, dask_gufunc_kwargs = {'allow_rechunk': True}
            # exclude_dims could be useful for apply_dimension?
        )
    else:
        raise Exception("Not implemented yet for Python")

def get_labels(data):
    labels = []
    for k in data.coords:
        labels.append(data.coords[k].data)
    return labels

def create_dummy_cube(dims, sizes, labels):
    npData = np.random.rand(*sizes)
    if (labels['x'] is None):
        labels['x'] = np.arange(npData.shape[0])
    if (labels['y'] is None):
        labels['y'] = np.arange(npData.shape[1])
    xrData = xr.DataArray(npData, dims = dims, coords = labels)
    return xrData

def chunk_cube(data, dimension = None, size = 1000):
    # Determin chunk sizes
    chunks = dict(data.sizes)
    for k,v in chunks.items():
        if k != dimension and v > size:
            chunks[k] = size

    # Chunk data
    return data.chunk(chunks = chunks)

def generate_filename():
    return "./udfs/temp.R" # todo

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