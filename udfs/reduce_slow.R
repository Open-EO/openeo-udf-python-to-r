# This is the function that is passed to st_apply for reduction of a dimension
# This runs per "chunk"
udf_chunked = function(data, context) {
  max(data) * context
}