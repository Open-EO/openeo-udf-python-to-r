# remotes::install_github(repo="Open-EO/openeo-r-client", dependencies=TRUE, ref="develop")

# auth -------------------------------------------------------------------------
library(openeo)
library(stars)
library(mapview)
host = "https://openeo.cloud"
con = connect(host, provider = "egi")

# get vaja storm extent --------------------------------------------------------
# tst = read_stars("/mnt/CEPH_PROJECTS/ECO4Alps/Forest_Disturbances/03_results/bfast/magn_2016_2020_start_2018_level_0.001.tif")
# tst[[1]][tst[[1]] > -0.2] = NA
# mapview(tst) + mapview(bbox)
# mapedit::drawFeatures(map = mapview(tst))
# tst = tst[st_transform(st_as_sfc(bbox), crs = st_crs(tst))]
# length(tst[[1]])
# dim(tst)

# set extents --------------------------------------------------------

# big extent
# bbox = st_bbox(c(xmin = 11.50, xmax = 11.60, ymin = 46.40, ymax = 46.47), crs = st_crs(4326))
# mapview(bbox)
# spatial_extent = list("east" = 11.60,
#                       "north" = 46.47,
#                       "south" = 46.40,
#                       "west" = 11.50) # ~ 265*265 px = 70225 px

# mini extent
# bbox = st_bbox(c(xmin = 11.57189, xmax = 11.57729, ymin = 46.45701, ymax = 46.46135), crs = st_crs(4326))
# mapview(bbox) + mapview(tst)

# small extent
# bbox = st_bbox(c(xmin = 11.564, xmax = 11.577, ymin = 46.454, ymax = 46.461), crs = st_crs(4326))
# mapview(bbox) + mapview(tst)



spatial_extent = list("west" = 11.564,
                      "east" = 11.577,
                      "south" = 46.454,
                      "north" = 46.461) # ~ 35*26px = 910 px

temporal_extent = list("2016-01-01", "2020-01-01") # 5 yrs, 6 daily = 365*5/6 = 300 ts
collection = "SENTINEL2_L2A" # "boa_sentinel_2" # "SENTINEL2_L2A"
bands = c("B04", "B08", "CLD")
format = "NETCDF"

title = "r4openeo_uc2_ndvi_bfast_mskd3"
out_dir = "/home/pzellner@eurac.edu/"

# process graph ----------------------------------------------------------------
p = processes()

s2 = p$load_collection(bands = bands,
                       id = collection,
                       spatial_extent = spatial_extent,
                       temporal_extent = temporal_extent)
s2_cld = p$filter_bands(bands = list("CLD"),
                        data = s2, wavelengths = list())
s2_bnd = p$filter_bands(bands = list("B04", "B08"),
                        data = s2, wavelengths = list())
s2_ndvi = p$ndvi(data = s2_bnd, nir = "B08", red = "B04")
s2_masked = p$mask(data = s2_ndvi, mask = s2_cld)

# s2_linint = p$apply_dimension(data = s2_masked, dimension = "t", process = function(x, context){
#   p$array_interpolate_linear(x)
# })

s2_result = p$save_result(data = s2_masked, format = "NETCDF")

# Batch
job = create_job(graph=s2_result, title = title)
start_job(job = job)

describe_job(job = job)
list_results(job = job)


dwnld = download_results(job = job, folder = paste0(out_dir, title))

res = stars::read_stars(dwnld[[1]])
res = stars::read_stars("~/r4openeo_uc2_ndvi_mskd.ncdf/r4openeo_uc2_ndvi_mskd.nc")
plot(res)
mapview(st_bbox(res)) + mapview(bbox)
file.size(dwnld[[1]])/1000000
res1 = res[st_transform(st_as_sfc(bbox), crs = st_crs(res))]
res[1,50,50,] %>% dplyr::pull() %>% c() %>% plot()
res
st_crs(res)



