import xarray as xr
import numpy as np
from typing import Union
import json


def open_feltordataset(
    datapath: str = "./*.nc",
    chunks: Union[int, dict] = None,
    restart_indices: bool = False,
    inputfile_as_attr: bool = True,
    **kwargs: dict,
) -> xr.Dataset:
    """Loads FELTOR output into one xarray Dataset. Can load either a single
    output file or multiple coherent files for restarted simulations.

    Parameters
    ----------
    datapath : str or (list or tuple of xr.Dataset), optional
        Path to the data to open. Can point to either a set of one or more *nc
        files.
    chunks : dict, optional
        Dictionary with keys given by dimension names and values given by chunk sizes.
        By default, chunks will be chosen to load entire input files into memory at once.
        This has a major impact on performance: please see the full documentation for more details:
        http://xarray.pydata.org/en/stable/user-guide/dask.html#chunking-and-performance
    restart_indices: bool, optional
        if True, duplicate time steps from restared runs are kept
    inputfile_as_attr: bool, optional
        if True, read in the global attribute "inputfile" as a json string and store its variables
            as attributes of the xarray Dataset
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
    if inputfile_as_attr:
        input_variables = json.loads(ds.attrs["inputfile"])

        for i in input_variables:
            ds.attrs[i] = input_variables[i]

    return ds.isel(time=index)
