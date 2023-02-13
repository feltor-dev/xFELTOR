import warnings
from matplotlib.animation import PillowWriter
import matplotlib.pyplot as plt
import xarray as xr
from functools import partial
from pprint import pformat as prettyformat
import animatplot as amp
import numpy as np
from .plotting import _add_controls


# A mechanism to extend the xarray.Dataset class by registering a custom property
# https://docs.xarray.dev/en/stable/internals/extending-xarray.html
@xr.register_dataset_accessor("feltor")
class FeltorDatasetAccessor:
    """Contains FELTOR-specific methods to use on FELTOR datasets opened using
    `open_feltordataset()`.

    This class extends xarray's Dataset class and can be used like:

    ds = xfeltor.open_feltordataset( file ) # create an xarray Dataset
    feltor_ds = ds.feltor                   # convert to a FeltorDatasetAccessor
    feltor_ds.animate_list(
        variables = [
            ds["electrons"],
            ds["ions"].isel(y=100),
            ds["potential"],
            ds["vorticity"],]
    )                                       # use its methods

    """

    def __init__(self, ds):
        self.data = ds

    # What is the advantage over simply using print(ds) ?
    def __str__(self):
        """String representation of the FeltorDataset.

        You can print a summary of the Dataset's content via
        ds = xfeltor.open_feltordataset( file ) # create an xarray Dataset
        print(ds)                               # print summary of its content

        Sometimes, you do not want the "inputfile" attribute to be printed.
        Then use:
        print(ds.feltor)
        # same as above but will not print the "inputfile" attribute
        """
        ds = self.data.copy()  # a shallow copy ...
        del ds.attrs["inputfile"]
        styled = partial(prettyformat, indent=4, compact=False)
        return "<xfeltor.FeltorDataset>" + "\n{}\n".format(styled(ds))

    def animate_list(
        self,
        variables,
        nrows=None,
        ncols=None,
        subplots_adjust=None,
        animate_over=None,
        show=False,
        save_as=None,
        tight_layout=True,
        controls="both",
        fps=100,
        **kwargs,
    ):
        """
        Animates list of FeltorDataArrays
        Parameters
        ----------
        variables : list of BoutDataArray
            Both 2d and 3d variables are valid
        nrows : int, optional
            Specify the number of rows of plots
        ncols : int, optional
            Specify the number of columns of plots
        subplots_adjust : dict, optional
            Arguments passed to fig.subplots_adjust()()
        animate_over : str, optional
            Dimension over which to animate, defaults to the time dimension
        show : bool, optional
            Call pyplot.show() to display the animation
        save_as : str, optional
            If passed, a gif is created with this filename
        tight_layout : bool or dict, optional
            If set to False, don't call tight_layout() on the figure.
            If a dict is passed, the dict entries are passed as arguments to
            tight_layout()
        controls : string or None, default "both"
            By default, add both the timeline and play/pause toggle to the animation. If
            "timeline" is passed add only the timeline, if "toggle" is passed add only
            the play/pause toggle. If None or an empty string is passed, add neither.
        fps : float, optional
            Indicates the number of frames per second to play
        **kwargs : dict, optional
            Additional keyword arguments are passed on to each animation function
        """

        if animate_over is None:
            animate_over = "time"
        nvars = len(variables)

        if nrows is None and ncols is None:
            ncols = int(np.ceil(np.sqrt(nvars)))
            nrows = int(np.ceil(nvars / ncols))
        elif nrows is None:
            nrows = int(np.ceil(nvars / ncols))
        elif ncols is None:
            ncols = int(np.ceil(nvars / nrows))
        elif nrows * ncols < nvars:
            raise ValueError("Not enough rows*columns to fit all variables")

        fig, axes = plt.subplots(nrows, ncols, squeeze=False)
        axes = axes.flatten()

        ncells = nrows * ncols

        if nvars < ncells:
            for index in range(ncells - nvars):
                fig.delaxes(axes[ncells - index - 1])

        if subplots_adjust is not None:
            fig.subplots_adjust(**subplots_adjust)

        line_blocks = []
        for v, ax in zip(variables, axes):
            assert len(v.dims) in [
                2,
                3,
            ], f"{v.name} variabel has neither 2 or 3 dimensions and can't be animated"

            if len(v.dims) == 3:
                line_blocks.append(
                    v.T.feltor.animate2D(
                        animate_over="time", animate=False, ax=ax, **kwargs
                    )
                )
            elif len(v.dims) == 2:
                line_blocks.append(
                    v.feltor.animate1D(
                        animate_over="time", animate=False, ax=ax, **kwargs
                    )
                )

        timeline = amp.Timeline(self.data["time"], fps=fps)
        anim = amp.Animation(line_blocks, timeline)

        if tight_layout:
            if subplots_adjust is not None:
                warnings.warn(
                    "tight_layout argument to animate_list() is True, but "
                    "subplots_adjust argument is not None. subplots_adjust "
                    "is being ignored."
                )
            if not isinstance(tight_layout, dict):
                tight_layout = {}
            fig.tight_layout(**tight_layout)

        _add_controls(anim, controls, "time")

        if save_as is not None:
            anim.save(save_as + ".gif", writer=PillowWriter(fps=fps))

        if show:
            plt.show()

        return anim
