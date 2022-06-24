# plotCLC
# Transformation necessary as they are discrete classes
library("raster")
library("ggplot")

r<-raster("models/starsprediction2.nc")
r2<-as.data.frame(r,xy=TRUE) %>% setNames(c("x","y","Class"))
ggplot(r2,aes(x,y,fill=Class))+geom_raster()+theme_bw()
