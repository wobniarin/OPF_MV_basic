""" Pandapower tutorial on Colormaps.
Date: 3/June/2021
"""
import pandapower as pp
import pandapower.networks as nw
import pandapower.plotting as plot
import matplotlib.pyplot as plt
import numpy as np

# load network case
# net = nw.mv_oberrhein()
# net=nw.case33bw()
net = nw.create_synthetic_voltage_control_lv_network(network_class='rural_1')
# run pf
pp.runpp(net)

def plot_network(net):
    # create buses ID
    buses = net.bus.index.tolist() # list of all bus indices
    coords = zip(net.bus_geodata.x.loc[buses].values +0.15, net.bus_geodata.y.loc[buses].values+0.07) # tuples of all bus coords
    bic = plot.create_annotation_collection(size=0.2, texts=np.char.mod('%d', buses), coords=coords, zorder=3, color="black")
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
    tlc, tpc = plot.create_trafo_collection(net, net.trafo.index, color="g")
    sc = plot.create_bus_collection(net, net.ext_grid.bus.values, patch_type="rect", size=.08, color="y", zorder=11)
    # draw the different collections
    plot.draw_collections([lc, bc,tlc,tpc,sc, bic], figsize=(8,6))
    plt.show()

