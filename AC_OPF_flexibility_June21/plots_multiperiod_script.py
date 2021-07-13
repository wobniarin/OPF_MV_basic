""""
Script for plotting multiperiod results
Author: Ingrid Munne Collado
Date: 10/06/2021
"""

import plot_func as myfun
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

output_dir = "../results_multiperiod_opf/"

def voltageplot():
    # vm_pu_file = os.path.join(output_dir, "res_bus", "vm_pu.xlsx")
    vm_pu = pd.read_excel("../results_multiperiod_opf/time_series_acopf_in_ok/res_bus/vm_pu.xlsx", index_col=0)
    myfun.plot_style_LaTex()
    plt.figure(figsize=(15, 10))
    plt.plot(vm_pu.index, vm_pu[5], color='black', linestyle=':', linewidth=3,
             label='Node 5')
    plt.plot(vm_pu.index, vm_pu[4], color='grey', linewidth=3,
             label='Node 4')
    plt.plot(vm_pu.index, vm_pu[22], color='cornflowerblue', linestyle='--', linewidth=3,
             label='Node 22')
    plt.hlines(y=[1.04, 0.98], xmin=0, xmax=23, colors='crimson', linestyles=':', linewidth=2,
               label='operational limits')
    plt.xlabel("Time [h]")
    plt.ylabel("Voltage Magnitude [p.u.]")
    plt.ylim(0.97, 1.05)
    plt.xticks(np.arange(24), ('00', '01', '02', '03', '04', '05', '06', '07', '08', '09',
                               '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                               '20', '21', '22', '23'))
    plt.legend(ncol=4, bbox_to_anchor=(0.90, 0.99))
    plt.savefig("../plots/voltage_pu_nodes_2.png", dpi=300)
    plt.show()

# vm_pu = voltageplot()

def two_axis_P_Q_request():
    p_request_up = pd.read_excel("../results_multiperiod_opf/time_series_acopf_in_ok/res_sgen/p_mw.xlsx",
                                 index_col=0)
    p_request_up = p_request_up[[5]]
    #, names=['P_up']
    p_request_down = pd.read_excel("../results_multiperiod_opf/time_series_acopf_in_ok/res_load/p_mw.xlsx",
                                   index_col=0)
    p_request_down = p_request_down[[14,15]]
    q_request = pd.read_excel("../results_multiperiod_opf/time_series_acopf_in_ok/res_sgen/q_mvar.xlsx",
                                 index_col=0)
    q_request = q_request[[5]]
    # convert from MW to kW
    p_request_up = p_request_up * 1000
    p_request_down = p_request_down * -1000
    q_request = q_request * 1000
    # plot results
    myfun.plot_style_LaTex()
    plt.figure(figsize=(15, 10))
    fig, ax = plt.subplots(figsize=(15, 10))
    # plot 1
    ax.plot(p_request_up.index, p_request_up[5], color='black', linestyle=':', linewidth=3,
             label='Active Power Request Node 5')
    ax.plot(p_request_down.index,p_request_down[14], color='grey', linewidth=3, label='Active Power Request Node 9')
    ax.plot(p_request_down.index, p_request_down[15], color='black', linewidth=3, label='Active Power Request Node 13')
    ax.set_xlabel('Time [h]')
    ax.set_ylabel('Power [kW]')
    ax.set_ylim(-30,60)
    # ax.set_yticks(np.arange(0, 20, 0.25))
    plt.xticks(np.arange(24), ('00', '01', '02', '03', '04', '05', '06', '07', '08', '09',
                               '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                               '20', '21', '22', '23'))
    ax2 = ax.twinx()

    # plot 2
    ax2.plot(q_request.index, q_request[5], color='cornflowerblue', linestyle='-', linewidth=3,
             label='Reactive Power Request Node 5')
    plt.plot()
    ax2.set_ylabel('Reactive Power [kvar]')
    # ax2.set_yticks(np.arange(0, 60))
    ax2.set_ylim(-30,60)
    fig.legend(bbox_to_anchor=(0.4,0.95))  #ncol=1, loc='upper left', bbox_to_anchor=(0.5, 0.95))
    fig.savefig("../plots/flex_requests.png", dpi=300)
    plt.show()


def line_load():
    line_per = pd.read_excel("../results_multiperiod_opf/time_series_acopf_in_ok/res_line/loading_percent.xlsx",
                             index_col=0)
    myfun.plot_style_LaTex()
    plt.figure(figsize=(15, 10))
    plt.plot(line_per.index, line_per[5], color='black', linestyle=':', linewidth=3,
             label='Load line 5-9')
    plt.plot(line_per.index, line_per[4], color='grey', linewidth=3,
             label='Load line 5-4')
    plt.plot(line_per.index, line_per[16], color='cornflowerblue', linestyle='--', linewidth=3,
             label='Load line 15-22')
    plt.plot(line_per.index, line_per[14], color='indigo', linestyle='-.', linewidth=3,
             label='Load line 14-15')
    plt.hlines(y=70, xmin=0, xmax=23, colors='crimson', linestyles=':', linewidth=2, label='operational limits')
    plt.xlabel("Time [h]")
    plt.ylabel("Line load percentage [%]")
    plt.ylim(0.05, 100)
    plt.yticks(np.arange(0, 110, 10))
    plt.xticks(np.arange(24), ('00', '01', '02', '03', '04', '05', '06', '07', '08', '09',
                               '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                               '20', '21', '22', '23'))
    plt.legend(ncol=3, bbox_to_anchor=(0.90, 0.97))
    plt.savefig("../plots/line_load.png", dpi=300)
    plt.show()