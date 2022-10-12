# This is the function that is passed to st_apply to be applied along a dimension

udf_chunked = function(data, context) {
  avg_data = c()
  for (i in 1:length(data)) {
    start = max(1, i-context)
    end = min(length(data), i+context)
    print(c(start, end))
    avg_data[i] = mean(data[start:end])
  }
  return(avg_data)
}

# udf = function(data, context) {
#   ...
# }