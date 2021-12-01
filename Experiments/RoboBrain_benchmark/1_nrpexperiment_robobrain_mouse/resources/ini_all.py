#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
## ini_all.py
##
## This contains region-specific initialization functions, based on provided parameters.

# nest_routines contains all nest-specific calls
import numpy as np
import nest_routine
import nest
import time
import collections

#---------------------------------------------------------------------------------------------
# instantiate cortex model
#---------------------------------------------------------------------------------------------
def instantiate_ctx(ctx_params,scalefactor, initial_ignore, region_name):
  Layer_Name = ctx_params[region_name]['structure_info']['Layer_Name']
  layer_size = ctx_params[region_name]['structure_info']['region_size']
  layer_thickness = ctx_params[region_name]['structure_info']['layer_thickness']
  layer_depth = ctx_params[region_name]['structure_info']['layer_depth']
  SubSubRegion_Excitatory = []
  SubSubRegion_Inhibitory = []
  ctx_layers = {}
  for l in range(len(Layer_Name)):
    print('#-------------------------------------------#')
    print('start to create layer in  '+region_name+' ' + Layer_Name[l])
    ctx_params[region_name]['neuro_info'][Layer_Name[l]] = collections.OrderedDict(sorted(ctx_params[region_name]['neuro_info'][Layer_Name[l]].items(), key=lambda t: t[0]))
    for n_type in ctx_params[region_name]['neuro_info'][Layer_Name[l]].keys():
      print (Layer_Name[l])
      print('neuron type:'+n_type)
      n_type_info = ctx_params[region_name]['neuro_info'][Layer_Name[l]][n_type]
      neuronmodel = nest_routine.copy_neuron_model(ctx_params[region_name]['neuro_info'][Layer_Name[l]][n_type]['neuron_model'], n_type_info, region_name+'_'+Layer_Name[l]+'_'+n_type)
      Neuron_pos=nest_routine.gen_neuron_postions_ctx(layer_depth[l], layer_thickness[l], n_type_info['Cellcount_mm2'], layer_size, scalefactor, 'Neuron_pos_'+region_name+'_'+Layer_Name[l]+'_'+n_type)
      if n_type_info['EorI'] == "E":
        SubSubRegion_Excitatory.append(nest_routine.create_layers_ctx( Neuron_pos, neuronmodel))
        ctx_layers[region_name+'_'+Layer_Name[l]+'_'+n_type] = SubSubRegion_Excitatory[-1]
        nest_routine.save_layers_position(region_name+'_'+Layer_Name[l]+'_'+n_type, SubSubRegion_Excitatory[-1],Neuron_pos)
        layer_name = region_name + '_' + Layer_Name[l] + '_' + n_type
        nest_routine.add_poisson_generator(SubSubRegion_Excitatory [-1], n_type_info['EorI'],layer_name, initial_ignore, region_name)
      elif n_type_info['EorI'] == "I":
        SubSubRegion_Inhibitory.append(nest_routine.create_layers_ctx(Neuron_pos, neuronmodel))
        ctx_layers[region_name+'_'+Layer_Name[l]+'_'+n_type] = SubSubRegion_Inhibitory[-1]
        nest_routine.save_layers_position(region_name+'_'+Layer_Name[l]+'_'+n_type, SubSubRegion_Inhibitory[-1], Neuron_pos)
        layer_name = region_name + '_' + Layer_Name[l] + '_' + n_type
        nest_routine.add_poisson_generator(SubSubRegion_Inhibitory[-1], n_type_info['EorI'], layer_name, initial_ignore, region_name)
      else:
        print('Error: Unknow E or I')
      _ = nest_routine.randomizing_mp(ctx_layers[region_name + '_' + Layer_Name[l] + '_' + n_type], n_type_info['spike_threshold'], n_type_info['reset_value'])
  # make connections
  print("Start to connect the layers")
  ctx_layers = collections.OrderedDict(sorted(ctx_layers.items(), key=lambda t: t[0]))
  internal_connection = np.load('ctx/'+ ctx_params[region_name]['connection_info']['internal'], allow_pickle=True)
  from collections import defaultdict
  for pre_layer_name in ctx_layers.keys():
    for post_layer_name in ctx_layers.keys():
      print ('start to connect '+pre_layer_name+' with '+post_layer_name)
      nest_routine.connect_layers_ctx(ctx_layers[pre_layer_name], ctx_layers[post_layer_name],internal_connection[pre_layer_name][post_layer_name])
  return ctx_layers
