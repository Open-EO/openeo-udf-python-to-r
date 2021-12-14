import rpy2
import rpy2.robjects as robjects

import rpy2.robjects.packages as rpackages
utils = rpackages.importr('stars')


file = open('/R/stars.test.R',mode='r')

rCode= file.read()
robjects.r(rCode)

file.close()



