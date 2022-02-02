# This is the function that is passed to st_apply for reduction of a dimension
udf = function(data, context = NULL) {
  mean(data) * context
}