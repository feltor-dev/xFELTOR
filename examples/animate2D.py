from xfeltor import open_feltordataset
import matplotlib.pyplot as plt

ds = open_feltordataset("output.nc")

_ = ds["electrons"].feltor.animate2D(x="x", y="y", fps=100)
plt.show()
