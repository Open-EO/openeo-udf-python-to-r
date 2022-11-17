udf = function(data, context) {
  do.call(pmax, as.data.frame(data))
}