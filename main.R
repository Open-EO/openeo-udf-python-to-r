library(stars)

main = function(data, dimensions, labels, file, process, dimension = NULL, context = NULL) {
  source(file)
  if(process == 'apply') {
    result = udf(data, context)
    return (result)
  }
  else if(process == 'reduce_dimension') {
    dc = stars(data, labels = labels)
    st_dimensions(data) <- dimensions
    st_apply(data, dimension, function(x) { udf(x, context) })
    df = as.data.frame(data)
    return (df)
  }
  else {
    stop("Not implemented yet for R");
  }
}
