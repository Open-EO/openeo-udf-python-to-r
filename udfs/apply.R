# Receives a multi-dimensional stars object and you can run vectorized functions on a per pixel basis
udf = function(x, context = NULL) {
  abs(x) * context
}