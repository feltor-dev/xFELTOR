import matplotlib as mpl
import matplotlib.pyplot as plt
import warnings
from matplotlib.animation import PillowWriter
import numpy as np
import animatplot as amp


def _add_controls(anim, controls, t_label):
    if controls == "both":
        # Add both time slider and play/pause toggle
        anim.controls(timeline_slider_args={"text": t_label})
    elif controls == "timeline":
        # Add time slider
        anim.timeline_slider(text=t_label)
    elif controls == "toggle":
        # Add play/pause toggle
        anim.toggle()
    elif controls is not None and controls != "":
        raise ValueError(f"Unrecognised value for controls={controls}")


def _parse_coord_option(coord, axis_coords, da):
    if isinstance(axis_coords, dict):
        option_value = axis_coords.get(coord, None)
    else:
        option_value = axis_coords

    if option_value is None:
        return _extracted_from__parse_coord_option_8(da, coord)
    elif option_value == "index":
        return np.arange(da.sizes[coord]), f"{coord} index"
    elif isinstance(option_value, str):
        return _extracted_from__parse_coord_option_8(da, option_value)
    else:
        return option_value, None


def _normalise_time_coord(time_values):
    """amp.Timeline() does not do a good job of displaying time values that are
    very small (they get rounded to zero).

    This function scales the time values by a power of 10 to get nice
    values and modifies the units by the scale factor.
    """
    tmax = time_values.max()
    if tmax < 1.0e-2 or tmax > 1.0e6:
        scale_pow = int(np.floor(np.log10(tmax)))
        scale_factor = 10**scale_pow
        time_values = time_values / scale_factor
        suffix = f"e{scale_pow}"
    else:
        suffix = ""

    return time_values, suffix


# TODO Rename this here and in `_parse_coord_option`
def _extracted_from__parse_coord_option_8(da, arg1):
    c = da[arg1]
    label = c.long_name if "long_name" in c.attrs else arg1
    if "units" in c.attrs:
        label = label + f" [{c.units}]"
    return c, label


def _create_norm(logscale, norm, vmin, vmax):
    if logscale:
        if norm is not None:
            raise ValueError(
                "norm and logscale cannot both be passed at the same time."
            )
        if vmin * vmax > 0:
            # vmin and vmax have the same sign, so can use standard log-scale
            norm = mpl.colors.LogNorm(vmin=vmin, vmax=vmax)
        else:
            # vmin and vmax have opposite signs, so use symmetrical logarithmic scale
            linear_scale = logscale if not isinstance(logscale, bool) else 1.0e-5
            linear_threshold = min(abs(vmin), abs(vmax)) * linear_scale
            norm = mpl.colors.SymLogNorm(linear_threshold, vmin=vmin, vmax=vmax)
    elif norm is None:
        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

    return norm