'''
def instantiate_ctx_M1(ctx_M1_params,scalefactor, initial_ignore):
  region_name = 'M1'
  # set the parameters for M1 model
  M1_Layer_Name = ctx_M1_params[region_name]['structure_info']['Layer_Name']
  M1_layer_size = ctx_M1_params[region_name]['structure_info']['region_size']
  M1_layer_size = np.array(M1_layer_size)
  M1_layer_thickness = ctx_M1_params['M1']['structure_info']['layer_thickness']
  M1_layer_depth = ctx_M1_params[region_name]['structure_info']['layer_depth']
  topo_extend = [M1_layer_size[0]*int(scalefactor[0])+1.,  M1_layer_size[1]*int(scalefactor[1])+ 1., 3.]
  topo_center = [0.0, 0.0, 0.0]
  SubSubRegion_Excitatory = []
  SubSubRegion_Inhibitory = []
  SubSubRegion_Excitatory_ntype = []
  SubSubRegion_Inhibitory_ntype = []
  ctx_M1_layers = {}
  for l in range(len(M1_Layer_Name)):
    print('###########################################')
    print('start to create layer in M1: ' + M1_Layer_Name[l])
    ## Fix for multiple nodes ##
    ctx_M1_params[region_name]['neuro_info'][M1_Layer_Name[l]] = collections.OrderedDict(sorted(ctx_M1_params[region_name]['neuro_info'][M1_Layer_Name[l]].items(), key=lambda t: t[0]))
    ##########################
    for n_type in ctx_M1_params[region_name]['neuro_info'][M1_Layer_Name[l]].keys():
      n_type_index = ctx_M1_params[region_name]['neuro_info'][M1_Layer_Name[l]][n_type]['n_type_index']
      print (M1_Layer_Name[l])
      print('n_type_index:', n_type_index)
      print(n_type)
      n_type_info = ctx_M1_params[region_name]['neuro_info'][M1_Layer_Name[l]][n_type]
      neuronmodel = nest_routine.copy_neuron_model(ctx_M1_params[region_name]['neuro_info'][M1_Layer_Name[l]][n_type]['neuron_model'], n_type_info, region_name + '_' +M1_Layer_Name[l] + '_' + n_type)
      topo_center[2] = M1_layer_depth[l] + 0.5 * M1_layer_thickness[l]
      Neuron_pos = nest_routine.gen_neuron_postions_ctx(M1_layer_depth[l], M1_layer_thickness[l], n_type_info['Cellcount_mm2'], M1_layer_size, scalefactor,'Neuron_pos_' +region_name+'_'+M1_Layer_Name[l]+'_'+n_type)
      if n_type_info['EorI'] == "E":
        SubSubRegion_Excitatory.append(nest_routine.create_layers_ctx_M1(topo_extend, topo_center, Neuron_pos, neuronmodel))
        SubSubRegion_Excitatory_ntype.append([M1_Layer_Name[l], n_type])
        ctx_M1_layers[region_name+'_'+M1_Layer_Name[l]+ '_' +n_type] = SubSubRegion_Excitatory[-1]
        nest_routine.save_layers_position(region_name + '_' + M1_Layer_Name[l] + '_' + n_type, SubSubRegion_Excitatory[-1], Neuron_pos)
        layer_name = region_name+'_'+M1_Layer_Name[l]+ '_' +n_type
        nest_routine.add_poisson_generator(SubSubRegion_Excitatory[-1], n_type_info['EorI'],layer_name,initial_ignore, region_name)
        print(n_type_info['spike_threshold'], n_type_info['reset_value'])
        _ = nest_routine.randomizing_mp(SubSubRegion_Excitatory[-1], n_type_info['spike_threshold'], n_type_info['reset_value'])
      elif n_type_info['EorI'] == "I":
        SubSubRegion_Inhibitory.append(nest_routine.create_layers_ctx_M1(topo_extend, topo_center, Neuron_pos, neuronmodel))
        SubSubRegion_Inhibitory_ntype.append([M1_Layer_Name[l], n_type])
        ctx_M1_layers[region_name+'_'+M1_Layer_Name[l]+ '_' +n_type] = SubSubRegion_Inhibitory[-1]
        nest_routine.save_layers_position(region_name + '_' + M1_Layer_Name[l] + '_' + n_type,SubSubRegion_Inhibitory[-1], Neuron_pos)
        layer_name = region_name + '_' + M1_Layer_Name[l] + '_' + n_type
        nest_routine.add_poisson_generator(SubSubRegion_Inhibitory[-1], n_type_info['EorI'], layer_name, initial_ignore, region_name)
        print(n_type_info['spike_threshold'], n_type_info['reset_value'])
        _ = nest_routine.randomizing_mp(SubSubRegion_Inhibitory[-1], n_type_info['spike_threshold'], n_type_info['reset_value'])
      else:
        print('Error: Unknow E or I')
  
  print("Start to connect the layers")
  M1_internal_connection = np.load('ctx/'+ ctx_M1_params['M1']['connection_info']['M1toM1'], allow_pickle=True)
  from collections import defaultdict
  for pre_layer_name in ctx_M1_layers.keys():
    for post_layer_name in ctx_M1_layers.keys():
      print ('start to connect '+pre_layer_name+' with '+post_layer_name)
      nest_routine.connect_layers_ctx_M1(ctx_M1_layers[pre_layer_name], ctx_M1_layers[post_layer_name], M1_internal_connection[pre_layer_name][post_layer_name])
  return ctx_M1_layers



def instantiate_ctx_M2(ctx_M2_params):
  # set the parameters for M2 model
  M2_Layer_Name = ctx_M2_params['M2']['structure_info']['Layer_Name']
  M2_layer_size = ctx_M2_params['M2']['structure_info']['region_size']
  M2_layer_size = np.array(M2_layer_size)
  topo_extend = M2_layer_size + 1.
  topo_center = M2_layer_size/2.
  SubSubRegion_Excitatory = []
  SubSubRegion_Inhibitory = []
  SubSubRegion_Excitatory_ntype = []
  SubSubRegion_Inhibitory_ntype = []
  ctx_M2_layers = {}
  for l in range(len(M2_Layer_Name)):
    print('###########################################')
    print('start to create layer: ' + M2_Layer_Name[l])
    Neuron_pos_fileload = np.load('ctx/M2/'+ ctx_M2_params['M2']['position_type_info'][M2_Layer_Name[l]])
    Neuron_pos = Neuron_pos_fileload['Neuron_pos']
    print('Network Architecture:')
    print(Neuron_pos.shape)
    print(ctx_M2_params['M2']['neuro_info'][M2_Layer_Name[l]].keys())
    for n_type in ctx_M2_params['M2']['neuro_info'][M2_Layer_Name[l]].keys():
      n_type_index = ctx_M2_params['M2']['neuro_info'][M2_Layer_Name[l]][n_type]['n_type_index']
      neuronmodel=ctx_M2_params['M2']['neuro_info'][M2_Layer_Name[l]][n_type]['neuron_model']
      print (M2_Layer_Name[l])
      print('n_type_index:', n_type_index)
      print(n_type)
      n_type_info = ctx_M2_params['M2']['neuro_info'][M2_Layer_Name[l]][n_type]
      if n_type_info['EorI'] == "E":
        pos = Neuron_pos[np.where(Neuron_pos[:, :, :, 3] == n_type_index)]
        SubSubRegion_Excitatory.append(nest_routine.create_layers_ctx_M2(topo_extend, topo_center, pos, neuronmodel, n_type_info))
        SubSubRegion_Excitatory_ntype.append([M2_Layer_Name[l], n_type])
        print (len(nest.GetNodes(SubSubRegion_Excitatory[-1])[0]))
        ctx_M2_layers[M2_Layer_Name[l]+n_type] = SubSubRegion_Excitatory[-1]
      elif n_type_info['EorI'] == "I":
        pos = Neuron_pos[np.where(Neuron_pos[:, :, :, 3] == n_type_index)]
        SubSubRegion_Inhibitory.append(nest_routine.create_layers_ctx_M2(topo_extend, topo_center, pos, neuronmodel, n_type_info))
        SubSubRegion_Inhibitory_ntype.append([M2_Layer_Name[l], n_type])
        print(len(nest.GetNodes(SubSubRegion_Inhibitory[-1])[0]))
        ctx_M2_layers[M2_Layer_Name[l]+n_type] = SubSubRegion_Inhibitory[-1]
      else:
        print('Error: Unknow E or I')
  
  print("Start to connect the layers")
  M2_internal_connection = np.load('ctx/M2/'+ ctx_M2_params['M2']['connection_info']['M2toM2'])

  from collections import defaultdict
  ctx_M2_layers_conn = defaultdict(dict)
  for pre_layer_name in ctx_M2_layers.keys():
      for post_layer_name in ctx_M2_layers.keys():
          print ('start to connect '+pre_layer_name+' with '+post_layer_name)
          connect_layers_ctx_M2(ctx_M2_layers[pre_layer_name], ctx_M2_layers[post_layer_name], M2_internal_connection[pre_layer_name][post_layer_name])
          conn_num= len(nest.GetConnections(nest.GetNodes(ctx_M2_layers[pre_layer_name])[0], nest.GetNodes(ctx_M2_layers[post_layer_name])[0]))
          ctx_M2_layers_conn[pre_layer_name][post_layer_name]={'conn_num':conn_num, 'neuron_num': len(nest.GetNodes(ctx_M2_layers[pre_layer_name])[0])}

  with open('log/ctx.log', 'a+') as f:
      for pre_layer_name in ctx_M2_layers.keys():
          count_in  = 0
          count_out = 0
          for post_layer_name in ctx_M2_layers.keys():
              print ('from layer '+ pre_layer_name+' to layer '+post_layer_name+' '+str(ctx_M2_layers_conn[pre_layer_name][post_layer_name]['conn_num']) + ' synapses were created', file=f)
              print ('synapse/neuron_num: '+ str(ctx_M2_layers_conn[pre_layer_name][post_layer_name]['conn_num']/ctx_M2_layers_conn[pre_layer_name][post_layer_name]['neuron_num']), file=f)
              count_out  = count_out + ctx_M2_layers_conn[pre_layer_name][post_layer_name]['conn_num']/ctx_M2_layers_conn[pre_layer_name][post_layer_name]['neuron_num']
              count_in = count_in + ctx_M2_layers_conn[post_layer_name][pre_layer_name]['conn_num']/ctx_M2_layers_conn[post_layer_name][pre_layer_name]['neuron_num']
              print('Layer ' + pre_layer_name + ' indegree : ' +str(count_in), file=f)
              print('Layer ' + pre_layer_name + ' outdegree : ' + str(count_out), file=f)
  f.close()
  return ctx_M2_layers

'''


