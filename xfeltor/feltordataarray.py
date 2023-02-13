import xarray as xr
from xarray import register_dataarray_accessor
from .plotting import animate_pcolormesh, _create_norm, animate_line
from typing import Union, Optional
import matplotlib.pyplot as plt
import animatplot as amp
from functools import partial
from pprint import pformat as prettyformat

# The README says the plotting routines are from xBOUT. How far is that copy verbose and do we have to mention them here (License)?
# Or are the methods just named like in the xBOUT library?


# A mechanism to extend the xarray.DataArray class by registering a custom property
# https://docs.xarray.dev/en/stable/generated/xarray.register_dataarray_accessor.html
@register_dataarray_accessor("feltor")
class FeltorDataArrayAccessor:
    """Contains FELTOR-specific methods to use on FELTOR dataarrays opened by
    selecting a variable from a FELTOR dataset.

    This class extends xarray's DataArray class and can be used like:

    ds = xfeltor.open_feltordataset( file ) # create an xarray Dataset
    feltor_ds = ds['electrons'].feltor      # convert to FeltorDataArrayAccessor
    feltor_ds.animate2D(x="x", y="y")       # use its methods
    """

    def __init__(self, da):
        self.data: xr.Dataset = da

    # What is the advantage over simply using print(ds) ?
    def __str__(self):
        """String representation of the FeltorDataset.

        You can print a summary of the DataArray's properties via
        ds = xfeltor.open_feltordataset( file ) # create an xarray Dataset
        print(ds["electrons"])
        # or equivalent
        print(ds["electrons"].feltor)
        """
        styled = partial(prettyformat, indent=4, compact=False)
        return "<xfeltor.FeltorDataset>" + "\n{}\n".format(styled(self.data))

    def animate2D(
        self,
        animate_over: str = "time",
        x: str = None,
        y: str = None,
        animate: bool = True,
        axis_coords: Union[Optional[str], Optional[dict]] = None,
        fps: int = 10,
        save_as: Union[bool, str] = None,
        ax: plt.Axes = None,
        logscale: Union[bool, float] = None,
        **kwargs: dict,
    ) -> Union[amp.Animation, amp.blocks.Pcolormesh]:
        """
        Plots a color plot which is animated with time over the specified
        coordinate.
        Currently only supports 2D+1 data, which it plots with animatplot's
        wrapping of matplotlib's pcolormesh.
        See also the free function version of this method: xfeltor.plotting.animate_pcolormesh
        Parameters
        ----------
        animate_over : str, optional
            Dimension over which to animate, defaults to the time dimension
        x : str, optional
            Dimension to use on the x axis, default is None - then use the first spatial
            dimension of the data
        y : str, optional
            Dimension to use on the y axis, default is None - then use the second spatial
            dimension of the data
        animate : bool, optional
            If set to false, do not create the animation, just return the block or blocks
        axis_coords : None, str, dict
            Coordinates to use for axis labelling.
            - None: Use the dimension coordinate for each axis, if it exists.
            - "index": Use the integer index values.
            - dict: keys are dimension names, values set axis_coords for each axis
            separately. Values can be: None, "index", the name of a 1d variable or
            coordinate (which must have the dimension given by 'key'), or a 1d
            numpy array, dask array or DataArray whose length matches the length of
            the dimension given by 'key'.
            Only affects time coordinate for plots with poloidal_plot=True.
        fps : int, optional
            Frames per second of resulting gif
        save_as : True or str, optional
            If str is passed, save the animation as save_as+'.gif'.
            If True is passed, save the animation with a default name,
            '<variable name>_over_<animate_over>.gif'
        ax : matplotlib.pyplot.axes object, optional
            Axis on which to plot the gif
        logscale : bool or float, optional
            If True, default to a logarithmic color scale instead of a linear one.
            If a non-bool type is passed it is treated as a float used to set the linear
            threshold of a symmetric logarithmic scale as
            linthresh=min(abs(vmin),abs(vmax))*logscale, defaults to 1e-5 if True is
            passed.
        kwargs : dict, optional
            Additional keyword arguments are passed on to the plotting function
            (animatplot.blocks.Pcolormesh).
        Returns
        -------
        animation or blocks
            If animate==True, returns an animatplot.Animation object, otherwise
            returns a list of animatplot.blocks.Pcolormesh instances.
        """

        data = self.data
        variable = data.name
        n_dims = len(data.dims)

        if n_dims != 3:
            raise ValueError(
                f"Data passed has an unsupported number of dimensions ({n_dims})"
            )

        vmin = kwargs.pop("vmin") if "vmin" in kwargs else data.min().values
        vmax = kwargs.pop("vmax") if "vmax" in kwargs else data.max().values
        kwargs["norm"] = _create_norm(logscale, kwargs.get("norm", None), vmin, vmax)

        print(
            f"{variable} data passed has {n_dims} dimensions - will use "
            "animatplot.blocks.Pcolormesh()"
        )
        return animate_pcolormesh(
            data=data,
            animate_over=animate_over,
            x=x,
            y=y,
            animate=animate,
            axis_coords=axis_coords,
            fps=fps,
            save_as=save_as,
            ax=ax,
            **kwargs,
        )

    def animate1D(
        self,
        animate_over=None,
        animate=True,
        axis_coords=None,
        fps=10,
        save_as=None,
        ax=None,
        **kwargs,
    ):
        """
        Plots a line plot which is animated over time over the specified coordinate.
        Currently only supports 1D+1 data, which it plots with animatplot's wrapping of
        matplotlib's plot.
        See also the free function version of this method: xfeltor.plotting.animate_line
        Parameters
        ----------
        animate_over : str, optional
            Dimension over which to animate, defaults to the time dimension
        axis_coords : None, str, dict
            Coordinates to use for axis labelling.
            - None: Use the dimension coordinate for each axis, if it exists.
            - "index": Use the integer index values.
            - dict: keys are dimension names, values set axis_coords for each axis
            separately. Values can be: None, "index", the name of a 1d variable or
            coordinate (which must have the dimension given by 'key'), or a 1d
            numpy array, dask array or DataArray whose length matches the length of
            the dimension given by 'key'.
        fps : int, optional
            Frames per second of resulting gif
        save_as : True or str, optional
            If str is passed, save the animation as save_as+'.gif'.
            If True is passed, save the animation with a default name,
            '<variable name>_over_<animate_over>.gif'
        ax : Axes, optional
            A matplotlib axes instance to plot to. If None, create a new
            figure and axes, and plot to that
        aspect : str or None, optional
            Argument to set_aspect(), defaults to "auto"
        kwargs : dict, optional
            Additional keyword arguments are passed on to the plotting function
            (animatplot.blocks.Line).
        Returns
        -------
        animation or block
            If animate==True, returns an animatplot.Animation object, otherwise
            returns an animatplot.blocks.Line instance.
        """

        data = self.data
        n_dims = len(data.dims)

        assert n_dims == 2, "data must be two dimensional"

        variable = data.name
        print(
            f"{variable} data passed has {n_dims} dimensions - will use "
            "animatplot.blocks.Line()"
        )
        return animate_line(
            data=data,
            animate_over=animate_over,
            axis_coords=axis_coords,
            animate=animate,
            fps=fps,
            save_as=save_as,
            ax=ax,
            **kwargs,
        )
