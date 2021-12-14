reducer <- function(data, context = NULL) {
  mean(data) * context
}