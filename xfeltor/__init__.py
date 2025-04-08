# docstring displayed by help(xfeltor)
"""Feltor utility functions built on xarray

feltordataarray, feltordataset and load are automatically imported by xfeltor

    ds = open_feltordataset("feltor_output.nc")
    print(ds)       # print a summary of the file's contents
    ds["electrons"].feltor.animate2D( x="x", y="y")
    ds["electrons"].isel(y=100).feltor.animate1D(animate_over="time")
    ds.feltor.animate_list(
        variables=[
            ds["electrons"],
            ds["ions"].isel(y=100),
            ds["potential"],
            ds["vorticity"],
        ]
    )
"""
from .load import open_feltordataset
from .feltordataarray import FeltorDataArrayAccessor
from .feltordataset import FeltorDatasetAccessor

# Why is plotting not loaded? Should it be hidden from help(xfeltor)?
