""" Pandapower tutorial on Colormaps.
Date: 3/June/2021
"""
import pandapower as pp
import pandapower.networks as nw
import pandapower.plotting as plot
import matplotlib.pyplot as plt

# load network case
# net = nw.mv_oberrhein()
net=nw.case33bw()
# net = nw.create_synthetic_voltage_control_lv_network(network_class='rural_1')
# run pf
pp.runpp(net)

# creating a color function to get a linear a colormap with color centers green at 30%, yellow at 50% and red at 60%
# line loading
cmap_list_lines=[(20, "green"), (50, "yellow"), (60, "red")]
cmap_lines, norm_lines = plot.cmap_continuous(cmap_list_lines)
# create a collection for colouring each line according to a line color range.
lc = plot.create_line_collection(net, net.line.index, zorder=2, cmap=cmap_lines, norm=norm_lines, linewidths=2)
# create discrete map for node pu magnitude
cmap_list_nodes=[(0.975, "blue"), (1.0, "green"), (1.03, "red")]
cmap_nodes, norm_nodes = plot.cmap_continuous(cmap_list_nodes)
bc = plot.create_bus_collection(net, net.bus.index, size=0.07, zorder=2, cmap=cmap_nodes, norm=norm_nodes) #80 of mv obherreim and 0.07 for ieee
# tlc, tpc = plot.create_trafo_collection(net, net.trafo.index, color="g")
sc = plot.create_bus_collection(net, net.ext_grid.bus.values, patch_type="rect", size=.08, color="y", zorder=11)
# plot.draw_collections([lc, bc, sc], figsize=(8,6))
# plt.show()

net_generic = nw.case33bw()
net_generic.bus_geodata.drop(net_generic.bus_geodata.index, inplace=True)
net_generic.line_geodata.drop(net_generic.line_geodata.index, inplace=True)
plot.create_generic_coordinates(net_generic, respect_switches=True) #create artificial coordinates with the igraph package
colors = ["b", "g", "r", "c", "y"]
plot.fuse_geodata(net_generic)
bc = plot.create_bus_collection(net_generic, net_generic.bus.index, size=.08, color=colors[0], zorder=10)
lcd = plot.create_line_collection(net_generic, net_generic.line.index, color="grey", linewidths=0.5, use_bus_geodata=True)
sc = plot.create_bus_collection(net_generic, net_generic.ext_grid.bus.values, patch_type="rect", size=.08, color="y", zorder=11)
plot.draw_collections([lcd, bc, sc], figsize=(8,6))
plt.show()
