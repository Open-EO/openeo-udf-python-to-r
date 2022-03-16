suppressWarnings(suppressMessages(library("bfast", quietly = T)))

udf_chunked = function(data, context) {
  pixels = unlist(data) # this are 150000 pixels right now. why? Should be 500
  dates = names(data)

  val = if(is.null(context) || is.null(context$val)) "breakpoint" else context$val
  level = if(is.null(context) || is.null(context$level) || length(context$val) == 0) c(0.001, 0.001) else context$level

  # error handling
  stopifnot(length(pixels) == length(dates)) 
  stopifnot(val %in% c("breakpoint", "magnitude"))

  # create ts object for bfast
  lsts = bfastts(pixels, dates, type = c("irregular"))

  # make sure there are enough observations
  if (sum(!is.na(lsts)) < 100){
    return(NA)
  }
 
  # run bfast
  res = bfastmonitor(lsts, 
                     context$start_monitor, 
                     formula = response~harmon, 
                     order = 1, 
                     history = "all", 
                     level = level,
                     verbose = F)[[val]]
  if(is.na(res)){
    return(0)
  }
  return(res) 
}

udf_setup = function(context) {
  if (!require("bfast")) {
    install.packages("bfast", quiet = TRUE)
  }
}