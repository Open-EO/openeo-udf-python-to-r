import time

import rpy2
import rpy2.robjects as robjects

import rpy2.robjects.packages as rpackages
stars = rpackages.importr('stars')

# Read R Code
file = open('../R/read_stars.R', mode='r')
rCode = file.read()
file.close()

# Run R code
t1 = time.time() # Start benchmark
rObject.r(rCode)
t2 = time.time() # End benchmark

# Print benchmark
print("Time elapsed: %s" % (t2 - t1))
