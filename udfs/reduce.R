# This is the function that is passed to st_apply for reduction of a dimension

# vectorized
# document that data is a list and do.call might be useful
udf = function(data, context = NULL) {
  do.call(pmax, data) * context
}

# slow per pixel
# udf = function(data, context = NULL) {
#  max(data) * context
#}