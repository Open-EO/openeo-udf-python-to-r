
# libs
library("stars")
library("bfast")
library("mapview")

# load input ndvi
pth_ndvi = "~/git_projects/openeo-udf-python-to-r/r4openeo_uc2_ndvi_mskd.nc"
ndvi = stars::read_ncdf(pth_ndvi)
st_crs(ndvi) = st_crs(32632)

# bfast function
spatial_bfm = function(pixels, dates, start_monitor = 2018, level = c(0.05, 0.05), 
                       val = "breakpoint") {
  # error handling
  stopifnot(length(pixels) == length(dates))
  stopifnot(val %in% c("breakpoint", "magnitude"))
  
  # create ts object for bfast
  lsts = bfastts(pixels, dates, type = c("irregular"))
  
  # make sure there are enough observations
  if (sum(!is.na(lsts)) < 100){
    return(NA)
  }
  
  # run bfast and return the selected value into the raster
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
  return(res)
}

# apply function
level = c(0.001, 0.001)
start_monitor = 2018
dates = st_get_dimension_values(ndvi, "t")

a = Sys.time()
bfast_brks = st_apply(X = ndvi, MARGIN = c("x", "y"), function(x){
  spatial_bfm(pixels = x, 
              dates = dates, 
              start_monitor = start_monitor, 
              level = level, val = "breakpoint")
})
b = Sys.time()
duration = b-a
duration


# compare to udf result
pth_udf_result = "~/git_projects/openeo-udf-python-to-r/result.nc"
bfast_brks_udf = stars::read_stars(pth_udf_result)
st_crs(bfast_brks_udf) = st_crs(32632)
plot(bfast_brks_udf)












