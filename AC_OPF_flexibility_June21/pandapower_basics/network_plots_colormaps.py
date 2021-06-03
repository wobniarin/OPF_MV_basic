""" Pandapower tutorial on Colormaps.
Date: 3/June/2021
"""
import pandapower as pp
import pandapower.networks as nw
import pandapower.plotting as plot
import matplotlib.pyplot as plt

# load network case
net = nw.mv_oberrhein()
# run pf
pp.runpp(net)

# creating a color function to get a linear a colormap with color centers green at 30%, yellow at 50% and red at 60%
# line loading
cmap_list=[(20, "green"), (50, "yellow"), (60, "red")]
cmap, norm = plot.cmap_continuous(cmap_list)

# create a bus collection for passing those parameters to the plot function
lc = plot.create_line_collection(net, net.line.index, zorder=1, cmap=cmap, norm=norm, linewidths=2)
plot.draw_collections([lc], figsize=(8,6))
cmap_list=[(0.975, "blue"), (1.0, "green"), (1.03, "red")]
cmap, norm = plot.cmap_continuous(cmap_list)
bc = plot.create_bus_collection(net, net.bus.index, size=80, zorder=2, cmap=cmap, norm=norm)
plot.draw_collections([lc, bc], figsize=(8,6))
plt.show()

