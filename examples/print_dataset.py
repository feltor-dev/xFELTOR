from xfeltor import open_feltordataset
from functools import partial
from pprint import pformat as prettyformat

ds = open_feltordataset("output.nc")

print(ds.feltor)