def animate_pcolormesh(
    data,
    animate_over="time",
    x=None,
    y=None,
    animate=True,
    axis_coords=None,
    vmin=None,
    vmax=None,
    vsymmetric=False,
    logscale=False,
    fps=10,
    save_as=None,
    ax=None,
    cax=None,
    aspect="auto",
    extend=None,
    controls="both",
    **kwargs,
):
    """
    Plots a color plot which is animated with time over the specified
    coordinate.
    Currently only supports 2D+1 data, which it plots with animatplotlib's
    wrapping of matplotlib's pcolormesh.
    Parameters
    ----------
    data : xarray.DataArray
    animate_over : str, optional
        Dimension over which to animate, defaults to the time dimension
    x : str, optional
        Dimension to use on the x axis, default is None - then use the first spatial
        dimension of the data
    y : str, optional
        Dimension to use on the y axis, default is None - then use the second spatial
        dimension of the data
    animate : bool, optional
        If set to false, do not create the animation, just return the block
    axis_coords : None, str, dict
        Coordinates to use for axis labelling.
        - None: Use the dimension coordinate for each axis, if it exists.
        - "index": Use the integer index values.
        - dict: keys are dimension names, values set axis_coords for each axis
          separately. Values can be: None, "index", the name of a 1d variable or
          coordinate (which must have the dimension given by 'key'), or a 1d
          numpy array, dask array or DataArray whose length matches the length of
          the dimension given by 'key'.
    vmin : float, optional
        Minimum value to use for colorbar. Default is to use minimum value of
        data across whole timeseries.
    vmax : float, optional
        Maximum value to use for colorbar. Default is to use maximum value of
        data across whole timeseries.
    vsymmetric : bool, optional
        If set to true, make the color-scale symmetric
    logscale : bool or float, optional
        If True, default to a logarithmic color scale instead of a linear one.
        If a non-bool type is passed it is treated as a float used to set the linear
        threshold of a symmetric logarithmic scale as
        linthresh=min(abs(vmin),abs(vmax))*logscale, defaults to 1e-5 if True is
        passed.
    fps : int, optional
        Frames per second of resulting gif
    save_as : True or str, optional
        If str is passed, save the animation as save_as+'.gif'.
        If True is passed, save the animation with a default name,
        '<variable name>_over_<animate_over>.gif'
    ax : Axes, optional
        A matplotlib axes instance to plot to. If None, create a new
        figure and axes, and plot to that
    cax : Axes, optional
        Matplotlib axes instance where the colorbar will be plotted. If None, the default
        position created by matplotlab.figure.Figure.colorbar() will be used.
    aspect : str or None, optional
        Argument to set_aspect(), defaults to "auto"
    extend : str or None, optional
        Passed to fig.colorbar()
    controls : string or None, default "both"
        By default, add both the timeline and play/pause toggle to the animation. If
        "timeline" is passed add only the timeline, if "toggle" is passed add only the
        play/pause toggle. If None or an empty string is passed, add neither.
    kwargs : dict, optional
        Additional keyword arguments are passed on to the animation function
        animatplot.blocks.Pcolormesh
    Returns
    -------
    animation or block
        If animate==True, returns an animatplot.Animation object, otherwise
        returns an animatplot.blocks.Pcolormesh instance.
    """

    variable = data.name

    # Check plot is the right orientation
    spatial_dims = list(data.dims)

    if len(data.dims) != 3:
        raise ValueError("Data passed to animate_imshow must be 3-dimensional")

    try:
        spatial_dims.remove(animate_over)
    except ValueError:
        raise ValueError(
            f"Dimension animate_over={animate_over} is not present in the data"
        )

    if x is None and y is None:
        x, y = spatial_dims
    elif x is None:
        try:
            spatial_dims.remove(y)
        except ValueError:
            raise ValueError(f"Dimension {y} is not present in the data")
        x = spatial_dims[0]
    elif y is None:
        try:
            spatial_dims.remove(x)
        except ValueError:
            raise ValueError(f"Dimension {x} is not present in the data")
        y = spatial_dims[0]

    if extend is None:
        # Replicate default for older matplotlib that does not handle extend=None
        # matplotlib-3.3 definitely does not need this. Not sure about 3.0, 3.1, 3.2.
        extend = "neither"

    x_values, x_label = _parse_coord_option(x, axis_coords, data)
    y_values, y_label = _parse_coord_option(y, axis_coords, data)

    data = data.transpose(animate_over, y, x, transpose_coords=True)
    # Load values eagerly otherwise for some reason the plotting takes
    # 100's of times longer - for some reason animatplot does not deal
    # well with dask arrays!
    image_data = data.values

    # If not specified, determine max and min values across entire data series
    if vmax is None:
        vmax = np.max(image_data)
    if vmin is None:
        vmin = np.min(image_data)
    if vsymmetric:
        vmax = max(np.abs(vmin), np.abs(vmax))
        vmin = -vmax
    kwargs["norm"] = _create_norm(logscale, kwargs.get("norm", None), vmin, vmax)

    if not ax:
        fig, ax = plt.subplots()

    ax.set_aspect(aspect)

    # Note: animatplot's Pcolormesh gave strange outputs without passing
    # explicitly x- and y-value arrays, although in principle these should not
    # be necessary.
    with warnings.catch_warnings():
        # The coordinates we pass are a logically rectangular grid, so should be fine
        # even if this warning is triggered by pcolor or pcolormesh
        warnings.filterwarnings(
            "ignore",
            "The input coordinates to pcolormesh are interpreted as cell centers, but "
            "are not monotonically increasing or decreasing. This may lead to "
            "incorrectly calculated cell edges, in which case, please supply explicit "
            "cell edges to pcolormesh.",
            UserWarning,
        )
        pcolormesh_block = amp.blocks.Pcolormesh(
            x_values,
            y_values,
            image_data,
            ax=ax,
            **kwargs,
            # shading parameter triggers error when trying to set manually
        )

    if animate:
        t_values, t_label = _parse_coord_option(animate_over, axis_coords, data)
        t_values, t_suffix = _normalise_time_coord(t_values)

        timeline = amp.Timeline(t_values, fps=fps, units=t_suffix)
        anim = amp.Animation([pcolormesh_block], timeline)

    cbar = plt.colorbar(pcolormesh_block.quad, ax=ax, cax=cax, extend=extend)
    cbar_label = data.long_name if "long_name" in data.attrs else variable
    if "units" in data.attrs:
        cbar_label += f" [{data.units}]"
    cbar.ax.set_ylabel(cbar_label)

    # Add title and axis labels
    ax.set_title(variable)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    if animate:
        _add_controls(anim, controls, t_label)

        if save_as is not None:
            if save_as is True:
                save_as = f"{variable}_over_{animate_over}"
            anim.save(save_as + ".gif", writer=PillowWriter(fps=fps))
        return anim
    return pcolormesh_block


