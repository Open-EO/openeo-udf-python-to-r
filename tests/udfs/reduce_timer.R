udf = function(data, context) {
  sink("/mnt/c/Dev/openeo-r-udf-experiments/output.txt")

  start_time <- Sys.time()
  data = do.call(pmax, as.data.frame(data))
  end_time <- Sys.time()
  time =  end_time - start_time

  print(time)
  sink()
  
  return(data)
}