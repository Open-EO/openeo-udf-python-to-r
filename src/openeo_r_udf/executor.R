suppressWarnings(suppressMessages(library("stars", quietly = T)))

main = function(data, dimensions, labels, file, process, dimension = NULL, context = NULL) {
  dimensions = jsonlite::fromJSON(dimensions)
  context = if (is.null(context)) context else jsonlite::fromJSON(context)
  dim_labels = NULL

  source(file)

  # create data cube in stars
  dim_names = names(dimensions)
  dc = st_as_stars(data)
  dc = st_set_dimensions(dc, names = dim_names)
  for(i in 1:length(dim_names)) {
    name = dim_names[i]
    type = dimensions[name]
    values = unlist(labels[i])
    if (type == "spatial") {
      dc = st_set_dimensions(dc, name, values = as.numeric(values))
    }
    else if (type == "temporal") {
      dc = st_set_dimensions(dc, name, values = lubridate::as_datetime(values))
    }
    else {
      dc = st_set_dimensions(dc, name, values = values)
    }
    if (!is.null(dimension) && name == dimension) {
      dim_labels = values
    }
  }

  if(process == 'apply') {
    # apply on each pixel
    dc = udf(dc, context)
  }
  else if(process == 'reduce_dimension' || process == 'apply_dimension') {
    # reduce data cube OR
    # apply along a single dimension, e.g. along t for timeseries
    margin = dim_names[dim_names != dimension]
    if (exists("udf_chunked")) {
      if (exists("udf_setup")) {
        udf_setup(context)
      }
      prepare = function(data) {
        names(data) = dim_labels
        result = udf_chunked(data, context)
        return(result)
      }
      old_length = dim(dc)[dimension]
      if (process == 'reduce_dimension') {
        dc = st_apply(dc, margin, prepare)
      }
      else { # apply_dimension
        # apply the function and keep the labels. aperm restores the old dimension order.
        dc = st_apply(dc, margin, prepare, keep = TRUE) |> aperm(dim_names)
        new_length = dim(dc)[dimension]
        if (new_length != old_length) {
          # Create new coordinates (integers starting with 0) as the length has changed
          dc = st_set_dimensions(dc, dimension, values = 1:new_length)
        }
      }
      if (exists("udf_teardown")) {
        udf_teardown(context)
      }
    }
    else {
      prepare = function(x1, x2, ...) {
        d = dim(x1)
        l = lapply(append(list(x1, x2), list(...)), structure, dim = NULL)
        data = do.call(cbind, l)

        colnames(data) = dim_labels
        
        result = udf(data, context)
        if (process == 'reduce_dimension') {
            dim(result) = d
        }
        else { # apply_dimension
            dim(result) = c(nrow(result), d)
        }
        return (result)
      }
      if (process == 'reduce_dimension') {
        dc = st_apply(dc, margin, prepare, single_arg = FALSE)
      }
      else { # apply_dimension
        dc = st_apply(dc, margin, prepare, single_arg = FALSE, keep = TRUE) |> aperm(dim_names)
      }
    }
  }
  else {
    stop("Not implemented yet for R");
  }

  # return data cube as array
  df = dc[[1]]
  return (df)
}
