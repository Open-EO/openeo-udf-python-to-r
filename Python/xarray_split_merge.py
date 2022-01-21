import xarray as xr
import numpy as np

## Create a xArray.DataArray without chunks
npData = np.random.rand(1000,100,3)
xrData = xr.DataArray(npData, dims = ['x', 'y', 'b'], coords = {'x': np.arange(npData.shape[0]), 'y': np.arange(npData.shape[1]), 'b': ['b1', 'b2', 'b3']})
xrData_chunked = xrData.chunk({'x':100,'y':100,'b':-1})

## Split the data into 4 sub-blocks
xrData_part1 = xrData.loc[{'x':slice(xrData.x[0],xrData.x[499]),'y':slice(xrData.y[0],xrData.y[49])}]
xrData_part2 = xrData.loc[{'x':slice(xrData.x[0],xrData.x[499]),'y':slice(xrData.y[50],xrData.y[99])}]
xrData_part3 = xrData.loc[{'x':slice(xrData.x[500],xrData.x[999]),'y':slice(xrData.y[50],xrData.y[99])}]
xrData_part4 = xrData.loc[{'x':slice(xrData.x[500],xrData.x[999]),'y':slice(xrData.y[0],xrData.y[49])}]

print("Original data shape: ",xrData.shape)
print("Sub parts shape:")
print(xrData_part1.shape)
print(xrData_part2.shape)
print(xrData_part3.shape)
print(xrData_part4.shape)

## Perform any operation on the data

## Recombine the data
xrData_recombined = xr.combine_by_coords(data_objects=[xrData_part1,xrData_part2,xrData_part3,xrData_part4], compat='no_conflicts', data_vars='all', coords='different', join='outer', combine_attrs='no_conflicts', datasets=None)

print("Are the original and recombined DataArray equal?",(xrData_recombined == xrData).all().values)