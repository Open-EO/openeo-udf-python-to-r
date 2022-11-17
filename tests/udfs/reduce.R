# This is the function that is passed to st_apply to be applied along a dimension
# This runs vectorized
udf = function(data, context) {
  print(context)
  apply(data, 1, max) * context
}