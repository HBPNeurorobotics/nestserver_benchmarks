# coding: utf-8

import numpy as np
import nest

class Network(object):

    @staticmethod
    def pons_to_gr(layer_pons, layer_gr, subCB):
        weights = 0.1
        g = [0.18, 0.025, 0.028, 0.028]
        alpha_const = [1.0, 1.0, 0.43, 0.57]
        multiplier = 0.225
        weight = np.max(weights * np.multiply(g, alpha_const)) * multiplier

        sigma_x = 0.05
        sigma_y = 0.05
        p_center = 1.
        delay = 1.0  # 1.0
        
        conn_dict = {'rule': 'pairwise_bernoulli',
             'p': p_center * nest.spatial_distributions.gaussian2D(
                 nest.spatial.distance.x, nest.spatial.distance.y, std_x=sigma_x, std_y=sigma_y),
             'mask': {'box':
                          {'lower_left': [-2., -2., -2.],
                           'upper_right': [2., 2., 2.]}},
             'allow_autapses': False,
             'allow_multapses': False,
             'allow_oversized_mask': True
             }
        syn_spec = {'weight': weight, 'delay': delay}
        
        nest.Connect(layer_pons, layer_gr, conn_dict, syn_spec)

    """
    @staticmethod
    def pons_to_gr(layer_pons, layer_gr, subCB, kernel=0.5, weights=2.4, g=[0.18, 0.025, 0.028, 0.028], alpha_const=[1.0, 1.0, 0.43, 0.57], multiplier=0.225):

        configuration = {'connection_type': 'divergent', 'mask': {'box': {}}}
        configuration['kernel'] = kernel
        configuration['sources'] = {'model': subCB+'_layer_pons'}
        configuration['targets'] = {'model': subCB+'_layer_gr'}
        lower_left = [-0.05, -0.05, -0.5]
        upper_right =[0.05, 0.05, 0.5]
        configuration['mask']['box']['lower_left'] = lower_left
        configuration['mask']['box']['upper_right'] = upper_right
        weights = weights * np.multiply(g, alpha_const) * multiplier
        configuration['weights'] = np.max(weights)
        tp.ConnectLayers(layer_pons, layer_gr, configuration)
    """
    """
    @staticmethod
    def pons_to_gr(columns_data_pons, columns_data_gr, subCB_name):
        for i in range (len(columns_data_gr)):
            print ('start to connenct pons to gr circle '+str(i) )
            source=[gid[0] for gid in columns_data_pons[i]]
            target = [gid[0] for gid in columns_data_gr[i]]
            weights = 2.4
            g = [0.18, 0.025, 0.028, 0.028]
            alpha_const = [1.0, 1.0, 0.43, 0.57]
            multiplier=0.225
            weights = np.ones((len(source), len(target)))*np.max(weights * np.multiply(g, alpha_const))* multiplier
            syn_dict = {"model": "static_synapse",
                        "weight": weights,
                        "delay": 1.0}
            nest.Connect(source, target, "all_to_all", syn_spec=syn_dict)
    """
