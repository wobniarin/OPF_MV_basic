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
print("Creating network")
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
# costeg = pp.create_poly_cost(net, 0, 'ext_grid', cp1_eur_per_mw=0)
# costgen1 = pp.create_poly_cost(net, 0, 'gen', cp1_eur_per_mw=-1)
# costgen2 = pp.create_poly_cost(net, 1, 'gen', cp1_eur_per_mw=-1)

print("Network created")
print("Executing Power Flow")

# IDENTIFY CONGESTIONS ------------------------------------------------
# run powerflow to check congestions
pp.runpp(net)
print("Power flow done")
# indentify congestions
# identify overcurrent
loading_percent_max = 50
overcurrent_line = net.res_line[net.res_line['loading_percent'] >= loading_percent_max]
if len(overcurrent_line.index) != 0:
    for i_overcurrent in overcurrent_line.index:
        overcurrent_line_value = overcurrent_line['loading_percent'][i_overcurrent]
        overcurrent_line_id = i_overcurrent
        print(f"Line with overcurrent:{overcurrent_line_id}, load_percentage:{overcurrent_line_value}")
else:
    print("No overcurrent issues found")

# identify overvoltage
vm_max = 1.00
overvoltage_bus = net.res_bus[net.res_bus['vm_pu']>vm_max]
for i_overvoltage in  overvoltage_bus.index:
    overvoltage_bus_value = overvoltage_bus['vm_pu'][i_overvoltage]
    overvoltage_bus_id = i_overvoltage
    print(f"Bus with overvoltage:{overvoltage_bus_id}, load_percentage:{overvoltage_bus_value}")

# visualize network
colors = seaborn.color_palette()
if 1==0:
    plot.simple_plot(net, show_plot=True)
if 1==0:
    low_voltage_buses = net.res_bus[net.res_bus.vm_pu < 0.98].index
    lc = plot.create_line_collection(net, net.line.index, color="grey", zorder=1)
    bc = plot.create_bus_collection(net, net.bus.index, size=90, color=colors[0], zorder=10)
    bch = plot.create_bus_collection(net, low_voltage_buses, size=90, color=colors[2], zorder=11)
    plot.draw_collections([lc, bc, bch], figsize=(8, 6))
    plt.show()

# OPF Part--------------------------------------------------------------
# creating virtual generators and virtual loads for OPF execution
print("OPF part. Creation of flexible sources")
# add virtual demands and generators to quantify the flexibility request
net_opf = pp.pandapowerNet(net)
flex_source_1_up = pp.create_gen(net_opf,bus4, name='Flex_1_UP', min_p_mw=0, p_mw=0, max_p_mw=100, min_q_mvar=0, max_q_mvar=200, controllable=True)
flex_source_1_down = pp.create_load(net_opf, bus4,name='Flex_1_DOWN', p_mw=0, min_p_mw=0, max_p_mw=100, min_q_mvar=0, max_q_mvar=200, controllable=True)
dummy = 1

# costs parameters for flexibility activation
# pp.create_poly_cost(net, 0, 'ext_grid', cp1_eur_per_mw=0)
# pp.create_poly_cost(net, 0, 'gen', cp1_eur_per_mw=-1)
# pp.create_poly_cost(net, 1, 'gen', cp1_eur_per_mw=-1)
pp.create_poly_cost(net_opf, 2, 'gen', cp1_eur_per_mw=2, cq1_eur_per_mvar=2)
pp.create_poly_cost(net_opf, 3 , 'load', cp1_eur_per_mw =2, cq1_eur_per_mvar=2)
pp.create_poly_cost(net_opf, 0, 'ext_grid', cp1_eur_per_mw =100, cq1_eur_per_mvar=100)
# costeg = pp.create_poly_cost(net, 0, 'ext_grid', cp1_eur_per_mw=0)
# costgen1 = pp.create_poly_cost(net, 0, 'gen', cp1_eur_per_mw=-1)
# costgen2 = pp.create_poly_cost(net, 1, 'gen', cp1_eur_per_mw=-1)

# run OPF
print("Executing AC-OPF")
pp.runopp(net_opf, verbose=True)

# CHECK RESULTS -------------------------------------------------------
# check results of the OPF - They are stored inside net_opf.results
print("Flexibility Request calculated. Showing results...")
# Flexibility activated UP
id_flex_up = net_opf.gen[net_opf.gen['name'] == 'Flex_1_UP'].index[0]
id_bus_flex_up = net_opf.gen['bus'][id_flex_up]
flex_act_p_up = net_opf.res_gen['p_mw'][id_flex_up]
flex_act_q_up = net_opf.res_gen['q_mvar'][id_flex_up]
print(f"Flexibility UP in node {id_bus_flex_up}, P = {flex_act_p_up}, Q = {flex_act_q_up}")

# Flexibility activated DOWN
id_flex_down = net_opf.load[net_opf.load['name'] == 'Flex_1_DOWN'].index[0]
id_bus_flex_down = net_opf.load['bus'][id_flex_down]
flex_act_p_down = net_opf.res_load['p_mw'][id_flex_down]
flex_act_q_down = net_opf.res_load['q_mvar'][id_flex_down]
print(f"Flexibility DOWN in node {id_bus_flex_down}, P = {flex_act_p_down}, Q = {flex_act_q_down}")

# Congestion - overvoltage solved
for i_overcurrent in overcurrent_line.index:
    print(f"{net.line['name'][i_overcurrent]}. Previous loading percentage: {net.res_line['loading_percent'][i_overcurrent]},"
          f" Current loading percentage: {net_opf.res_line['loading_percent'][i_overcurrent]} ")

# Congestion - overcurrent solved
for i_overvoltage in  overvoltage_bus.index:
    print(f"{net.bus['name'][i_overvoltage]}. Previous voltage magnitude: {net.res_bus['vm_pu'][i_overvoltage]},"
          f" Current voltage magnitude: {net_opf.res_bus['vm_pu'][i_overvoltage]} ")