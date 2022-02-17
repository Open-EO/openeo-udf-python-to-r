from udf_lib import execute_udf, create_dummy_cube
import time

# Data Cube config
dims = ['x', 'y', 't', 'b']
sizes = [740, 1000, 100, 3]
labels = {
    # x and y get generated automatically for now (todo: get from actual data)
    'x': None,
    'y': None,
    't': ['2021-01-06T05:19:03Z','2021-01-09T12:46:57Z','2021-01-09T13:39:54Z','2021-01-17T07:14:04Z','2021-01-24T05:41:00Z','2021-01-25T17:47:10Z','2021-01-28T09:52:43Z','2021-02-14T03:53:09Z','2021-03-01T16:36:40Z','2021-03-02T00:26:53Z','2021-03-13T22:10:14Z','2021-03-20T12:45:39Z','2021-03-22T00:16:53Z','2021-04-12T15:09:44Z','2021-04-30T02:23:52Z','2021-05-09T08:53:29Z','2021-05-27T18:00:33Z','2021-05-31T20:46:57Z','2021-06-04T17:29:23Z','2021-06-07T23:56:50Z','2021-06-08T14:04:34Z','2021-07-08T00:10:26Z','2021-07-10T16:32:32Z','2021-07-15T13:47:57Z','2021-07-19T22:38:12Z','2021-07-25T00:52:59Z','2021-08-19T08:01:07Z','2021-08-22T08:20:00Z','2021-08-22T20:35:09Z','2021-08-23T07:37:44Z','2021-08-24T01:07:16Z','2021-09-04T13:19:42Z','2021-09-07T14:48:32Z','2021-09-10T02:20:54Z','2021-09-15T03:59:30Z','2021-09-20T05:32:27Z','2021-10-09T09:29:12Z','2021-10-12T19:07:14Z','2021-10-20T16:09:52Z','2021-11-10T03:27:35Z','2021-11-17T06:41:29Z','2021-11-18T17:53:12Z','2021-11-19T07:04:41Z','2021-11-26T06:09:18Z','2021-11-27T02:23:13Z','2021-12-05T18:49:00Z','2021-12-06T03:23:48Z','2021-12-12T03:58:22Z','2021-12-12T18:40:36Z','2021-12-14T00:58:37Z','2021-12-17T15:50:38Z','2021-12-21T22:30:21Z','2021-12-21T22:52:37Z','2021-12-26T07:54:16Z','2022-01-01T17:20:07Z','2022-01-02T20:30:54Z','2022-01-08T07:42:07Z','2022-01-30T06:28:31Z','2022-01-30T18:43:56Z','2022-02-08T17:28:54Z','2022-02-16T06:12:07Z','2022-02-23T05:17:15Z','2022-03-09T11:54:28Z','2022-03-20T07:01:31Z','2022-03-27T07:05:13Z','2022-03-28T22:54:21Z','2022-04-05T03:53:34Z','2022-05-04T02:39:04Z','2022-05-05T21:43:20Z','2022-05-11T09:43:22Z','2022-05-16T01:30:25Z','2022-05-18T07:26:21Z','2022-05-22T01:58:58Z','2022-05-25T08:53:32Z','2022-06-06T17:34:48Z','2022-06-10T03:11:15Z','2022-06-22T02:40:58Z','2022-07-03T06:07:18Z','2022-07-09T23:48:32Z','2022-07-20T02:17:56Z','2022-07-25T00:42:00Z','2022-07-26T07:01:22Z','2022-07-29T03:56:47Z','2022-07-31T12:09:27Z','2022-08-06T01:00:20Z','2022-08-06T04:23:19Z','2022-08-16T05:38:21Z','2022-08-18T19:09:34Z','2022-08-20T15:56:10Z','2022-08-21T09:52:13Z','2022-09-05T05:31:52Z','2022-09-09T08:36:00Z','2022-09-18T18:28:20Z','2022-09-29T03:31:14Z','2022-10-06T19:36:48Z','2022-11-09T17:21:43Z','2022-11-15T06:34:40Z','2022-11-27T04:20:35Z','2022-12-06T04:49:40Z','2022-12-12T19:30:06Z'],
    'b': ['b1', 'b2', 'b3']
}
parallelize = True
chunk_size = 2000

def run(process, udf, dimension = None, context = None):
    # Prepare data
    data = create_dummy_cube(dims, sizes, labels)

    # Run UDF executor
    t1 = time.time() # Start benchmark
    result = execute_udf(process, udf, data, dimension = dimension, context = context, parallelize = parallelize, chunk_size = chunk_size)
    t2 = time.time() # End benchmark

    # Print result and benchmark
    print('  Time elapsed: %s' % (t2 - t1))
    #print(result)


print('apply')
run('apply', './udfs/apply.R', context = -1)

print('reduce_dimension')
run('reduce_dimension', './udfs/reduce.R', dimension = 'b', context = -1)

print('reduce_dimension bfast')
run('reduce_dimension', './udfs/reduce_bfast.R', dimension = 't')

# Benchmark for 100x100x10x3:
# apply: 1.5 sec
# reduce_dimension: 0.3 sec
# old variant for reduce_dimension: 233 sec
#
# Benchmark for 7400x1000x10x3 unparallelized:
# apply: ~ 20 sec
# reduce_dimension: ~ 25 sec
#
# Benchmark for 7400x1000x10x3 and a chunk size of 2000:
# apply: ~ 12 sec
# reduce_dimension: ~ 12 sec
