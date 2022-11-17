# This is the function that is passed to st_apply to be applied along a dimension

udf_chunked = function(data, context) {
  filter(data, rep(1/5, 5))
}