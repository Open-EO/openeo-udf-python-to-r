# openeo-udf-python-to-r

This is an experimental engine for openEO to run R UDFs from an R environment.

This currently is limited to R UDFs that are running without any other processes in the following processes:
- `apply`
- `reduce_dimension`

This repository contains the following content:
- The script to run for testing is `test.py`.
- The folder `udfs` contains example UDFs as users could provide them.
- The script to benchmark againt plain R is `benchmark.R`.
- `udf_lib.py` is a Python library with the Python code required to run R UDFs from Python
- `executor.r` is the R script that is run from R and executes the R UDF in the Python environment.

The following image shows how the implementation roughly works:
![Workflow](docs/workflow.png)

## Writing a UDF

A UDF must be written differently depending on where it is executed.
The underlying library used for data handling is always [`stars`](https://r-spatial.github.io/stars/).

### apply

A UDF that is executed inside the process `apply` manipulates the values on a per-pixel basis.
You **can't** add or remove labels or dimensions.

The UDF function must be named `udf` and receives two parameters:

- `x` is a multi-dimensional stars object and you can run vectorized functions on a per pixel basis, e.g. `abs`.
- `context` passes through the data that has been passed to the `context` parameter of the parent process (here: `apply`). If nothing has been provided explicitly, the parameter is set to `NULL`.
  
  This can be used to pass through configurable options, parameters or some additional data.
  For example, if you would execute `apply(process = run_udf(...), context = list(m = -1, max = -100))` then you could access the corresponding values in the UDF below as `context$m` and `context$max` (see example below).

The UDF must return a stars object with exactly the same shape.

**Example:**

```r
udf = function(x, context) {
  max(abs(x) * context$a, context$max)
}
```

### reduce_dimension

A UDF that is executed inside the process `reduce_dimension` takes all values along a dimension and computes a single value for it.
This could for example compute an average for a timeseries.

There are two different variants of UDFs that can be used as reducers for `reduce_dimension`.
A reducer can be executed either "vectorized" or "per chunk".

#### vectorized

The vectorized variant is usually the more efficient variant as it's executed once on a larger chunk of the data cube.

The UDF function must be named `udf` and receives two parameters:

- `data` is a list of lists of values that you can run vectorized functions on a per pixel basis, e.g. `pmax`.
- `context` -> see the description of `context` for `apply`.

The UDF must return a list of values.

**Example:**

Please note that you may need to use `do.call` to execute functions in a vectorized way. We also need to use `pmax` for this, instead of `max`.

```r
udf = function(data, context) {
  # To get the labels for the values once:
  # labels = names(data)
  do.call(pmax, data) * context
}
```

The input data may look like this if you reduce along a band dimension with three bands `r`, `g` and `b`:

- `data` could be `list(r = c(1, 2, 6), g = c(3, 4, 5), b = c(7, 1, 0))`
- `names(data)` would be `c("r", "g", "b")`
- Exeucting the example above would return `c(7, 4, 6)`

#### per chunk

This variant is usually slower, but might be required for certain use cases. It is executed multiple times on the smallest chunk possible for the dimension given, e.g. a single time series.

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
- Exeucting the example above would return `3`

##### Setup and Teardown

As `udf_chunked` is usually executed many times in a row, you can optionally define two additional functions that are executed once before and once after the execution.
These functions must be named `udf_setup` and `udf_teardown` and be placed in the same file as `udf_chunked`.
`udf_setup` could be useful to initially load some data, e.g. a machine learning (ML) model.
`udf_teardown` could be used to clean-up stuff that has been opened in `udf_setup`.

Both functions receive a single parameter, which is the `context` parameter explained above.
Here the context parameter could contain the path to a ML model file, for example.
By using the context parameter, you can avoid hard-coding information, which helps to make UDFs reusable.

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

**Note:** `udf_teardown` is only executed if none of the `udf_chunked` calls has resulted in an error.
