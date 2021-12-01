#!/usr/bin/env python
# -*- coding: utf-8 -*-
# please set all flags before run the simulation
##

import fetch_params
import ini_all
import nest_routine
import nest
import numpy as np
import time


def main():
    start_time = time.time()
    # 1) reads parameters
    sim_params = fetch_params.read_sim()

    for sim_model in sim_params['sim_model'].keys():
        if sim_params['sim_model'][sim_model]['on']:
            sim_regions = sim_params['sim_model'][sim_model]['regions']
            sim_model_on = sim_model
            print('simulation model ', sim_model_on, ' will start')
    if sim_regions['S1']:
        ctx_params = fetch_params.read_ctx()
    if sim_regions['M1']:
        ctx_M1_params = fetch_params.read_ctx_M1()
    if sim_regions['TH_S1'] or sim_regions['TH_M1']:
        th_params = fetch_params.read_th()
    if sim_regions['BG']:
        bg_params = fetch_params.read_bg()
    if sim_regions['CB_S1'] or sim_regions['CB_M1']:
        cb_params = fetch_params.read_cb()
    conn_params = fetch_params.read_conn()

    # 1.5) initialize nest
    nest_routine.initialize_nest(sim_params)

    # 2) instantiates regions
    if sim_regions['S1']:
        ctx_layers = ini_all.instantiate_ctx(ctx_params, sim_params['scalefactor'], sim_params['initial_ignore'], 'S1')
    if sim_regions['M1']:
        ctx_M1_layers = ini_all.instantiate_ctx(ctx_M1_params, sim_params['scalefactor'], sim_params['initial_ignore'],
                                                'M1')
        # ctx_M1_layers = ini_all.instantiate_ctx_M1(ctx_M1_params, sim_params['scalefactor'],sim_params['initial_ignore'])
    if sim_regions['TH_S1'] or sim_regions['TH_M1']:
        th_layers = ini_all.instantiate_th(th_params, sim_params['scalefactor'], sim_params['initial_ignore'])
    if sim_regions['CB_S1']:
        cb_layers_S1 = ini_all.instantiate_cb('S1', sim_params['scalefactor'], sim_params)
    if sim_regions['CB_M1']:
        cb_layers_M1 = ini_all.instantiate_cb('M1', sim_params['scalefactor'], sim_params)
    if sim_regions['BG']:
        bg_layers, ctx_bg_input = ini_all.instantiate_bg(bg_params, fake_inputs=True, ctx_inputs=None,
                                                         scalefactor=sim_params['scalefactor'])

    if sim_regions['BG']:
        if sim_params['channels']:  # if True
            bg_params['channels'] = True  # for channels input tasks
        else:
            bg_params['channels'] = False  # resting state
        bg_params['circle_center'] = nest_routine.get_channel_centers(sim_params, hex_center=[0, 0],
                                                                      ci=sim_params['channels_nb'],
                                                                      hex_radius=sim_params['hex_radius'])
        #### Basal ganglia inter-regional connection with S1 and M1 ######
        if sim_regions['S1']:
            if sim_regions['M1']:
                bg_layers, ctx_bg_input = ini_all.instantiate_bg(bg_params, fake_inputs=True,
                                                                 ctx_inputs={'M1': {'layers': ctx_M1_layers,
                                                                                    'params': ctx_M1_params},
                                                                             'S1': {'layers': ctx_layers,
                                                                                    'params': ctx_params},
                                                                             'M2': None},
                                                                 scalefactor=sim_params['scalefactor'])
            else:
                bg_layers, ctx_bg_input = ini_all.instantiate_bg(bg_params, fake_inputs=True,
                                                                 ctx_inputs={'M1': None,
                                                                             # {'layers': ctx_M1_layers, 'params': ctx_M1_params},
                                                                             'S1': {'layers': ctx_layers,
                                                                                    'params': ctx_params},
                                                                             'M2': None},
                                                                 scalefactor=sim_params['scalefactor'])
        else:
            if sim_regions['M1']:
                bg_layers, ctx_bg_input = ini_all.instantiate_bg(bg_params, fake_inputs=True,
                                                                 ctx_inputs={'M1': {'layers': ctx_M1_layers,
                                                                                    'params': ctx_M1_params},
                                                                             'S1': None,
                                                                             # {'layers': ctx_layers, 'params': ctx_params},
                                                                             'M2': None},
                                                                 scalefactor=sim_params['scalefactor'])
            else:
                bg_layers, ctx_bg_input = ini_all.instantiate_bg(bg_params, fake_inputs=True,
                                                                 ctx_inputs={'M1': None,
                                                                             # {'layers': ctx_M1_layers, 'params': ctx_M1_params},
                                                                             'S1': None,
                                                                             # {'layers': ctx_layers, 'params': ctx_params},
                                                                             'M2': None},
                                                                 scalefactor=sim_params['scalefactor'])
    with open('/opt/data/log/' + 'performance.txt', 'a') as file:
        file.write('Network_Building_Time ' + str(time.time() - start_time) + '\n')
        # 3) interconnect regions
    start_time = time.time()
    if sim_regions['S1'] and sim_regions['M1']:
        pass
        # _ = nest_routine.connect_region_ctx_cb(ctx_layers['S1_L5B_Pyr'], cb_layers_S1['CB_S1_layer_pons'], 'S1')
    if sim_regions['S1'] and sim_regions['CB_S1']:
        _ = nest_routine.connect_region_ctx_cb(ctx_layers['S1_L5B_Pyr'], cb_layers_S1['CB_S1_layer_pons'], 'S1')
    if sim_regions['M1'] and sim_regions['CB_M1']:
        _ = nest_routine.connect_region_ctx_cb(ctx_M1_layers['M1_L5B_PT'], cb_layers_M1['CB_M1_layer_pons'], 'M1')
    if sim_regions['S1'] and sim_regions['TH_S1']:
        _ = nest_routine.connect_region_ctx_th(ctx_layers, th_layers, 'S1')
    if sim_regions['M1'] and sim_regions['TH_M1']:
        _ = nest_routine.connect_region_ctx_th(ctx_M1_layers, th_layers, 'M1')
    if sim_regions['TH_S1'] and sim_regions['S1']:
        _ = nest_routine.connect_region_th_ctx(th_layers, ctx_layers, 'S1')
    if sim_regions['TH_M1'] and sim_regions['M1']:
        _ = nest_routine.connect_region_th_ctx(th_layers, ctx_M1_layers, 'M1')
    if sim_regions['CB_S1'] and sim_regions['S1']:
        _ = nest_routine.connect_region_cb_th(cb_layers_S1, th_layers, 'S1')
    if sim_regions['CB_M1'] and sim_regions['M1']:
        _ = nest_routine.connect_region_cb_th(cb_layers_M1, th_layers, 'M1')
    if sim_regions['BG'] and sim_regions['TH_M1']:
        _ = nest_routine.connect_region_bg_th(bg_layers, th_layers)
    with open('/opt/data/log/' + 'performance.txt', 'a') as file:
        file.write('Interconnect_Regions_Time ' + str(time.time() - start_time) + '\n')

    # 2.5) detectors

    detectors = {}
    if sim_regions['BG']:
        for layer_name in bg_layers.keys():
            detectors[layer_name] = nest_routine.layer_spike_detector(bg_layers[layer_name], layer_name,
                                                                      sim_params['initial_ignore'])
            # detectors[layer_name] = []
    '''
    if sim_regions['S1']:
        for layer_name in ctx_layers.keys():
            detectors[layer_name] = nest_routine.layer_spike_detector(ctx_layers[layer_name], layer_name, sim_params['initial_ignore'])
    if sim_regions['M1']:
        for layer_name in ctx_M1_layers.keys():
            detectors[layer_name] = nest_routine.layer_spike_detector(ctx_M1_layers[layer_name], layer_name, sim_params['initial_ignore'])
    if sim_regions['CB_S1']:
        for layer_name in cb_layers_S1.keys():
            detectors[layer_name] = nest_routine.layer_spike_detector(cb_layers_S1[layer_name], layer_name, sim_params['initial_ignore'])
    if sim_regions['CB_M1']:
        for layer_name in cb_layers_M1.keys():
            detectors[layer_name] = nest_routine.layer_spike_detector(cb_layers_M1[layer_name], layer_name, sim_params['initial_ignore'])
    '''
    if sim_regions['TH_S1']:
        for layer_name in th_layers['TH_S1_EZ'].keys():
            detectors['TH_S1_EZ' + '_' + layer_name] = nest_routine.layer_spike_detector(
                th_layers['TH_S1_EZ'][layer_name], 'TH_S1_EZ_' + layer_name, sim_params['initial_ignore'])
        for layer_name in th_layers['TH_S1_IZ'].keys():
            detectors['TH_S1_IZ' + '_' + layer_name] = nest_routine.layer_spike_detector(
                th_layers['TH_S1_IZ'][layer_name], 'TH_S1_IZ_' + layer_name, sim_params['initial_ignore'])
    if sim_regions['TH_M1']:
        for layer_name in th_layers['TH_M1_EZ'].keys():
            detectors['TH_M1_EZ' + '_' + layer_name] = nest_routine.layer_spike_detector(
                th_layers['TH_M1_EZ'][layer_name], 'TH_M1_EZ_' + layer_name, sim_params['initial_ignore'])
        for layer_name in th_layers['TH_M1_IZ'].keys():
            detectors['TH_M1_IZ' + '_' + layer_name] = nest_routine.layer_spike_detector(
                th_layers['TH_M1_IZ'][layer_name], 'TH_M1_IZ_' + layer_name, sim_params['initial_ignore'])
    print('Start simulation for : ', sim_model_on)

    if sim_model_on == 'resting_state':
        simulation_time = sim_params['simDuration'] + sim_params['initial_ignore']
        start_time = time.time()
        print('Simulation Started:', start_time)
        # BF nest.Simulate(simulation_time)
        with open('/opt/data/log/' + 'performance.txt', 'a') as file:
            file.write('Simulation_Elapse_Time ' + str(time.time() - start_time) + '\n')
        print('Simulation Finish')

        if sim_regions['BG']:
            for layer_name in bg_layers.keys():
                rate = nest_routine.average_fr(detectors[layer_name], sim_params['simDuration'], len(
                    bg_layers[layer_name]))  # nest_routine.count_layer(bg_layers[layer_name]))
                print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")

        # if sim_regions['BG']:
        #    for layer_name in bg_layers.keys():
        #        rate = nest_routine.get_firing_rate_from_gdf_files(layer_name, detectors[layer_name], sim_params['simDuration'],
        #                                       nest_routine.count_layer(bg_layers[layer_name]))
        #        print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")
        ''' 
        if sim_regions['S1']:
            for layer_name in ctx_layers.keys():
              rate = nest_routine.average_fr(detectors[layer_name], sim_params['simDuration'],nest_routine.count_layer(ctx_layers[layer_name]))
              print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")

        #if sim_regions['S1']:
        #    for layer_name in ctx_layers.keys():
        #        rate = nest_routine.get_firing_rate_from_gdf_files(layer_name,detectors[layer_name], sim_params['simDuration'],
        #                                       nest_routine.count_layer(ctx_layers[layer_name]))
        #        print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")

        if sim_regions['M1']:
            for layer_name in ctx_M1_layers.keys():
              rate = nest_routine.average_fr(detectors[layer_name], sim_params['simDuration'], nest_routine.count_layer(ctx_M1_layers[layer_name]))
              print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")

        #if sim_regions['M1']:
        #    for layer_name in ctx_M1_layers.keys():
        #        rate = nest_routine.get_firing_rate_from_gdf_files(layer_name,detectors[layer_name], sim_params['simDuration'],
        #                                       nest_routine.count_layer(ctx_M1_layers[layer_name]))
        #        print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")

        if sim_regions['CB_S1']:
            for layer_name in cb_layers_S1.keys():
                rate = nest_routine.average_fr(detectors[layer_name], sim_params['simDuration'],
                                               nest_routine.count_layer(cb_layers_S1[layer_name]))
                print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")

        if sim_regions['CB_M1']:
            for layer_name in cb_layers_M1.keys():
                rate = nest_routine.average_fr(detectors[layer_name], sim_params['simDuration'],
                                               nest_routine.count_layer(cb_layers_M1[layer_name]))
                print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")

        #if sim_regions['CB_S1']:
        #    for layer_name in cb_layers_S1.keys():
        #        rate = nest_routine.get_firing_rate_from_gdf_files(layer_name,detectors[layer_name], sim_params['simDuration'],
        #                                       nest_routine.count_layer(cb_layers_S1[layer_name]))
        #        print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")
        #if sim_regions['CB_M1']:
        #    for layer_name in cb_layers_M1.keys():
        #        rate = nest_routine.get_firing_rate_from_gdf_files(layer_name, detectors[layer_name], sim_params['simDuration'],
        #                                       nest_routine.count_layer(cb_layers_M1[layer_name]))
        #        print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")
        '''
        if sim_regions['TH_S1']:
            for layer_name in th_layers['TH_S1_EZ'].keys():
                rate = nest_routine.average_fr(detectors['TH_S1_EZ' + '_' + layer_name], sim_params['simDuration'],
                                               nest_routine.count_layer(th_layers['TH_S1_EZ'][layer_name]))
                print('Layer ' + 'TH_S1_EZ_' + layer_name + " fires at " + str(rate) + " Hz")
            for layer_name in th_layers['TH_S1_IZ'].keys():
                rate = nest_routine.average_fr(detectors['TH_S1_IZ' + '_' + layer_name], sim_params['simDuration'],
                                               nest_routine.count_layer(th_layers['TH_S1_IZ'][layer_name]))
                print('Layer ' + 'TH_S1_IZ_' + layer_name + " fires at " + str(rate) + " Hz")
        if sim_regions['TH_M1']:
            for layer_name in th_layers['TH_M1_EZ'].keys():
                rate = nest_routine.average_fr(detectors['TH_M1_EZ' + '_' + layer_name], sim_params['simDuration'],
                                               nest_routine.count_layer(th_layers['TH_M1_EZ'][layer_name]))
                print('Layer ' + 'TH_M1_EZ_' + layer_name + " fires at " + str(rate) + " Hz")

            for layer_name in th_layers['TH_M1_IZ'].keys():
                rate = nest_routine.average_fr(detectors['TH_M1_IZ' + '_' + layer_name], sim_params['simDuration'],
                                               nest_routine.count_layer(th_layers['TH_M1_IZ'][layer_name]))
                print('Layer ' + 'TH_M1_IZ_' + layer_name + " fires at " + str(rate) + " Hz")

        print('>>> simulation ended <<<')
        print('Kernel Status: ')
        print(nest.GetKernelStatus())

        return ctx_M1_layers

        # if sim_regions['TH_S1']:
        #    for layer_name in th_layers['TH_S1_EZ'].keys():
        #        rate = nest_routine.get_firing_rate_from_gdf_files(layer_name, detectors['TH_S1_EZ' + '_' + layer_name], sim_params['simDuration'],
        #                                       nest_routine.count_layer(th_layers['TH_S1_EZ'][layer_name]))
        #        print('Layer ' + 'TH_S1_EZ_' + layer_name + " fires at " + str(rate) + " Hz")
        # if sim_regions['TH_S1']:
        #    for layer_name in th_layers['TH_S1_IZ'].keys():
        #        rate = nest_routine.get_firing_rate_from_gdf_files(layer_name, detectors['TH_S1_IZ' + '_' + layer_name], sim_params['simDuration'],
        #                                       nest_routine.count_layer(th_layers['TH_S1_IZ'][layer_name]))
        #        print('Layer ' + 'TH_S1_IZ_' + layer_name + " fires at " + str(rate) + " Hz")
        # if sim_regions['TH_M1']:
        #    for layer_name in th_layers['TH_M1_EZ'].keys():
        #        rate = nest_routine.get_firing_rate_from_gdf_files(layer_name, detectors['TH_M1_EZ' + '_' + layer_name], sim_params['simDuration'],
        #                                       nest_routine.count_layer(th_layers['TH_M1_EZ'][layer_name]))
        #        print('Layer ' + 'TH_M1_EZ_' + layer_name + " fires at " + str(rate) + " Hz")
        # if sim_regions['TH_M1']:
        #    for layer_name in th_layers['TH_M1_IZ'].keys():
        #        rate = nest_routine.get_firing_rate_from_gdf_files(layer_name, detectors['TH_M1_IZ' + '_' + layer_name], sim_params['simDuration'],
        #                                       nest_routine.count_layer(th_layers['TH_M1_IZ'][layer_name]))
        #        print('Layer ' + 'TH_M1_IZ_' + layer_name + " fires at " + str(rate) + " Hz")

    elif sim_model_on == 'cb_learning':

        stimulus_L5B = nest_routine.create_stimulus(scaling_stim=30 * 31.3, bias=15.)
        M1_psg_L5B, M1_syn_L5B = nest_routine.create_psg_channels(syn_weight=13., syn_delay=1.5,
                                                                  channels_nb=sim_params['channels_nb'])

        circle_center_params = nest_routine.get_channel_centers(sim_params, hex_center=[0, 0],
                                                                ci=sim_params['channels_nb'],
                                                                hex_radius=sim_params['hex_radius'])
        M1_L5B_columns_gids = nest_routine.get_columns_data('M1_L5B_PT', circle_center_params,
                                                            sim_params['channels_radius'])

        M1_L5B_circle_gid_detector, M1_L5B_circle_j_gids_nb = nest_routine.connect_channels_psg(M1_L5B_columns_gids,
                                                                                                M1_psg_L5B,
                                                                                                M1_syn_L5B)

        learning_rate = [1., 1., 0.5, 1., 1., 1.]
        circle_center_params = nest_routine.get_channel_centers(sim_params, hex_center=[0, 0],
                                                                ci=sim_params['channels_nb'],
                                                                hex_radius=sim_params['hex_radius'])

        columns_data_gr = nest_routine.get_columns_data('CB_M1_layer_gr', circle_center_params,
                                                        radius_small=sim_params['channels_radius'])
        columns_data_pkj = nest_routine.get_columns_data('CB_M1_layer_pkj', circle_center_params,
                                                         radius_small=sim_params['channels_radius'])
        columns_data_vn = nest_routine.get_columns_data('CB_M1_layer_vn', circle_center_params,
                                                        radius_small=sim_params['channels_radius'])

        CB_GR_circle_gid_detector, CB_GR_circle_j_gids_nb = nest_routine.spike_detector_channels(columns_data_gr)
        CB_PKJ_circle_gid_detector, CB_PKJ_circle_j_gids_nb = nest_routine.spike_detector_channels(columns_data_pkj)
        CB_VN_circle_gid_detector, CB_VN_circle_j_gids_nb = nest_routine.spike_detector_channels(columns_data_vn)

        nest.Simulate(int(sim_params['sim_model'][sim_model_on]['delta_t']))
        trials_nb = sim_params['sim_model'][sim_model_on]['trials_nb']
        trial_counter = 0

        while trial_counter < trials_nb:
            direction = 'CU'
            _ = nest_routine.apply_direction_stimulus_generic(direction=direction,
                                                              time_start=trial_counter * 500. + 100.,
                                                              time_stop=trial_counter * 500. + 400.,
                                                              psg=M1_psg_L5B, stimulus=stimulus_L5B)
            nest.Simulate(sim_params['sim_model'][sim_model_on]['delta_t'])

            for layer_name in ctx_M1_layers.keys():
                rate = nest_routine.average_fr_pre(detectors[layer_name],
                                                   nest_routine.count_layer(ctx_M1_layers[layer_name]),
                                                   start_time=trial_counter * sim_params['simDuration'] + 500,
                                                   end_time=(trial_counter + 1) * sim_params[
                                                       'simDuration'] + 500)
                print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")

            for layer_name in cb_layers_M1.keys():
                rate = nest_routine.average_fr_pre(detectors[layer_name],
                                                   nest_routine.count_layer(cb_layers_M1[layer_name]),
                                                   start_time=trial_counter * sim_params['simDuration'] + 500,
                                                   end_time=(trial_counter + 1) * sim_params[
                                                       'simDuration'] + 500)
                print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")

            for layer_name in CB_GR_circle_gid_detector.keys():
                rate = nest_routine.average_fr_pre(CB_GR_circle_gid_detector[layer_name],
                                                   CB_GR_circle_j_gids_nb[layer_name],
                                                   start_time=trial_counter * sim_params['simDuration'] + 500,
                                                   end_time=(trial_counter + 1) * sim_params[
                                                       'simDuration'] + 500)
                print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")

            for layer_name in CB_PKJ_circle_gid_detector.keys():
                rate = nest_routine.average_fr_pre(CB_PKJ_circle_gid_detector[layer_name],
                                                   CB_PKJ_circle_j_gids_nb[layer_name],
                                                   start_time=trial_counter * sim_params['simDuration'] + 500,
                                                   end_time=(trial_counter + 1) * sim_params[
                                                       'simDuration'] + 500)
                print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")
            for layer_name in CB_VN_circle_gid_detector.keys():
                rate = nest_routine.average_fr_pre(CB_VN_circle_gid_detector[layer_name],
                                                   CB_VN_circle_j_gids_nb[layer_name],
                                                   start_time=trial_counter * sim_params['simDuration'] + 500,
                                                   end_time=(trial_counter + 1) * sim_params[
                                                       'simDuration'] + 500)
                print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")
            _ = nest_routine.update_conn_info(columns_data_gr, columns_data_pkj, 'conn_gr_pkj',
                                              trial_counter + 1,
                                              learning_rate)
            trial_counter += 1
        print('cb learning finish')

    elif sim_model_on == 'multiple_arm_reaching':
        from wbnao import WBNao
        # Run the network for 500 ms to get a steady state....
        nest.Simulate(int(sim_params['sim_model'][sim_model_on]['delta_t']))

        # 5) Check if File exists to run simulation, if it doesn't exists wait some time and then check again.
        trials_nb = sim_params['sim_model'][sim_model_on]['trials_nb']
        trial_counter = 0
        # file_path = './log/LCR.txt'

        total_sim_time = sim_params['sim_model'][sim_model_on]['delta_t'] * trials_nb
        senders, spiketimes = [], []
        my_actions = [2, 3, 1, 2, 3, 1]

        wbnaox = WBNao()
        wbnaox.clean()
        stimulus_L5A = nest_routine.create_stimulus(scaling_stim=300 * 17.7, bias=2.)
        stimulus_L5B = nest_routine.create_stimulus(scaling_stim=300 * 31.3, bias=15.)
        M1_psg_L5A, M1_syn_L5A = nest_routine.create_psg_channels(syn_weight=11.5, syn_delay=1.5,
                                                                  channels_nb=sim_params['channels_nb'])
        M1_psg_L5B, M1_syn_L5B = nest_routine.create_psg_channels(syn_weight=13., syn_delay=1.5,
                                                                  channels_nb=sim_params['channels_nb'])
        S1_psg_L5A, S1_syn_L5A = nest_routine.create_psg_channels(syn_weight=2., syn_delay=1.5,
                                                                  channels_nb=sim_params['channels_nb'])
        S1_psg_L5B, S1_syn_L5B = nest_routine.create_psg_channels(syn_weight=2.2, syn_delay=1.5,
                                                                  channels_nb=sim_params['channels_nb'])

        circle_center_params = nest_routine.get_channel_centers(sim_params, hex_center=[0, 0],
                                                                ci=sim_params['channels_nb'],
                                                                hex_radius=sim_params['hex_radius'])
        M1_L5A_columns_gids = nest_routine.get_columns_data('M1_L5A_CS', circle_center_params,
                                                            sim_params['channels_radius'])
        M1_L5B_columns_gids = nest_routine.get_columns_data('M1_L5B_PT', circle_center_params,
                                                            sim_params['channels_radius'])
        S1_L5A_columns_gids = nest_routine.get_columns_data('S1_L5A_Pyr', circle_center_params,
                                                            sim_params['channels_radius'])
        S1_L5B_columns_gids = nest_routine.get_columns_data('S1_L5B_Pyr', circle_center_params,
                                                            sim_params['channels_radius'])

        M1_L5A_circle_gid_detector, M1_L5A_circle_j_gids_nb = nest_routine.connect_channels_psg(M1_L5A_columns_gids,
                                                                                                M1_psg_L5A, M1_syn_L5A)
        M1_L5B_circle_gid_detector, M1_L5B_circle_j_gids_nb = nest_routine.connect_channels_psg(M1_L5B_columns_gids,
                                                                                                M1_psg_L5B, M1_syn_L5B)
        S1_L5A_circle_gid_detector, S1_L5A_circle_j_gids_nb = nest_routine.connect_channels_psg(S1_L5A_columns_gids,
                                                                                                S1_psg_L5A, S1_syn_L5A)
        S1_L5B_circle_gid_detector, S1_L5B_circle_j_gids_nb = nest_routine.connect_channels_psg(S1_L5B_columns_gids,
                                                                                                S1_psg_L5B, S1_syn_L5B)

        while trial_counter < trials_nb:
            # while not os.path.exists(file_path):
            #    time.sleep(30)              #wait some time until NEO deposits a file.
            if True:  # os.path.isfile(file_path):
                # direction = wbnaox.getDesiredDirection()
                direction = 'CU'

                _ = nest_routine.apply_direction_stimulus_generic(direction=direction,
                                                                  time_start=trial_counter * 500. + 100.,
                                                                  time_stop=trial_counter * 500. + 400.,
                                                                  psg=M1_psg_L5A, stimulus=stimulus_L5A)
                _ = nest_routine.apply_direction_stimulus_generic(direction=direction,
                                                                  time_start=trial_counter * 500. + 100.,
                                                                  time_stop=trial_counter * 500. + 400.,
                                                                  psg=M1_psg_L5B, stimulus=stimulus_L5B)
                _ = nest_routine.apply_direction_stimulus_generic(direction=direction,
                                                                  time_start=trial_counter * 500. + 100.,
                                                                  time_stop=trial_counter * 500. + 400.,
                                                                  psg=S1_psg_L5A, stimulus=stimulus_L5A)
                _ = nest_routine.apply_direction_stimulus_generic(direction=direction,
                                                                  time_start=trial_counter * 500. + 100.,
                                                                  time_stop=trial_counter * 500. + 400.,
                                                                  psg=S1_psg_L5B, stimulus=stimulus_L5B)

                nest.Simulate(int(sim_params['sim_model'][sim_model_on]['delta_t']))
                rate = []
                for circle_name in M1_L5B_circle_gid_detector.keys():
                    rate.append(nest_routine.average_fr_pre(M1_L5B_circle_gid_detector[circle_name],
                                                            M1_L5B_circle_j_gids_nb[circle_name],
                                                            start_time=trial_counter * 500. + 100.,
                                                            end_time=(trial_counter + 1) * 500. - 100.))
                    trial_counter += 1  # will access up to maximum_iterations times to a file
                print(rate)
                trial_counter += 1
                # wbnaox.putPopulationVector(rate)
    elif sim_model_on == 'single_arm_reaching':

        stimulus_L5A = nest_routine.create_stimulus(scaling_stim=30 * 17.7, bias=2.)
        stimulus_L5B = nest_routine.create_stimulus(scaling_stim=30 * 31.3, bias=15.)
        M1_psg_L5A, M1_syn_L5A = nest_routine.create_psg_channels(syn_weight=11.5, syn_delay=1.5,
                                                                  channels_nb=sim_params['channels_nb'])
        M1_psg_L5B, M1_syn_L5B = nest_routine.create_psg_channels(syn_weight=13., syn_delay=1.5,
                                                                  channels_nb=sim_params['channels_nb'])
        S1_psg_L5A, S1_syn_L5A = nest_routine.create_psg_channels(syn_weight=2., syn_delay=1.5,
                                                                  channels_nb=sim_params['channels_nb'])
        S1_psg_L5B, S1_syn_L5B = nest_routine.create_psg_channels(syn_weight=2.2, syn_delay=1.5,
                                                                  channels_nb=sim_params['channels_nb'])

        circle_center_params = nest_routine.get_channel_centers(sim_params, hex_center=[0, 0],
                                                                ci=sim_params['channels_nb'],
                                                                hex_radius=sim_params['hex_radius'])
        M1_L5A_columns_gids = nest_routine.get_columns_data('M1_L5A_CS', circle_center_params,
                                                            sim_params['channels_radius'])
        M1_L5B_columns_gids = nest_routine.get_columns_data('M1_L5B_PT', circle_center_params,
                                                            sim_params['channels_radius'])
        S1_L5A_columns_gids = nest_routine.get_columns_data('S1_L5A_Pyr', circle_center_params,
                                                            sim_params['channels_radius'])
        S1_L5B_columns_gids = nest_routine.get_columns_data('S1_L5B_Pyr', circle_center_params,
                                                            sim_params['channels_radius'])

        M1_L5A_circle_gid_detector, M1_L5A_circle_j_gids_nb = nest_routine.connect_channels_psg(M1_L5A_columns_gids,
                                                                                                M1_psg_L5A, M1_syn_L5A)
        M1_L5B_circle_gid_detector, M1_L5B_circle_j_gids_nb = nest_routine.connect_channels_psg(M1_L5B_columns_gids,
                                                                                                M1_psg_L5B, M1_syn_L5B)
        S1_L5A_circle_gid_detector, S1_L5A_circle_j_gids_nb = nest_routine.connect_channels_psg(S1_L5A_columns_gids,
                                                                                                S1_psg_L5A, S1_syn_L5A)
        S1_L5B_circle_gid_detector, S1_L5B_circle_j_gids_nb = nest_routine.connect_channels_psg(S1_L5B_columns_gids,
                                                                                                S1_psg_L5B, S1_syn_L5B)
        direction = 'CU'
        _ = nest_routine.apply_direction_stimulus_generic(direction=direction, time_start=2000., time_stop=2300.,
                                                          psg=M1_psg_L5A, stimulus=stimulus_L5A)
        _ = nest_routine.apply_direction_stimulus_generic(direction=direction, time_start=2000., time_stop=2300.,
                                                          psg=M1_psg_L5B, stimulus=stimulus_L5B)
        _ = nest_routine.apply_direction_stimulus_generic(direction=direction, time_start=2000., time_stop=2300.,
                                                          psg=S1_psg_L5A, stimulus=stimulus_L5A)
        _ = nest_routine.apply_direction_stimulus_generic(direction=direction, time_start=2000., time_stop=2300.,
                                                          psg=S1_psg_L5B, stimulus=stimulus_L5B)

        nest.Simulate(int(sim_params['simDuration'] + sim_params['initial_ignore']))


    elif sim_model_on == 'reinf_learning':

        ##################################################################################################################
        ################### simulated Input on S1 L5B and L5A Pyr from hand position by Poisson generator ################
        ##################################################################################################################
        ## get target GIDS
        S1_L5A_columns_gids = nest_routine.get_columns_data('S1_L5A_Pyr', bg_params['circle_center'],
                                                            sim_params['channels_radius'])
        S1_L5B_columns_gids = nest_routine.get_columns_data('S1_L5B_Pyr', bg_params['circle_center'],
                                                            sim_params['channels_radius'])
        print('S1 L5B columns gids: ', S1_L5B_columns_gids)
        ## create stimulus based on distance. They are diccionaries to be used in function set_stimulus ####
        stimulus_L5A = {'scaling_stim': 30 * 17.7, 'bias': 2., 'mu': 0., 'sig': 0.25}
        stimulus_L5B = {'scaling_stim': 30 * 31.3, 'bias': 15., 'mu': 0., 'sig': 0.25}
        ## create PG and synapses
        S1_L5A_psg, S1_L5A_syn = nest_routine.create_psg_channels(syn_weight=4., syn_delay=1.5,
                                                                  channels_nb=sim_params['channels_nb'])  # original: 2.
        S1_L5B_psg, S1_L5B_syn = nest_routine.create_psg_channels(syn_weight=4.2, syn_delay=1.5, channels_nb=sim_params[
            'channels_nb'])  # original: 2.2
        ## connect PG to GIDS
        _ = nest_routine.connect_psg_to_channels(S1_L5A_columns_gids, S1_L5A_psg, S1_L5A_syn)
        _ = nest_routine.connect_psg_to_channels(S1_L5B_columns_gids, S1_L5B_psg, S1_L5B_syn)

        ##################################################################################################################
        ################### Simulated Input on MSN from M2 by Poisson generator ##########################################
        ##################################################################################################################
        ## get target GIDS
        MSN_CSN_columns_gids = nest_routine.get_columns_data('CSN', bg_params['circle_center'],
                                                             sim_params['channels_radius'])
        print('MSN columns gids: ', MSN_CSN_columns_gids)
        ## create stimulus (array with PG rates) - Fixed (no-distance dependent)
        stimulus_M2_to_MSN = nest_routine.create_stimulus(scaling_stim=500., bias=0.)
        print('stimulus on MSN from M2: ', stimulus_M2_to_MSN)
        ## create PG and synapses
        M2_to_MSN_psg, M2_to_MSN_syn = nest_routine.create_psg_channels(syn_weight=0., syn_delay=1.5,
                                                                        channels_nb=sim_params[
                                                                            'channels_nb'])  # original: 11.5
        ## connect PG to GIDS
        _ = nest_routine.connect_psg_to_channels(MSN_CSN_columns_gids, M2_to_MSN_psg, M2_to_MSN_syn)

        ###############   map the stimulus as needed and runs M episodes #####################################
        dt_task = 500.  # (ms)　
        dt_task_no_stim = 100.
        start_point = sim_params['initial_ignore'] + dt_task
        trials_nb = sim_params['sim_model'][sim_model_on]['trials_nb']
        nest.Simulate(start_point)  # 500ms (initial ignore) the network is silent due not input in CTX by PG.

        # Choice reaching
        print('circle centers: ', bg_params['circle_center'])  # print all the channels
        xtarget = np.array(bg_params['circle_center'][1:4])  # select the top 3 targets
        print('targets involve: ', xtarget)
        target = 1  # target index
        print('prefered target: ', xtarget[1])  # the preferred target, Xd

        current_pos = bg_params['circle_center']  # current position x testing only

        for i in np.arange(trials_nb):

            print('current_pos: ', current_pos[i])

            S1_start = start_point + i * dt_task + dt_task_no_stim  # start_point+(new_delta_t*trial_counter)
            S1_end = start_point + (
                        i + 1) * dt_task - dt_task_no_stim  # start_point+S1_span+(new_delta_t*trial_counter)
            M1_start = start_point + i * dt_task + dt_task_no_stim  # start_point+S1_span-S1M1_overlap+(new_delta_t*trial_counter)
            M1_end = start_point + (
                        i + 1) * dt_task - dt_task_no_stim  # start_point+S1_span+M1_span-S1M1_overlap+(new_delta_t*trial_counter)
            dopa_start = start_point + i * dt_task  # new_delta_t-dopa_span/2.+(new_delta_t*trial_counter)
            dopa_end = start_point + (i + 1) * dt_task  # dopa_start + 10.

            ###### appply the stimulus based on current position to S1   ##########
            print('S1 start: ', S1_start, '  S1 end: ', S1_end, '\n')
            _ = nest_routine.set_stimulus(current_position=current_pos[i], time_start=S1_start, time_stop=S1_end,
                                          psg=S1_L5A_psg, stimulus=stimulus_L5A,
                                          centers=bg_params['circle_center'])  # S1
            _ = nest_routine.set_stimulus(current_position=current_pos[i], time_start=S1_start, time_stop=S1_end,
                                          psg=S1_L5B_psg, stimulus=stimulus_L5B,
                                          centers=bg_params['circle_center'])  # S1

            ###### apply stimulus from M2 to the desired channel directly to MSN (not based on current position)####
            _ = nest_routine.apply_direction_stimulus_generic(direction='CU_MSN_M2', time_start=S1_start,
                                                              time_stop=S1_end, psg=M2_to_MSN_psg,
                                                              stimulus=stimulus_M2_to_MSN)  # M1

            nest.Simulate(dt_task)  # simulation

            #### getting the mean firing rates #####
            sp = nest.GetStatus(detectors['MSN'], 'events')[0]
            idx_dt = np.where(np.logical_and(sp['times'] >= S1_start, sp['times'] <= S1_end))
            # get the 3 top GIDs:
            for col in [1, 2, 3]:  # indexes of the top 3 columns
                mask = np.in1d(sp['senders'][idx_dt], np.array([gid[0] for gid in MSN_CSN_columns_gids[col]]))
                mean_act = len(sp['times'][idx_dt][mask]) / (
                            (dt_task - 2. * dt_task_no_stim) * float(len(MSN_CSN_columns_gids[col]))) * 1000.
                print('mean firing rate for col ', col, ':  ', mean_act)

    ####################################################
    # arm movement selection start
    ####################################################
    elif sim_model_on == 'arm_movement':
        trial_nb = 1
        sub_trial_nb = 1
        simulation_duration_per_trial = 100
        sub_simulation_duration = 100.
        # Test pmm2
        pm = pmm2()

        ut = [0., 0.]
        xt = [0., 0.]
        nest.Simulate(sim_params['initial_ignore'])
        for i in range(trial_nb):
            for j in range(sub_trial_nb):
                for k in range(int(simulation_duration_per_trial / sub_simulation_duration)):
                    # get the activities for previous step
                    # _=position_encode()
                    # _=movement_decode()
                    #########simulation start############
                    nest.Simulate(sub_simulation_duration)
                    #########simulation end############
                    start_time = (i * sub_trial_nb * int(
                        simulation_duration_per_trial / sub_simulation_duration) + j * int(
                        simulation_duration_per_trial / sub_simulation_duration) + k) * sub_simulation_duration + \
                                 sim_params['initial_ignore']
                    end_time = (i * sub_trial_nb * int(
                        simulation_duration_per_trial / sub_simulation_duration) + j * int(
                        simulation_duration_per_trial / sub_simulation_duration) + k + 1) * sub_simulation_duration + \
                               sim_params['initial_ignore']

                    xt = pm.x  # record position
                    pm.move(ut, 100. / 1000.)  # move unit is second
                    print('(i, j, k):', (i, j, k), 'xt:', xt, 'ut:', ut)
                    print('start_time', 'end_time')
                    print(start_time, end_time)
                    ctx_S1_macro_columns_activity = {}
                    ctx_S1_micro_columns_activity = {}
                    for layer_name in ctx_layers.keys():
                        ctx_S1_macro_columns_activity[layer_name] = nest_routine.get_firing_rate_macro_column(
                            layer_name, ctx_S1_macro_columns_gids[layer_name], start_time, end_time)
                        print(ctx_S1_macro_columns_activity[layer_name])
                        for i in range(sim_params['macro_columns_nb']):
                            ctx_S1_micro_columns_activity[
                                layer_name + '_macro_column_' + str(i)] = nest_routine.get_firing_rate_micro_column(
                                layer_name, ctx_S1_micro_columns_gids[layer_name + '_macro_column_' + str(i)],
                                start_time, end_time, i)
                            print(ctx_S1_micro_columns_activity[layer_name + '_macro_column_' + str(i)])

                    ctx_M1_macro_columns_activity = {}
                    ctx_M1_micro_columns_activity = {}
                    for layer_name in ctx_M1_layers.keys():
                        ctx_M1_macro_columns_activity[layer_name] = nest_routine.get_firing_rate_macro_column(
                            layer_name,
                            ctx_M1_macro_columns_gids[
                                layer_name],
                            start_time,
                            end_time)
                        print(ctx_M1_macro_columns_activity[layer_name])
                        for i in range(sim_params['macro_columns_nb']):
                            ctx_M1_micro_columns_activity[
                                layer_name + '_macro_column_' + str(i)] = nest_routine.get_firing_rate_micro_column(
                                layer_name, ctx_M1_micro_columns_gids[layer_name + '_macro_column_' + str(i)],
                                start_time,
                                end_time, i)
                            print(ctx_M1_micro_columns_activity[layer_name + '_macro_column_' + str(i)])

    ####################################################
    # arm movement selection end
    ####################################################

    ####################################################
    # TESTING MIGRATION TO NEST 3
    ###################################################

    elif sim_model_on == 'BG_only':
        simulation_time = sim_params['simDuration'] + sim_params['initial_ignore']
        print('Simulation Started:')
        start_time = time.time()
        nest.Simulate(simulation_time)
        with open('/opt/data/log/' + 'performance.txt', 'a') as file:
            file.write('Simulation_Elapse_Time ' + str(time.time() - start_time) + '\n')
        print('Simulation Finish')

        if sim_regions['BG']:
            for layer_name in bg_layers.keys():
                rate = nest_routine.average_fr(detectors[layer_name], sim_params['simDuration'], len(
                    bg_layers[layer_name]))  # nest_routine.count_layer(bg_layers[layer_name]))
                print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")

        # if sim_regions['BG']:
        #    for layer_name in bg_layers.keys():
        #        rate = nest_routine.get_firing_rate_from_gdf_files(layer_name, detectors[layer_name], sim_params['simDuration'],
        #        nest_routine.count_layer(bg_layers[layer_name]))
        #        print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")

    # --------------------------------------------------------------------------------------------
    # test S1 model on NEST 3
    #
    # --------------------------------------------------------------------------------------------

    elif sim_model_on == 'S1_only':
        print('test line from Sun ....  ')
        simulation_time = sim_params['simDuration'] + sim_params['initial_ignore']
        print('Simulation Started:')
        start_time = time.time()
        nest.Simulate(simulation_time)
        with open('/opt/data/log/' + 'performance.txt', 'a') as file:
            file.write('Simulation_Elapse_Time ' + str(time.time() - start_time) + '\n')
        print('Simulation Finish')

        if sim_regions['S1']:
            for layer_name in ctx_layers.keys():
                rate = nest_routine.average_fr(detectors[layer_name], sim_params['simDuration'],
                                               nest_routine.count_layer(ctx_layers[layer_name]))
                print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")
    elif sim_model_on == 'M1_only':
        simulation_time = sim_params['simDuration'] + sim_params['initial_ignore']
        print('Simulation Started:')
        start_time = time.time()
        nest.Simulate(simulation_time)
        with open('/opt/data/log/' + 'performance.txt', 'a') as file:
            file.write('Simulation_Elapse_Time ' + str(time.time() - start_time) + '\n')
        print('Simulation Finish')

        if sim_regions['M1']:
            for layer_name in ctx_M1_layers.keys():
                rate = nest_routine.average_fr(detectors[layer_name], sim_params['simDuration'],
                                               nest_routine.count_layer(ctx_M1_layers[layer_name]))
                print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")



    elif sim_model_on == 'CB_only':
        print('test line from Yamaura ....  ')
        simulation_time = sim_params['simDuration'] + sim_params['initial_ignore']
        print('Simulation Started:')
        start_time = time.time()
        nest.Simulate(simulation_time)
        with open('/opt/data/log/' + 'performance.txt', 'a') as file:
            file.write('Simulation_Elapse_Time ' + str(time.time() - start_time) + '\n')
        print('Simulation Finish')

        if sim_regions['CB_S1']:
            for layer_name in cb_layers_S1.keys():
                rate = nest_routine.average_fr(detectors[layer_name], sim_params['simDuration'],
                                               nest_routine.count_layer(cb_layers_S1[layer_name]))
                print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")

        if sim_regions['CB_M1']:
            for layer_name in cb_layers_M1.keys():
                rate = nest_routine.average_fr(detectors[layer_name], sim_params['simDuration'],
                                               nest_routine.count_layer(cb_layers_M1[layer_name]))
                print('Layer ' + layer_name + " fires at " + str(rate) + " Hz")

    elif sim_model_on == 'TH_only':
        print('test line from Sun ....  ')
        simulation_time = sim_params['simDuration'] + sim_params['initial_ignore']
        print('Simulation Started:')
        start_time = time.time()
        nest.Simulate(simulation_time)
        with open('/opt/data/log/' + 'performance.txt', 'a') as file:
            file.write('Simulation_Elapse_Time ' + str(time.time() - start_time) + '\n')
        print('Simulation Finish')
        if sim_regions['TH_S1']:
            for layer_name in th_layers['TH_S1_EZ'].keys():
                rate = nest_routine.average_fr(detectors['TH_S1_EZ' + '_' + layer_name], sim_params['simDuration'],
                                               nest_routine.count_layer(th_layers['TH_S1_EZ'][layer_name]))
                print('Layer ' + 'TH_S1_EZ_' + layer_name + " fires at " + str(rate) + " Hz")
            for layer_name in th_layers['TH_S1_IZ'].keys():
                rate = nest_routine.average_fr(detectors['TH_S1_IZ' + '_' + layer_name], sim_params['simDuration'],
                                               nest_routine.count_layer(th_layers['TH_S1_IZ'][layer_name]))
                print('Layer ' + 'TH_S1_IZ_' + layer_name + " fires at " + str(rate) + " Hz")
        if sim_regions['TH_M1']:
            for layer_name in th_layers['TH_M1_EZ'].keys():
                rate = nest_routine.average_fr(detectors['TH_M1_EZ' + '_' + layer_name], sim_params['simDuration'],
                                               nest_routine.count_layer(th_layers['TH_M1_EZ'][layer_name]))
                print('Layer ' + 'TH_M1_EZ_' + layer_name + " fires at " + str(rate) + " Hz")

            for layer_name in th_layers['TH_M1_IZ'].keys():
                rate = nest_routine.average_fr(detectors['TH_M1_IZ' + '_' + layer_name], sim_params['simDuration'],
                                               nest_routine.count_layer(th_layers['TH_M1_IZ'][layer_name]))
                print('Layer ' + 'TH_M1_IZ_' + layer_name + " fires at " + str(rate) + " Hz")


    else:
        print('wrong model set')


if __name__ == '__main__':
    main()



