import xarray as xr


def open_feltordataset(datapath="./*.nc",):
    return xr.open_dataset(datapath, decode_times=False)
