suppressWarnings(suppressMessages(library("stars", quietly = T)))

main = function(data, dimensions, labels, file, process, dimension = NULL, context = NULL) {
  dimensions = unlist(dimensions)

  source(file)

  if(process == 'apply') {
    result = udf(data, context)
    return (result)
  }
  else if(process == 'reduce_dimension') {
    # create data cube in stars
    dc = st_as_stars(data)
    dc = st_set_dimensions(dc, names = dimensions)
    for(i in 1:length(dimensions)) {
      name = dimensions[i]
      values = unlist(labels[i])
      if (name == "x" || name == "y") {
        dc = st_set_dimensions(dc, name, values = as.numeric(values))
      }
      else if (name == "t") {
        dc = st_set_dimensions(dc, name, values = lubridate::as_datetime(values))
      }
      else {
        dc = st_set_dimensions(dc, name, values = values)
      }
    }
    # reduce data cube
    margin = dimensions[dimensions != dimension]
    prepare = function(x1, x2, ...) {
      data = append(list(x1, x2), list(...))
      return (udf(data, context))
    }
    dc = st_apply(dc, margin, prepare)
    # return data cube as array
    df = dc[[1]]
    return (df)
  }
  else {
    stop("Not implemented yet for R");
  }
}
