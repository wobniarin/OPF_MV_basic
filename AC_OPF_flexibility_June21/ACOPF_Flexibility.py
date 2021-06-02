"""
AC-OPF Formulation for calculating flexibility request in a distribution network
Code developed by Íngrid Munné Collado
Date 2/6/2021
"""

# import libraries
import math
import matplotlib.pyplot as plt
import pyomo.environ as pyo
import os
import pandas as pd
import numpy as np
import pandapower as pp
import pandapower.networks
import scipy
import seaborn
import pandapower.plotting as plot

# load case study/create network
#create empty net
net = pp.create_empty_network()
# netmv = net = pandapower.networks.mv_oberrhein("load")

# create buses
bus1 = pp.create_bus(net, vn_kv=220, name= 'SLACK', min_vm_pu=0.99, max_vm_pu=1.00)
bus2 = pp.create_bus(net, vn_kv=110, name= 'Bus2', min_vm_pu=0.99, max_vm_pu=1.00)
bus3 = pp.create_bus(net, vn_kv=110, name= 'Bus3', min_vm_pu=0.99, max_vm_pu=1.00)
bus4 = pp.create_bus(net, vn_kv=110, name= 'Bus4', min_vm_pu=0.99, max_vm_pu=1.00)

# create 220/110 kV transformer
pp.create_transformer(net, bus1, bus2, std_type= "100 MVA 220/110 kV", max_loading_percent=100)

# create 110 kV lines
pp.create_line(net, bus2, bus3, length_km=70., std_type= '149-AL1/24-ST1A 110.0', name= 'Line23', max_loading_percent=100 )
pp.create_line(net, bus3, bus4, length_km=50., std_type= '149-AL1/24-ST1A 110.0', name= 'Line34', max_loading_percent=100)
pp.create_line(net, bus4, bus2, length_km=40., std_type= '149-AL1/24-ST1A 110.0', name= 'Line42',max_loading_percent=70)

# create loads
pp.create_load(net, bus2, p_mw=60, controllable=False)
pp.create_load(net, bus3, p_mw=70, controllable=False)
pp.create_load(net, bus4, p_mw=10, controllable=False)

# create generators
eg = pp.create_ext_grid(net, bus1) #slack bus
g0 = pp.create_gen(net, bus3, p_mw=80, min_p_mw=0, max_p_mw=80, vm_pu=1.01, controllable=True)
g1 = pp.create_gen(net, bus4, p_mw=100, min_p_mw=0, max_p_mw=100, vm_pu=1.01, controllable=True)

# costs parameters
costeg = pp.create_poly_cost(net, 0, 'ext_grid', cp1_eur_per_mw=0)
costgen1 = pp.create_poly_cost(net, 0, 'gen', cp1_eur_per_mw=-1)
costgen2 = pp.create_poly_cost(net, 1, 'gen', cp1_eur_per_mw=-1)

# IDENTIFY CONGESTIONS ------------------------------------------------
# run powerflow to check congestions
pp.runpp(net)
# indentify congestions
# identify overcurrent
loading_percent_max = 50
overcurrent_line = net.res_line[net.res_line['loading_percent'] >= loading_percent_max]
for i in overcurrent_line.index:
    overcurrent_line_value = overcurrent_line['loading_percent'][i]
    overcurrent_line_id = i
    print(f"Line with overcurrent:{overcurrent_line_id}, load_percentage:{overcurrent_line_value}")

# identify overvoltage
vm_max = 1.00
overvoltage_bus = net.res_bus[net.res_bus['vm_pu']>vm_max]
for i in  overvoltage_bus.index:
    overvoltage_bus_value = overvoltage_bus['vm_pu'][i]
    overvoltage_bus_id = i
    print(f"Bus with overvoltage:{overvoltage_bus_id}, load_percentage:{overvoltage_bus_value}")

# visualize network
colors = seaborn.color_palette()
if 1==1:
    plot.simple_plot(net, show_plot=True)
if 1==0:
    low_voltage_buses = net.res_bus[net.res_bus.vm_pu < 0.98].index
    lc = plot.create_line_collection(net, net.line.index, color="grey", zorder=1)
    bc = plot.create_bus_collection(net, net.bus.index, size=90, color=colors[0], zorder=10)
    bch = plot.create_bus_collection(net, low_voltage_buses, size=90, color=colors[2], zorder=11)
    plot.draw_collections([lc, bc, bch], figsize=(8, 6))
    plt.show()

# OPF Part--------------------------------------------------------------
# add virtual demands and generators to quantify the flexibility request
net_opf = net
flex_source_1_up = pp.create_gen(net_opf,bus4, name='Flex_1_UP', min_p_mw=0, p_mw=0, max_p_mw=200, min_q_mvar=0, max_q_mvar=200, controllable=True)
flex_source_1_down = pp.create_load(net_opf, bus4,name='Flex_1_DOWN', p_mw=0, min_p_mw=0, max_p_mw=200, min_q_mvar=0, max_q_mvar=200, controllable=True)

# create costs for flexible units
pp.create_poly_cost(net_opf, 4, 'gen', cp1_eur_per_mw=0)

# run OPF


pp.runopp(net_opf, verbose=True)

# CHECK RESULTS -------------------------------------------------------
# check results of the OPF - Run PF


