# Receives a multi-dimensional data frame(?) and you can run vectorized functions on a per pixel basis
# todo: could be a stars object in the future...
udf = function(data, context = NULL) {
  abs(data) * context
}