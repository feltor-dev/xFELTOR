import xarray as xr
import numpy as np
from xfeltor import open_feltordataset


def create_single_test_dataset() -> None:
    """create dataset for testung open_feltordataset()"""

    time = np.linspace(0, 4, 5)
    x = np.linspace(0, 4, 5)
    y = np.linspace(0, 4, 5)

    electrons = np.random.rand(5, 5, 5)

    ds = xr.Dataset(
        data_vars=dict(
            electrons=(["x", "y", "time"], electrons),
        ),
        coords=dict(
            time=time,
            x=x,
            y=y,
        ),
        attrs=dict(inputfile='{\n\t"Nx" : 5,\n\t"Nx_out" : 5,\n\t"maxout" : 5}\n'),
    )
    ds.to_netcdf("test_single_dataset.nc")
    return


def create_two_test_dataset() -> None:
    """create dataset for testung open_feltordataset()"""

    time = np.linspace(0, 4, 5)
    x = np.linspace(0, 4, 5)
    y = np.linspace(0, 4, 5)

    electrons = np.random.rand(5, 5, 5)

    ds = xr.Dataset(
        data_vars=dict(
            electrons=(["x", "y", "time"], electrons),
        ),
        coords=dict(
            time=time,
            x=x,
            y=y,
        ),
        attrs=dict(inputfile='{\n\t"Nx" : 5,\n\t"Nx_out" : 5,\n\t"maxout" : 5}\n'),
    )
    ds.to_netcdf("test_multiple_dataset_1.nc")

    time = np.linspace(3, 7, 5)

    electrons = np.random.rand(5, 5, 5)

    ds = xr.Dataset(
        data_vars=dict(
            electrons=(["x", "y", "time"], electrons),
        ),
        coords=dict(
            time=time,
            x=x,
            y=y,
        ),
        attrs=dict(inputfile='{\n\t"Nx" : 5,\n\t"Nx_out" : 5,\n\t"maxout" : 5}\n'),
    )
    ds.to_netcdf("test_multiple_dataset_2.nc")
    return


def test_single_load():
    """test whether singel dataset is loaded"""
    create_single_test_dataset()
    assert open_feltordataset("test_single_dataset.nc")


def test_two_load():
    """test whether multiple datasets are loaded and concatenated correctly"""
    create_two_test_dataset()
    ds = open_feltordataset("test_multiple_dataset*.nc")
    assert list(ds.time.values) == [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]


def test_attributes():
    """test wheteher input file parameters are stored corretly as attributes"""
    create_single_test_dataset()
    ds = open_feltordataset("test_single_dataset.nc")
    assert ds.attrs["Nx"] == 5
    assert ds.attrs["Nx_out"] == 5
    assert ds.attrs["maxout"] == 5
