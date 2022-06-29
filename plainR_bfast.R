# execute the same function as the udf in plain R
# benchmark time
# compare results
#

# libs -------------------------------------------------------------------------
library("stars")
library("bfast")
library("mapview")
library("dplyr")
library("ggplot2")
library("units")
library("lubridate")

# load input ndvi --------------------------------------------------------------
pth_ndvi = "~/git_projects/openeo-udf-python-to-r/r4openeo_uc2_ndvi_mskd_small.nc"
ndvi = stars::read_ncdf(pth_ndvi)
st_crs(ndvi) = st_crs(32632)

# bfast function ---------------------------------------------------------------

# this is the fun used in py2r... trimmed to xarray data struct
# source(file = "~/git_projects/openeo-udf-python-to-r/udfs/reduce_bfast.R")

# this is the fun we based the udf upon...
spatial_bfm = function(pixels, dates, start_monitor = 2018, level = c(0.001, 0.001),
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

# apply function ---------------------------------------------------------------
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
duration # 5 mins

write_stars(obj = bfast_brks, dsn = "~/git_projects/openeo-udf-python-to-r/result_bfast_r_small.nc")


# compare to udf result --------------------------------------------------------

# udf result
pth_udf_result = "~/git_projects/openeo-udf-python-to-r/result_bfast_udf_small.nc"
bfast_brks_udf = stars::read_stars(pth_udf_result)
st_crs(bfast_brks_udf) = st_crs(32632)
bfast_brks_udf[[1]][bfast_brks_udf[[1]] < 2018] = NA

# plain r result
pth_r_result = "~/git_projects/openeo-udf-python-to-r/result_bfast_r_small.nc"
bfast_brks_r = stars::read_stars(pth_r_result)
bfast_brks_r[[1]][bfast_brks_r[[1]] < 2018] = NA

# eco4alps result (better input data)
pth_eco4alps = "/mnt/CEPH_PROJECTS/ECO4Alps/Forest_Disturbances/03_results/bfast/magn_2016_2020_start_2018_level_0.001.tif"
pth_eco4alps = "/mnt/CEPH_PROJECTS/ECO4Alps/Forest_Disturbances/03_results/bfast/brks_2016_2020_start_2018_level_0.001.tif"
bfast_brks_eco = stars::read_stars(pth_eco4alps)
#bfast_brks_eco[[1]][bfast_brks_eco[[1]] > -0.2] = NA
bfast_brks_eco[[1]][bfast_brks_eco[[1]] < 2018] = NA
bfast_brks_eco = st_warp(src = bfast_brks_eco, dest = bfast_brks_udf)

# show that plain r and udf results are identical
round(bfast_brks_r - bfast_brks_udf, 3) # to the 3rd decimal

# plot individual results
plot(bfast_brks_eco)
plot(bfast_brks_r)
plot(bfast_brks_udf)

# interactively plot results as overlay
mapview(bfast_brks_eco) + 
  mapview(bfast_brks_r) + 
  mapview(bfast_brks_udf)


# look at trajectory -----------------------------------------------------------

# get a point
pnt = mapedit::drawFeatures(map = mapview(bfast_brks_eco) + mapview(bfast_brks_udf)) %>% st_transform(st_crs(ndvi))
ndvi_ts = ndvi[pnt] %>% pull() %>% c()
ndvi_ts = data.frame(ndvi = ndvi_ts, 
                     ndvi_int = zoo::na.approx(ndvi_ts),
                     dates = st_get_dimension_values(ndvi, "t"))

# mapview(pnt) + mapview(bfast_brks_r) + mapview(bfast_brks_udf)

# extract the breakpoints from bfast
brk_r = bfast_brks_r[pnt] %>% pull() %>% c() %>% date_decimal()
brk_udf = bfast_brks_udf[pnt] %>% pull() %>% c() %>% date_decimal()
brk_eco = bfast_brks_eco[pnt] %>% pull() %>% c() %>% date_decimal()

# plot the ts
ggplot(ndvi_ts, aes(x=dates, y=ndvi)) +
  geom_point() + 
  geom_line() +
  geom_line(aes(x = dates, y = ndvi_int), col = "gray", lty = "dashed", alpha = 0.5) + 
  geom_vline(aes(xintercept = brk_udf, col = "udf"), alpha = 0.5) + 
  geom_vline(aes(xintercept = brk_r, col = "r"), alpha = 0.5) + 
  geom_vline(aes(xintercept = brk_eco, col = "eco4alps"), alpha = 0.5)




