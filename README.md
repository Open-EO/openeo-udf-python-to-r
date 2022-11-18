# openeo-udf-python-to-r / openeo-r-udf

This is an experimental engine for openEO to run R UDFs from an R environment.

This implementation is currently limited to R UDFs that are running without any other processes in the following processes:
- `apply`
- `apply_dimension`
- `reduce_dimension`

This repository contains the following content:
- The scripts to run for testing: `tests/test.py` (single core) and `tests/test_parallel.py` (parallelized).
- The folder `tests/udfs` contains UDF examples as users could provide them.
- `udf_lib.py` is a Python library with the Python code required to run R UDFs from Python
- `executor.R` is the R script that is run from R and executes the R UDF in the Python environment.

The following image shows how the implementation roughly works:
![Workflow](docs/workflow.png)

## UDF integration

This section is for back-end developers who want to add R UDF capabilities to their back-end 
or for end-users who want to test their UDFs locally.

### Install from pypi

You may want to install all dependencies as a new conda environment first:

`conda env create -f environment.yml`

You can install this library from pypi then:

`pip install openeo-r-udf`

### Run UDFs

In the following chapter we'll give examples on how to use the UDF library from a Python environment.

The following variables should be defined:
- `udf` (string - The content of the parameter `udf` from `run_udf`, i.e. UDF code or a path/URL to a UDF)
- `udf_folder` (string - The folder where the UDFs reside or should be written to)
- `process` (string - The parent process, i.e. `apply`, `apply_dimension` or `reduce_dimension`)
- `data` (xarray.DataArray - The data to process)
- `dimension` (string, defaults to `None` - The dimension to work on if applicable, doesn't apply for `apply`)
- `context` (Any, defaults to `None` - The data that has been passed in the `context` parameter)

Additionally, if your back-end keeps track of it, you can pass `spatial_dims` and `temporal_dims` to `execute_udf`
where each is a list of dimension names (as strings) for the corresponding dimension types spatial (x,y,z) and temporal.

### Without Parallelization *or* With Parallelization through Dask

If your back-end parallelizes already, you can directly run the following code:

```python
# import the UDF library
from openeo_r_udf.udf_lib import prepare_udf, execute_udf

# Define variables as documented above

# Load UDF file (this should not be paralelized)
udf_path = prepare_udf(udf, udf_folder)

# Execute UDF file (this can be parallelized)
result = execute_udf(process, udf_path, data, dimension=dimension, context=context)
```

If you parallelize with Dask, the xarray.DataArray must consist of Dask arrays, i.e. the `chunks` attribute of the DataArray MUST NOT be `None`.

### With Parallelization through joblib

If your back-end is not parallelizing at all, you can run the following:

```python
# import the UDF library - make sure to install joblib before
from openeo_r_udf.udf_lib import prepare_udf, execute_udf, chunk_cube, combine_cubes
from joblib import Parallel, delayed as joblibDelayed

# Parallelization config
chunk_size = 1000
num_jobs = -1

# Define variables as documented above

# Load UDF file (this should not be paralelized)
udf_path = prepare_udf(udf, udf_folder)

# Define callback function
def compute_udf(data):
    return execute_udf(process, udf_path, data.compute(), dimension=dimension, context=context)

# Run UDF in parallel
input_data_chunked = chunk_cube(data, size=chunk_size)
results = Parallel(n_jobs=num_jobs, verbose=51)(joblibDelayed(compute_udf)(data) for data in input_data_chunked)
result = combine_cubes(results)
```

The `result` variable holds the processed data as an `xarray.DataArray` again.

## Writing a UDF

*This is for end-users*

A UDF must be written differently depending on where it is executed.
The underlying library used for data handling is always [`stars`](https://r-spatial.github.io/stars/).

### apply

A UDF that is executed inside the process `apply` manipulates the values on a per-pixel basis.
You **can't** add or remove labels or dimensions.

The UDF function must be named `udf` and receives two parameters:

- `x` is a multi-dimensional stars object and you can run vectorized functions on a per pixel basis, e.g. `abs`.
- `context` passes through the data that has been passed to the `context` parameter of the parent process (here: `apply`). If nothing has been provided explicitly, the parameter is set to `NULL`.
  
  This can be used to pass through configurable options, parameters or some additional data.
  For example, if you would execute `apply(process = run_udf(...), context = list(min = -1, max = -100))` then you could access the corresponding values in the UDF below as `context$min` and `context$max` (see example below).

The UDF must return a stars object with exactly the same shape.

**Example:**

```r
udf = function(x, context) {
  min(max(x, context$min), context$max) 
}
```

### apply_dimension

A UDF that is executed inside the process `apply_dimension` takes all values along a dimension and computes new values based on them.
This could for example compute a moving average over a timeseries.

There are two different variants of UDFs that can be used as processes for `apply_dimension`.
A reducer can be executed either "vectorized" or "per chunk".
This is the same behavior as defined for `reduce_dimension`. 
Please see below for more details.

### reduce_dimension

A UDF that is executed inside the process `reduce_dimension` takes all values along a dimension and computes a single value for it.
This could for example compute an average for a timeseries.

There are two different forms of UDFs that can be used as reducers
for `reduce_dimension`: a reducer can be executed either "vectorized"
or "per chunk".

#### vectorized

The vectorized variant is usually the more efficient variant as it's executed once on a larger chunk of the data cube.

The UDF function must be named `udf` and receives two parameters:

- `data` is a matrix. Each row contains the values for a "pixel" and the columns are the values along the given dimension.
  So, if you reduce along the temporal dimension, the columns are the individual timestamps.
- `context` -> see the description of `context` for `apply`.

The UDF must return a list of values.

**Example:**

```r
udf = function(data, context) {
  # To get the labels for the values once:
  # labels = colnames(data)
  do.call(pmax, as.data.frame(data))
  # You could also use apply, but this is much slower as it is not vectorized:
  # apply(data, 1, max) * context
}
```

The input data may look like this if you reduce along a band dimension with three bands `r`, `g` and `b`:

- `data` could be `matrix(c(1,2,6,3,4,5,7,1,0), nrow = 3, dimnames = list(NULL, c("r","g","b")))`
- `colnames(data)` would be `c("r", "g", "b")`
- Executing the example above would return `c(7, 4, 6)`

#### per chunk

This variant is usually slower, but might be required for certain use cases. It is executed multiple times on the smallest chunk possible for the dimension given, e.g., a single time series.

The UDF function must be named `udf_chunked` and receives two parameters:

- `data` is a list of values, e.g. a single time series which you could pass to `max` or `mean`.
- `context` -> see the description of `context` for `apply`.

The UDF must return a single value.

**Example:**

```r
udf_chunked = function(data, context) {
  # To get the labels for the values:
  # labels = names(data)
  max(data)
}
```

The input data may look like this if you reduce along a band dimension with three bands `r`, `g` and `b`:

- `data` could be `c(1, 2, 3)`
- `names(data)` would be `c("r", "g", "b")`
- Executing the example above would return `3`

##### Setup and Teardown

As `udf_chunked` is usually executed many times in a row, you can optionally define two additional functions that are executed once before and once after the execution.
These functions must be named `udf_setup` and `udf_teardown` and be placed in the same file as `udf_chunked`.
`udf_setup` could be useful to initially load some data, e.g. a machine learning (ML) model.
`udf_teardown` could be used to clean-up stuff that has been opened in `udf_setup`.

**Note:** `udf_setup` and `udf_teardown` are only available if you implement `udf_chunked`.
If you implement `udf`, the two additional functions are not available as you can execute them directly in the `udf` function, which is only executed once (for each worker).

Both functions receive a single parameter, which is the `context` parameter explained above.
Here the context parameter could contain the path to a ML model file, for example.
By using the context parameter, you can avoid hard-coding information, which helps to make UDFs more reusable.

**Example:**

```r
udf_setup = function(context) {
  # e.g. load a ML model from a file
}

udf_chunked = function(data, context) {
  max(data)
}

udf_teardown = function(context) {
  # e.g. clean-up tasks
}
```

**Note:** `udf_teardown` is only executed if none of the `udf_chunked` calls have resulted in an error.

If you'd like to make some data available in `udf_chunked` and/or `udf_teardown` that you have prepared in `udf_setup` (or `udf_chunked`), you can use a global variable
and the [special assignment operator](https://cran.r-project.org/doc/manuals/R-intro.html#Scope) `<<-` to assign to variables in the outer environments.

**Example:**

This loads a trained ML model object from an URL in `udf_setup` and makes it available for prediction in `udf_chunked`.
This is important as loading the ML model in udf_chunked may download the model very often, usually thousands of times and as such the computation gets very slow.

```r
model <- NULL

udf_setup = function(context) {
  model <<- load_model("https://example.com/model")
}

udf_chunked = function(data, context) {
  return(predict(data, model))
}
```

## Examples
### Dockerimage for running on a backend
Here's an example of an Dockerimage that is used to run the R-UDF service on an openEO platform backend:
<https://github.com/Open-EO/r4openeo-usecases/tree/main/vito-docker>

### Implementation at Eurac
Here is an example how the R-UDF service is integrated in the Eurac openEO backend based on Open Data Cube:
<https://github.com/SARScripts/openeo_odc_driver/blob/f34cd35107e4fb137fc1d23cae246ed362517c75/openeo_odc_driver.py#L289>

### R4openEO use cases
Here are use cases that use the R-UDF service:
<https://github.com/Open-EO/r4openeo-usecases>


## Development

Clone this repository and switch into the corresponding folder.

1. Install environment via conda: `conda env create -f environment.yml`
2. Install package for development: `pip install -e .`
3. Now you can run one of the tests for example: `python3 tests/test.py`
