import json

# Compile R Code once
def compile_udf_executor():
    file = open('./executor.R', mode = 'r')
    rCode = file.read()
    file.close()

    from rpy2.robjects import numpy2ri
    numpy2ri.activate()

    import rpy2.robjects as robjects
    rEnv = robjects.r(rCode)
    return robjects.globalenv['main']

def call_r(data, dimensions, labels, file, process, dimension, context):
    
    rFunc = compile_udf_executor()
    if dimension is None and context is None:
        vector = rFunc(data, dimensions, labels, file, process)
    if context is None:
        vector = rFunc(data, dimensions, labels, file, process, dimension = dimension)
    elif dimension is None:
        vector = rFunc(data, dimensions, labels, file, process, context = json.dumps(context))
    else:
        vector = rFunc(data, dimensions, labels, file, process, dimension = dimension, context = json.dumps(context))
    return vector