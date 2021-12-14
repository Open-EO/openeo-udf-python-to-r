reducer <- function(data, context = NULL) {
  print(data)
  mean(data) * context
}