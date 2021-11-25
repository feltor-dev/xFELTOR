from xfeltor import open_feltordataset
import matplotlib.pyplot as plt

ds = open_feltordataset("output.nc")

_ = ds.feltor.animate_list(
    variables=[
        ds["electrons"],
        ds["ions"].isel(y=100),
        ds["potential"],
        ds["vorticity"],
    ]
)
plt.show()
