udf = function(data, context = NULL) {
  pixels = unlist(data)
  dates = names(data)
  start_monitor = if(is.null(context) || is.null(context$start_monitor)) 2018 else context$start_monitor
  val = if(is.null(context) || is.null(context$val)) "breakpoint" else context$val
  level = if(is.null(context) || is.null(context$level) || length(context$val) == 0) c(0.05, 0.05) else context$level

  # create ts object for bfast
  lsts = bfast::bfastts(pixels, dates, type = c("irregular"))
 
  # run bfast
  res = bfast::bfastmonitor(lsts, 
                     start_monitor, 
                     formula = response~harmon, 
                     order = 1, 
                     history = "all", 
                     level = level,
                     verbose = F)[[val]]
  if(is.na(res)){
    return(0)
  }
  return(res * context) 
}


# unnecessary stuff removed from fun
  #error handling
  #stopifnot(length(pixels) == length(dates)) 
  #stopifnot(val %in% c("breakpoint", "magnitude"))
  
  # make sure there are enough observations
  #if (sum(!is.na(lsts)) < 100){
  #  return(NA)
  #}
