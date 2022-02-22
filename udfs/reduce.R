# This is the function that is passed to st_apply for reduction of a dimension
# This runs vectorized
udf = function(data, context) {
  do.call(pmax, data) * context
}