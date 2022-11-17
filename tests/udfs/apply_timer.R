# Receives a multi-dimensional stars object and you can run vectorized functions on a per pixel basis
udf = function(x, context) {
  sink("/mnt/c/Dev/openeo-r-udf-experiments/output.txt")

  start_time <- Sys.time()
  x = x * -1
  end_time <- Sys.time()
  time =  end_time - start_time

  print(time)
  sink()
  
  return(x)
}