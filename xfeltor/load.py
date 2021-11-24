import xarray as xr
import numpy as np
from typing import Union
import json


def open_feltordataset(
    datapath: str = "./*.nc",
    chunks: Union[int, dict] = None,
    restart_indices: bool = False,
    **kwargs: dict,
) -> xr.Dataset:
    """Load a dataset of FELTOR ouput files

    Parameters
    ----------
    datapath : str or (list or tuple of xr.Dataset), optional
        Path to the data to open. Can point to either a set of one or more *nc
        files.
    chunks : dict, optional
    restart_indices: bool, optional
        if True, dublicate time steps from restared runs are kept
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

    if restart_indices:
        return ds

    _, index = np.unique(ds["time"], return_index=True)

    # store inputfile data in ds.attrs
    tmp = ds.attrs["inputfile"]
    tmp = tmp.replace("\n", "")
    tmp = tmp.replace("\t", "")
    result = json.loads(tmp)

    for i in result:
        ds.attrs[i] = result[i]

    return ds.isel(time=index)