def instantiate_th(th_params, scalefactor,initial_ignore):
  # set the parameters for Th model
  th_layers={}
  for rg in th_params.keys():
    th_layers[rg]={}
    subregion_name = th_params[rg]['structure_info']['subregion_name']
    subregion_size = th_params[rg]['structure_info']['region_size']
    subregion_size=np.array(subregion_size)
    SubSubRegion_Excitatory = []
    SubSubRegion_Inhibitory = []

    x_side_th_neurons = 32 * int(scalefactor[0])
    y_side_th_neurons = 32 * int(scalefactor[0])
    Neuron_pos_x = np.linspace(-subregion_size[0]*int(scalefactor[0])/2., subregion_size[0]*int(scalefactor[0])/2., x_side_th_neurons, endpoint=True)
    Neuron_pos_y = np.linspace(-subregion_size[1]*int(scalefactor[1])/2., subregion_size[1]*int(scalefactor[1])/2., y_side_th_neurons, endpoint=True)
    Neuron_pos_list = []
    for i in range(x_side_th_neurons):
      for j in range(y_side_th_neurons):
        Neuron_pos_list.append([Neuron_pos_x[i], Neuron_pos_y[j], 0.])
    for l in range(len(subregion_name)):
      print('###########################################')
      print('start to create subregions: ' + subregion_name[l])
      print(th_params[rg]['neuro_info'][subregion_name[l]].keys())
      for n_type in th_params[rg]['neuro_info'][subregion_name[l]].keys():
        n_type_info = th_params[rg]['neuro_info'][subregion_name[l]][n_type]
        neuronmodel = nest_routine.copy_neuron_model(th_params[rg]['neuro_info'][subregion_name[l]][n_type]['neuron_model'], n_type_info, rg + '_' + subregion_name[l]+ '_' + n_type)
        if n_type_info['EorI'] == "E":
          SubSubRegion_Excitatory.append(nest_routine.create_layers_th( Neuron_pos_list, neuronmodel))
          th_layers[rg][subregion_name[l]+'_'+n_type] = SubSubRegion_Excitatory[-1]
          nest_routine.save_layers_position(rg + '_' + subregion_name[l] + '_' + n_type,SubSubRegion_Excitatory[-1], np.array(Neuron_pos_list))
          layer_name = rg + '_' + subregion_name[l]+'_'+n_type
          #ADD line below by Carlos :)
          nest_routine.add_poisson_generator(SubSubRegion_Excitatory[-1], n_type_info['EorI'],layer_name,initial_ignore,'TH')
        elif n_type_info['EorI'] == "I":
          SubSubRegion_Inhibitory.append(nest_routine.create_layers_th( Neuron_pos_list, neuronmodel))
          th_layers[rg][subregion_name[l]+'_'+n_type] = SubSubRegion_Inhibitory[-1]
          nest_routine.save_layers_position(rg + '_' + subregion_name[l] + '_' + n_type, SubSubRegion_Inhibitory[-1], np.array(Neuron_pos_list))
          layer_name = rg + '_' + subregion_name[l]+'_'+n_type
          nest_routine.add_poisson_generator(SubSubRegion_Inhibitory[-1], n_type_info['EorI'], layer_name,initial_ignore,'TH')
        else:
          print('Error: Unknow E or I')

    # make connections
    print("Start to connect the neurons")
    connection_info=th_params[rg]['connection_info']
    for pre_l in th_layers[rg].keys():
      for post_l in th_layers[rg].keys():
        print('start to connect ' + pre_l + ' with ' + post_l+' in region '+rg)
        nest_routine.connect_layers_th(th_layers[rg][pre_l], th_layers[rg][post_l], connection_info[pre_l][post_l])
  return th_layers


