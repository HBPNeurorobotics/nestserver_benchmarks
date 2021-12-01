#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
## nest_routine.py
##
## This script defines creation, connection, and simulation routines using PyNest
##
## It is split in several parts, one for each brain region simulated:
## `CTX`, 'CTX_M2' `TH`, `BH`, `CERE`
##
## Functions should be sufffixed by their regions: `_ctx`, 'ctx_M2' `_th`, `_bg`, `_cb`

#import nest.topology as ntop
from nest.lib.hl_api_info import SetStatus
import nest
import numpy as np
import math
import time
import collections
import os
#import pandas as pd
import random

import logging
log = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

import nest.lib.hl_api_parallel_computing as hapc

###########
# General #
###########
#### global variable to be updated when initializing nest #######
pyrngs = []

#-------------------------------------------------------------------------------
# Create new neuron model
#-------------------------------------------------------------------------------

def copy_neuron_model(elements, neuron_info, new_model_name):
    configuration = {}
    # Membrane potential in mV
    configuration['V_m'] = 0.0
    # Leak reversal Potential (aka resting potential) in mV
    configuration['E_L'] = -70.0
    # Membrane Capacitance in pF
    configuration['C_m'] = 250.0
    # Refractory period in ms
    configuration['t_ref'] = float(neuron_info['absolute_refractory_period'])
    # Threshold Potential in mV
    configuration['V_th'] = float(neuron_info['spike_threshold'])
    # Reset Potential in mV
    configuration['V_reset'] = float(neuron_info['reset_value'])
    # Excitatory reversal Potential in mV
    configuration['E_ex'] = float(neuron_info['E_ex'])
    # Inhibitory reversal Potential in mV
    configuration['E_in'] = float(neuron_info['E_in'])
    # Leak Conductance in nS
    configuration['g_L'] = 250./float(neuron_info['membrane_time_constant'])
    # Time constant of the excitatory synaptic exponential function in ms
    configuration['tau_syn_ex'] = float(neuron_info['tau_syn_ex'])
    # Time constant of the inhibitory synaptic exponential function in ms
    configuration['tau_syn_in'] = float(neuron_info['tau_syn_in'])
    # Constant Current in pA
    configuration['I_e'] = float(neuron_info['I_ex'])
    nest.CopyModel(elements, new_model_name, configuration)
    return new_model_name

#-------------------------------------------------------------------------------
# Create new synapse model
#-------------------------------------------------------------------------------
def create_synapse_model(elements, synapse_info, new_model_name):
   pass

#-------------------------------------------------------------------------------
# Nest initialization
#-------------------------------------------------------------------------------
def initialize_nest(sim_params):
  nest.set_verbosity("M_WARNING")
  nest.SetKernelStatus({"overwrite_files": sim_params['overwrite_files']}) # should we erase previous traces when redoing a simulation?
  nest.SetKernelStatus({'local_num_threads': int(sim_params['nbcpu'])})
  nest.SetKernelStatus({"data_path": '/opt/data/log'})
  if sim_params['dt'] != '0.1':
    nest.SetKernelStatus({'resolution': float(sim_params['dt'])})
  ####### adding changes to nest seeds for independent experiments ##########
  ### changing python seeds ####
  N_vp = nest.GetKernelStatus(['total_num_virtual_procs'])[0]
  global pyrngs
  pyrngs = [np.random.RandomState(s) for s in range(sim_params['msd'], sim_params['msd']+N_vp)]
  ### global nest rng ###
  nest.SetKernelStatus({'grng_seed' : sim_params['msd']+N_vp})
  ### per process rng #####
  nest.SetKernelStatus({'rng_seeds' : range(sim_params['msd']+N_vp+1, sim_params['msd']+2*N_vp+1)})



#-------------------------------------------------------------------------------
# Starts the Nest simulation, given the general parameters of `sim_params`
#-------------------------------------------------------------------------------
def run_simulation(sim_params):
  nest.ResetNetwork()
  nest.Simulate(sim_params['simDuration']+ sim_params['initial_ignore'])

#-------------------------------------------------------------------------------
# Instantiate a spike detector and connects it to the entire layer `layer_gid`
#-------------------------------------------------------------------------------
def layer_spike_detector(layer_gid, layer_name, ignore_time, params={"withgid": True, "withtime": True, "to_file": True}):
#def layer_spike_detector(layer_gid, layer_name, params={"withgid": True, "withtime": True, "to_file": True, 'fbuffer_size': 8192}):
    #return []
    print ('spike detector for '+layer_name)
    #params.update({'label': layer_name, "start": float(ignore_time)})
    
    detector = nest.Create("spike_recorder",
                params={
                        "record_to": "ascii",
                        "label": layer_name})
    
    #params.update({'label': layer_name})
    #detector = nest.Create("spike_detector", params= params)
    
    log.debug("CONNECT %s %s", layer_gid, detector)
    nest.Connect(layer_gid, detector)
    
    #if layer_name in ['CSN','PTN','CMPf','MSN','FSI','STN','GPe','GPi','GPi_fake', 'GPi-']:
    #    pass
    #else:
    #    print (layer_name)
        # add multimeter just for to record V_m and conductance (inhibitory and excitatory) of a single cell each cell population
    #    nest_mm = nest.Create('multimeter',
    #                          params={"interval": 0.1, "record_from": ["V_m", "g_ex", "g_in"], "withgid": True, "to_file": True,
    #                                  'label': layer_name, 'withtime': True, "start": float(ignore_time),
    #                                  'use_gid_in_filename': True})  #
    #   nest.Connect(nest_mm, [random.choice(nest.GetNodes(layer_gid)[0])])
    return detector

def col_spike_detector(layer_gids_inside, layer_name, ignore_time, params = {"withgid": True, "withtime": True, "to_file": True}):
    params.update({'label': layer_name, "start": float(ignore_time)})
    # Add detector for all neuron types
    detector = nest.Create( "spike_detector", params= params )
    log.debug("CONNECT %s %s", layer_gids_inside, detector)
    nest.Connect( pre=layer_gids_inside, post=detector)

    return detector

#-------------------------------------------------------------------------------
# Returns the average firing rate of a population
# It is relative to the simulation duration `simDuration` and the population size `n`
#-------------------------------------------------------------------------------
# def findfile(keyword, root):
#     filelist = []
#     find_file_list = []
#     for root, dirs, files in os.walk(root):
#         for name in files:
#             fitfile = filelist.append(os.path.join(root, name))
#             # print(fitfile)
#             # print(os.path.join(root, name))
#     # print(filelist)
# #    print('...........................................')
#     for i in filelist:
#         if os.path.isfile(i):
#             # print(i)
#             if keyword in os.path.split(i)[1]:
#                 name, ext = os.path.splitext(os.path.split(i)[1])
#                 # print (ext)
#                 if ext == '.gdf':
#                     find_file_list.append(i)
#     return find_file_list
#
def average_fr(detector, simDuration, n):
    return detector.n_events / (float(simDuration) * float(n) / 1000.)
    

#     root = os.path.abspath('log/')
#     results_filelist = []
#     results_filelist.append(findfile(detector, root))
# #    print (results_filelist[0])
#     for i in range(len(results_filelist[0])):
#         file = results_filelist[0][i]
# #        print (file)
#         spike_list = pd.read_csv(file, header=None, delimiter=r"\s+").values
#         if i == 0:
#             sd_data = spike_list
#         else:
#             sd_data = np.concatenate((sd_data, spike_list), axis=0)
#     return nest.GetStatus(sd_data.shape[0] / (float(simDuration) * float(n) / 1000.))
# #populate a dictionary with all the spikes from gdf files
def average_fr_pre(detector,  n, start_time, end_time):
    circle_events=nest.GetStatus(detector, 'events')[0]
    circle_events_times=circle_events['times']
    print ('#####################################')
    print (circle_events)
    print (circle_events_times)
    print (len(circle_events_times))
    circle_events_select=circle_events_times[np.logical_and(circle_events['times']>=start_time, circle_events['times']<=end_time)]
    return len(circle_events_select)/(float(end_time-start_time) * float(n) / 1000.)

#-------------------------------------------------------------------------------
# Returns the average firing rate of one topology layer from gdf files
#
#-------------------------------------------------------------------------------
def get_firing_rate_from_gdf_files(layer_name, layer_gid, simDuration, neuron_nb):
    if hapc.Rank()==0:
        macro_columns_activity = []
        macro_columns_spikes = []
        pop,pop_gid = {},{}
        gdf_path = 'log/'
        onlyfiles = [f for f in os.listdir(gdf_path) if os.path.isfile(os.path.join(gdf_path, f))]
        is_first = True
        for i in onlyfiles:
            if layer_name == i[:len(layer_name)] and i[-4:]=='.gdf':
                if os.stat(gdf_path+i).st_size>0:
                    try:
                        a = np.loadtxt(gdf_path+i)
                        if is_first:
                            if len(a)!=0:
                                pop[layer_name] = a
                                is_first = False
                        else:
                            if len(pop[layer_name].shape)==1:
                                pop[layer_name]=np.expand_dims(pop[layer_name], axis=0)
                            if len(a.shape)==1:
                                a=np.expand_dims(a, axis=0)
                            pop[layer_name] = np.concatenate((pop[layer_name], a), axis=0)
                    except:
                        pass
        if is_first:
            pop[layer_name] = np.array([])
        if len(pop[layer_name])>0:
            return len(pop[layer_name])/ (float(simDuration) * float(neuron_nb) / 1000.)
        else:
            return 0.


#-------------------------------------------------------------------------------
# Returns the average firing rate of one macro column
#
#-------------------------------------------------------------------------------
def get_firing_rate_macro_column(layer_name, macro_column_neuron_gids, start_time, end_time):
    print ('macro column neuron gids for '+ layer_name)
    if hapc.Rank()==0:
        macro_columns_activity = []
        macro_columns_spikes = []
        pop,pop_gid = {},{}
        gdf_path = 'log/'
        onlyfiles = [f for f in os.listdir(gdf_path) if os.path.isfile(os.path.join(gdf_path, f))]
        is_first = True
        for i in onlyfiles:
            if layer_name == i[:len(layer_name)] and i[-4:]=='.gdf':
                if os.stat(gdf_path+i).st_size>0:
                    try:
                        a = np.loadtxt(gdf_path+i)
                        if is_first:
                            if len(a)!=0:
                                pop[layer_name] = a
                                is_first = False
                        else:
                            if len(pop[layer_name].shape)==1:
                                pop[layer_name]=np.expand_dims(pop[layer_name], axis=0)
                            if len(a.shape)==1:
                                a=np.expand_dims(a, axis=0)
                            pop[layer_name] = np.concatenate((pop[layer_name], a), axis=0)
                    except:
                        pass
        if is_first:
            pop[layer_name] = np.array([])
        if len(pop[layer_name])>0:
            if len(pop[layer_name].shape) == 1:
                pop[layer_name] = np.expand_dims(pop[layer_name], axis=0)
            my_arg = np.argsort(pop[layer_name][:,1])
            pop[layer_name] = pop[layer_name][my_arg,:]
            t_idx=np.where(np.logical_and(pop[layer_name][:,1]>=start_time, pop[layer_name][:,1]<=end_time))
            pop[layer_name] = pop[layer_name][t_idx[0]]
            if len(pop[layer_name])>0:
                for mc_gids in macro_column_neuron_gids:
                    gid_index=np.zeros((0))
                    for g in mc_gids:
                        if len(np.nonzero(pop[layer_name][:, 0]== g)[0])>0:
                            gid_index=np.append(gid_index, np.nonzero(pop[layer_name][:, 0]== g)[0])
                    gid_index=gid_index.astype(np.int32)
                    if len(gid_index)>0:
                        macro_columns_activity.append(len(gid_index)/len(macro_column_neuron_gids)/(end_time-start_time)*1000)
                        macro_columns_spikes.append(pop[layer_name][gid_index, :])
                    else:
                        macro_columns_activity.append(0)
                        macro_columns_spikes.append(np.array([0]))
                return (macro_columns_activity)

            else:
                for mc_gids in macro_column_neuron_gids:
                    macro_columns_activity.append(0)
                return macro_columns_activity
        else:
            for mc_gids in macro_column_neuron_gids:
                macro_columns_activity.append(0)
            return macro_columns_activity


#-------------------------------------------------------------------------------
# Returns the average firing rate of one micro column
#
#-------------------------------------------------------------------------------
def get_firing_rate_micro_column(layer_name, micro_column_neuron_gids, start_time, end_time, macro_column_idx):
    print ('micro column neuron gids for '+ layer_name)
    if hapc.Rank()==0:
        micro_columns_activity = []
        micro_columns_spikes = []
        pop,pop_gid = {},{}
        gdf_path = 'log/'
        onlyfiles = [f for f in os.listdir(gdf_path) if os.path.isfile(os.path.join(gdf_path, f))]
        is_first = True
        for i in onlyfiles:
            if layer_name == i[:len(layer_name)] and i[-4:]=='.gdf':
                if os.stat(gdf_path+i).st_size>0:
                    try:
                        a = np.loadtxt(gdf_path+i)
                        if is_first:
                            if len(a)!=0:
                                pop[layer_name] = a
                                is_first = False
                        else:
                            if len(pop[layer_name].shape)==1:
                                pop[layer_name]=np.expand_dims(pop[layer_name], axis=0)
                            if len(a.shape)==1:
                                a=np.expand_dims(a, axis=0)
                            pop[layer_name] = np.concatenate((pop[layer_name], a), axis=0)
                            #pop[layer_name] = np.append(pop[layer_name],a,axis=0)
                    except:
                        pass
        if is_first:
            pop[layer_name] = np.array([])
        if len(pop[layer_name])>0:
            if len(pop[layer_name].shape) == 1:
                pop[layer_name] = np.expand_dims(pop[layer_name], axis=0)
            my_arg = np.argsort(pop[layer_name][:,1])
            pop[layer_name] = pop[layer_name][my_arg,:]
            t_idx=np.where(np.logical_and(pop[layer_name][:,1]>=start_time, pop[layer_name][:,1]<=end_time))
            pop[layer_name] = pop[layer_name][t_idx[0]]
            if len(pop[layer_name])>0:
                for mc_gids in micro_column_neuron_gids:
                    gid_index=np.zeros((0))
                    for g in mc_gids:
                        if len(np.nonzero(pop[layer_name][:, 0]== g)[0])>0:
                            gid_index = np.append(gid_index, np.nonzero(pop[layer_name][:, 0] == g)[0])
                    gid_index = gid_index.astype(np.int32)
                    if len(gid_index)>0:
                        micro_columns_activity.append(len(gid_index)/len(micro_column_neuron_gids)/(end_time-start_time)*1000)
                        micro_columns_spikes.append(pop[layer_name][gid_index, :])
                    else:
                        micro_columns_activity.append(0)
                        micro_columns_spikes.append(np.array([0]))
                return (micro_columns_activity)
            else:
                for mc_gids in micro_column_neuron_gids:
                    micro_columns_activity.append(0)
                return micro_columns_activity
        else:
            for mc_gids in micro_column_neuron_gids:
                micro_columns_activity.append(0)
            return micro_columns_activity

#-------------------------------------------------------------------------------
# Returns the number of neurons inside a layer
#-------------------------------------------------------------------------------
def count_layer(layer_gid):
  return len(layer_gid) #len(nest.GetNodes(layer_gid)[0])

#-------------------------------------------------------------------------------
# Returns the positions of neurons inside a layer -sun-20180911
#-------------------------------------------------------------------------------
def get_position(layer_gid):
  return 0 #ntop.GetPosition(layer_gid)

#-------------------------------------------------------------------------------
# Returns the connections of neurons inside a layer -sun-20180912
#-------------------------------------------------------------------------------
def get_connection(gids):
  return nest.GetConnections(gids)