def animate_line(
    data,
    animate_over=None,
    animate=True,
    axis_coords=None,
    vmin=None,
    vmax=None,
    fps=10,
    save_as=None,
    ax=None,
    aspect=None,
    controls="both",
    **kwargs,
):
    """
    Plots a line plot which is animated with time.
    Currently only supports 1D+1 data, which it plots with animatplot's Line animation.
    Parameters
    ----------
    data : xarray.DataArray
    animate_over : str, optional
        Dimension over which to animate, defaults to the time dimension
    animate : bool, optional
        If set to false, do not create the animation, just return the block
    axis_coords : None, str, dict
        Coordinates to use for axis labelling.
        - None: Use the dimension coordinate for each axis, if it exists.
        - "index": Use the integer index values.
        - dict: keys are dimension names, values set axis_coords for each axis
          separately. Values can be: None, "index", the name of a 1d variable or
          coordinate (which must have the dimension given by 'key'), or a 1d
          numpy array, dask array or DataArray whose length matches the length of
          the dimension given by 'key'.
    vmin : float, optional
        Minimum value to use for colorbar. Default is to use minimum value of
        data across whole timeseries.
    vmax : float, optional
        Maximum value to use for colorbar. Default is to use maximum value of
        data across whole timeseries.
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
    controls : string or None, default "both"
        By default, add both the timeline and play/pause toggle to the animation. If
        "timeline" is passed add only the timeline, if "toggle" is passed add only the
        play/pause toggle. If None or an empty string is passed, add neither.
    kwargs : dict, optional
        Additional keyword arguments are passed on to the plotting function
        animatplot.blocks.Line
    Returns
    -------
    animation or block
        If animate==True, returns an animatplot.Animation object, otherwise
        returns an animatplot.blocks.Line instance.
    """

    if animate_over is None:
        animate_over = "time"

    if aspect is None:
        aspect = "auto"

    variable = data.name

    _, x = data.dims

    # Load values eagerly otherwise for some reason the plotting takes
    # 100's of times longer - for some reason animatplot does not deal
    # well with dask arrays!
    image_data = data.values

    # If not specified, determine max and min values across entire data series
    if vmax is None:
        vmax = np.max(image_data)
    if vmin is None:
        vmin = np.min(image_data)

    x_values, x_label = _parse_coord_option(x, axis_coords, data)

    if not ax:
        fig, ax = plt.subplots()

    ax.set_aspect(aspect)

    # set range of plot
    ax.set_ylim([vmin, vmax])

    line_block = amp.blocks.Line(x_values, image_data, ax=ax, **kwargs)

    if animate:
        t_values, t_label = _parse_coord_option(animate_over, axis_coords, data)
        t_values, t_suffix = _normalise_time_coord(t_values)

        timeline = amp.Timeline(t_values, fps=fps, units=t_suffix)
        anim = amp.Animation([line_block], timeline)

    # Add title and axis labels
    ax.set_title(variable)
    ax.set_xlabel(x_label)
    y_label = data.long_name if "long_name" in data.attrs else variable
    if "units" in data.attrs:
        y_label = y_label + f" [{data.units}]"
    ax.set_ylabel(y_label)

    if animate:
        _add_controls(anim, controls, t_label)

        if save_as is not None:
            if save_as is True:
                save_as = f"{variable}_over_{animate_over}"
            anim.save(save_as + ".gif", writer=PillowWriter(fps=fps))

        return anim

    return line_block
