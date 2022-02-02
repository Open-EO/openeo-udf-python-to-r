suppressWarnings(suppressMessages(library("stars", quietly = T)))

main = function(data, dimensions, labels, file, process, dimension = NULL, context = NULL) {
  dimensions = unlist(dimensions)

  source(file)

  if(process == 'apply') {
    result = udf(data, context)
    return (result)
  }
  else if(process == 'reduce_dimension') {
    dc = st_as_stars(data)
    dc = st_set_dimensions(dc, names = dimensions)
    # st_set_dimensions(x, "band", values = c(1,2,3,4,5,7), names = "band_number", point = TRUE))
    margin = dimensions[dimensions != dimension]
    dc = st_apply(dc, margin, function(x) { udf(x, context) })
    df = dc[[1]]
    return (df)
  }
  else {
    stop("Not implemented yet for R");
  }
}