#-------------------------------------------------------------------------------
# Make a table of connections -sun-20180912
#-------------------------------------------------------------------------------
def get_connection_summary(region_params, layers, region):
    if region=='S1':
        import matplotlib.pyplot as plt
        from scipy import stats
        S1_internal_connection = np.load('ctx/'+ region_params['S1']['connection_info']['S1toS1'])
        columns = ['pre_nodes_num', 'post_nodes_num', 'p_center', 'sigma', 'analy_conn_num', 'conn_num', 'weight_per_neuron', 'weight_per_connection']
        for post_l in layers.keys():
            rows_in = []
            cell_text_in = []
            conn_num_in_excitatory = 0.
            conn_num_in_inhibitory = 0.
            E_weight_per_conn_in = 0.
            E_weight_per_neuron_in = 0.
            I_weight_per_conn_in = 0.
            I_weight_per_neuron_in = 0.
            for pre_l in layers.keys():
                print(pre_l, post_l)
                p_center_in = S1_internal_connection[pre_l][post_l]['p_center']
                sigma_in = S1_internal_connection[pre_l][post_l]['sigma'] / 1000.
                # analytical_total_conn_num = 0.0
                pre_l_nodes = nest.GetNodes(layers[pre_l])[0]
                post_l_nodes = nest.GetNodes(layers[post_l])[0]
                analogical_total_conn_num = 0.0
                if p_center_in!=0. and sigma_in!=0.:
                  rows_in.append(pre_l)
                  print("layer " + post_l + " in-degree output")
                  connectome = nest.GetConnections(pre_l_nodes, post_l_nodes )
                  connection_weights = list(nest.GetStatus(connectome, "weight"))
                  conn_num_in = len(connectome)
                  weight_per_connection=0
                  if len(connection_weights)>0:
                      weight_per_connection=sum(connection_weights)/len(connection_weights)
                  weight_per_neuron = 0.0
                  weight_per_neuron = sum(connection_weights) / len(post_l_nodes)
                  analytical_total_conn_num =len(pre_l_nodes)*p_center_in*2*np.pi*sigma_in*sigma_in
                  cell_text_in.append([len(pre_l_nodes), len(post_l_nodes), S1_internal_connection[pre_l][post_l]['p_center'],S1_internal_connection[pre_l][post_l]['sigma'],analytical_total_conn_num, conn_num_in/len(post_l_nodes),weight_per_neuron, weight_per_connection])
                  if pre_l in ['S1_L2_Pyr', 'S1_L3_Pyr', 'S1_L4_Pyr', 'S1_L5A_Pyr', 'S1_L5B_Pyr', 'S1_L6_Pyr']:
                    print (pre_l)
                    conn_num_in_excitatory +=conn_num_in
                    E_weight_per_conn_in += weight_per_connection
                    E_weight_per_neuron_in += weight_per_neuron
                    #E_weight_neuron_nb_in += 1
                  else:
                    conn_num_in_inhibitory +=conn_num_in
                    I_weight_per_conn_in  += weight_per_connection
                    I_weight_per_neuron_in += weight_per_neuron
            if len(rows_in)>0:
                columns[5] = 'conn_num/post_neuron_nb'
                rows_in.append('Total Excitatory')
                cell_text_in.append(['/', '/', '/', '/', '/', conn_num_in_excitatory/len(post_l_nodes), E_weight_per_neuron_in, E_weight_per_conn_in])
                rows_in.append('Total Inhibitory')
                cell_text_in.append(['/', '/', '/', '/', '/', conn_num_in_inhibitory/len(post_l_nodes), I_weight_per_neuron_in, I_weight_per_conn_in])
                rows_in.append('Total')
                cell_text_in.append(['/', '/', '/', '/', '/', conn_num_in_excitatory/len(post_l_nodes)+conn_num_in_inhibitory/len(post_l_nodes), E_weight_per_neuron_in+I_weight_per_neuron_in,E_weight_per_conn_in+I_weight_per_conn_in ])
                rows_in.append('I/E')
                if conn_num_in_excitatory > 0. and E_weight_per_neuron_in!=0 and E_weight_per_conn_in!=0:
                    cell_text_in.append(['/', '/', '/', '/', '/', conn_num_in_inhibitory / conn_num_in_excitatory, I_weight_per_neuron_in/E_weight_per_neuron_in, I_weight_per_conn_in/E_weight_per_conn_in])
                else:
                    cell_text_in.append(['/', '/', '/', '/', '/', '/', 0.0, 0.0])
                fig = plt.figure(figsize=(20, 10))
                ax = plt.subplot(111, frame_on=False)
                ax.xaxis.set_visible(False)
                ax.yaxis.set_visible(False)
                ax.title.set_text(post_l + ' cell in degree connections')
                plt.table(cellText=cell_text_in , rowLabels=rows_in,colLabels=columns, loc='center')
                plt.savefig('log/'+post_l + '_cell_in_degree_connections.png')

        for pre_l in layers.keys():
            rows_out = []
            cell_text_out = []
            conn_num_out_excitatory=0.
            conn_num_out_inhibitory=0.
            E_weight_per_conn_out = 0.0
            E_weight_per_neuron_out = 0.0
            I_weight_per_conn_out = 0.0
            I_weight_per_neuron_out = 0.0
            for post_l in layers.keys():
                print (pre_l, post_l)
                p_center_out = S1_internal_connection[pre_l][post_l]['p_center']
                sigma_out = S1_internal_connection[pre_l][post_l]['sigma']/1000.
                #analytical_total_conn_num = 0.0
                pre_l_nodes=nest.GetNodes(layers[pre_l])[0]
                post_l_nodes = nest.GetNodes(layers[post_l])[0]
                # out-degree
                #analogical_total_conn_num=0.0
                if p_center_out!=0. and sigma_out!=0.:
                  rows_out.append(post_l)
                  print ("layer " + pre_l +" out-degree output")
                  connectome = nest.GetConnections(pre_l_nodes, post_l_nodes)
                  connection_weights = list(nest.GetStatus(connectome, "weight"))
                  weight_per_connection=0
                  if len(connection_weights)>0:
                      weight_per_connection = sum(connection_weights)/len(connection_weights)
                  weight_per_neuron=0.0
                  weight_per_neuron=sum(connection_weights)/len(pre_l_nodes)
                  conn_num_out = len(connectome)
                  analytical_total_conn_num = len(post_l_nodes)*p_center_out*2*np.pi*sigma_out*sigma_out
                  cell_text_out.append([len(pre_l_nodes), len(post_l_nodes), S1_internal_connection[pre_l][post_l]['p_center'], S1_internal_connection[pre_l][post_l]['sigma'],analytical_total_conn_num, conn_num_out/len(pre_l_nodes),weight_per_neuron, weight_per_connection ])
                  if pre_l in ['S1_L2_Pyr', 'S1_L3_Pyr', 'S1_L4_Pyr', 'S1_L5A_Pyr', 'S1_L5B_Pyr', 'S1_L6_Pyr']:
                    conn_num_out_excitatory += conn_num_out
                    E_weight_per_conn_out += weight_per_connection
                    E_weight_per_neuron_out += weight_per_neuron
                  else:
                    print (pre_l)
                    conn_num_out_inhibitory += conn_num_out
                    I_weight_per_conn_out  += weight_per_connection
                    I_weight_per_neuron_out += weight_per_neuron
            if len(rows_out)>0:
                columns[5]='conn_num/pre_neuron_nb'
                rows_out.append('Total Excitatory')
                cell_text_out.append(['/', '/', '/', '/', '/', conn_num_out_excitatory/len(pre_l_nodes), E_weight_per_neuron_out, E_weight_per_conn_out])
                rows_out.append('Total Inhibitory')
                cell_text_out.append(['/', '/', '/', '/', '/', conn_num_out_inhibitory/len(pre_l_nodes), I_weight_per_neuron_out, I_weight_per_conn_out])

                rows_out.append('Total')
                cell_text_out.append(['/', '/', '/', '/', '/',conn_num_out_excitatory/len(pre_l_nodes)+conn_num_out_inhibitory/len(pre_l_nodes), E_weight_per_neuron_out+I_weight_per_neuron_out, E_weight_per_conn_out+I_weight_per_conn_out])
                rows_out.append('I/E')
                if conn_num_out_excitatory > 0. and E_weight_per_neuron_out!=0 and E_weight_per_conn_out!=0:
                    cell_text_out.append(['/', '/', '/', '/', '/', conn_num_out_inhibitory / conn_num_out_excitatory, I_weight_per_neuron_out/E_weight_per_neuron_out, I_weight_per_conn_out/E_weight_per_conn_out])
                else:
                    cell_text_out.append(['/', '/', '/', '/', '/','/', 0.0, 0.0])

            fig = plt.figure(figsize=(20, 10))
            ax = plt.subplot(111, frame_on=False)
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)
            ax.title.set_text(pre_l+' cell out degree connections')
            plt.table(cellText=cell_text_out, rowLabels=rows_out, colLabels=columns, loc='center')
            plt.savefig('log/'+pre_l+'_cell_out_degree_connections.png')
            #table_in = plt.figure()
    elif region=='M1':
        import matplotlib.pyplot as plt
        from scipy import stats
        S1_internal_connection = np.load('ctx/'+ region_params['M1']['connection_info']['M1toM1'])
        columns = ['pre_nodes_num', 'post_nodes_num', 'p_center', 'sigma','analy_conn_num', 'conn_num', 'weight_per_neuron', 'weight_per_connection']
        for post_l in layers.keys():
            rows_in = []
            cell_text_in = []
            conn_num_in_excitatory = 0.
            conn_num_in_inhibitory = 0.
            E_weight_per_conn_in = 0.0
            E_weight_per_neuron_in = 0.0
            I_weight_per_conn_in = 0.0
            I_weight_per_neuron_in = 0.0
            for pre_l in layers.keys():
                print(pre_l, post_l)
                p_center_in = S1_internal_connection[pre_l][post_l]['p_center']
                sigma_in = S1_internal_connection[pre_l][post_l]['sigma'] / 1000.
                # analytical_total_conn_num = 0.0
                pre_l_nodes = nest.GetNodes(layers[pre_l])[0]
                post_l_nodes = nest.GetNodes(layers[post_l])[0]
                analogical_total_conn_num = 0.0
                if p_center_in!=0. and sigma_in!=0.:
                  rows_in.append(pre_l)
                  print("layer " + post_l + " in-degree output")
                  connectome = nest.GetConnections(pre_l_nodes, post_l_nodes )
                  connection_weights = list(nest.GetStatus(connectome, "weight"))
                  conn_num_in = len(connectome)
                  weight_per_connection=0
                  if len(connection_weights)>0:
                      weight_per_connection=sum(connection_weights)/len(connection_weights)
                  weight_per_neuron = 0.0
                  weight_per_neuron = sum(connection_weights) / len(post_l_nodes)
                  analytical_total_conn_num =len(pre_l_nodes)*p_center_in*2*np.pi*sigma_in*sigma_in
                  cell_text_in.append([len(pre_l_nodes), len(post_l_nodes), S1_internal_connection[pre_l][post_l]['p_center'],S1_internal_connection[pre_l][post_l]['sigma'],analytical_total_conn_num, conn_num_in/len(post_l_nodes),weight_per_neuron, weight_per_connection])
                  if pre_l in ['M1_L23_CC', 'M1_L5A_CC', 'M1_L5A_CS', 'M1_L5A_CT', 'M1_L5B_CC', 'M1_L5B_CS', 'M1_L5B_PT', 'M1_L6_CT']:
                    print (pre_l)
                    conn_num_in_excitatory +=conn_num_in
                    E_weight_per_conn_in += weight_per_connection
                    E_weight_per_neuron_in += weight_per_neuron
                    #E_weight_neuron_nb_in += 1
                  else:
                    conn_num_in_inhibitory +=conn_num_in
                    I_weight_per_conn_in  += weight_per_connection
                    I_weight_per_neuron_in += weight_per_neuron
            if len(rows_in)>0:
                columns[5] = 'conn_num/post_neuron_nb'
                rows_in.append('Total Excitatory')
                cell_text_in.append(['/', '/', '/', '/', '/', conn_num_in_excitatory/len(post_l_nodes), E_weight_per_neuron_in, E_weight_per_conn_in])
                rows_in.append('Total Inhibitory')
                cell_text_in.append(['/', '/', '/', '/', '/', conn_num_in_inhibitory/len(post_l_nodes), I_weight_per_neuron_in, I_weight_per_conn_in])
                rows_in.append('Total')
                cell_text_in.append(['/', '/', '/', '/', '/', conn_num_in_excitatory/len(post_l_nodes)+conn_num_in_inhibitory/len(post_l_nodes), E_weight_per_neuron_in+I_weight_per_neuron_in,E_weight_per_conn_in+I_weight_per_conn_in ])
                rows_in.append('I/E')
                if conn_num_in_excitatory > 0. and E_weight_per_neuron_in!=0 and E_weight_per_conn_in!=0:
                    cell_text_in.append(['/', '/', '/', '/', '/', conn_num_in_inhibitory / conn_num_in_excitatory, I_weight_per_neuron_in/E_weight_per_neuron_in, I_weight_per_conn_in/E_weight_per_conn_in])
                else:
                    cell_text_in.append(['/', '/', '/', '/', '/', '/', 0.0, 0.0])
                fig = plt.figure(figsize=(20, 10))
                ax = plt.subplot(111, frame_on=False)
                ax.xaxis.set_visible(False)
                ax.yaxis.set_visible(False)
                ax.title.set_text(post_l + ' cell in degree connections')
                plt.table(cellText=cell_text_in , rowLabels=rows_in,colLabels=columns, loc='center')
                plt.savefig('log/'+post_l + '_cell_in_degree_connections.png')

        for pre_l in layers.keys():
            rows_out = []
            cell_text_out = []
            conn_num_out_excitatory=0.
            conn_num_out_inhibitory=0.
            E_weight_per_conn_out = 0.0
            E_weight_per_neuron_out = 0.0
            I_weight_per_conn_out = 0.0
            I_weight_per_neuron_out = 0.0
            for post_l in layers.keys():
                print (pre_l, post_l)
                p_center_out = S1_internal_connection[pre_l][post_l]['p_center']
                sigma_out = S1_internal_connection[pre_l][post_l]['sigma']/1000.
                #analytical_total_conn_num = 0.0
                pre_l_nodes=nest.GetNodes(layers[pre_l])[0]
                post_l_nodes = nest.GetNodes(layers[post_l])[0]
                # out-degree
                #analogical_total_conn_num=0.0
                if p_center_out!=0. and sigma_out!=0.:
                  rows_out.append(post_l)
                  print ("layer " + pre_l +" out-degree output")
                  connectome = nest.GetConnections(pre_l_nodes, post_l_nodes)
                  connection_weights = list(nest.GetStatus(connectome, "weight"))
                  weight_per_connection=0
                  if len(connection_weights)>0:
                      weight_per_connection = sum(connection_weights)/len(connection_weights)
                  weight_per_neuron=0.0
                  weight_per_neuron=sum(connection_weights)/len(pre_l_nodes)
                  conn_num_out = len(connectome)
                  analytical_total_conn_num = len(post_l_nodes)*p_center_out*2*np.pi*sigma_out*sigma_out
                  cell_text_out.append([len(pre_l_nodes), len(post_l_nodes), S1_internal_connection[pre_l][post_l]['p_center'], S1_internal_connection[pre_l][post_l]['sigma'],analytical_total_conn_num, conn_num_out/len(pre_l_nodes),weight_per_neuron, weight_per_connection ])
                  if pre_l in ['M1_L23_CC', 'M1_L5A_CC', 'M1_L5A_CS', 'M1_L5A_CT', 'M1_L5B_CC', 'M1_L5B_CS', 'M1_L5B_PT', 'M1_L6_CT']:
                    conn_num_out_excitatory += conn_num_out
                    E_weight_per_conn_out += weight_per_connection
                    E_weight_per_neuron_out += weight_per_neuron
                  else:
                    print (pre_l)
                    conn_num_out_inhibitory += conn_num_out
                    I_weight_per_conn_out  += weight_per_connection
                    I_weight_per_neuron_out += weight_per_neuron

            if len(rows_out)>0:
                columns[5]='conn_num/pre_neuron_nb'
                rows_out.append('Total Excitatory')
                cell_text_out.append(['/', '/', '/', '/', '/', conn_num_out_excitatory/len(pre_l_nodes), E_weight_per_neuron_out, E_weight_per_conn_out])
                rows_out.append('Total Inhibitory')
                cell_text_out.append(['/', '/', '/', '/', '/', conn_num_out_inhibitory/len(pre_l_nodes), I_weight_per_neuron_out, I_weight_per_conn_out])

                rows_out.append('Total')
                cell_text_out.append(['/', '/', '/', '/', '/',conn_num_out_excitatory/len(pre_l_nodes)+conn_num_out_inhibitory/len(pre_l_nodes), E_weight_per_neuron_out+I_weight_per_neuron_out, E_weight_per_conn_out+I_weight_per_conn_out])
                rows_out.append('I/E')
                if conn_num_out_excitatory > 0. and E_weight_per_neuron_out!=0 and E_weight_per_conn_out!=0:
                    cell_text_out.append(['/', '/', '/', '/', '/', conn_num_out_inhibitory / conn_num_out_excitatory, I_weight_per_neuron_out/E_weight_per_neuron_out, I_weight_per_conn_out/E_weight_per_conn_out])
                else:
                    cell_text_out.append(['/', '/', '/', '/', '/','/', 0.0, 0.0])

            fig = plt.figure(figsize=(20, 10))
            ax = plt.subplot(111, frame_on=False)
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)
            ax.title.set_text(pre_l+' cell out degree connections')
            plt.table(cellText=cell_text_out, rowLabels=rows_out, colLabels=columns, loc='center')
            plt.savefig('log/'+pre_l+'_cell_out_degree_connections.png')
            #table_in = plt.figure()

# -------------------------------------------------------------------------------
#Generator for efficient looping over local nodes
#Assumes nodes is a continous list of gids [1, 2, 3, ...], e.g., as
#returned by Create. Only works for nodes with proxies, i.e.,
#regular neurons.
# -------------------------------------------------------------------------------
def get_local_nodes(nodes):
  nvp = nest.GetKernelStatus('total_num_virtual_procs')  # step size
  i = 0
  print (len(nodes))
  while i < len(nodes):
    if nest.GetStatus([nodes[i]], 'local')[0]:
      yield nodes[i]
      i += nvp
    else:
      i += 1

def save_layers_position(layer_name, layer, positions):
    ids = np.array(layer.tolist())   # FIXME THIS IS BUG #1361  should not use tolist
    gid_and_positions=np.column_stack((positions, ids))
    if not os.path.exists('log/'+layer_name+'.txt'):
        np.savetxt('log/'+layer_name+'.txt', gid_and_positions, fmt='%1.3f')
    
# -------------------------------------------------------------------------------
#randomizing the membarne potential
#
# -------------------------------------------------------------------------------
def randomizing_mp(layer, Vth, Vrest):
    layer.set({"V_m": Vrest + (Vth - Vrest) * np.random.rand()})


#######
# CTX #
#######

######
# S1 #
######

