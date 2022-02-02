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
      if (name != "x" && name != "y") {
        values = unlist(labels[i])
        dc = st_set_dimensions(dc, name, values = values)
      }
    }
    # reduce data cube
    margin = dimensions[dimensions != dimension]
    dc = st_apply(dc, margin, function(x) { udf(x, context) })
    # return data cube as array
    df = dc[[1]]
    return (df)
  }
  else {
    stop("Not implemented yet for R");
  }
}
