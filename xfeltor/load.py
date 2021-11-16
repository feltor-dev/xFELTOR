import xarray as xr
import numpy as np


def open_feltordataset(
    datapath="./*.nc",
    chunks=None,
    **kwargs,
):
    ds = xr.open_mfdataset(
        datapath,
        chunks=chunks,
        combine="nested",
        concat_dim="time",
        decode_times=False,
        join="outer",
        **kwargs,
    )
    _, index = np.unique(ds["time"], return_index=True)
    return ds.isel(time=index)