def gen_neuron_postions_ctx(layer_dep, layer_thickness, nbneuron, S1_layer_size, scalefactor, pop_name):
    neuron_per_grid = math.pow((nbneuron / layer_thickness), 1.0 / 3)
    Sub_Region_Architecture=[0, 0, 0]
    Sub_Region_Architecture[0] = int(np.round(neuron_per_grid * S1_layer_size[0] * scalefactor[0]))
    Sub_Region_Architecture[1] = int(np.round(neuron_per_grid * S1_layer_size[1] * scalefactor[1]))
    Sub_Region_Architecture[2] = int(np.round(neuron_per_grid * layer_thickness))

    Neuron_pos_x = np.linspace(-0.5*scalefactor[0], 0.5*scalefactor[0], num=Sub_Region_Architecture[0], endpoint=True)
    Neuron_pos_y = np.linspace(-0.5*scalefactor[1], 0.5*scalefactor[1], num=Sub_Region_Architecture[1], endpoint=True)
    Neuron_pos_z = np.linspace(layer_dep, (layer_dep+layer_thickness), num=Sub_Region_Architecture[2], endpoint=True)
    Neuron_pos_z = Neuron_pos_z-S1_layer_size[2]/2.
    Neuron_pos = []
    for i in range(Sub_Region_Architecture[0]):
        for j in range(Sub_Region_Architecture[1]):
            for k in range(Sub_Region_Architecture[2]):
                Neuron_pos.append([Neuron_pos_x[i], Neuron_pos_y[j], Neuron_pos_z[k]])
    #np.savez( 'ctx/'+pop_name, Neuron_pos=Neuron_pos)
    return Neuron_pos

#-----------------------------------------------------------------------------------
# Create a neurons population for S1 M1(?)
#-----------------------------------------------------------------------------------
def create_layers_ctx(positions, element):
    print('creating %d neurons in layer' % len(positions))
    layer = nest.Create(element, positions=nest.spatial.free(positions, edge_wrap=True))  # nest 3
    print('created %d neurons' % len(layer.tolist()))
    return layer



#-----------------------------------------------------------------------------------
# connect (internal regional connection) nest 3
#-----------------------------------------------------------------------------------
def connect_layers_ctx(pre_SubSubRegion, post_SubSubRegion, conn_params):
    sigma_x = conn_params['sigma']/1000.
    sigma_y = conn_params['sigma']/1000.
    #print (conn_params)
    weight_distribution=conn_params['weight_distribution']
    if weight_distribution == 'lognormal':

        conn_dict = {'rule': 'pairwise_bernoulli',
                     'p': conn_params['p_center']*nest.spatial_distributions.gaussian2D(
                         nest.spatial.distance.x, nest.spatial.distance.y, std_x=sigma_x, std_y=sigma_y),
                     'mask': {'box':
                                  {'lower_left': [-1., -1., -2.],
                                   'upper_right': [1., 1., 2.]}},
                     'allow_autapses': False,
                     'allow_multapses': False,
                     'allow_oversized_mask': True
                     }
        syn_spec = {'weight': nest.random.lognormal(mean=conn_params['weight'], std=1.0), 'delay': conn_params['delay']}
    else:
        conn_dict = {'rule': 'pairwise_bernoulli',
                     'p': conn_params['p_center']*nest.spatial_distributions.gaussian2D(
                         nest.spatial.distance.x, nest.spatial.distance.y, std_x=sigma_x, std_y=sigma_y),
                     'mask': {'box':
                                  {'lower_left': [-1., -1., -2.],
                                   'upper_right': [1., 1., 2.]}
                              },
                     'allow_autapses': False,
                     'allow_multapses': False,
                     'allow_oversized_mask': True
                     }
        syn_spec = {'weight': conn_params['weight'], 'delay': conn_params['delay']}
    if conn_params['p_center'] != 0.0 and sigma_x != 0.0 and conn_params['weight'] != 0.0:
        nest.Connect(pre_SubSubRegion, post_SubSubRegion, conn_dict, syn_spec)


#######
# CTX #
#######

######
# M1 #
######

def create_layers_ctx_M1(extent, center, positions, elements):
    newlayer = 0 #ntop.CreateLayer({'extent': extent, 'center': center, 'positions': positions, 'elements': elements})
    return newlayer

