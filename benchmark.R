source('./executor.R')

dims = c('x', 'y', 't', 'b')
sizes = c(7400, 1000, 10, 3)
length = prod(sizes)
data = array(1:length, sizes)
labels = list(
    x = array(1:sizes[1]),
    y = array(1:sizes[2]),
    t = c('2020-01-01T00:00:00Z', '2020-01-02T00:00:00Z', '2020-01-03T00:00:00Z', '2020-01-04T00:00:00Z', '2020-01-05T00:00:00Z', '2020-01-06T00:00:00Z', '2020-01-07T00:00:00Z', '2020-01-08T00:00:00Z', '2020-01-09T00:00:00Z', '2020-01-10T00:00:00Z'),
    b = c('b1', 'b2', 'b3')
)

start_time <- Sys.time()

main(data, dims, labels, './udfs/reduce.R', process = 'reduce_dimension', dimension = 'b', context = -1)

print(Sys.time() - start_time)