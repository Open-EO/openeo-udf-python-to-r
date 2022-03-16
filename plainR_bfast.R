
# libs
library("stars")
library("bfast")
library("mapview")
library("dplyr")
library("ggplot2")
library("units")
library("lubridate")


# load input ndvi
pth_ndvi = "~/git_projects/openeo-udf-python-to-r/r4openeo_uc2_ndvi_mskd.nc"
ndvi = stars::read_ncdf(pth_ndvi)
st_crs(ndvi) = st_crs(32632)

# bfast function
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
duration # 5 mins
write_stars(obj = bfast_brks, dsn = "~/git_projects/openeo-udf-python-to-r/result_bfast_r.nc")


# compare to udf result
pth_udf_result = "~/git_projects/openeo-udf-python-to-r/result.nc"
bfast_brks_udf = stars::read_stars(pth_udf_result)
st_crs(bfast_brks_udf) = st_crs(32632)
bfast_brks_udf[[1]][bfast_brks_udf[[1]] < 2018] = NA


pth_r_result = "~/git_projects/openeo-udf-python-to-r/result_bfast_r.nc"
bfast_brks_r = stars::read_stars(pth_r_result)
bfast_brks_r[[1]][bfast_brks_r[[1]] < 2018] = NA

pth_eco4alps = ""
bfast_brks_eco = stars::read_stars()

plot(bfast_brks_eco)
plot(bfast_brks_r)
plot(bfast_brks_udf)


# look at trajectory
pnt = mapedit::drawFeatures(map = mapview(st_bbox(ndvi))) %>% st_transform(crs = st_crs(ndvi))
ndvi_ts = ndvi[pnt] %>% pull() %>% c()
ndvi_ts = data.frame(ndvi = ndvi_ts, 
                     dates = st_get_dimension_values(ndvi, "t"))

brk_r = bfast_brks_r[pnt] %>% pull() %>% c() %>% date_decimal()
brk_udf = bfast_brks_udf[pnt] %>% pull() %>% c() %>% date_decimal()


date <- ymd("2009-02-10")
decimal <- decimal_date(date)  # 2009.11
date_decimal(decimal) # "2009-02-10 UTC"


ggplot(ndvi_ts, aes(x=dates, y=ndvi)) +
  geom_line() + 
  geom_point() +
  geom_vline(xintercept = brk_udf) + 
  geom_vline(xintercept = brk_r)




