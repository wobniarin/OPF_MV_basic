""" Time series with OPF in pandapower - PhD Case study LV network
Author: Ingrid Munne Collado
Date 10/6/21
"""
# import libraries
import pandapower as pp
import pandapower.networks as nw
import numpy as np
import os
import pandas as pd
import tempfile
from pandapower.timeseries import DFData
from pandapower.timeseries import OutputWriter
from pandapower.timeseries.run_time_series import  run_timeseries
from pandapower.control import ConstControl
import matplotlib.pyplot as plt
import plot_func as myfun

# create dataframes for time series P value
def create_data_source(n_timesteps=24):
    profiles = pd.DataFrame()
    profiles['load1_p'] = np.random.random(n_timesteps) * 0.008
    profiles['sgen1_p'] = np.random.random(n_timesteps) * 0.002
    ds = DFData(profiles)
    return profiles, ds

# define control variables - controllers to update the P value of the load and the static generator at each time step
# this control variables will update at each time period the forecast value of the load and the generator
def create_controllers(net, ds):
    ConstControl(net, element='load', variable='p_mw', element_index=[14],
                 data_source=ds, profile_name=["load1_p"])
    ConstControl(net, element='sgen', variable='p_mw', element_index=[5],
                 data_source=ds, profile_name=["sgen1_p"])

# Instead of saving the whole net (which takes a lot of time), we extract only predefined outputs.
# The variables of create_output_writer are saved to the hard drive after the time series loop
def create_output_writer(net, time_steps, output_dir):
    ow = OutputWriter(net, time_steps, output_path=output_dir, output_file_type=".xlsx", log_variables=list())
    ow.log_variable('res_sgen', 'p_mw')
    ow.log_variable('res_sgen', 'q_mvar')
    ow.log_variable('res_bus', 'vm_pu')
    ow.log_variable('res_line', 'loading_percent')
    ow.log_variable('res_line', 'i_ka')
    ow.log_variable('res_load', 'p_mw')
    ow.log_variable('res_load', 'q_mvar')
    return ow

# ---------------------- CODE----------------------------------------------
# Lets run the code for the timeseries simulation with OPF.
# Note that parameter 'run' is set to the function that runs OPF (run=pp.runopp).
output_dir = os.path.join(tempfile.gettempdir(), "time_series_acopf_in_3")
print("Results can be found in your local temp folder: {}".format(output_dir))
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

# create network
net = nw.create_synthetic_voltage_control_lv_network(network_class='rural_1')
pp.create_load(net, 8, 0.08, controllable=False)
# add controllable variables - load and generation
flex_source_1_up = pp.create_sgen(net, 5, name='Flex_1_UP', min_p_mw=0, p_mw=0.02, max_p_mw=10, min_q_mvar=0,
                                  max_q_mvar=10, controllable=True)
flex_source_1_down = pp.create_load(net, 4, name='Flex_1_DOWN', min_p_mw=0, p_mw=0.02,  max_p_mw=10, min_q_mvar=0,
                                    max_q_mvar=10, controllable=True)
# activating operational constraints:
if 1==0:
    net.bus["min_vm_pu"] = 0.5  #0.9
if 1==0:
    net.bus["max_vm_pu"] = 100 #1.05
if 1==0:
    net.line['max_loading_percent'] = 80

# costs parameters for flexibility activation
pp.create_poly_cost(net, 5, 'sgen', cp1_eur_per_mw=1)
pp.create_poly_cost(net, 15, 'load', cp1_eur_per_mw =1)
pp.create_poly_cost(net, 0, 'ext_grid', cp1_eur_per_mw =10)

# load data
# df = pd.read_csv("./AC_OPF_flexibility_June21/data/profiles_2_csv.csv", sep=';')

# create (random) data source
n_timesteps = 24
profiles, ds = create_data_source(n_timesteps)

# create controllers (to control P values of the load and the sgen)
create_controllers(net, ds)

# time steps to be calculated. Could also be a list with non-consecutive time steps
time_steps = range(0, n_timesteps)

# the output writer with the desired results to be stored to files.
ow = create_output_writer(net, time_steps, output_dir=output_dir)

# the main time series function with optimal power flow
run_timeseries(net, time_steps, run=pp.runopp)

# ------------------------- PLOTS --------------------------------------
# We can see that all of the bus voltages are in the defined constraint range according to the OPF
# voltage results (min_vm_pu=0.98, max_vm_pu=1.05)
vm_pu_file = os.path.join(output_dir, "res_bus", "vm_pu.xlsx")
vm_pu = pd.read_excel(vm_pu_file, index_col=0)
vm_pu.plot(label="vm_pu")
plt.xlabel("time step")
plt.ylabel("voltage mag. [p.u.]")
plt.title("Voltage Magnitude")
plt.grid()
plt.show()

# All lines should be inside the range of 80 % maximum load
# line loading results
ll_file = os.path.join(output_dir, "res_line", "loading_percent.xlsx")
line_loading = pd.read_excel(ll_file, index_col=0)
line_loading.plot()
plt.xlabel("time step")
plt.ylabel("line loading [%]")
plt.title("Line Loading")
plt.grid()
plt.show()

# We can also compare the results of the generation scheduled on the forecast with the results of the OPF formulation
# sgen results
sgen_file = os.path.join(output_dir, "res_sgen", "p_mw.xlsx")
sgen = pd.read_excel(sgen_file, index_col=0)
ax=sgen[0].plot(label="sgen (after OPF)")
ds.df.sgen1_p.plot(ax=ax, label="sgen (original)", linestyle='--')
ax.legend()
plt.xlabel("time step")
plt.ylabel("P [MW]")
plt.grid()
plt.show()


# load results
load_file = os.path.join(output_dir, "res_load", "p_mw.xlsx")
sgen = pd.read_excel(sgen_file, index_col=0)
ax=sgen[0].plot(label="load (after OPF)")
ds.df.sgen1_p.plot(ax=ax, label="load (original)", linestyle='--')
ax.legend()
plt.xlabel("time step")
plt.ylabel("P [MW]")
plt.grid()
plt.show()
