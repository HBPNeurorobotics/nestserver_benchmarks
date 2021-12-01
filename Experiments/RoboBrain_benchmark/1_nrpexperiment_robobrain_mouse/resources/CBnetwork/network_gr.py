# coding: utf-8

import numpy as np
import nest

class Network(object):

    @staticmethod
    def gr_to_go(layer_gr, layer_go, subCB, kernel=0.05, weights=0.00005, g=[45.5, 30.0, 30.0], alpha_const=[1.0, 0.33, 0.67],  multiplier=1.0):
        """GRからGOへの接続を行う

        Example:

            ::

            Network.gr_to_go(layer_gr, layer_go)

        Args:
            layer_gr (tuple): grレイヤー
            layer_go (tuple): goレイヤー
            kernel (float): 接続確率
            weights (float): 接続の重み。負だと抑制、正だと興奮性となる。
            g (list): 各ゲートのg
            alpha_const (list): 各ゲートのアルファ関数にかけられる係数
            lower_left (list): 長方形の範囲で、ニューロンが接続される。lower_leftは長方形の左下の相対座標となる。
            upper_right (list): 長方形の範囲で、ニューロンが接続される。upper_rightは長方形の右上の相対座標となる。
            multiplier (float): 重みにかけられる係数で、調整用
        """#nbcpu
        #    1024. / 32. = 32. is the length between granule clusters
        #    excitatory inputs from 7x7 nearby model granule clusters with probability 0.5
        #    synaptic weights: 0.00004

        conn_dict = {'rule': 'pairwise_bernoulli',
             'p': 1.,
             'mask': {'box':
                          {'lower_left': [-0.1, -0.1, -0.1],
                           'upper_right': [0.1, 0.1, 0.1]}},
             'allow_autapses': False,
             'allow_multapses': False,
             'allow_oversized_mask': True
             }
        syn_spec = {'weight': np.max(weights * np.multiply(g, alpha_const)) * multiplier}
        
        nest.Connect(layer_gr, layer_go, conn_dict, syn_spec)

############################
#gr to pkj new function
#2019-8-9 sun
##############################

    @staticmethod
    def gr_to_pkj(layer_gr, layer_pkj, subCB):

        weights = 0.007
        g = [0.7, 1.0]
        alpha_const = [1.0, 1.0]
        multiplier = 1.0
        weight = np.max(weights * np.multiply(g, alpha_const)) * multiplier

        sigma_x = 0.1
        sigma_y = 0.1
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
        
        nest.Connect(layer_gr, layer_pkj, conn_dict, syn_spec)

    """
    @staticmethod
    def gr_to_pkj(columns_data_gr, columns_data_pkj, subCB_name):
        for i in range (len(columns_data_gr)):
            print ('start to connenct gr to pkj circle '+str(i) )
            source=[gid[0] for gid in columns_data_gr[i]]
            target = [gid[0] for gid in columns_data_pkj[i]]
            weights = 0.007
            g = [0.7, 1.0]
            alpha_const = [1.0, 1.0]
            multiplier = 1.0
            weights = np.ones((len(source), len(target)))*np.max(weights * np.multiply(g, alpha_const))* multiplier
            syn_dict = {"model": "static_synapse",
                        "weight": weights,
                        "delay": 1.0}
            nest.Connect(source, target, "all_to_all", syn_spec=syn_dict)
            
    """

    """
    @staticmethod
    def gr_to_pkj(layer_gr, layer_pkj, subCB, kernel=1.0, weights=0.007, g=[0.7, 1.0], alpha_const=[1.0, 1.0],  mutiplier=1.0):
        GRからPKJへの接続を行う

        Example:

        ::

        Network.gr_to_pkj(layer_gr, layer_pkj)

        Args:
        layer_gr (tuple): grレイヤー
        layer_pkj (tuple): pkjレイヤー
        kernel (float): 接続確率
        weights (float): 接続の重み。負だと抑制、正だと興奮性となる。
        g (list): 各ゲートのg
        alpha_const (list): 各ゲートのアルファ関数にかけられる係数
        lower_left (list): 長方形の範囲で、ニューロンが接続される。lower_leftは長方形の左下の相対座標となる。
        upper_right (list): 長方形の範囲で、ニューロンが接続される。upper_rightは長方形の右上の相対座標となる。
        multiplier (float): 重みにかけられる係数で、調整用
        
        #granule to pkj
        #1024. / 32. = 32. is the length between granule clusters
        #excitatory inputs from 32x9 nearby model granule clusters with probability 1.0
        #synaptic weights: 0.003
        configuration = {'connection_type': 'divergent', 'mask': {'box': {}}}
        configuration['kernel'] = kernel
        configuration['sources'] = {'model': subCB+'_layer_gr'}
        configuration['targets'] = {'model': subCB+'_layer_pkj'}
        lower_left = [-0.5, -0.1, -0.5]
        upper_right = [0.5,  0.1, 0.5]
        configuration['mask']['box']['lower_left'] = lower_left
        configuration['mask']['box']['upper_right'] = upper_right
        weights = weights * np.multiply(g, alpha_const) * mutiplier
        configuration['weights'] = np.max(weights)
        tp.ConnectLayers(layer_gr, layer_pkj, configuration)
    """

    @staticmethod
    def gr_to_bs(layer_gr, layer_bs, subCB, kernel=1.0, weights=0.015):
        """GRからBSへの接続を行う

        Example:

            ::

            Network.gr_to_bs(layer_gr, layer_bs)

        Args:
            layer_gr (tuple): grレイヤー
            layer_bs(tuple): bsレイヤー
            kernel (float): 接続確率
            weights (float): 接続の重み。負だと抑制、正だと興奮性となる。
            g (list): 各ゲートのg
            alpha_const (list): 各ゲートのアルファ関数にかけられる係数
            lower_left (list): 長方形の範囲で、ニューロンが接続される。lower_leftは長方形の左下の相対座標となる。
            upper_right (list): 長方形の範囲で、ニューロンが接続される。upper_rightは長方形の右上の相対座標となる。
        """
        # granule to bs
        #    1024. / 32. = 32. is the length between granule clusters
        #    excitatory inputs from 32x9 nearby model granule clusters with probability 1.0
        #    synaptic weights: 0.003

        conn_dict = {'rule': 'pairwise_bernoulli',
             'p': 1.,
             'mask': {'box':
                          {'lower_left': [-0.5, -0.1, -0.5],
                           'upper_right': [0.5, 0.1, 0.5]}},
             'allow_autapses': False,
             'allow_multapses': False,
             'allow_oversized_mask': True
             }
        syn_spec = {'weight': weights}
        
        nest.Connect(layer_gr, layer_bs, conn_dict, syn_spec)
