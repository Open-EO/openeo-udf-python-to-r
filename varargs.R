# script to show how variable number of arguments ... can be used
# in an R udf, using the fast path (one function call receiving
# entire bands, rather than one function call per pixel)

# following https://github.com/r-spatial/stars/issues/390
library("stars")

file = system.file("tif/L7_ETMs.tif", package = "stars")
ras = read_stars(file, proxy = FALSE)

# not sure if ndvi2 is correct
ndvi2 = function(x1, x2, x3, x4, x5, x6) { (x4-x3)/(x4+x3) }
st_apply(ras, c("x", "y"), ndvi2)

# can we write ndvi2 without listing all arguments, using ... ?
fast_min = function(x1, x2, ...) { 
		args = append(list(x1, x2), list(...))
		do.call(pmin, args) # pmin is a vectorized min
}

min1 = st_apply(ras, c("x", "y"), fast_min)

# check with not-so-fast-min:
fast_min = min # to make sure that the name of the attribute in output matches
min2 = st_apply(ras, c("x", "y"), fast_min)

all.equal(min1, min2)

# can we get the difference between band 15 and 16?
# create an 18-band stars object:
ras18 = c(ras,ras,ras, along = "band")

my_diff = function(x1, x2, ...) { 
		args = append(list(x1, x2), list(...))
		args[[15]] - args[[16]]
}

(dif1 = st_apply(ras18, c("x", "y"), my_diff))

# verify
my_diff = function(x) x[15]-x[16] # slow
dif2 = st_apply(ras18, c("x", "y"), my_diff)
all.equal(dif1, dif2)