# connect (intra regional connection?)
def connect_layers_ctx_M1(pre_SubSubRegion, post_SubSubRegion, conn_dict):
    sigma_x = conn_dict['sigma']/1000.
    sigma_y = conn_dict['sigma']/1000.
    weight_distribution=conn_dict['weight_distribution']
    if weight_distribution == 'lognormal':
        conndict = {'connection_type': 'divergent',
                    'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.],}},
                    'kernel': {
                        'gaussian2D': {'p_center': float(conn_dict['p_center']), 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                    'weights': {'lognormal': {'mu': float(conn_dict['weight']), 'sigma': 1.0}},
                    'delays': float(conn_dict['delay']),
                    'allow_autapses': False,
                    'allow_multapses': False}
    else:
        conndict = {'connection_type': 'divergent',
                    'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.],}},
                    'kernel': {
                        'gaussian2D': {'p_center': float(conn_dict['p_center']), 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                    'weights': float(conn_dict['weight']),
                    'delays': float(conn_dict['delay']),
                    'allow_autapses': False,
                    'allow_multapses': False}
    if conn_dict['p_center'] != 0.0 and sigma_x != 0.0 and conn_dict['weight'] != 0.0:
        #ntop.ConnectLayers(pre_SubSubRegion, post_SubSubRegion, conndict)
        assert False


######
# TH #
######

def create_layers_th(positions, elements):
    print('creating %d neurons in layer' % len(positions))
    layer = nest.Create(elements, positions=nest.spatial.free(positions, edge_wrap=True))  # nest 3
    print('created %d neurons' % len(layer.tolist()))
    return layer

# connect (intra regional connection?)
def connect_layers_th(pre_SubSubRegion, post_SubSubRegion, conn_params):
    sigma_x = conn_params['sigma']
    sigma_y = conn_params['sigma']

    conn_dict = {'rule': 'pairwise_bernoulli',
                 'p': conn_params['p_center'] * nest.spatial_distributions.gaussian2D(
                     nest.spatial.distance.x, nest.spatial.distance.y, std_x=sigma_x, std_y=sigma_y),
                 'mask': {'box':
                              {'lower_left': [-1., -1., -2.],
                               'upper_right': [1., 1., 2.]}
                          },
                 'allow_autapses': False,
                 'allow_multapses': False,
                 'allow_oversized_mask': True
                 }
    syn_spec = {'weight': conn_params['weight'], 'delay': conn_params['delay']}

    if sigma_x != 0 and conn_params['p_center']!=0. :
        nest.Connect(pre_SubSubRegion, post_SubSubRegion, conn_dict, syn_spec)

def add_poisson_generator(layer_gid, n_type, layer_name, ignore_time, region):      #
    ini_time = ignore_time - 150
    ini_time_ini = ignore_time - 300
    if region=='M1':
        if n_type == "E":
            if layer_name in ['M1_L23_CC']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 800.0, "start": float( ini_time - 40. )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.0, 'delay': 1.5} )
            elif layer_name in ['M1_L5A_CC']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 900.0, "start": float( ini_time - 20. )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.5, 'delay': 1.5} )
            elif layer_name in ['M1_L5A_CS']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 900.0, "start": float( ini_time + 30. )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.5, 'delay': 1.5} )
            elif layer_name in ['M1_L5A_CT']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 900.0, "start": float( ini_time + 10. )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.5, 'delay': 1.5} )
            elif layer_name in ['M1_L5B_CC']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 1050.0, "start": float( ini_time - 30. )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.5, 'delay': 1.5} )
            elif layer_name in ['M1_L5B_CS']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 1050.0, "start": float( ini_time + 20. )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.5, 'delay': 1.5} )
            elif layer_name in ['M1_L5B_PT']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 1050.0, "start": float( ini_time - 10. )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.5, 'delay': 1.5} )
            elif layer_name in ['M1_L6_CT']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 1050.0, "start": float( ini_time )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.0, 'delay': 1.5} )

        if n_type == "I":
            if layer_name in ['M1_L1_SBC']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 1100.0, "start": float( ini_time_ini - 50. )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.5, 'delay': 1.5} )
            elif layer_name in ['M1_L1_ENGC']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 1100.0, "start": float( ini_time_ini + 30. )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.5, 'delay': 1.5} )
            elif layer_name in ['M1_L23_PV']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 1350.0, "start": float( ini_time_ini - 40. )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.5, 'delay': 1.5} )
            elif layer_name in ['M1_L23_SST']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 650.0, "start": float( ini_time_ini + 40. )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.5, 'delay': 1.5} )
            elif layer_name in ['M1_L23_VIP']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 1400.0, "start": float( ini_time_ini + 20. )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.5, 'delay': 1.5} )
            elif layer_name in ['M1_L5A_PV']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 1300.0, "start": float( ini_time_ini - 30. )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.5, 'delay': 1.5} )
            elif layer_name in ['M1_L5A_SST']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 650.0, "start": float( ini_time_ini + 10. )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.5, 'delay': 1.5} )
            elif layer_name in ['M1_L5B_PV']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 1300.0, "start": float( ini_time_ini - 20. )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.5, 'delay': 1.5} )
            elif layer_name in ['M1_L5B_SST']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 700.0, "start": float( ini_time_ini + 50. )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.5, 'delay': 1.5} )
            elif layer_name in ['M1_L6_PV']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 1350.0, "start": float( ini_time_ini - 10. )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.5, 'delay': 1.5} )
            elif layer_name in ['M1_L6_SST']:
                PSG = nest.Create( 'poisson_generator', 1, params={'rate': 700.0, "start": float( ini_time_ini )} )
                nest.Connect( pre=PSG, post=layer_gid, syn_spec={'weight': 4.5, 'delay': 1.5} )
    elif region == 'S1':
        if n_type == "E":
            if layer_name in ['S1_L2_Pyr']:
                PSG = nest.Create('poisson_generator', 1, params={'rate': 600.0, "start": float(ini_time)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L3_Pyr']:
                PSG = nest.Create('poisson_generator', 1, params={'rate': 500.0, "start": float(ini_time)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L4_Pyr']:
                PSG = nest.Create('poisson_generator', 1,
                                  params={'rate': 500.0, "start": float(ini_time)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L5A_Pyr']:
                PSG = nest.Create('poisson_generator', 1,
                                  params={'rate': 1000.0, "start": float(ini_time)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L5B_Pyr']:
                PSG = nest.Create('poisson_generator', 1,
                                  params={'rate': 1000.0, "start": float(ini_time)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L6_Pyr']:
                PSG = nest.Create('poisson_generator', 1,
                                  params={'rate': 1100.0, "start": float(ini_time)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
        if n_type == "I":
            if layer_name in ['S1_L1_SBC']:
                PSG = nest.Create('poisson_generator', 1, params={'rate': 600.0, "start": float(
                    ini_time_ini)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L1_ENGC']:
                PSG = nest.Create('poisson_generator', 1, params={'rate': 600.0, "start": float(
                    ini_time_ini)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L2_SST']:
                PSG = nest.Create('poisson_generator', 1, params={'rate': 600.0, "start": float(
                    ini_time_ini)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L2_VIP']:
                PSG = nest.Create('poisson_generator', 1, params={'rate': 1200.0, "start": float(
                    ini_time_ini)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L2_PV']:
                PSG = nest.Create('poisson_generator', 1, params={'rate': 1100.0, "start": float(
                    ini_time_ini)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L3_SST']:
                PSG = nest.Create('poisson_generator', 1, params={'rate': 600.0, "start": float(
                    ini_time_ini)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L3_VIP']:
                PSG = nest.Create('poisson_generator', 1, params={'rate': 1200.0, "start": float(
                    ini_time_ini)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L3_PV']:
                PSG = nest.Create('poisson_generator', 1, params={'rate': 1100.0, "start": float(
                    ini_time_ini)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L4_SST']:
                PSG = nest.Create('poisson_generator', 1, params={'rate': 600.0, "start": float(
                    ini_time_ini)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L4_PV']:
                PSG = nest.Create('poisson_generator', 1, params={'rate': 1100.0, "start": float(
                    ini_time_ini)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L5A_SST']:
                PSG = nest.Create('poisson_generator', 1, params={'rate': 850., "start": float(
                    ini_time_ini)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L5A_PV']:
                PSG = nest.Create('poisson_generator', 1, params={'rate': 1600.0, "start": float(
                    ini_time_ini)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L5B_SST']:
                PSG = nest.Create('poisson_generator', 1, params={'rate': 850., "start": float(
                    ini_time_ini)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L5B_PV']:
                PSG = nest.Create('poisson_generator', 1, params={'rate': 1600.0, "start": float(
                    ini_time_ini)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L6_SST']:
                PSG = nest.Create('poisson_generator', 1, params={'rate': 850.5, "start": float(
                    ini_time_ini)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})
            elif layer_name in ['S1_L6_PV']:
                PSG = nest.Create('poisson_generator', 1, params={'rate': 1700.0, "start": float(
                    ini_time_ini)})  # , 'label': layer_name})
                nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 5.0, 'delay': 1.5})

    #else:print ('please check the region name for add poisson generator')
    elif region=='TH':##added by Carlos amigo san.
        if layer_name in ['TH_M1_IZ_thalamic_nucleus_TC']: ## added to compensate the input from BG so TC gets resting state same as other TH populations
            PSG = nest.Create('poisson_generator', 1, params={'rate': 210.0, "start": float(ini_time_ini)})   #higher rate than others.
            nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 50.0, 'delay': 1.5})
        else:
            PSG = nest.Create('poisson_generator', 1, params={'rate': 20.0, "start": float(ini_time_ini)})
            nest.Connect(pre=PSG, post=layer_gid, syn_spec={'weight': 50.0, 'delay': 1.5})
    else:print ('please check the region name for add poisson generator')

################################################################
# add poisson generator for each micro and macro column
#################################################################
def add_poisson_generator_pop(gids, layer_name):
    #def layer_spike_detector(layer_gid, layer_name, params={"withgid": True, "withtime": True, "to_file": True, 'fbuffer_size': 8192}):
    if layer_name == 'S1_L4_Pyr':
        PSG_arrow = nest.Create('poisson_generator', 1, params={'rate': 50.0}) #, 'label': layer_name})
        log.debug("CONNECT %s", "X"*100)
        nest.Connect(pre=PSG_arrow, post=layer_gid, syn_spec={'weight': 10.0, 'delay': 1.5})
    return PSG_arrow

#########################################################################
#
#########################################################################
def get_input_column_layers_ctx_M1(ctx_M1_layers):
    # tmp progress
    # make circles for bg input
    radius_big = 0.5 / np.cos(np.pi / 4.) / 2.
    radius_small = 0.2
    circle_center = [[0.25, np.tan(np.pi / 4.) / 4.],
                     [np.tan(np.pi / 4.) / 4., 0.25],
                     [-0.25, np.tan(np.pi / 4.) / 2.],
                     [-np.tan(np.pi / 4.) / 4., 0.25],
                     [-0.25, -np.tan(np.pi / 4.) / 4.],
                     [-np.tan(np.pi / 4.) / 4., -0.25],
                     [-np.tan(np.pi / 4.) / 4., 0.25],
                     [0.25, -np.tan(np.pi / 4.) / 4.]
                     ]
    circle_1_gids = []
    circle_2_gids = []
    circle_3_gids = []
    circle_4_gids = []
    circle_5_gids = []
    circle_6_gids = []
    circle_7_gids = []
    circle_8_gids = []
    gid_M1_L5B_PT = nest.GetNodes(ctx_M1_layers['M1_L5B_PT'])[0]
    neuron_positions_M1_L5B_PT = 0 #ntop.GetPosition(gid_M1_L5B_PT)
    circle_gids=[]
    for nn in range(len(gid_M1_L5B_PT)):
        print (neuron_positions_M1_L5B_PT[nn])
        print (circle_center[0])
        print(circle_center[1])
        print(circle_center[2])
        print(circle_center[3])
        print(circle_center[4])
        print(circle_center[5])
        if np.linalg.norm([(neuron_positions_M1_L5B_PT[nn][0] - circle_center[0][0]),
                           (neuron_positions_M1_L5B_PT[nn][1] - circle_center[0][1])]) <= radius_small:
            circle_1_gids.append(gid_M1_L5B_PT[nn])
        if np.linalg.norm([(neuron_positions_M1_L5B_PT[nn][0] - circle_center[1][0]),
                           (neuron_positions_M1_L5B_PT[nn][1] - circle_center[1][1])]) <= radius_small:
            circle_2_gids.append(gid_M1_L5B_PT[nn])
        if np.linalg.norm([(neuron_positions_M1_L5B_PT[nn][0] - circle_center[2][0]),
                           (neuron_positions_M1_L5B_PT[nn][1] - circle_center[2][1])]) <= radius_small:
            circle_3_gids.append(gid_M1_L5B_PT[nn])
        if np.linalg.norm([(neuron_positions_M1_L5B_PT[nn][0] - circle_center[3][0]),
                           (neuron_positions_M1_L5B_PT[nn][1] - circle_center[3][1])]) <= radius_small:
            circle_4_gids.append(gid_M1_L5B_PT[nn])
        if np.linalg.norm([(neuron_positions_M1_L5B_PT[nn][0] - circle_center[4][0]),
                           (neuron_positions_M1_L5B_PT[nn][1] - circle_center[4][1])]) <= radius_small:
            circle_5_gids.append(gid_M1_L5B_PT[nn])
        if np.linalg.norm([(neuron_positions_M1_L5B_PT[nn][0] - circle_center[5][0]),
                           (neuron_positions_M1_L5B_PT[nn][1] - circle_center[5][1])]) <= radius_small:
            circle_6_gids.append(gid_M1_L5B_PT[nn])
        if np.linalg.norm([(neuron_positions_M1_L5B_PT[nn][0] - circle_center[6][0]),
                           (neuron_positions_M1_L5B_PT[nn][1] - circle_center[6][1])]) <= radius_small:
            circle_7_gids.append(gid_M1_L5B_PT[nn])
        if np.linalg.norm([(neuron_positions_M1_L5B_PT[nn][0] - circle_center[7][0]),
                           (neuron_positions_M1_L5B_PT[nn][1] - circle_center[7][1])]) <= radius_small:
            circle_8_gids.append(gid_M1_L5B_PT[nn])
    circle_gids=[circle_1_gids, circle_2_gids, circle_3_gids, circle_4_gids, circle_5_gids, circle_6_gids, circle_7_gids, circle_8_gids]
    return circle_gids

##### Function below added taking as example Sun's code above get_input_column_layers_ctx_M1 #################
##### General function for M1, S1, M2 ########################################################################
def get_input_column_layers_ctx(ctx_layers,circle_center,radius_small,my_area): #my_area is 'M1' or 'S1'
    if my_area == 'M1':
        gid_pos_L5B = np.loadtxt('./log/M1_L5B_PT.txt') #ntop.GetPosition(gid_M1_L5B_PT)
        gid_pos_L5A = np.loadtxt('./log/M1_L5A_CS.txt') #ntop.GetPosition(gid_M1_L5B_PT)
    if my_area == 'S1':
        gid_pos_L5B = np.loadtxt('./log/S1_L5B_Pyr.txt') #ntop.GetPosition(gid_M1_L5B_PT)
        gid_pos_L5A = np.loadtxt('./log/S1_L5A_Pyr.txt') #ntop.GetPosition(gid_M1_L5B_PT)
        
    print('gids and pos l5a ', len(gid_pos_L5A))
    print('gids and pos l5b ', len(gid_pos_L5B))
    
    circle_gids_L5B,circle_gids_L5A = [],[]
    
    for i in np.arange(len(circle_center)):
        idx_L5B = np.where(np.linalg.norm([(gid_pos_L5B[:,1]-circle_center[i][0]),(gid_pos_L5B[:,2]-circle_center[i][1])],axis=0)<=radius_small)[0]
        print('number of neurons in channel ',str(i),'for ',my_area,' L5B: ',str(len(idx_L5B)))
        circle_gids_L5B.append([[int(x[0]),x[1:].tolist()] for x in gid_pos_L5B[idx_L5B,:]])

        idx_L5A = np.where(np.linalg.norm([(gid_pos_L5A[:,1]-circle_center[i][0]),(gid_pos_L5A[:,2]-circle_center[i][1])],axis=0)<=radius_small)[0]
        print('number of neurons in channel ',str(i),'for ',my_area,' L5A: ',str(len(idx_L5A)))
        circle_gids_L5A.append([[int(x[0]),x[1:].tolist()] for x in gid_pos_L5A[idx_L5A,:]])

    return [circle_gids_L5B,circle_gids_L5A] #circle_gids

def get_columns_data(layer_name,circle_center,radius_small,my_area=None):
    #### example ##########
    #pkj_M1 = get_columns_data('CB_M1_layer_pkj',bg_params['circle_center'] ,bg_params['channels_radius'])
    ##########################
    gid_pos = np.loadtxt('./log/'+layer_name+'.txt')
    print('gids and pos  ', len(gid_pos))
    circle_gids = []
    for i in np.arange(len(circle_center)):
        idx = np.where(np.linalg.norm([(gid_pos[:,1]-circle_center[i][0]),(gid_pos[:,2]-circle_center[i][1])],axis=0)<=radius_small)[0]
        print('number of neurons in channel ',str(i),'for ',layer_name,' : ',str(len(idx)))
        circle_gids.append([[int(x[0]),x[1:].tolist()] for x in gid_pos[idx,:]])
    return circle_gids #circle_gids

def get_macro_columns_data(layer_name,circle_center,radius_small,my_area=None):
    gid_pos = np.loadtxt('./log/'+layer_name+'.txt')
    print('gids and pos  ', len(gid_pos))
    circle_gids = []
    circle_gids_pos = []

    for i in np.arange(len(circle_center)):
        idx = np.where(np.linalg.norm([(gid_pos[:,1]-circle_center[i][0]),(gid_pos[:,2]-circle_center[i][1])],axis=0)<=radius_small)[0]
        print('number of neurons in channel ',str(i),'for ',layer_name,' : ',str(len(idx)))
        circle_gids.append([int(x[0]) for x in gid_pos[idx,:]])
        circle_gids_pos.append([x[1:].tolist() for x in gid_pos[idx, :]])
        if len(circle_gids_pos[i]) >= 1:
            np.savetxt('./log/' + my_area + '_macro_column_' + str(i)+'.txt', circle_gids_pos[i], fmt='%.3f')
    return circle_gids #circle_gids

def get_micro_columns_data(layer_name,circle_center,radius_small,my_area=None):
    gid_pos = np.loadtxt('./log/'+layer_name+'.txt')
    print('gids and pos  ', len(gid_pos))
    circle_gids = []
    circle_gids_pos = []
    for i in np.arange(len(circle_center)):
        idx = np.where(np.linalg.norm([(gid_pos[:,1]-circle_center[i][0]),(gid_pos[:,2]-circle_center[i][1])],axis=0)<=radius_small)[0]
        print('number of neurons in channel ',str(i),'for ',layer_name,' : ',str(len(idx)))
        circle_gids.append([int(x[0]) for x in gid_pos[idx,:]])
        circle_gids_pos.append([x[1:].tolist() for x in gid_pos[idx, :]])
        if len(circle_gids_pos[i]) >= 1:
            np.savetxt('./log/' + my_area + '_micro_column_' + str(i)+'.txt', circle_gids_pos[i], fmt='%.3f')
    return circle_gids #circle_gids


'''
######
# M2 #
######

def create_layers_ctx_M2(extent, center, positions, elements, neuron_info):
    Neuron_pos_list=positions[:, :3].tolist()
    nest.SetDefaults(elements, {"I_e": float(neuron_info['I_ex']), "V_th": float(neuron_info['spike_threshold']), "V_reset": float(neuron_info['reset_value']),
                                "t_ref": float(neuron_info['absolute_refractory_period'])})
    newlayer = ntop.CreateLayer({ 'extent': extent, 'center': center, 'positions' : Neuron_pos_list , 'elements': elements} )
    #Neurons = nest.GetNodes(newlayer)
    return newlayer
    

# connect (intra regional connection?)
def connect_layers_ctx_M2(pre_SubSubRegion, post_SubSubRegion, conn_dict):
    sigma_x = conn_dict['sigma']/1000.
    sigma_y = conn_dict['sigma']/1000.
    weight_distribution=conn_dict['weight_distribution']
    if weight_distribution == 'lognormal':
        conndict = {'connection_type': 'divergent',
                    'mask': {'spherical': {'radius': 2.0}},
                    'kernel': {
                        'gaussian2D': {'p_center': conn_dict['p_center'], 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                    'weights': {'lognormal': {'mu': conn_dict['weight'], 'sigma': 1.0}},
                    'delays': conn_dict['delay'],
                    'allow_autapses': False,
                    'allow_multapses': False}
    else:
        conndict = {'connection_type': 'divergent',
                    'mask': {'spherical': {'radius': 2.0}},
                    'kernel': {
                        'gaussian2D': {'p_center': conn_dict['p_center'], 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                    'weights': conn_dict['weight'],
                    'delays': conn_dict['delay'],
                    'allow_autapses': False,
                    'allow_multapses': False}
    if sigma_x != 0:
        ntop.ConnectLayers(pre_SubSubRegion, post_SubSubRegion, conndict)
        
        
'''


########
# CERE #
########

#def connect_layers_bg():
#    print ("Fill connection later")
#    pass

#nest_routine for cb
def connect_layers_cb():
    pass
    
def create_layers_cb(rows, columns, subCB_name, elements, extent, center):
    print ('Create a CB layer: '+elements[0])
    if elements[0] in [subCB_name+'_layer_gr', subCB_name+'_layer_go', subCB_name+'_layer_vn', subCB_name+'_layer_pkj', subCB_name+'_layer_bs', subCB_name+'_layer_pons'] :
        pos_x = np.linspace(-extent[0] / 2., extent[0] / 2., num=int(rows), endpoint=True)
        pos_y = np.linspace(-extent[1] / 2., extent[1] / 2., num=int(columns), endpoint=True)
        pos_z=0.0
        positions = np.zeros((int(rows*columns), 3))
        for i in range(int(rows)):
            for j in range (int(columns)):
                positions[int(i*columns+j)]=np.array([pos_x[i], pos_y[j], pos_z])
        if elements[1] > 1:
            positions_cluster=np.repeat(positions, 400, axis=0)
            layer = nest.Create(elements[0], positions=nest.spatial.free(positions_cluster.tolist(), edge_wrap=True))
            save_layers_position(elements[0], layer, positions_cluster)
        else:
            layer = nest.Create(elements[0], positions=nest.spatial.free(positions.tolist(), edge_wrap=True))
            save_layers_position(elements[0], layer, positions)

    # elif elements[0]=='PKJ' or elements[0]=='BS':
    #     pos_x = 0.0
    #     pos_y = np.linspace(-extent[1] / 2., extent[1] / 2., num=columns, endpoint=True)
    #     pos_z = 0.0
    #     for i in range (columns):
    #         positions = np.zeros((columns, 3))
    #         positions[i,:]=np.array([pos_x, pos_y[i], pos_z])
    #     layer = ntop.CreateLayer({'extent': [extent[0]+1.,extent[1]+1.,extent[2]+1. ], 'center': center, 'positions': positions.tolist(), 'elements': elements[0]})
    elif elements[0]==subCB_name+'_layer_io':
        pos_x = 0.0
        pos_y = 0.0
        pos_z = 0.0
        positions=[[pos_x, pos_y, pos_z]]
        layer = nest.Create(elements[0], positions=nest.spatial.free(positions.tolist(), edge_wrap=True))
        save_layers_position(elements[0], layer, positions)
    return layer

def create_neurons_cb():
    import CBneurons
    CBneurons.create_neurons()

######
# BG #
######

AMPASynapseCounter_bg = 0 # initialize global counter variable for AMPA/NMDA colocalization in BG (unfortunate design choice, but required by nest fast connect procedure)

#-------------------------------------------------------------------------------
# Provides circular positions (check whether the position are within the layer dimensions beforehand !)
#
# nbCh: integer stating the number of channels to be created
# c: distance to the center (small distance means more channels in competition)
# r: radius of each channel (leading to larger overlap and thus broader competition)
#-------------------------------------------------------------------------------
# helper function that gives the channel center
def circular_center(nbCh, c, Ch=None):
    # equi-distant points on a circle
    if Ch == None:
        indices = np.arange(0, nbCh, dtype=float) + 0.5
    else:
        indices = np.array(Ch) + 0.5
    angles = (1. - indices/nbCh) * 2. * np.pi
    x, y = np.cos(angles)*c, np.sin(angles)*c
    return {'x': x, 'y': y}

def circular_positions(nbCh, c, r, sim_pts, Ch=None):  # circular positions only work in scale [1,1]
    #N_vp = nest.GetKernelStatus(['total_num_virtual_procs'])[0]
    #pyrngs = [np.random.RandomState(123456)] # for s in ([123456]*N_vp)]
    if Ch == None:
        Ch = range(nbCh)
    center_xy = circular_center(nbCh, c, Ch=Ch)
    xSim = []
    ySim = []
    for i in range(len(Ch)):
        angleSim = pyrngs[0].uniform(0., 2.*np.pi, int(sim_pts))
        rSim = pyrngs[0].uniform(0., r, int(sim_pts))
        xSim = xSim + (np.cos(angleSim)*rSim + center_xy['x'][i]).tolist()
        ySim = ySim + (np.sin(angleSim)*rSim + center_xy['y'][i]).tolist()
    return (xSim, ySim)

## Function hex_corner provides vertex coordinates of a hexagon, given a center, a radius (size) and the vertex id.
def hex_corner(center,size,i):
    angle_deg = 60 * i - 30
    angle_rad = np.pi / 180 * angle_deg
    return [center[0] + size * np.cos(angle_rad),center[1] + size * np.sin(angle_rad)]

#define the centers that will connect ctx to bg, and store them at bg_params['circle_center']
#centers must be within grid 2D dimensions.
def get_channel_centers(bg_params,hex_center=[0,0],ci=6,hex_radius=0.240):
    center_aux = []
    if bg_params['channels']:
        if len(bg_params['circle_center'])==0: #must be done before bg instantiation.
            for i in np.arange(ci):
                x_y = hex_corner(hex_center,hex_radius,i) #center, radius, vertex id # gives x,y of an hexagon vertexs.
                center_aux.append(x_y)
                            #bg_params['circle_center'].append(x_y)
            np.savetxt('./log/centers.txt',center_aux) #save the centers.
            print('generated centers: ',center_aux)
    return center_aux

########################################################################
#20191029 sun,
#
########################################################################
def get_macro_channel_centers(bg_params,hex_center=[0,0],ci=7,hex_radius=0.240):
    center_aux = []
    center_aux.append([0., 0.])
    if bg_params['channels']:
        if len(bg_params['circle_center'])==0: #must be done before bg instantiation.
            for i in np.arange(ci-1):
                x_y = hex_corner(hex_center,hex_radius,i) #center, radius, vertex id # gives x,y of an hexagon vertexs.
                center_aux.append(x_y)
            np.savetxt('./log/macro_centers.txt',center_aux) #save the centers.
            print('generated centers: ',center_aux)
    return center_aux

########################################################################
#20191029 sun,
#
########################################################################
def get_micro_channel_centers(macro_channel_centers,ci=7,hex_radius=0.16/3.*2.):
    micro_center_aux = {}
    for i in range(len(macro_channel_centers)):
        center_aux=[]
        center_aux.append(macro_channel_centers[i])
        for j in np.arange(ci-1):
            x_y = hex_corner(macro_channel_centers[i], hex_radius, j)  # center, radius, vertex id # gives x,y of an hexagon vertexs.
            center_aux.append(x_y)
        micro_center_aux['macro_channel_'+str(i)] =center_aux
    return micro_center_aux

####### set up stimulus based on distance to the current position #################
def gaussian(x, stimulus):
    return stimulus['bias'] + stimulus['scaling_stim'] * np.exp(-np.power(x - stimulus['mu'], 2.) / (2 * np.power(stimulus['sig'], 2.)))

def set_stimulus(current_position, time_start, time_stop, psg, stimulus,centers):
    # calculate the stimulus amplitud to apply on-to the top 3 channels
    # by calculating the distance between the channels centers and current position.
    # current position receives the highest stimulus amplitud, which modeled as a 2D GAussian function, and 
    # amplitud decreases when distance to current position increases.
    stim_amplitud = []
    for c in centers: 
        new_pos = np.array(c) #np.random.rand(2)-0.5 #np.array([0.,0.4])
        dist = np.linalg.norm(current_position-new_pos) 
        stim_amplitud.append(gaussian(np.array([dist]), stimulus)[0])

    for j,i in zip([0,1,2,3,4,5],stim_amplitud):  # [PG indexes] ,[stim_intensity] (Stimulus rate index)
        if j==0 or j>3: # to be removed later for all channels case.
            i = 0. # we set up stimulus equal to 0 for the 3 bottom channels.
        nest.SetStatus([psg[j]],{'rate':i,'start':time_start,'stop':time_stop})


###### generic function to apply stimulus to any layer ####################
def apply_direction_stimulus_generic(direction, time_start, time_stop, psg, stimulus):
    '''
    PG = nest.Create('poisson_generator',6)
    syn_PG = {'weight': float(strength), 'delay': 1.5}

    start_stim = time_start
    stop_stim = time_stop
    x = np.arange(-180,180,60)
    scaling_stim = 30.#110.
    a2=31.3*scaling_stim #/3.
    my_input = 15.+a2*(1.+np.sin((x+90.)/360.*2.*math.pi))/2.    # input  for M1 L5B
    print('stimulus model:   ',my_input)

    for j in np.arange(len(gids)):
        circle_j_gids=[k[0] for k in gids[j]]
        print ('circle', j, 'contrains #: ', len(circle_j_gids))
        nest.Connect(pre=[PG[j]], post=circle_j_gids, syn_spec=syn_PG)
    '''

    stim_intensity=[0,1,2,3,2,1]
    #################################### Set up rates and times for eac PG's ##############################
    if direction =='RD':
        stim_intensity = [3,2,1,0,1,2]
    if direction =='RU':
        stim_intensity = [2,3,2,1,0,1]
    if direction =='CU':
        stim_intensity = [1,2,3,2,1,0]
    if direction =='LU':
        stim_intensity = [0,1,2,3,2,1]
    if direction =='LD':
        stim_intensity = [1,0,1,2,3,2]
    if direction =='CD':
        stim_intensity = [2,1,0,1,2,3]
    if direction =='CU_MSN_M2':
        stim_intensity = [0,0,3,0,0,0] # only the center receives input (from M2) (special option for motor task implementation)  
    for j,i in zip([0,1,2,3,4,5],stim_intensity):  # [PG indexes] ,[stim_intensity] (Stimulus rate index)
        nest.SetStatus([psg[j]],{'rate':stimulus[i],'start':time_start,'stop':time_stop})

                       

def create_psg_channels(syn_weight, syn_delay, channels_nb):
    psg = nest.Create('poisson_generator', channels_nb)
    syn = {'weight':syn_weight, 'delay': syn_delay}  # syn_PG_S1_L5A_Pyr={'weight': 2.0,'delay': 1.5}
    return psg, syn


def position_encode(x, macro_center_params, time_start,time_stop):
    #determine nearest column for position x
    #for n columns
    #   calculation the distance (x, column)

    #detemining the sensory input based on nearest column
    #use the function of apply_direction_stimulus
    pass

def movement_decode(x, macro_center_params, time_start,time_stop):
    #detemining the movement output based on activities of columns
    #use the function of apply_direction_stimulus

    pass

def apply_direction_stimulus(ctx_bg_input,direction,time_start,time_stop):
    ################## Arm movement #################################
    ####### testing input to M1 and S1 ################################
    
    bg_PG_ctx = {}
    bg_PG_ctx['M1_L5A_CS'] = nest.Create('poisson_generator',6)
    bg_PG_ctx['M1_L5B_PT'] = nest.Create('poisson_generator',6)
    syn_PG_M1_L5A_CS={'weight': 11.5, 'delay': 1.5} #syn_PG_M1_L5A_CS={'weight': 11.0, 'delay': 1.5}    #good one -> syn_PG_M1_L5A_CS={'weight': 10.0, 'delay': 1.5}
    syn_PG_M1_L5B_PT={'weight': 13., 'delay': 1.5} #syn_PG_M1_L5B_PT={'weight': 12.5, 'delay': 1.5}    #good one -> syn_PG_M1_L5B_PT={'weight': 10.0, 'delay': 1.5}
    bg_PG_ctx['S1_L5A_Pyr'] = nest.Create('poisson_generator',6)
    bg_PG_ctx['S1_L5B_Pyr'] = nest.Create('poisson_generator',6)
    syn_PG_S1_L5A_Pyr={'weight': 2.,'delay': 1.5} #syn_PG_S1_L5A_Pyr={'weight': 2.0,'delay': 1.5}
    syn_PG_S1_L5B_Pyr={'weight': 2.2, 'delay': 1.5} #syn_PG_S1_L5B_Pyr={'weight': 2.2, 'delay': 1.5}  ## good one -> syn_PG_S1_L5B_Pyr={'weight': 4., 'delay': 1.5}
    
    start_stim = time_start
    stop_stim = time_stop
    x = np.arange(-180,180,60)
    scaling_stim = 30.#110.
    a1=17.7*scaling_stim #/3.
    a2=31.3*scaling_stim #/3.
    y_CSN = 2+a1*(1.+np.sin((x+90.)/360.*2.*math.pi))/2.      # input for M1 L5A (gives rates, they should be in the order of 1300 Hz?)
    y_PTN = 15.+a2*(1.+np.sin((x+90.)/360.*2.*math.pi))/2.    # input  for M1 L5B
    print('y_CSN:   ',y_CSN)
    print('y_PTN:   ',y_PTN)
    
    ############################# Connecting PG to M1 L5B and L5A ####################################
    #ctx_bg_input['M1']:   #2 elements, 1st element is L5B ->ctx_bg_input['M1'][0], 2nd is L5A ->ctx_bg_input['M1'][1]
    circle_j_gids_nb={}
    circle_gid_detector={}
    for j in np.arange(len(ctx_bg_input['M1'][0])): #for each circle of gids
        circle_j_gids = [k[0] for k in ctx_bg_input['M1'][0][j]]
        print('circl  M1 L5B_PT ',j,' contains #: ',len(circle_j_gids))
        circle_j_gids_nb['str(j)']=len(circle_j_gids)
        log.debug("CONNECT %s", "X"*100)
        nest.Connect(pre=[bg_PG_ctx['M1_L5B_PT'][j]],post=circle_j_gids,syn_spec=syn_PG_M1_L5B_PT)
        params={'label': 'circle_'+str(j)}
        circle_gid_detector[str(j)] = nest.Create("spike_detector", params=params)
        log.debug("CONNECT %s", "X"*100)
        nest.Connect(pre=circle_j_gids, post=circle_gid_detector[str(j)])

    for j in np.arange(len(ctx_bg_input['M1'][1])): #for each circle of gids
        circle_j_gids = [k[0] for k in ctx_bg_input['M1'][1][j]]
        print('circle M1 L5A_CS ',j,' contains #: ',len(circle_j_gids))
        log.debug("CONNECT %s", "X"*100)
        nest.Connect(pre=[bg_PG_ctx['M1_L5A_CS'][j]],post=circle_j_gids,syn_spec=syn_PG_M1_L5A_CS)

    ############################# Connecting PG to S1 as well  ####################
    for j in np.arange(len(ctx_bg_input['S1'][0])): #for each circle of gids
        circle_j_gids = [k[0] for k in ctx_bg_input['S1'][0][j]]
        print('circle S1 L5B_Pyr ',j,' contains #: ',len(circle_j_gids))
        log.debug("CONNECT %s", "X"*100)
        nest.Connect(pre=[bg_PG_ctx['S1_L5B_Pyr'][j]],post=circle_j_gids,syn_spec=syn_PG_S1_L5B_Pyr)

    for j in np.arange(len(ctx_bg_input['S1'][1])): #for each circle of gids
        circle_j_gids = [k[0] for k in ctx_bg_input['S1'][1][j]]
        print('circle S1 L5A_Pyr ',j,' contains #: ',len(circle_j_gids))
        log.debug("CONNECT %s", "X"*100)
        nest.Connect(pre=[bg_PG_ctx['S1_L5A_Pyr'][j]],post=circle_j_gids,syn_spec=syn_PG_S1_L5A_Pyr)

    #################################### Set up rates and times for eac PG's ##############################
    if direction =='L':
        stim_intensity = [0,0,0,3,0,0] #Nao[0,1,2,3,0,0]  # if much weaker in the neighbors is desired, choose: [0,1,1,3,0,0]
    if direction =='R':
        stim_intensity = [0,3,0,0,0,0]#Nao[0,2,3,4,0,0] # if much weaker in the neighbors is desired, choose: [0,1,3,5,0,0]
    if direction =='C':
        stim_intensity = [0,0,3,0,0,0] #Nao[0,3,2,1,0,0]  # if much weaker in the neighbors is desired, choose: [0,3,1,1,0,0]

    for j,i in zip([0,1,2,3,4,5],stim_intensity):  # [PG indexes] ,[stim_intensity] (Stimulus rate index)
        nest.SetStatus([bg_PG_ctx['M1_L5A_CS'][j]],{'rate':y_CSN[i],'start':start_stim,'stop':stop_stim})
        nest.SetStatus([bg_PG_ctx['M1_L5B_PT'][j]],{'rate':y_PTN[i],'start':start_stim,'stop':stop_stim})
        nest.SetStatus([bg_PG_ctx['S1_L5A_Pyr'][j]],{'rate':y_CSN[i],'start':start_stim,'stop':stop_stim})
        nest.SetStatus([bg_PG_ctx['S1_L5B_Pyr'][j]],{'rate':y_PTN[i],'start':start_stim,'stop':stop_stim})
    return circle_gid_detector,circle_j_gids_nb


def create_stimulus(scaling_stim,  bias):
    x = np.arange(-180, 180, 60)
    stim_vector = bias + scaling_stim * (1. + np.sin((x + 90.) / 360. * 2. * math.pi)) / 2.  # input for M1 L5A (gives rates, they should be in the order of 1300 Hz?)
    #y_PTN = 15. + a2 * (1. + np.sin((x + 90.) / 360. * 2. * math.pi)) / 2.  # input  for M1 L5B
    return stim_vector

def connect_channels_psg(columns_gids, psg, syn):
    circle_j_gids_nb = {}
    circle_gid_detector = {}
    for j in np.arange(len(columns_gids)):  # for each circle of gids
        circle_j_gids = [k[0] for k in columns_gids[j]]
        print('circle  ', j, ' contains #: ', len(circle_j_gids))
        circle_j_gids_nb[str(j)] = len(circle_j_gids)
        log.debug("CONNECT %s", "X"*100)
        nest.Connect(pre=[psg[j]], post=circle_j_gids, syn_spec=syn)
        params = {'label': 'circle_' + str(j)}
        circle_gid_detector[str(j)] = nest.Create("spike_detector", params=params)
        log.debug("CONNECT %s", "X"*100)
        nest.Connect(pre=circle_j_gids, post=circle_gid_detector[str(j)])
    return circle_gid_detector, circle_j_gids_nb

def connect_psg_to_channels(columns_gids, psg, syn):
    circle_j_gids_nb = {}
    for j in np.arange(len(columns_gids)):  # for each circle of gids
        circle_j_gids = [k[0] for k in columns_gids[j]]
        print('circle  ', j, ' contains #: ', len(circle_j_gids))
        circle_j_gids_nb[str(j)] = len(circle_j_gids)
        log.debug("CONNECT %s", "X"*100)
        nest.Connect(pre=[psg[j]], post=circle_j_gids, syn_spec=syn)

def spike_detector_channels(columns_gids):
    circle_gid_detector = {}
    circle_j_gids_nb = {}
    for j in np.arange(len(columns_gids)):  # for each circle of gids
        circle_j_gids = [k[0] for k in columns_gids[j]]
        params = {'label': 'circle_' + str(j)}
        circle_gid_detector[str(j)] = nest.Create("spike_detector", params=params)
        circle_j_gids_nb[str(j)] = len(columns_gids[j])
        log.debug("CONNECT %s", "X"*100)
        nest.Connect(pre=circle_j_gids, post=circle_gid_detector[str(j)])
    return circle_gid_detector, circle_j_gids_nb

################################################################################################################################
######### given columns mean firing rate, columns positions and current position, it infers (heuristically) the next positions 
########## attention !: points_to_reach and mean_fr should be aligned !!!! ####################
########### attention !: mean_fr of is sorted as channels R, C, L respectively (based on points_to_reach order -> centers[1:4])
#############################################################################################################################
def get_next_pos(points_to_reach,mean_fr,current_position=[0.,0.],delta_x=0.1):
    xt = current_position #x,y components between -0.5 and 0.5 (receptive field, this need to be scaled to map physical positions)
    # normalize firing rates 
    a = mean_fr/sum(np.array(mean_fr)) #normalization between 3 rates # also can be used -> mean_fr/np.array([150.]) normalize against a maximum allowed.
    # calculate each of their delta_x contribution. x,y components.
    aa = a * delta_x
    xt1 = []
    for j,i in enumerate(points_to_reach):
        theta = math.degrees(math.atan((i[1]-xt[1])/(i[0]-xt[0])))
        if theta<0.:
            theta = 180.+theta
        if xt[1] > i[1] and (j==0 or j==2): # only will do this if the L and R are left behind
            theta = 180.+theta
        xt_i = [aa[j]*(math.cos(math.radians(theta))),aa[j]*(math.sin(math.radians(theta)))]
        xt_i[0] = xt_i[0] + xt[0] #shift
        xt_i[1] = xt_i[1] + xt[1] #shift
        xt1.append(xt_i)
    xt1=np.array(xt1)
    for k in np.arange(len(xt1)):
        xt1[k,0] = xt1[k,0] - xt[0] #shift
        xt1[k,1] = xt1[k,1] - xt[1] #shift

    xnew = [xt1[:,0].sum()+xt[0],xt1[:,1].sum()+xt[1]]
    #plt.plot(xt[0],xt[1],'k*')
    #plt.plot(xnew[0],xnew[1],'s')
    #plt.show()
    return xnew


### function to define BG grid positions in 2D
### parameters: 
# nbCh: number of channels (always 1)
# sim_pts: number of points to generate
# a0, a1:  -x shift, distance from starting point (x axis)
# b0, b1:  -y shift, distance from starting point (y axis)
# -----------------------------------------------------
def grid_positions(nbCh, sim_pts,a0,a1,b0,b1):
    
    n = int(sim_pts*nbCh)
    n_squared = np.ceil(np.sqrt(n))
    coord = [[x/n_squared*a1-a0, y/n_squared*b1-b0] for x in np.arange(0,n_squared, dtype=float) for y in np.arange(0,n_squared, dtype=float)]
    # too many points due to square root rounding? remove at random # same random numbers over multiple nodes
    if len(coord) > n:
        coord = np.array(coord)[np.sort(pyrngs[0].choice(range(len(coord)), size=n, replace=False))].tolist()
    aux_x = [coord[i][0] for i in range(len(coord))]
    aux_y = [coord[i][1] for i in range(len(coord))]
    return [aux_x, aux_y]

### function to get connections in format source,target,weigth and save as txt ######
def get_connections_to_file(source_name,target_name,source_layer,target_layer):
    np.savetxt('./log/'+source_name+'_to_'+target_name+'.txt',nest.GetStatus(nest.GetConnections(source=nest.GetNodes(source_layer)[0],target=nest.GetNodes(target_layer)[0]),keys={'source','target','weight'}))


#-------------------------------------------------------------------------------
# Establishes a topological layer and returns it
# bg_params: basal ganglia parameters
# nucleus: name of the nucleus to instantiate
# fake: numerical value - if 0, then a real population of iaf is instantiated
#                       - if fake > 0, then a Poisson generator population firing at `fake` Hz is instantiated
# force_pop_size: if defined, initialize only this number of neurons
#                 -> this is useful for the cortical connections, as some inputs will be derived from L5A and L5B layers
#-------------------------------------------------------------------------------
def create_layers_bg(bg_params, nucleus, fake=0, mirror_neurons=None, mirror_pos=None,scalefactor=[1,1]):
  
  #define extent and center for 2D layer
  my_extent = [1.*int(scalefactor[0])+1.,1.*int(scalefactor[1])+1.]
  my_center = [0.0, 0.0]

  if mirror_neurons is None:
    # normal case: full input layer is created
    if nucleus =='GPi_fake':
      nucleus_tmp = nucleus[:3]
      pop_size = int(bg_params['nb'+nucleus_tmp])
    else:
      pop_size = int(bg_params['nb' + nucleus]) 
  else:
    # inputs come from existing ctx layer: only a fraction of poisson generators are created
    pop_size = int(bg_params['nb' + nucleus]) - len(mirror_neurons)
  
  print('population size for '+nucleus+': '+str(pop_size))

  if nucleus=='GPi_fake':
    positions_z = pyrngs[0].uniform(0., 0.5, pop_size).tolist()
    positions = np.loadtxt('/opt/data/log/'+nucleus[:3]+'.txt') # retrive positions x,y from GPi
    position_nD = [[positions[i][1], positions[i][2], positions_z[i]] for i in range(len(positions))]
    my_extent = my_extent + [1.]
    my_center = my_center + [0.]
  else:
    if (nucleus=='GPi' or nucleus=='STN'):
      positions = grid_positions(1,pop_size,0.4*scalefactor[0],scalefactor[0]-0.1,0.4*scalefactor[1],scalefactor[1]-0.1)
    else:
      positions = grid_positions(1,pop_size,0.5*scalefactor[0],scalefactor[0],0.5*scalefactor[1],scalefactor[1])
    position_nD = [[positions[0][i], positions[1][i]] for i in range(len(positions[0]))]

  if mirror_neurons != None:
    # 3 lines below needed for multiple nodes # 
    mirror_neurons.sort(key=lambda x: x[0]) #sort by Gids and arrange related positions
    mirror_gids = [gids[0] for gids in mirror_neurons]
    mirror_pos = [pos[1] for pos in mirror_neurons]

    # add all positions together
    print('mirror neurons!   original position_nD: ',len(position_nD),'   ',position_nD[:3])
    print('mirror neurons!  mirror positions: ',len(mirror_pos),'  ',mirror_pos[:3])
    position_nD = position_nD + mirror_pos
    print('positions len for fake including mirrors: ',len(position_nD))

  if fake == 0:
    # fake == 0 is the normal case, where actual iaf neurons are instantiated
    if nucleus=='GPi_fake':
      element = 'parrot_neuron'
    else:
      nest.SetDefaults('iaf_psc_alpha_multisynapse', bg_params['common_iaf'])
      nest.SetDefaults('iaf_psc_alpha_multisynapse', bg_params[nucleus+'_iaf'])
      nest.SetDefaults('iaf_psc_alpha_multisynapse', {"I_e": bg_params['Ie'+nucleus]})
      element = 'iaf_psc_alpha_multisynapse'
  else:
    # when fake > 0, parrot neurons instantiated (specially for fake input)
    element = 'parrot_neuron'
  
  #layer_gid = ntop.CreateLayer({'positions': position_nD, 'elements': element, 'extent':my_extent, 'center':my_center, 'edge_wrap': True})
  print('creating %d neurons in layer' % len(position_nD))
  layer = nest.Create(element, positions=nest.spatial.free(position_nD)) #nest 3
  print('created %d neurons' % len(layer.tolist()))
  #save_layers_position(nucleus, layer_gid, np.array(position_nD))
  save_layers_position(nucleus, layer, np.array(position_nD)) #nest 3
  
  if fake > 0:
    # when fake > 0, parrot neurons are connected to poisson generators firing at `fake`Hz
    ## adding 2 lines below just in case (fix for multiple nodes)
    print('creating poisson gennnnnnnnnnn          rate: ', fake)
    print('pop_size: ', pop_size)
    poisson = nest.Create('poisson_generator', 1) 
    nest.SetStatus(poisson, {'rate': fake})

    #log.debug("CONNECT %s %s", poisson, layer)
    ##### poisoon input to BG #######
    print('##### poisoon input to BG #######')
    nest.GetStatus(poisson)
    
    #nest.Connect(pre=poisson_string, post=my_post[0:pop_size], conn_spec={'rule':'one_to_one'})
    conn_dic = {'rule': 'all_to_all','allow_multapses': False,
             'allow_autapses': False}
    nest.Connect(poisson, layer[0:pop_size], conn_dic)#conn_spec={'rule':'all_to_all'}) #nest3

    print('static synapse settings: ', nest.GetDefaults('static_synapse'))
    
    #if mirror_neurons != None:
    #  print('special handling of '+ nucleus + ' input layer => the remaining neurons will be connected to the original ctx neurons')
    #  print('connecting mirror neurons of len: ',len(mirror_gids),' to ',nucleus)
    #  nest.Connect(pre=mirror_gids, post=my_post[-len(mirror_gids):], conn_spec={'rule':'one_to_one'},syn_spec={'delay':10.}) ## added delay !!!!
 
  return layer

#-------------------------------------------------------------------------------
# Establishes a topological connection between two populations
# bg_params: basal ganglia parameters
# nType : a string 'ex' or 'in', defining whether it is excitatory or inhibitory
# bg_layers : dictionary of basal ganglia layers
# nameTgt, nameSrc : strings naming the populations, as defined in NUCLEI list
# projType : type of projections. For the moment: 'focused' (only channel-to-channel connection) and
#            'diffuse' (all-to-one with uniform distribution)
# redundancy, RedundancyType : contrains the inDegree - see function `connect` for details
# LCGDelays : shall we use the delays obtained by (Liénard, Cos, Girard, in prep) or not (default = True)
# gain : allows to amplify the weight normally deduced from LG14
# stochastic_delays: to enable stochasticity in the axonal delays
# spreads: a 2-item list specifying the radius of focused and diffuse projections
#-------------------------------------------------------------------------------
def connect_layers_bg(bg_params, nType, bg_layers, nameSrc, nameTgt, projType, redundancy, RedundancyType, LCGDelays=True, gain=1., stochastic_delays=None, spreads=None, verbose=False,scalefactor=[1,1]):
  def printv(text):
    if verbose:
      print(text)

  printv("\n* connecting "+nameSrc+" -> "+nameTgt+" with "+nType+" "+projType+" connection")

  recType = {'AMPA':1,'NMDA':2,'GABA':3}

  if RedundancyType == 'inDegreeAbs':
    # inDegree is already provided in the right form
    inDegree = float(redundancy)
  elif RedundancyType == 'outDegreeAbs':
    #### fractional outDegree is expressed as a fraction of max axo-dendritic contacts
    inDegree = get_frac_bg(bg_params, 1./redundancy, nameSrc, nameTgt, bg_params['count'+nameSrc], bg_params['count'+nameTgt], verbose=verbose)
  elif RedundancyType == 'outDegreeCons':
    #### fractional outDegree is expressed as a ratio of min/max axo-dendritic contacts
    inDegree = get_frac_bg(bg_params, redundancy, nameSrc, nameTgt, bg_params['count'+nameSrc], bg_params['count'+nameTgt], useMin=True, verbose=verbose)
  else:
    raise KeyError('`RedundancyType` should be one of `inDegreeAbs`, `outDegreeAbs`, or `outDegreeCons`.')

  # check if in degree acceptable (not larger than number of neurons in the source nucleus)
  if projType == 'focused' and inDegree > bg_params['nb'+nameSrc]:
    printv("/!\ WARNING: required 'in degree' ("+str(inDegree)+") larger than number of neurons in individual source channels ("+str(bg_params['nb'+nameSrc])+"), thus reduced to the latter value")
    inDegree = bg_params['nb'+nameSrc]
  if projType == 'diffuse' and inDegree > bg_params['nb'+nameSrc]:
    printv("/!\ WARNING: required 'in degree' ("+str(inDegree)+") larger than number of neurons in the overall source population ("+str(bg_params['nb'+nameSrc])+"), thus reduced to the latter value")
    inDegree = bg_params['nb'+nameSrc]

  if inDegree == 0.:
    printv("/!\ WARNING: non-existent connection strength, will skip")
    return

  global AMPASynapseCounter_bg

  # prepare receptor type lists:
  if nType == 'ex':
    lRecType = ['AMPA','NMDA']
    AMPASynapseCounter_bg = AMPASynapseCounter_bg + 1
    lbl = AMPASynapseCounter_bg # needs to add NMDA later
  elif nType == 'AMPA':
    lRecType = ['AMPA']
    lbl = 0
  elif nType == 'NMDA':
    lRecType = ['NMDA']
    lbl = 0
  elif nType == 'in':
    lRecType = ['GABA']
    lbl = 0
  else:
    raise KeyError('Undefined connexion type: '+nType)

  # compute the global weight of the connection, for each receptor type:
  W = computeW_bg(bg_params, lRecType, nameSrc, nameTgt, inDegree, gain, verbose=verbose)
  printv("  W="+str(W)+" and inDegree="+str(inDegree))

  # determine which transmission delay to use:
  if LCGDelays:
    delay = bg_params['tau'][nameSrc+'->'+nameTgt]
  else:
    delay = 1.

  if projType == 'focused': # if projections focused, input come only from the same channel as tgtChannel
    if nType == 'ex':
        mass_connect_bg(bg_params, bg_layers, nameSrc, nameTgt, lbl, inDegree, recType[lRecType[0]], W[lRecType[0]], lRecType,delay, spread=bg_params['spread_focused'], stochastic_delays = stochastic_delays, verbose=verbose,rec_mode='double_ex')
        mass_connect_bg(bg_params, bg_layers, nameSrc, nameTgt, lbl, inDegree, recType[lRecType[1]], W[lRecType[1]], lRecType,delay, spread=bg_params['spread_focused'], stochastic_delays = stochastic_delays, verbose=verbose,rec_mode='double_ex')
    else:
        mass_connect_bg(bg_params, bg_layers, nameSrc, nameTgt, lbl, inDegree, recType[lRecType[0]], W[lRecType[0]], lRecType, delay, spread=bg_params['spread_focused'], stochastic_delays = stochastic_delays, verbose=verbose,rec_mode='single_in')
        #mass_connect_bg(bg_params, bg_layers, nameSrc, nameTgt, lbl, inDegree, recType[lRecType[0]], W[lRecType[0]], delay, spread=bg_params['spread_focused'], stochastic_delays = stochastic_delays, verbose=verbose,rec_mode='single_in')
  elif projType == 'diffuse': # if projections diffused, input connections are shared among each possible input channel equally
    if nType == 'ex':
      mass_connect_bg(bg_params, bg_layers, nameSrc, nameTgt, lbl, inDegree, recType[lRecType[0]], W[lRecType[0]], lRecType,delay, spread=bg_params['spread_focused'], stochastic_delays = stochastic_delays, verbose=verbose,rec_mode='double_ex')
      mass_connect_bg(bg_params, bg_layers, nameSrc, nameTgt, lbl, inDegree, recType[lRecType[1]], W[lRecType[1]], lRecType,delay, spread=bg_params['spread_focused'], stochastic_delays = stochastic_delays, verbose=verbose,rec_mode='double_ex')
      #mass_connect_bg(bg_params, bg_layers, nameSrc, nameTgt, lbl, inDegree, recType, W, lRecType, delay, spread=bg_params['spread_diffuse']*max(scalefactor), stochastic_delays = stochastic_delays, verbose=verbose,rec_mode='double_ex')
    else:
      mass_connect_bg(bg_params, bg_layers, nameSrc, nameTgt, lbl, inDegree, recType[lRecType[0]], W[lRecType[0]], lRecType, delay, spread=bg_params['spread_diffuse']*max(scalefactor), stochastic_delays = stochastic_delays, verbose=verbose,rec_mode='single_in')

  #if nType == 'ex':
    # mirror the AMPA connection with similarly connected NMDA connections
    #mass_mirror_bg(bg_params,nameSrc, nameTgt,bg_layers[nameSrc], lbl, recType['NMDA'], W['NMDA'], delay, stochastic_delays = stochastic_delays)
    #print('nothing')
  return W


#------------------------------------------------------------------------------
# Routine to perform the fast connection using nest built-in `connect` function
# - `bg_params` is basal ganglia parameters
# - `bg_layers` is the dictionary of basal ganglia layers
# - `sourceName` & `destName` are names of two different layers
# - `synapse_label` is used to tag connections and be able to find them quickly
#   with function `mass_mirror`, that adds NMDA on top of AMPA connections
# - `inDegree`, `receptor_type`, `weight`, `delay` are Nest connection params
# - `spread` is a parameter that affects the diffusion level of the connection
#------------------------------------------------------------------------------
def mass_connect_bg(bg_params, bg_layers, sourceName, destName, synapse_label, inDegree, receptor_type, weight, lRecType, delay, spread, stochastic_delays=None, verbose=False,rec_mode='double_ex'):
  def printv(text):
    if verbose:
      print(text)

  # potential initialization of stochastic delays
  if stochastic_delays != None and delay > 0:
    printv('Using stochastic delays in mass-connect')
    low = delay * 0.5
    high = delay * 1.5
    sigma = delay * stochastic_delays
    delay =  {'distribution': 'normal_clipped', 'low': low, 'high': high, 'mu': delay, 'sigma': sigma}

  ## set default synapse model with the chosen label
  #nest.SetDefaults('static_synapse_lbl', {'synapse_label': synapse_label, 'receptor_type': receptor_type})
  # creation of the topological connection dict
  #conndict = {'connection_type': 'convergent',
  #            'mask': {'circular': {'radius': spread}},
  #            'synapse_model': 'static_synapse_lbl', 'weights': weight, 'delays':delay,
  #            'allow_oversized_mask': True, 'allow_multapses': True}
  
  if rec_mode == 'double_ex':
    nest.SetDefaults('static_synapse_lbl', {'synapse_label':synapse_label,'receptor_type': receptor_type, 'weight': weight,
                 'delay':delay})

    syn_dict = {'synapse_model': 'static_synapse_lbl'}#,'weight': weight, 'delay':delay, 'receptor_type':receptor_type}

    #syn_spec=[{'synapse_model':'static_synapse_lbl','weight': weight[lRecType[0]], 'delay':delay},#, 'receptor_type':receptor_type[lRecType[0]] },
    #          {'synapse_model':'static_synapse_lbl','weight': weight[lRecType[1]], 'delay':delay}#, 'receptor_type':receptor_type[lRecType[1]] }
    #         ] 
  else:
    nest.SetDefaults('static_synapse_lbl', {'receptor_type': receptor_type, 'weight': weight,
                  'delay':delay, 'synapse_label':synapse_label})
    syn_dict = {'synapse_model': 'static_synapse_lbl'}
   
  # The first call ensures that all neurons in `destName`
  # have at least `int(inDegree)` incoming connections
  integer_inDegree = np.floor(inDegree)
  if integer_inDegree>0:
    printv('Adding '+str(int(integer_inDegree*bg_params['nb'+destName]))+' connections with rule `fixed_indegree`')
    
    integer_conndict = {'rule': 'fixed_indegree','indegree':int(integer_inDegree),
             'mask': {'circular':{'radius':spread}},
             'allow_oversized_mask': True, 'allow_multapses': True}
    #integer_conndict.update({'number_of_connections': int(integer_inDegree)})
    if rec_mode == 'double_ex':
      nest.Connect(bg_layers[sourceName], bg_layers[destName], integer_conndict, syn_dict) #syn_spec = syn_spec)
    else:
      nest.Connect(bg_layers[sourceName], bg_layers[destName], integer_conndict, syn_dict) 
    

  # The second call distributes the approximate number of remaining axonal
  # contacts at random (i.e. the remaining fractional part after the first step)
  # Why "approximate"? Because with pynest layers, there are only two ways to specify
  # the number of axons in a connection:
  #    1) with an integer, specified with respect to each source (alt. target) neurons
  #    2) as a probability
  # Here, we have a fractional part - not an integer number - so that leaves us option 2.
  # However, because the new axonal contacts are drawn at random, we will not have the
  # exact number of connections
  float_inDegree = inDegree - integer_inDegree
  remaining_connections = np.round(float_inDegree * bg_params['nb'+destName])
  if remaining_connections > 0:
    printv('Adding '+str(remaining_connections)+' remaining connections with rule `fixed_total_number`')
    #float_conndict = conndict.copy()
    
    float_conndict = {'rule': 'pairwise_bernoulli','use_on_source':True,
             'mask': {'circular':{'radius':spread}},
             'allow_oversized_mask': True, 'allow_multapses': True,
             'p': 1. / (bg_params['nb'+sourceName] * float(remaining_connections))}
    
    #float_conndict.update({'kernel': 1. / (bg_params['nb'+sourceName] * float(remaining_connections))})
    #ntop.ConnectLayers(bg_layers[sourceName], bg_layers[destName], float_conndict)
    if rec_mode == 'double_ex':
      nest.Connect(bg_layers[sourceName], bg_layers[destName], float_conndict, syn_dict) #syn_spec = syn_spec)
    else:
      nest.Connect(bg_layers[sourceName], bg_layers[destName], float_conndict, syn_dict)
    
#------------------------------------------------------------------------------
# Routine to duplicate a connection made with a specific receptor, with another
# receptor (typically to add NMDA connections to existing AMPA connections)
# - `source` & `synapse_label` should uniquely define the connections of
#   interest - typically, they are the same as in the call to `mass_connect`
# - `receptor_type`, `weight`, `delay` are Nest connection params
#------------------------------------------------------------------------------
def mass_mirror_bg(bg_params, nameSrc, nameTgt,source, synapse_label, receptor_type, weight, delay, stochastic_delays, verbose=False):
  def printv(text):
    if verbose:
      print(text)

  # find all AMPA connections for the given projection type
  printv('looking for AMPA connections to mirror with NMDA...\n')
  ampa_conns = nest.GetConnections(source, synapse_label=synapse_label)  
  # in rare cases, there may be no connections, guard against that
  if ampa_conns:
    # extract just source and target GID lists, all other information is irrelevant here
    printv('found '+str(len(ampa_conns))+' AMPA connections\n')
    if stochastic_delays != None and delay > 0:
      printv('Using stochastic delays in mass-miror')
      delay = np.array(ampa_conns.delay).flatten()
    
    #log.debug("CONNECT %s", "X"*100)
    
    #np.savetxt('/opt/data/log/source.txt',ampa_conns.source)
    #np.savetxt('/opt/dat/opt/data/log/target.txt',ampa_conns.target)
    
    nest.SetDefaults('static_synapse_lbl', {'receptor_type': receptor_type, 'weight': weight,
                 'delay':delay, 'synapse_label':synapse_label})
    syn_dict = {'synapse_model': 'static_synapse_lbl'}
    
    for s,t in zip(ampa_conns.source,ampa_conns.target):
      nest.Connect(nest.NodeCollection([s]), nest.NodeCollection([t]), 'one_to_one',syn_dict)
                 #{'model': 'static_synapse_lbl',
                 # 'synapse_label': synapse_label, # tag with the same number (doesn't matter)
                 # 'receptor_type': receptor_type, 'weight': weight, 'delay':delay})
  
#-------------------------------------------------------------------------------
# Helper function to set a basal ganglia internal projection
# computes the inDegree as a fraction of maximal possible inDegree
# `FractionalOutDegree` is the outDegree, expressed as a fraction
#-------------------------------------------------------------------------------
def get_frac_bg(bg_params, FractionalOutDegree, nameSrc, nameTgt, cntSrc, cntTgt, useMin=False, verbose=False):
  if useMin == False:
    # 'FractionalOutDegree' is taken to be relative to the maximal number of axo-dendritic contacts
    inDegree = get_input_range_bg(bg_params, nameSrc, nameTgt, cntSrc, cntTgt, verbose=verbose)[1] * FractionalOutDegree
  else:
    # 'FractionalOutDegree' is taken to be relative to the maximal number of axo-dendritic contacts and their minimal number
    r = get_input_range_bg(bg_params, nameSrc, nameTgt, cntSrc, cntTgt, verbose=verbose)
    inDegree = (r[1] - r[0]) * FractionalOutDegree + r[0]
  if verbose:
    print('\tConverting the fractional outDegree of '+nameSrc+' -> '+nameTgt+' from '+str(FractionalOutDegree)+' to inDegree neuron count: '+str(round(inDegree, 2))+' (relative to minimal value possible? '+str(useMin)+')')
  return inDegree

#-------------------------------------------------------------------------------
# Helper function to set a basal ganglia internal projection
# computes the weight of a connection, based on LG14 parameters
#-------------------------------------------------------------------------------
def computeW_bg(bg_params, listRecType, nameSrc, nameTgt, inDegree, gain=1.,verbose=False):
  recType = {'AMPA':1,'NMDA':2,'GABA':3}
  nu = get_input_range_bg(bg_params, nameSrc, nameTgt, bg_params['count'+nameSrc], bg_params['count'+nameTgt], verbose=verbose)[1]
  if verbose:
    print('\tCompare with the effective chosen inDegree   : '+str(inDegree))

  # attenuation due to the distance from the receptors to the soma of tgt:
  LX=bg_params['lx'][nameTgt]*np.sqrt((4.*bg_params['Ri'])/(bg_params['dx'][nameTgt]*bg_params['Rm']))
  attenuation = np.cosh(LX*(1-bg_params['distcontact'][nameSrc+'->'+nameTgt])) / np.cosh(LX)

  w={}
  for r in listRecType:
    w[r] = nu / float(inDegree) * attenuation * bg_params['wPSP'][recType[r]-1] * gain
  return w

#-------------------------------------------------------------------------------
# Helper function to set a basal ganglia internal projection
# returns the minimal & maximal numbers of distinct input neurons for one connection
#-------------------------------------------------------------------------------
def get_input_range_bg(bg_params, nameSrc, nameTgt, cntSrc, cntTgt, verbose=False):
  if nameSrc=='CSN' or nameSrc=='PTN':
    nu = bg_params['alpha'][nameSrc+'->'+nameTgt]
    nu0 = 0
    if verbose:
      print('\tMaximal number of distinct input neurons (nu): '+str(nu))
      print('\tMinimal number of distinct input neurons     : unknown (set to 0)')
  else:
    nu = cntSrc / float(cntTgt) * bg_params['ProjPercent'][nameSrc+'->'+nameTgt] * bg_params['alpha'][nameSrc+'->'+nameTgt]
    nu0 = cntSrc / float(cntTgt) * bg_params['ProjPercent'][nameSrc+'->'+nameTgt]
    if verbose:
      print('\tMaximal number of distinct input neurons (nu): '+str(nu))
      print('\tMinimal number of distinct input neurons     : '+str(nu0))
  return [nu0, nu]



######
# CB #
######

def connect_layers_cere():
  # CBnetwork was used instad of connect_layers_cere()
    pass

####################
# INTERCONNECTIONS #
####################

#-------------------------------------------------------------------------------
# If bgparams['channel'] is False it will
# identify randomly a pool of ctx neurons to project to bg
# (numb_neurons (bgparams['num_neurons']) are selected from l5a and l5b)
# if bgparams['channel'] (channels) is True it will select circular clusters with a
# of radius equal to radius_small for each center circle_center;
#
#-------------------------------------------------------------------------------

def identify_proj_neurons_ctx_bg_last(source_layer,params,numb_neurons,area_lbl,channels=False,channels_radius=0.16,circle_center=[]):
  #N_vp = nest.GetKernelStatus(['total_num_virtual_procs'])[0]
  #pyrngs = [np.random.RandomState(123456)] # for s in ([123456]*N_vp)]

  #if channels:
  #  radius_small = channels_radius #0.1 #0.2
  #  circle_center = []
    #centers = circular_center(8,0.3,Ch=None)
    #for i in np.arange(len(centers['x'])):
    #  circle_center.append([centers['x'][i],centers['y'][i]])
  #  for i in np.arange(6): # this number '6' should be a parameter.
  #    x_y = hex_corner([0,0],0.240,i) #center, radius, vertex id
  #    circle_center.append(x_y)
  #  np.savetxt('/opt/data/log/centers.txt',circle_center) #save the centers.

  if area_lbl=='M1':
    L5A = area_lbl+'_'+'L5A_CS'
    L5B = area_lbl+'_'+'L5B_PT'
    my_area = 'M1' 
    if channels:
      circles_l5b_l5a = get_input_column_layers_ctx(source_layer,circle_center,channels_radius,'M1') # A list with centers is sent as param
      my_PTN,my_CSN = [],[]
      for i in circles_l5b_l5a[0]: #l5b circles. iterate over circles
        for j in i:
          my_PTN.append([j[0],j[1][:2]]) #use only x and y positions in PTN
      for i in circles_l5b_l5a[1]: #l5a circles. iterate over circles
        for j in i:
          my_CSN.append([j[0],j[1][:2]]) #use only x and y positions in CSN
    else:
      #Neuron_pos_fileload = np.load('ctx/Neuron_pos_' + L5A + '.npz')
      #l5a_pos = Neuron_pos_fileload['Neuron_pos']
      #Neuron_pos_fileload = np.load('ctx/Neuron_pos_' +  L5B + '.npz')
      #l5b_pos = Neuron_pos_fileload['Neuron_pos']
      
      Neuron_pos_fileload = np.loadtxt('/opt/data/log/'+L5A+'.txt')
      l5a_pos = Neuron_pos_fileload[:,1:]
      Neuron_pos_fileload = np.loadtxt('/opt/data/log/'+L5B+'.txt')
      l5b_pos = Neuron_pos_fileload[:,1:]

      l5a_gids = nest.GetNodes(source_layer[L5A])[0]
      l5b_gids = nest.GetNodes(source_layer[L5B])[0]
      print('gids and pos l5a ', len(l5a_gids), len(l5a_pos))
      print('gids and pos l5b ', len(l5b_gids), len(l5b_pos))
      aux_l5a = np.arange(len(l5a_gids) - 10)
      aux_l5b = np.arange(len(l5b_gids) - 10)
      pyrngs[0].shuffle(aux_l5a)
      pyrngs[0].shuffle(aux_l5b)
      idx_l5a = aux_l5a[:numb_neurons]  #indexes of selected gids within safe range
      idx_l5b = aux_l5b[:numb_neurons]  #indexes of selected gids within safe range
      #### FIX for multiple nodes #######
      my_CSN = [[l5a_gids[i],l5a_pos[i,:2].tolist()] for i in idx_l5a]
      my_PTN = [[l5b_gids[j],l5b_pos[j,:2].tolist()] for j in idx_l5b]
      circles_l5b_l5a = []

    out = {'CSN': my_CSN,'PTN': my_PTN,'M1_CIR_L5A_L5B':circles_l5b_l5a}
    print('check lens of samples: ',len(out['CSN']),len(out['PTN']))#,
    print('check elements: ',out['CSN'][:3],'    ',out['PTN'][:3])
    return out

  if area_lbl=='S1':
    L5A = area_lbl+'_'+'L5A_Pyr'
    L5B = area_lbl+'_'+'L5B_Pyr'
    my_area = 'S1'

    if channels:
      circles_l5b_l5a = get_input_column_layers_ctx(source_layer,circle_center,channels_radius,'S1') # A list with centers is sent as param
      my_PTN,my_CSN = [],[]
      for i in circles_l5b_l5a[0]: #l5b circles. iterate over circles
        for j in i:
          my_PTN.append([j[0],j[1][:2]]) #use only x and y positions in PTN
      for i in circles_l5b_l5a[1]: #l5a circles. iterate over circles
        for j in i:
          my_CSN.append([j[0],j[1][:2]]) #use only x and y positions in CSN
    else:
      #Neuron_pos_fileload = np.load('ctx/Neuron_pos_' + L5A + '.npz')
      #l5a_pos = Neuron_pos_fileload['Neuron_pos']
      #Neuron_pos_fileload = np.load('ctx/Neuron_pos_' + L5B + '.npz')
      #l5b_pos = Neuron_pos_fileload['Neuron_pos']
      
      Neuron_pos_fileload = np.loadtxt('/opt/data/log/'+L5A+'.txt')
      l5a_pos = Neuron_pos_fileload[:,1:]
      Neuron_pos_fileload = np.loadtxt('/opt/data/log/'+L5B+'.txt')
      l5b_pos = Neuron_pos_fileload[:,1:]
      
      l5a_gids = nest.GetNodes(source_layer[L5A])[0]
      l5b_gids = nest.GetNodes(source_layer[L5B])[0]
      print('gids and pos l5a ', len(l5a_gids), len(l5a_pos))
      print('gids and pos l5b ', len(l5b_gids), len(l5b_pos))
      aux_l5a = np.arange(len(l5a_gids) - 10)
      aux_l5b = np.arange(len(l5b_gids) - 10)
      pyrngs[0].shuffle(aux_l5a)
      pyrngs[0].shuffle(aux_l5b)
      idx_l5a = aux_l5a[:numb_neurons]  # random.sample(range(len(l5a_gids)-10), numb_neurons) #indexes of selected gids within safe range
      idx_l5b = aux_l5b[:numb_neurons]  # random.sample(range(len(l5b_gids)-10), numb_neurons) #indexes of selected gids within safe range
    #### FIX for multiple nodes #######
      my_CSN = [[l5a_gids[i],l5a_pos[i,:2].tolist()] for i in idx_l5a]
      my_PTN = [[l5b_gids[j],l5b_pos[j,:2].tolist()] for j in idx_l5b]
      circles_l5b_l5a = []

    out = {'CSN': my_CSN,'PTN': my_PTN,'S1_CIR_L5A_L5B':circles_l5b_l5a}
    print('check lens of samples: ',len(out['CSN']),len(out['PTN']))#,
    print('check elements: ',out['CSN'][:3],'    ',out['PTN'][:3])
    return out
  
  if area_lbl=='M2':
    print('ADD NEURONS TYPES FOR M2 !!!! ')


#-------------------------------------------------------------------------------
# Connect the ctx neurons of the chosen subset to the basal ganglia
#-------------------------------------------------------------------------------
def connect_ctx_bg(ctx_neurons_gid, bg_layer_gid):
  #import ipdb; ipdb.set_trace()
  log.debug("CONNECT %s", "X"*100)
  nest.Connect(pre=ctx_neurons_gid, post=nest.GetNodes(bg_layer_gid)[0][-len(ctx_neurons_gid):], conn_spec={'rule':'one_to_one'})

def connect_GPi2d_GPi3d(GPi2d,GPi3d): #connect GPi layer to fake GPi

  #nest.SetDefaults('static_synapse',{'receptor_type':0})
  conn_dict = {'rule':'one_to_one'}
  syn_dict = {'receptor_type':0}
  ##log.debug("CONNECT %s %s conn_spec=%s syn_spec=%s", GPi2d, GPi3d, conn_dict, syn_dict)
  nest.Connect(GPi2d,GPi3d, conn_spec=conn_dict,syn_spec=syn_dict)


#-------------------------------------------------------------------------------
# Connect the ctx neurons of the chosen subset to the cerebellum
#-------------------------------------------------------------------------------
def connect_region_ctx_cb(layer_ctx, layer_cb, ctx_subregion):
    if ctx_subregion == 'S1':
        print('Connect the ctx_S1 neurons of the chosen subset to the cerebellum')
        sigma_x = 0.1
        sigma_y = 0.1
        p_center = 0.08
        weight = 1.0
        delay = 10. #1.0
        conndict = {'connection_type': 'divergent',
                    'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                    'kernel': {
                        'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                    'weights': weight,
                    'delays': delay}
        #ntop.ConnectLayers(layer_ctx, layer_cb, conndict)

    elif ctx_subregion == 'M1':
        print('Connect the ctx_M1 neurons of the chosen subset to the cerebellum')
        sigma_x = 0.1
        sigma_y = 0.1
        p_center = 0.05
        weight = 0.5
        delay = 10.0 #1.0
        conndict = {'connection_type': 'divergent',
                    'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                    'kernel': {
                        'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                    'weights': weight,
                    'delays': delay}
        #ntop.ConnectLayers(layer_ctx, layer_cb, conndict)

    else:
        print('Cortex Subregion is not set firmly to connect to the cerebellum. check the simulation file.')



#-------------------------------------------------------------------------------
# record one pre-neuron out-degree information
# sun 20190617
#-------------------------------------------------------------------------------
def save_conn(pre_layer_gid, post_layer_gid, conn_name):
    pre_neuron_GID = 0#ntop.FindCenterElement(pre_layer_gid)
    post_neuron_GIDs = nest.GetNodes(post_layer_gid)[0]
    connections = nest.GetConnections(pre_neuron_GID, post_neuron_GIDs)
    conn_list = np.zeros((len(connections), 10))
    for i_ in range(len(connections)):
        info = nest.GetStatus([connections[i_]])
        weight = info[0]['weight']
        delay = info[0]['delay']
        pre_neuron_GID = connections[i_][0]
        post_neuron_GID = connections[i_][1]
        conn_list[i_, 0] = pre_neuron_GID
        conn_list[i_, 1] = post_neuron_GID
        conn_list[i_, 2] = weight
        conn_list[i_, 3] = delay
        conn_list[i_, 4:7] = 0#np.asarray(ntop.GetPosition([pre_neuron_GID])[0])
        conn_list[i_, 7:] = 0#np.asarray(ntop.GetPosition([post_neuron_GID])[0])
    np.savetxt('/opt/data/log/conn_list_%s.csv' % conn_name, conn_list, delimiter=",", fmt='%.3f')

#-------------------------------------------------------------------------------
# Connect the thalamus neurons of the chosen subset to the ctx
# sun 20190603
#-------------------------------------------------------------------------------
def connect_region_th_ctx(layer_th, layer_ctx, ctx_subregion):
    if ctx_subregion == 'S1':
        print('Connect the ctx_S1 neurons of the chosen subset to the thalamus')
        ctx_rec1 = layer_ctx['S1_L5B_Pyr']
        ctx_rec2 = layer_ctx['S1_L5B_PV']
        ctx_rec3 = layer_ctx['S1_L5B_SST']
        th_e_proj = layer_th['TH_S1_EZ']['thalamic_nucleus_TC']
        th_i_proj = layer_th['TH_S1_IZ']['thalamic_nucleus_TC']

        # th to ctx
        # TC to L5B PY (S1)
        sigma_x = 0.1
        sigma_y = 0.1
        p_center = 0.2
        weight = 0.1
        delay = 10.0
        conndict = {'connection_type': 'divergent',
                     'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                    'kernel': {
                        'gaussian2D': {'p_center': p_center , 'sigma_x': sigma_x,
                                       'sigma_y': sigma_y}},
                    'weights': weight ,
                    'delays': delay}
        conndict_inh = {'connection_type': 'divergent',
                         'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                        'kernel': {
                            'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x,
                                           'sigma_y': sigma_y}},
                        'weights': weight ,
                        'delays': delay}

        #ntop.ConnectLayers(th_e_proj, ctx_rec1, conndict)
        #print ('TH_S1_EZ_thalamic_nucleus_TC to Pyr:')
        #_=save_conn(th_e_proj, ctx_rec1, 'TH_S1_EZ_thalamic_nucleus_TC_to_L5B_Pyr')

        #ntop.ConnectLayers(th_i_proj, ctx_rec1, conndict_inh)
        #print ('TH_S1_IZ_thalamic_nucleus_TC to Pyr:')
        #_ = save_conn(th_i_proj, ctx_rec1, 'TH_S1_IZ_thalamic_nucleus_TC_to_L5B_Pyr')

        # TC to L5B FS (S1)
        sigma_x = 0.1
        sigma_y = 0.1
        p_center = 1.
        weight = 0.1
        delay = 10.0
        conndict = {'connection_type': 'divergent',
                     'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                    'kernel': {
                        'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                    'weights': weight,
                    'delays': delay}
        conndict_inh = {'connection_type': 'divergent',
                         'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                        'kernel': {
                            'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x,
                                           'sigma_y': sigma_y}},
                        'weights': weight ,
                        'delays': delay}

        0#ntop.ConnectLayers(th_e_proj, ctx_rec2, conndict)
        #print ('TH_S1_EZ_thalamic_nucleus_TC to PV:')
        #_ = save_conn(th_e_proj, ctx_rec2, 'TH_S1_EZ_thalamic_nucleus_TC_to_L5B_PV')
        0#ntop.ConnectLayers(th_i_proj, ctx_rec2, conndict_inh)
        #print ('TH_S1_IZ_thalamic_nucleus_TC to PV:')
        #_ = save_conn(th_i_proj, ctx_rec2, 'TH_S1_IZ_thalamic_nucleus_TC_to_L5B_PV')



        # TC to L5B SST (S1)
        sigma_x = 0.1
        sigma_y = 0.1
        p_center = 1.
        weight = 0.1
        delay = 10.0
        conndict = {'connection_type': 'divergent',
                     'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                    'kernel': {
                        'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                    'weights': weight,
                    'delays': delay}
        conndict_inh = {'connection_type': 'divergent',
                         'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                        'kernel': {
                            'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x,
                                           'sigma_y': sigma_y}},
                        'weights': weight ,
                        'delays': delay}

        0#ntop.ConnectLayers(th_e_proj, ctx_rec3, conndict)

        #print ('TH_S1_EZ_thalamic_nucleus_TC to SST:')
        #_ = save_conn(th_e_proj, ctx_rec3, 'TH_S1_EZ_thalamic_nucleus_TC_to_L5B_SST')

        0#ntop.ConnectLayers(th_i_proj, ctx_rec3, conndict_inh)
        #print ('TH_S1_IZ_thalamic_nucleus_TC to SST:')
        #_ = save_conn(th_i_proj, ctx_rec3, 'TH_S1_IZ_thalamic_nucleus_TC_to_L5B_SST')


    elif ctx_subregion == 'M1':
        print('Connect the ctx_M1 neurons of the chosen subset to the thalamus')
        ctx_rec1 = layer_ctx['M1_L5B_PT']
        ctx_rec2 = layer_ctx['M1_L5B_PV']
        ctx_rec3 = layer_ctx['M1_L5B_SST']
        th_e_proj = layer_th['TH_M1_EZ']['thalamic_nucleus_TC']
        th_i_proj = layer_th['TH_M1_IZ']['thalamic_nucleus_TC']

        # th to ctx
        # TC to L5B PY (M1)
        sigma_x = 0.1
        sigma_y = 0.1
        p_center = 0.2
        weight = 0.1
        delay = 10.0
        conndict = {'connection_type': 'divergent',
                    'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                    'kernel': {
                        'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x,
                                       'sigma_y': sigma_y}},
                    'weights': weight ,
                    'delays': delay}
        conndict_inh = {'connection_type': 'divergent',
                         'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                        'kernel': {
                            'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x,
                                           'sigma_y': sigma_y}},
                        'weights': weight ,
                        'delays': delay}

        #ntop.ConnectLayers(th_e_proj, ctx_rec1, conndict)
        #print ('TH_M1_EZ_thalamic_nucleus_TC to PT:')
        #_ = save_conn(th_e_proj, ctx_rec1, 'TH_M1_EZ_thalamic_nucleus_TC_to_L5B_PT')

        #ntop.ConnectLayers(th_i_proj, ctx_rec1, conndict_inh)
        #print ('TH_M1_IZ_thalamic_nucleus_TC to PT:')
        #_ = save_conn(th_i_proj, ctx_rec1, 'TH_M1_IZ_thalamic_nucleus_TC_to_L5B_PT')

        # TC to L5B FS (S1)
        sigma_x = 0.1
        sigma_y = 0.1
        p_center = 1.0
        weight = 0.1
        delay = 10.0
        conndict = {'connection_type': 'divergent',
                     'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                    'kernel': {
                        'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                    'weights': weight,
                    'delays': delay}
        conndict_inh = {'connection_type': 'divergent',
                         'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                        'kernel': {
                            'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x,
                                           'sigma_y': sigma_y}},
                        'weights': weight,
                        'delays': delay}

        #ntop.ConnectLayers(th_e_proj, ctx_rec2, conndict)
        #print ('TH_M1_EZ_thalamic_nucleus_TC to PV:')
        #_ = save_conn(th_e_proj, ctx_rec2, 'TH_M1_EZ_thalamic_nucleus_TC_to_L5B_PV')

        #ntop.ConnectLayers(th_i_proj, ctx_rec2, conndict_inh)
        #print ('TH_M1_IZ_thalamic_nucleus_TC to PV:')
        #_ = save_conn(th_i_proj, ctx_rec2, 'TH_M1_IZ_thalamic_nucleus_TC_to_L5B_PV')

        # TC to L5B SST (S1)
        sigma_x = 0.1
        sigma_y = 0.1
        p_center = 1.0
        weight = 0.1
        delay = 10.0
        conndict = {'connection_type': 'divergent',
                     'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                    'kernel': {
                        'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                    'weights': weight,
                    'delays': delay}
        conndict_inh = {'connection_type': 'divergent',
                        'mask': {'box': {'lower_left': [-2., -2., -2.],
                                         'upper_right': [2., 2., 2.], }},
                        'kernel': {
                            'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x,
                                           'sigma_y': sigma_y}},
                        'weights': weight,
                        'delays': delay}

        #ntop.ConnectLayers(th_e_proj, ctx_rec3, conndict)
        #print ('TH_M1_EZ_thalamic_nucleus_TC to SST:')
        #_ = save_conn(th_e_proj, ctx_rec3, 'TH_M1_EZ_thalamic_nucleus_TC_to_L5B_SST')
        #ntop.ConnectLayers(th_i_proj, ctx_rec3, conndict_inh)
        #print ('TH_M1_IZ_thalamic_nucleus_TC to SST:')
        #_ = save_conn(th_i_proj, ctx_rec3, 'TH_M1_IZ_thalamic_nucleus_TC_to_L5B_SST')
    else:
        print ('Cortex Subregion is not set firmly to connect to the thalamus. check the simulation file.')


#-------------------------------------------------------------------------------
# Connect the ctx neurons of the chosen subset to the thalamus
#-------------------------------------------------------------------------------
def connect_region_ctx_th(layer_ctx, layer_th, ctx_subregion):
    if ctx_subregion == 'S1':
        print('Connect the ctx_S1 neurons of the chosen subset to the thalamus')
        ctx_proj1 = layer_ctx['S1_L6_Pyr']
        th_e_rec1 = layer_th['TH_S1_EZ']['thalamic_nucleus_TC']
        th_i_rec1 = layer_th['TH_S1_IZ']['thalamic_nucleus_TC']
        th_e_rec2 = layer_th['TH_S1_EZ']['thalamic_reticular_neucleus_RE']
        th_i_rec2 = layer_th['TH_S1_IZ']['thalamic_reticular_neucleus_RE']
        # ctx to th
        # L6PY to TC (S1)
        sigma_x = 0.1
        sigma_y = 0.1
        p_center = 0.2
        weight = 0.01
        delay = 10.0
        conndict = {'connection_type': 'divergent',
                    'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                    'kernel': {
                        'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                    'weights': weight,
                    'delays': delay}
        #ntop.ConnectLayers(ctx_proj1, th_e_rec1, conndict)
        #print ('S1_L6_Pyr to TH_S1_EZ_thalamic_nucleus_TC')
        #_ = save_conn(ctx_proj1, th_e_rec1, 'S1_L6_Pyr_TH_S1_EZ_thalamic_nucleus_TC')
        #ntop.ConnectLayers(ctx_proj1, th_i_rec1, conndict)
        #print ('S1_L6_Pyr to TH_S1_IZ_thalamic_nucleus_TC')
        #_ = save_conn(ctx_proj1, th_i_rec1, 'S1_L6_Pyr_TH_S1_IZ_thalamic_nucleus_TC')

        # L6PY to RE (S1)
        sigma_x = 0.1
        sigma_y = 0.1
        p_center = 1.0
        weight = 0.01
        delay = 10.0
        conndict = {'connection_type': 'divergent',
                    'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                    'kernel': {
                        'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                    'weights': weight,
                    'delays': delay}
        #ntop.ConnectLayers(ctx_proj1, th_e_rec2, conndict)
        #print ('S1_L6_Pyr to TH_S1_EZ_thalamic_reticular_neucleus_RE')
        #_ = save_conn(ctx_proj1, th_e_rec2, 'S1_L6_Pyr_TH_S1_EZ_thalamic_reticular_neucleus_RE')
        #ntop.ConnectLayers(ctx_proj1, th_i_rec2, conndict)
        #print ('S1_L6_Pyr to TH_S1_IZ_thalamic_reticular_neucleus_RE')
        #_ = save_conn(ctx_proj1, th_i_rec2, 'S1_L6_Pyr_TH_S1_IZ_thalamic_reticular_neucleus_RE')

    elif ctx_subregion == 'M1':
        print('Connect the ctx_M1 neurons of the chosen subset to the thalamus')

        ctx_proj1 = layer_ctx['M1_L6_CT']
        th_e_rec1 = layer_th['TH_M1_EZ']['thalamic_nucleus_TC']
        th_i_rec1 = layer_th['TH_M1_IZ']['thalamic_nucleus_TC']
        th_e_rec2 = layer_th['TH_M1_EZ']['thalamic_reticular_neucleus_RE']
        th_i_rec2 = layer_th['TH_M1_IZ']['thalamic_reticular_neucleus_RE']

        # ctx to th
        # L6PY to TC (S1)
        sigma_x = 0.1
        sigma_y = 0.1
        p_center = 0.2
        weight = 0.01
        delay = 10.0
        conndict = {'connection_type': 'divergent',
                    'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                    'kernel': {
                        'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                    'weights': weight,
                    'delays': delay}
        #ntop.ConnectLayers(ctx_proj1, th_e_rec1, conndict)
        #print ('M1_L6_CT to TH_M1_EZ_thalamic_nucleus_TC')
        #_ = save_conn(ctx_proj1, th_e_rec1, 'M1_L6_CT_TH_M1_EZ_thalamic_nucleus_TC')

        #ntop.ConnectLayers(ctx_proj1, th_i_rec1, conndict)
        #print ('M1_L6_CT to TH_M1_IZ_thalamic_reticular_neucleus_RE')
        #_ = save_conn(ctx_proj1, th_i_rec1, 'M1_L6_CT_TH_M1_IZ_thalamic_nucleus_TC')

        # L6PY to RE (S1)
        sigma_x = 0.1
        sigma_y = 0.1
        p_center = 1.0
        weight = 0.01
        delay = 10.0
        conndict = {'connection_type': 'divergent',
                    'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                    'kernel': {
                        'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                    'weights': weight,
                    'delays': delay}
        #ntop.ConnectLayers(ctx_proj1, th_e_rec2, conndict)
        #print ('M1_L6_CT to TH_M1_EZ_thalamic_nucleus_TC')
        #_ = save_conn(ctx_proj1, th_e_rec2, 'M1_L6_CT_TH_M1_EZ_thalamic_reticular_neucleus_RE')
        #ntop.ConnectLayers(ctx_proj1, th_i_rec2, conndict)
        #print ('M1_L6_CT to TH_M1_EZ_thalamic_reticular_neucleus_RE')
        #_ = save_conn(ctx_proj1, th_i_rec2, 'M1_L6_CT_TH_M1_IZ_thalamic_reticular_neucleus_RE')
    else:
        print ('Cortex Subregion is not set firmly to connect to the thalamus. check the simulation file.')


# Connest cb and th
def connect_region_cb_th(cb_layers, th_layers, cb_subregion):
    if cb_subregion == 'S1':
        print('Connect the sensory cb neurons of the chosen subset to the excitatory thalamus')
        cb_proj = cb_layers['CB'+'_'+cb_subregion+'_layer_vn']
        th_rec1 = th_layers['TH_S1_EZ']['thalamic_nucleus_TC']
        th_rec2 = th_layers['TH_S1_EZ']['thalamic_nucleus_IN']
        # #vn to TC
        # nest.Connect(nest.GetNodes(cb_layers['layer_vn'])[0], nest.GetNodes(th_layers['S1_EZ_th']['thalamic_nucleusTC'])[0], 'one_to_one', syn_spec={"weight": 3.0, "delay": 1.0})
        sigma_x = 0.1
        sigma_y = 0.1
        p_center = 1.0
        weight = 0.05
        delay = 2.  # 1.0
        conndict = {'connection_type': 'divergent',
                    'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                    'kernel': {
                        'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                    'weights': weight,
                    'delays': delay}
        #ntop.ConnectLayers(cb_proj, th_rec1, conndict)
        # print ('CB_'+cb_subregion+'_VN to thalamic_nucleus_TC')
        # _ = save_conn(cb_proj, th_rec1, 'CB_'+cb_subregion+'VN_thalamic_nucleus_TC')
        #
        # #vn to IN
        # nest.Connect(nest.GetNodes(cb_layers['layer_vn'])[0], nest.GetNodes(th_layers['S1_EZ_th']['thalamic_nucleusIN'])[0], 'one_to_one',syn_spec={"weight": 3.0, "delay": 1.0})
        sigma_x = 0.2
        sigma_y = 0.2
        p_center = 1.0
        weight = 0.1
        delay = 2.  # 1.0
        conndict = {'connection_type': 'divergent',
                    'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                    'kernel': {
                        'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                    'weights': weight,
                    'delays': delay}
        #ntop.ConnectLayers(cb_proj, th_rec2, conndict)
        # print ('CB_'+cb_subregion+'_IN to thalamic_nucleus_TC')
        # _ = save_conn(cb_proj, th_rec2, 'CB_'+cb_subregion+'IN_thalamic_nucleus_TC')



    elif cb_subregion == 'M1':
        print('Connect the sensory cb neurons of the chosen subset to the excitatory thalamus')
        cb_proj = cb_layers['CB'+'_'+cb_subregion+'_layer_vn']
        th_rec1 = th_layers['TH_M1_EZ']['thalamic_nucleus_TC']
        th_rec2 = th_layers['TH_M1_EZ']['thalamic_nucleus_IN']
        # #vn to TC
        # nest.Connect(nest.GetNodes(cb_layers['layer_vn'])[0], nest.GetNodes(th_layers['S1_EZ_th']['thalamic_nucleusTC'])[0], 'one_to_one', syn_spec={"weight": 3.0, "delay": 1.0})
        sigma_x = 0.1
        sigma_y = 0.1
        p_center = 1.0
        weight = 1.0
        delay = 2.  # 1.0
        conndict = {'connection_type': 'divergent',
                    'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                    'kernel': {
                        'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                    'weights': weight,
                    'delays': delay}
        #ntop.ConnectLayers(cb_proj, th_rec1, conndict)
        # print ('CB_'+cb_subregion+'_VN to thalamic_nucleus_TC')
        # _ = save_conn(cb_proj, th_rec1, 'CB_'+cb_subregion+'VN_thalamic_nucleus_TC')

        #
        # #vn to IN
        # nest.Connect(nest.GetNodes(cb_layers['layer_vn'])[0], nest.GetNodes(th_layers['S1_EZ_th']['thalamic_nucleusIN'])[0], 'one_to_one',syn_spec={"weight": 3.0, "delay": 1.0})
        sigma_x = 0.5
        sigma_y = 0.5
        p_center = 1.0
        weight = 0.1
        delay = 2.  # 1.0
        conndict = {'connection_type': 'divergent',
                    'mask': {'box': {'lower_left': [-2., -2., -2.],
                                     'upper_right': [2., 2., 2.], }},
                    'kernel': {
                        'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                    'weights': weight,
                    'delays': delay}
        #ntop.ConnectLayers(cb_proj, th_rec2, conndict)
        # print ('CB_'+cb_subregion+'_IN to thalamic_nucleus_TC')
        # _ = save_conn(cb_proj, th_rec2, 'CB_'+cb_subregion+'IN_thalamic_nucleus_TC')


def connect_region_bg_th(bg_layers, th_layers):
    print('Connect the bg neurons to the thalamus')
    #GPI to TC
    sigma_x = 0.13#0.5
    sigma_y = 0.13#0.5
    p_center = 0.9 #1.
    #PSG = nest.Create('poisson_generator', 1, params={'rate': 700.0, "start": 1000., "stop":2000.})
    #nest.Connect(PSG, nest.GetNodes(bg_layers['GPi_fake'])[0], syn_spec={'weight': -4.0, 'delay': 1.5})
    weight= -70.#-50.#1.0
    delay = 10.0 #1.0
    conndict = {'connection_type': 'divergent',
        #'mask': {'box': {'lower_left': [-2., -2., -2.],
        #                         'upper_right': [2., 2., 2.], }},
                 'mask': {'spherical': {'radius': 1.}},
                 'kernel': {
                     'gaussian2D': {'p_center': p_center, 'sigma_x': sigma_x, 'sigma_y': sigma_y}},
                 'weights': weight,
                 'delays': delay}

    #ntop.ConnectLayers(bg_layers['GPi_fake'], th_layers['TH_M1_IZ']['thalamic_nucleus_TC'], conndict)
    #print ('BG_GPi_fake to TH_M1_IZ_thalamic_nucleus_TC')
    #_ = save_conn(bg_layers['GPi_fake'], th_layers['TH_M1_IZ']['thalamic_nucleus_TC'], 'S1_L6_Pyr_TH_S1_IZ_thalamic_reticular_neucleus_RE')

########################################
#keep and update the weight information between two group gids
#save_conn_info for save all of the pre_gid post_gid and weight in a txt file
#pre_circle list from the all of circles' gid list for pre neurons
#post circle list from the all of circles' gid list for post neurons
########################################
def save_conn_info(pre_circle_list, post_circle_list, connfilename, trial_num):
  for i in range(len(pre_circle_list)):
    print ('start to get connections from gr to pkj circle ' + str(i))
    source = [gid[0] for gid in pre_circle_list[i]]
    target = [gid[0] for gid in post_circle_list[i]]
    connections = nest.GetConnections(source, target)
    conn_list = np.zeros((len(connections), 3))
    for j in range(len(connections)):
      info = nest.GetStatus([connections[j]])
      conn_list[j, 0] = connections[j][0]
      conn_list[j, 1] = connections[j][1]
      conn_list[j, 2] = info[0]['weight']
    np.savetxt('/opt/data/log/' + connfilename+'_circle_'+str(i) + '_trial_'+str(trial_num)+'.txt', conn_list, fmt='%1.5f', delimiter=',')

########################################
#keep and update the weight information between two group gids
#update connection weights of the pre_gid post_gid and weight in a txt file
#pre_circle list from the all of circles' gid list for pre neurons
#post circle list from the all of circles' gid list for post neurons
########################################
def update_conn_info(pre_circle_list, post_circle_list, connfilename, trial_num, learning_rate=[1., 1., 1., 1., 1. , 1. ]):
  #learning_rate=[1., 1., 0., 1., 1. , 1. ]
  new_weight_list=[0., 0., 0., 0., 0., 0.]
  for i in range (len(learning_rate)):
    conn_list = np.loadtxt('/opt/data/log/' + connfilename+'_circle_'+str(i)+ '_trial_'+str(trial_num-1)+'.txt', delimiter=',')
    new_weight_list[i]=conn_list[0][2]*learning_rate[i]
  for i in range(len(pre_circle_list)):
    print ('start to update gr to pkj circle ' + str(i))
    source = [gid[0] for gid in pre_circle_list[i]]
    target = [gid[0] for gid in post_circle_list[i]]
    connections = nest.GetConnections(source, target)
    nest.SetStatus(connections, {'weight': new_weight_list[i]})
    #conn_list=np.loadtxt('/opt/data/log/' + connfilename + '_circle_' + str(i) + '.txt', delimiter=',' )
    #for j in range(len(conn_list)):
      #conn=nest.GetConnections([int(conn_list[j, 0])], [int(conn_list[j, 1])])
      #nest.SetStatus(conn, {'weight': new_weight_list[i]})
  save_conn_info(pre_circle_list, post_circle_list, connfilename, trial_num)
