import xarray as xr
import numpy as np


def open_feltordataset(
    datapath="./*.nc",
    chunks=None,
    **kwargs,
):
    """Load a dataset of FELTOR ouput files

    Parameters
    ----------
    datapath : str or (list or tuple of xr.Dataset), optional
        Path to the data to open. Can point to either a set of one or more *nc
        files.
    chunks : dict, optional
    kwargs : optional
        Keyword arguments are passed down to `xarray.open_mfdataset`, which in
        turn passes extra kwargs down to `xarray.open_dataset`.
    """
    if chunks is None:
        chunks = {}

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
