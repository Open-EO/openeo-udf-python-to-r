udf = function(data, context) {
  sink("/mnt/c/Dev/openeo-r-udf-experiments/output.txt")

  start_time <- Sys.time()
  data = filter(t(data), rep(1/5, 5))
  end_time <- Sys.time()
  time =  end_time - start_time

  print(time)
  sink()
  
  return(data)
}