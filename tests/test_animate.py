import pytest
from matplotlib import pyplot as plt
import numpy as np
import xarray as xr
from animatplot.blocks import Pcolormesh, Line
import os


@pytest.fixture
def create_single_test_dataset() -> xr.Dataset:
    """create dataset for testung open_feltordataset()"""

    time = np.linspace(0, 4, 5)
    x = np.linspace(0, 4, 5)
    y = np.linspace(0, 4, 5)

    electrons = np.random.rand(5, 5, 5)

    return xr.Dataset(
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


class TestAnimate:
    """
    Set of tests to check whether animate1D() and animate2D() are running properly
    and PillowWriter is saving each animation correctly
    """

    def test_animate2D(self, create_single_test_dataset):
        ds = create_single_test_dataset
        save_dir = "."
        animation = ds["electrons"].feltor.animate2D(save_as="%s/testxy" % save_dir)

        assert len(animation.blocks) == 1
        block = animation.blocks[0]
        assert isinstance(block, Pcolormesh)

        assert block.ax.get_xlabel() == "x"
        assert block.ax.get_ylabel() == "y"

        plt.close()
        os.system("rm testxy.gif")

    def test_animate1D(self, create_single_test_dataset):
        ds = create_single_test_dataset

        save_dir = "."

        animation = (
            ds["electrons"].isel(y=2).feltor.animate1D(save_as="%s/test" % save_dir)
        )

        assert len(animation.blocks) == 1
        assert isinstance(animation.blocks[0], Line)

        plt.close()
        os.system("rm test.gif")

    def test_animate_list(self, create_single_test_dataset):
        ds = create_single_test_dataset

        animation = ds.feltor.animate_list([ds["electrons"], ds["electrons"].isel(y=1)])

        assert len(animation.blocks) == 2
        assert isinstance(animation.blocks[0], Pcolormesh)
        assert isinstance(animation.blocks[1], Line)

        plt.close()
