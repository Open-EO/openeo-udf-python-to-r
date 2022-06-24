udf = function(data,context){

  # read a machine learning model done with caret
  url1      <- 'https://github.com/Open-EO/openeo-udf-python-to-r/blob/UC1_ML/models/TestModel1.rds?raw=True'
  getModel  <- readRDS(gzcon(url(url1)))
  
  print(paste(getModel$modelInfo$label,"- Model Loaded successfully"))
  
  # saveRDS(data,"models/testdata.rds")

  # convert the data xarray to raster
  data<-readRDS("models/testdata.rds")
  if(class(data)=="stars") print("Data converted to Stars object") else stop()

  # STARS Package prediction
  data.split<-split(data,"var")
  names(data.split)<-caret::predictors(getModel)
  prediction.stars <-predict(data.split,getModel)
  
  # RASTER package prediction
  #s<-data[[1]]
  #st<-raster::brick(s)
  #names(st)=caret::predictors(getModel)
  #prediction.raster<-predict(st,getModel)
  print("Prediction Done")
  write_stars(prediction.stars,"models/starsprediction2.nc")

  # Return the raster
  return(prediction.stars)
}
