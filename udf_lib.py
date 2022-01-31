import xarray as xr
import numpy as np
import rpy2.robjects as robjects
import requests

NUM_CORES = 4
CHUNK_LIMIT = 100

def execute_udf(data, process, process_args, udf): # Only works for data which have spatial dimensions and no label support yet
    rFunc = prepare_r_udf(udf)

    if process == 'apply':
        raise Exception("apply not supported yet")
    elif process == 'reduce_dimension':
        chunks = chunk_cube(data, process, dimension = process_args.get('dimension', None))
        # func = lambda data, process, process_args, context: rFunc(process, process_args, {'data': data, 'context': process_args.get('context', None)})
        func = lambda data, process, process_args: print(data, process, process_args)
        return chunks.map_blocks(func = func, kwargs = {'process': process, 'process_args': process_args}).compute()
    else:
        raise Exception("Not supported yet")

def chunk_cube(data, process, dimension = None):
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
    xrData = xr.DataArray(npData, dims = dims) #, coords = {'x': np.arange(npData.shape[0]), 'y': np.arange(npData.shape[1]), 'b': ['b1', 'b2', 'b3']})
    return xrData

def generate_filename():
    return "./udfs/temp.R"

def prepare_r_udf(udf):
    if isinstance(udf, str) == False :
        raise "Invalid UDF specified"

    if udf.startswith("http://") or udf.startswith("https://"): # uri
        r = requests.get(udf)
        if r.status_code != 200:
            raise Exception("Provided URL for UDF can't be accessed")
        
        return write_udf(r.content)
    elif "\n" in udf or "\r" in udf: # code
        with open(filename, 'w') as f:
            f.write(udf)
            return filename
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
def compile_udf():
    file = open('./R/main.R', mode = 'r')
    rCode = file.read()
    file.close()

    rEnv = robjects.r(rCode)
    return robjects.globalenv['main']