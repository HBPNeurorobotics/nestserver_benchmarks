# coding: utf-8

import numpy as np
import nest

class Network(object):
    @staticmethod
    def pkj_to_vn(layer_pkj, layer_vn, subCB):
        weights = -0.00035
        g = [50.0, 25.8, 30.0]
        alpha_const = [1.0, 1.0, 1.0]
        multiplier = 2.0
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
        
        nest.Connect(layer_pkj, layer_vn, conn_dict, syn_spec)

    """
    @staticmethod
    def pkj_to_vn(columns_data_pkj, columns_data_vn, subCB_name):
        for i in range (len(columns_data_pkj)):
            print ('start to connenct pkj to vn circle '+str(i) )
            source=[gid[0] for gid in columns_data_pkj[i]]
            target = [gid[0] for gid in columns_data_vn[i]]
            weights = -0.00035
            g = [50.0, 25.8, 30.0]
            alpha_const = [1.0, 1.0, 1.0]
            multiplier = 2.0
            weights = np.max(weights * np.multiply(g, alpha_const))* multiplier


            syn_dict = {"model": "static_synapse",
                        "weight": weights,
                        "delay": 1.0}
            nest.Connect(source, target, "all_to_all", syn_spec=syn_dict)
    """
    # @staticmethod
    # def pkj_to_vn(layer_pkj, layer_vn, subCB, kernel=1.0, weights=-0.00035, g=[50.0, 25.8, 30.0], alpha_const=[1.0, 1.0, 1.0], multiplier=2.0):
    #     """PKJからVNへの接続を行う
    #
    #     Example:
    #
    #         ::
    #
    #         Network.pkj_to_vn(layer_pkj, layer_vn)
    #
    #     Args:
    #         layer_pkj (tuple): pkjレイヤー
    #         layer_vn (tuple): vnレイヤー
    #         kernel (float): 接続確率
    #         weights (float): 接続の重み。負だと抑制、正だと興奮性となる。
    #         g (list): 各ゲートのg
    #         alpha_const (list): 各ゲートのアルファ関数にかけられる係数
    #         lower_left (list): 長方形の範囲で、ニューロンが接続される。lower_leftは長方形の左下の相対座標となる。
    #         upper_right (list): 長方形の範囲で、ニューロンが接続される。upper_rightは長方形の右上の相対座標となる。
    #         multiplier (float): 重みにかけられる係数で、調整用
    #     """
    #     # pkj to vn
    #     #    1024. / 16. = 64.0 is the length between purkinje cells
    #     #    inhibitory inputs from 1x16 nearby model purkinje cells with probability 1.0
    #     #    synaptic weights: 0.008
    #     configuration = {'connection_type': 'divergent', 'mask': {'box': {}}}
    #     configuration['kernel'] = kernel
    #     configuration['sources'] = {'model': subCB+'_layer_pkj'}
    #     configuration['targets'] = {'model': subCB+'_layer_vn'}
    #     lower_left = [-0.1, -0.25, -0.5]
    #     upper_right = [0.1, 0.25, 0.5]
    #     configuration['mask']['box']['lower_left'] = lower_left
    #     configuration['mask']['box']['upper_right'] = upper_right
    #     weights = weights * np.multiply(g, alpha_const) * multiplier
    #     configuration['weights'] = np.max(weights)
    #     tp.ConnectLayers(layer_pkj, layer_vn, configuration)

#    @staticmethod
    #def pkj_to_s(layer_pkj, layer_s_pkj, kernel=1.0, weights=1.0, rows=1, columns=1):
    #    """PKJからSpike Detectorへの接続を行う
#
#        Example:
#
#            ::
#
#            Network.pkj_to_s(layer_pkj, layer_s_pkj)
#
#        Args:
#            layer_pkj (tuple): PKJレイヤー
#            layer_s_pkj (tuple): spike detectorのレイヤー
#            kernel (float): 接続確率
#            weights (float): 接続の重み。負だと抑制、正だと興奮性となる。
#            rows (int): ニューロンの接続範囲の行
#            columns (int): ニューロンの接続範囲の列
#        """
#        # vn to spike_detector
#        #        connections are confirmed
#        configuration = {'connection_type': 'convergent', 'mask': {'grid': {}}}
#        configuration['kernel'] = kernel
#        configuration['weights'] = weights
#        configuration['sources'] = {'model': 'PKJ'}
#        configuration['targets'] = {'model': 'SD'}
#        configuration['mask']['grid']['rows'] = rows
#        configuration['mask']['grid']['columns'] = columns
#        tp.ConnectLayers(layer_pkj, layer_s_pkj, configuration)
