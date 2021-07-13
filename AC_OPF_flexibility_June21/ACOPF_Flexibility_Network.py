"""
AC-OPF Formulation for calculating flexibility request in a distribution network
Code developed by Íngrid Munné Collado
Date 3/6/2021
"""

# import libraries
import math
import matplotlib.pyplot as plt
import pyomo.environ as pyo
import os
import pandas as pd
import numpy as np
import pandapower as pp
import pandapower.networks as nw
import scipy
import seaborn
import pandapower.plotting as plot
import plot_func as myfun

# load case study/create network
print("Creating network")
#create empty net
# net = pandapower.networks.mv_oberrhein("load")
# net = pandapower.networks.panda_four_load_branch()
net = nw.create_synthetic_voltage_control_lv_network(network_class='rural_1')
print("Network created")
print("Executing Power Flow")

# Adding generation/loads so we can create a scenario with great load
pp.create_load(net, 10, 0.08, controllable=False)
# pp.create_load(net, 22, 0.08, controllable=False)

# IDENTIFY CONGESTIONS ------------------------------------------------
# run powerflow to check congestions
pp.runpp(net)
print("Power flow done")
# indentify congestions
# identify overcurrent
loading_percent_max = 70
overcurrent_line = net.res_line[net.res_line['loading_percent'] >= loading_percent_max]
if len(overcurrent_line.index) != 0:
    for i_overcurrent in overcurrent_line.index:
        overcurrent_line_value = overcurrent_line['loading_percent'][i_overcurrent]
        overcurrent_line_id = i_overcurrent
        print(f"Line with overcurrent:{overcurrent_line_id}, load_percentage:{overcurrent_line_value}")
else:
    print("No overcurrent issues found")

# identify overvoltage
vm_max = 1.03
overvoltage_bus = net.res_bus[net.res_bus['vm_pu']>vm_max]
if len(overvoltage_bus.index) != 0:
    for i_overvoltage in  overvoltage_bus.index:
        overvoltage_bus_value = overvoltage_bus['vm_pu'][i_overvoltage]
        overvoltage_bus_id = i_overvoltage
        print(f"Bus with overvoltage:{overvoltage_bus_id}, vm_pu value:{overvoltage_bus_value}")
else:
    print("No overvoltage issues found")

# visualize network
colors = seaborn.color_palette()
if 1==1:
    myfun.plot_network(net)

# OPF Part--------------------------------------------------------------
# creating virtual generators and virtual loads for OPF execution
print("OPF part. Creation of flexible sources")
# creating a copy of the network to include flexibility
net_opf = pp.pandapowerNet(net)
# add virtual demands and generators to quantify the flexibility request
flex_source_1_up = pp.create_gen(net_opf, 5, name='Flex_1_UP', min_p_mw=0, p_mw=0.2, max_p_mw=10, min_q_mvar=0, max_q_mvar=10, controllable=True)
flex_source_1_down = pp.create_load(net_opf, 4, name='Flex_1_DOWN', min_p_mw=0, p_mw=0.2,  max_p_mw=10, min_q_mvar=0, max_q_mvar=10, controllable=True)
# flex_source_2_down = pp.create_load(net_opf, 3, name='Flex_2_DOWN', p_mw=0.05, min_p_mw=0, max_p_mw=10, min_q_mvar=0, max_q_mvar=10, controllable=True)
# flex_source_2_up = pp.create_gen(net_opf, 22, name='Flex_2_UP', min_p_mw=0, p_mw=0.1, max_p_mw=10, min_q_mvar=0, max_q_mvar=10, controllable=True)


# activating operational constraints:
if 1==1:
    net_opf.bus["min_vm_pu"] = 0.9
if 1==1:
    net_opf.bus["max_vm_pu"] = 1.03
if 1==0:
    net_opf.line['max_loading_percent'] = 80
# running power flow of the new network to check if we solve the network problem
if 1==0:
    pp.runpp(net_opf)
    myfun.plot_network(net_opf)

dummy= 1
# costs parameters for flexibility activation
pp.create_poly_cost(net_opf, 0, 'gen', cp1_eur_per_mw=0.1, cq1_eur_per_mvar=0.1)
# pp.create_poly_cost(net_opf, 1, 'gen', cp1_eur_per_mw=0.1, cq1_eur_per_mvar=0.1)
pp.create_poly_cost(net_opf, 15, 'load', cp1_eur_per_mw =0.1, cq1_eur_per_mvar=0.1)
pp.create_poly_cost(net_opf, 0, 'ext_grid', cp1_eur_per_mw =10, cq1_eur_per_mvar=10)

# run OPF
print("Executing AC-OPF")
pp.runopp(net_opf, verbose=True)

# CHECK RESULTS -------------------------------------------------------
# check results of the OPF - They are stored inside net_opf.results
print("Flexibility Request calculated. Showing results...")
# Flexibility activated UP
list = ['Flex_1_UP'] #['Flex_1_UP', 'Flex_2_UP'] #['Flex_1_UP']
for name in list:
    id_flex_up = net_opf.gen[net_opf.gen['name'] == name].index[0]
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
if len(overcurrent_line.index) != 0:
    for i_overcurrent in overcurrent_line.index:
        print(f"{net.line['name'][i_overcurrent]}. Previous loading percentage: {net.res_line['loading_percent'][i_overcurrent]},"
              f" Current loading percentage: {net_opf.res_line['loading_percent'][i_overcurrent]} ")
else:
    print("no line congestion to mitigate")
# Congestion - overcurrent solved
if len(overvoltage_bus.index) != 0:
    for i_overvoltage in  overvoltage_bus.index:
        print(f"{net.bus['name'][i_overvoltage]}. Previous voltage magnitude: {net.res_bus['vm_pu'][i_overvoltage]},"
              f" Current voltage magnitude: {net_opf.res_bus['vm_pu'][i_overvoltage]} ")
else:
    print("no bus congestion to mitigate")
# new plot with congestion solved
myfun.plot_network(net_opf)
# store line loading pre-post
line_variation = pd.concat([net.res_line.loading_percent, net_opf.res_line.loading_percent], axis=1)
# store bus vm_pu pre-post
bus_variation = pd.concat([net.res_bus.vm_pu, net_opf.res_bus.vm_pu], axis=1)
# store generation
# gen_variation_PF = pd.concat([net.res_gen.p_mw, net.gen.min_p_mw, net.gen.max_p_mw], axis=1)
gen_variation_OPF = pd.concat([net_opf.res_gen.p_mw, net_opf.gen.min_p_mw, net_opf.gen.max_p_mw], axis=1)
# store loads
# load_variation_PF = pd.concat([net.res_load.p_mw, net.load.min_p_mw, net.load.max_p_mw], axis=1)
load_variation_OPF = pd.concat([net_opf.res_load.p_mw, net_opf.load.min_p_mw, net_opf.load.max_p_mw], axis=1)