def instantiate_bg(bg_params, fake_inputs=False, ctx_inputs=None,scalefactor=[1,1]):
  bg_layers = {}
  ctx_bg_input = {}

  ################### CREATE LAYERS #######################
  print("BG Create Layers")

  #update bg_params with the scaled number of neurons
  # 1 mmmm2 is the base for # of neurons, if the surface increases more neurons are added
  for nucleus in ['MSN','FSI','STN','GPe','GPi','CSN','PTN','CMPf']:
    bg_params['nb' + nucleus] = bg_params['nb' + nucleus] * scalefactor[0] * scalefactor[1]
  
  for nucleus in ['GPi','MSN','FSI','STN','GPe','GPi_fake']:
    print("Creating MAIN nucleus "+nucleus+"...")
    bg_layers[nucleus] = nest_routine.create_layers_bg(bg_params, nucleus,scalefactor=scalefactor)
  
  #connect GPi2D to GPi3D(fake)
  print('connecting GPi 2D to fake GPi 3D ...')
  nest_routine.connect_GPi2d_GPi3d(bg_layers['GPi'], bg_layers['GPi_fake'])
  
  print('getting M connections GIDs and positions from cortex ...')
  numb_neurons = int(bg_params['num_neurons'] * scalefactor[0] * scalefactor[1])  # 1000 default, increasing with scaling
  minus_PG = 0
  ######
   ## missing part to be addressed later ...
  #####
  print('creating fake input layers in the BG ... ')
  rate=0.
  if fake_inputs:
    for fake_nucleus in ['CSN','PTN','CMPf']:
      rate = bg_params['normalrate'][fake_nucleus][0]
      mirror_neurons = None
      print("Creating fake input "+fake_nucleus+" with fire rate "+str(rate)+" Hz...")
      bg_layers[fake_nucleus]= nest_routine.create_layers_bg(bg_params, fake_nucleus, fake=rate, mirror_neurons=mirror_neurons,mirror_pos=None,scalefactor=scalefactor)

  
  ################### CONNECT LAYERS #######################
  print("BG connect layers")
  ## fix by NEST ##########
  #########################
  bg_params['alpha'] = collections.OrderedDict(sorted(bg_params['alpha'].items(), key=lambda t: t[0]))
  #########################
  for connection in bg_params['alpha']:
    src = connection[0:3]
    tgt = connection[-3:]
    if src == 'CMP':
      src = 'CMPf' # string split on '->' would be better
    # if not fake_inputs, wire only in case of intra-BG connection
    if fake_inputs or src in ['MSN','FSI','STN','GPe','GPi']:
      if src in ['MSN','FSI','GPe','GPi']:
        nType = 'in'
      else:
        nType = 'ex'
      nest_routine.connect_layers_bg(bg_params, nType, bg_layers, src, tgt, projType=bg_params['cType'+src+tgt], redundancy=bg_params['redundancy'+src+tgt], RedundancyType=bg_params['RedundancyType'],verbose=True,scalefactor=scalefactor)
    
  return bg_layers,ctx_bg_input    

