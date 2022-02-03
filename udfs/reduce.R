# This is the function that is passed to st_apply for reduction of a dimension

# vectorized
udf = function(a, b, c, context = NULL) {
  pmax(a,b,c) * context
}

# slow per pixel
# udf = function(data, context = NULL) {
#  max(data) * context
#}