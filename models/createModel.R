
# Load the Libraries
library("tibble")
library("dplyr")
library("stars")
library("tidyr")
library("caret")
library("randomForest")
library("tictoc")


# Predictors --------------------------------------------------------------
s2data<- readRDS("/mnt/CEPH_PROJECTS/SAO/SENTINEL-2/s2_processing/Output/S2_Archive_complete.rds") %>% 
  dplyr::filter(Tile=="T32TPS") %>% 
  na.omit

data<-s2data[128,]$ESA_L2A
data.read<-read_stars(data)


# Target ------------------------------------------------------------------
target<-read_stars("/mnt/CEPH_PROJECTS/SAO/ForestCanopy/01_Data/CORINE_2018_250m_Raster/DATA/U2018_CLC2018_V2020_20u1.tif")
extent<-st_bbox(data.read) %>% st_as_sfc %>% st_transform(.,st_crs(target))
target.crp<-st_crop(target,extent) %>% st_as_stars()


# Samples -----------------------------------------------------------------
set.seed(1)
rpts<- st_sample(extent,100) %>% st_as_sf() %>% mutate(ID=1:nrow(.))
rptsP<-st_transform(rpts,st_crs(data.read))


# Extraction --------------------------------------------------------------
tvals<-st_extract(target,st_coordinates(rpts))
pvals<-st_extract(data.read,st_coordinates(rptsP))
dataset<-cbind(tvals,pvals) %>% as_tibble() %>% setNames(c("Target","B02","B03","B04","B08"))


# Model -------------------------------------------------------------------
tic()
rf1<-train(Target~.,
           data=dataset,
           method="rf",
           ntree=100)
toc()

saveRDS(rf1,"models/TestModel1.rds")


