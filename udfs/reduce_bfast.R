# library(bfast)

udf = function(pixels, dates, start_monitor = 2018, level = c(0.05, 0.05), val = "breakpoint", context = NULL) {
  # create ts object for bfast
  lsts = bfastts(pixels, dates, type = c("irregular"))
 
  # run bfast
  res = bfastmonitor(lsts, 
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
