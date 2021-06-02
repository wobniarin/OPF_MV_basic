""" Plotting networks with Pandapower
Date: June,2 2021
Author: Ingrid Munné Collado
"""

import pandapower.plotting as plot
import pandapower.networks as nw

# load example net (IEEE 9 buses)
net = nw.mv_oberrhein()
# simple plot of net with existing geocoordinates or generated artificial geocoordinates
plot.simple_plot(net, show_plot=True)