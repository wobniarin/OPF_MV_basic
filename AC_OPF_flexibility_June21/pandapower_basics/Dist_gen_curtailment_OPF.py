"""
Pandapower - Run OPF basic Distributed generation curtailment
date 2/6/2021
Author: Ingrid Munné Collado
"""

import pandapower as pp
import pandapower.networks
import numpy as np

#create empty net
net = pp.create_empty_network()
# create buses
bus1 = pp.create_bus(net, vn_kv=220, min_vm_pu=1.0, max_vm_pu=1.02)
bus2 = pp.create_bus(net, vn_kv=110, min_vm_pu=1.0, max_vm_pu=1.02)
bus3 = pp.create_bus(net, vn_kv=110, min_vm_pu=1.0, max_vm_pu=1.02)
bus4 = pp.create_bus(net, vn_kv=110, min_vm_pu=1.0, max_vm_pu=1.02)

# create 220/110 kV transformer
pp.create_transformer(net, bus1, bus2, std_type= "100 MVA 220/110 kV", max_loading_percent=100)

# create 110 kV lines
pp.create_line(net, bus2, bus3, length_km=70., std_type= '149-AL1/24-ST1A 110.0', max_loading_percent=100 )
pp.create_line(net, bus3, bus4, length_km=50., std_type= '149-AL1/24-ST1A 110.0', max_loading_percent=100)
pp.create_line(net, bus4, bus2, length_km=40., std_type= '149-AL1/24-ST1A 110.0', max_loading_percent=100)

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

# run OPF
pp.runopp(net, verbose=True)