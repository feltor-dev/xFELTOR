import xarray as xr
from functools import partial
from pprint import pformat as prettyformat


@xr.register_dataset_accessor("feltor")
class FeltorDatasetAccessor:
    """
    Contains FELTOR-specific methods to use on FELTOR datasets opened using
    `open_feltordataset()`.

    """

    def __init__(self, ds):
        self.data = ds

    def __str__(self):
        """
        String representation of the FeltorDataset.
        Accessed by print(ds.feltor)
        """
        ds = self.data.copy()
        del ds.attrs["inputfile"]
        styled = partial(prettyformat, indent=4, compact=False)
        return "<xfeltor.FeltorDataset>" + "\n{}\n".format(styled(ds))
