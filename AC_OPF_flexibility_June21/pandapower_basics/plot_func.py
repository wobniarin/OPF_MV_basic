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
    cmap_list_lines=[(20, "green"), (50, "yellow"), (100, "red")]
    cmap_lines, norm_lines = plot.cmap_continuous(cmap_list_lines)
    # create a collection for colouring each line according to a line color range.
    lc = plot.create_line_collection(net, net.line.index, zorder=2, cmap=cmap_lines, norm=norm_lines, linewidths=2)
    # create discrete map for node pu magnitude
    cmap_list_nodes=[(0.975, "blue"), (1.0, "green"), (1.05, "red")]
    cmap_nodes, norm_nodes = plot.cmap_continuous(cmap_list_nodes)
    bc = plot.create_bus_collection(net, net.bus.index, size=0.07, zorder=2, cmap=cmap_nodes, norm=norm_nodes) #80 of mv obherreim and 0.07 for ieee
    tlc, tpc = plot.create_trafo_collection(net, net.trafo.index, color="g")
    sc = plot.create_bus_collection(net, net.ext_grid.bus.values, patch_type="rect", size=.08, color="y", zorder=11)
    # draw the different collections
    plot.draw_collections([lc, bc,tlc,tpc,sc, bic], figsize=(8,6))
    plt.show()

def plot_style_LaTex():
    plt.style.use('seaborn-ticks')
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams.update({'font.size': 20})
    # plt.rcParams.update({'font.size': 12})
    plt.rcParams["axes.grid"] = False
    plt.rcParams["legend.loc"] = 'best'
    plt.figure(figsize=[15,10])
    return


def plot():
    plt.figure(figsize=(15, 10))
    plt.plot(df.index, df['P_load_kw'], color='black', linestyle=':', linewidth=3, label='Active Load demand')
    plt.plot(df.index, df['P_pv_kw'], color='grey', linewidth=3, label='PV generation')
    plt.ylabel('Power [kW]')
    plt.xlabel('Time [h]')
    plt.yticks(np.arange(0, 5, 0.25))
    plt.xticks(np.arange(24), ('00', '01', '02', '03', '04', '05', '06', '07', '08', '09',
                               '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                               '20', '21', '22', '23'))
    plt.legend()
    plt.xlim(-.5, 23.5)
    plt.savefig("./plots/load_profile.png", dpi=200)
    plt.show()

def plot_q():
    plt.figure(figsize=(15, 10))
    plt.plot(df.index, df['Q_load_kvar'], color='black', linestyle=':', linewidth=3, label='Reactive Power Load')
    plt.ylabel('Power [kvar]')
    plt.xlabel('Time [h]')
    plt.yticks(np.arange(0, 5.25, 0.25))
    plt.xticks(np.arange(24), ('00', '01', '02', '03', '04', '05', '06', '07', '08', '09',
                               '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                               '20', '21', '22', '23'))
    plt.legend()
    plt.xlim(-.5, 23.5)
    plt.savefig("./plots/q_profile0_5.png", dpi=200)
    plt.show()

def two_axis_plot():
    plot_style_LaTex()
    plt.figure(figsize=(15, 10))
    fig, ax = plt.subplots(figsize=(15, 10))
    # plot 1
    plt.plot(df.index, df['P_load_kw'], color='black', linestyle=':', linewidth=3, label='Active Load demand')
    plt.plot(df.index, df['P_pv_kw'], color='grey', linewidth=3, label='PV generation')
    ax.set_xlabel('Time [h]')
    ax.set_ylabel('Power [kW]')
    ax.set_yticks(np.arange(0, 5.25, 0.25))
    plt.xticks(np.arange(24), ('00', '01', '02', '03', '04', '05', '06', '07', '08', '09',
                               '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                               '20', '21', '22', '23'))
    ax2 = ax.twinx()

    # plot 2
    ax2.plot(df.index, df['Q_load_kvar'], color='black', linestyle='-', linewidth=3, label='Reactive Power Load')
    ax2.set_ylabel('Reactive Power [kvar]')
    ax2.set_yticks(np.arange(0, 5.25, 0.25))
    fig.legend(ncol=3, loc='upper center', bbox_to_anchor=(0.5, 0.85))
    plt.show()