def instantiate_cb(subCB, scalefactor, sim_params):

  # define all neurons
  subCB_name='CB'+'_'+subCB
  import CBnetwork
  import CBneurons
  CBneurons.create_neurons(subCB_name)
  # define all layers
  print("start to create CB layers")

  layer_gr = nest_routine.create_layers_cb(32*scalefactor[0], 32*scalefactor[1], subCB_name, elements=[subCB_name+'_layer_gr', 400], extent=[scalefactor[0], scalefactor[1], 1.], center= [0., 0., 0.] )
  layer_go = nest_routine.create_layers_cb(32*scalefactor[0], 32*scalefactor[1], subCB_name, elements=[subCB_name+'_layer_go', 1], extent=[scalefactor[0], scalefactor[1], 1.], center= [0., 0., 0.])
  layer_pkj = nest_routine.create_layers_cb(32*scalefactor[0], 32*scalefactor[1], subCB_name, elements=[subCB_name+'_layer_pkj', 1], extent=[scalefactor[0], scalefactor[1], 1.], center= [0., 0., 0.])
  layer_bs = nest_routine.create_layers_cb(32*scalefactor[0], 32*scalefactor[1], subCB_name, elements=[subCB_name+'_layer_bs', 1], extent=[scalefactor[0], scalefactor[1], 1.], center= [0., 0., 0.])
  layer_vn = nest_routine.create_layers_cb(32*scalefactor[0], 32*scalefactor[1], subCB_name, elements=[subCB_name+'_layer_vn', 1], extent=[scalefactor[0], scalefactor[1], 1.], center= [0., 0., 0.])
  layer_pons = nest_routine.create_layers_cb(32 * scalefactor[0], 32 * scalefactor[1], subCB_name,elements=[subCB_name + '_layer_pons', 1],extent=[scalefactor[0], scalefactor[1], 1.], center=[0., 0., 0.])
  #layer_io = nest_routine.create_layers_cb(1, 1, elements=['IO'], extent=[1., 1. , 1.], center= [0., 0., 0.])
  #layer_io_input = nest_routine.create_layers_cb(1, 1, elements=['MF_IO'])

  cb_layers = {}
  cb_layers[subCB_name + '_layer_pons'] = layer_pons
  cb_layers[subCB_name+'_layer_gr'] = layer_gr
  cb_layers[subCB_name+'_layer_go'] = layer_go
  cb_layers[subCB_name+'_layer_pkj'] = layer_pkj
  cb_layers[subCB_name+'_layer_bs'] = layer_bs
  cb_layers[subCB_name+'_layer_vn'] = layer_vn

  #cb_layers['layer_io'] = layer_io

  # connect layers
  print("start to connect CB layers")


  CBnetwork.go.go_to_gr(cb_layers[subCB_name+'_layer_go'], cb_layers[subCB_name+'_layer_gr'], subCB_name)
  CBnetwork.gr.gr_to_go(cb_layers[subCB_name+'_layer_gr'], cb_layers[subCB_name+'_layer_go'], subCB_name)
  CBnetwork.gr.gr_to_pkj(cb_layers[subCB_name+'_layer_gr'], cb_layers[subCB_name+'_layer_pkj'], subCB_name)
  #CBnetwork.gr.gr_to_pkj(columns_data_gr, columns_data_pkj, subCB_name)

  CBnetwork.gr.gr_to_bs(cb_layers[subCB_name+'_layer_gr'], cb_layers[subCB_name+'_layer_bs'], subCB_name)
  CBnetwork.pkj.pkj_to_vn(cb_layers[subCB_name+'_layer_pkj'], cb_layers[subCB_name+'_layer_vn'], subCB_name)
  #CBnetwork.pkj.pkj_to_vn(columns_data_pkj, columns_data_vn, subCB_name)
  CBnetwork.bs.bs_to_pkj(cb_layers[subCB_name+'_layer_bs'], cb_layers[subCB_name+'_layer_pkj'], subCB_name)
  CBnetwork.pons.pons_to_gr(cb_layers[subCB_name + '_layer_pons'], cb_layers[subCB_name + '_layer_gr'], subCB_name)
  #CBnetwork.pons.pons_to_gr(columns_data_pons, columns_data_gr, subCB_name)

  return cb_layers

