from xfeltor import open_feltordataset
import matplotlib.pyplot as plt

ds = open_feltordataset("output.nc")

ds["electrons"].isel(y=100).feltor.animate1D(animate_over="time")
plt.show()
