# coding: utf-8

import numpy as np
import nest

class Network(object):

    @staticmethod
    def vn_to_io(layer_vn, layer_io, kernel=1.0, weights=-5.0, g=[1.0, 0.18], alpha_const=[1.0, 1.0], rows=1, columns=1, multiplier=0.0):
        """VNからIOへの接続を行う


        Example:

            ::

            Network.vn_to_io(layer_vn, layer_io)

        Args:
            layer_vn (tuple): vnレイヤー
            layer_io (tuple): vnレイヤー
            kernel (float): 接続確率
            weights (float): 接続の重み。負だと抑制、正だと興奮性となる。
            g (list): 各ゲートのg
            alpha_const (list): 各ゲートのアルファ関数にかけられる係数
            lower_left (list): 長方形の範囲で、ニューロンが接続される。lower_leftは長方形の左下の相対座標となる。
            upper_right (list): 長方形の範囲で、ニューロンが接続される。upper_rightは長方形の右上の相対座標となる。
            multiplier (float): 重みにかけられる係数で、調整用
        """
        # vn to io
        #    inhibitory inputs from 1x1 nearby model VN cells with probability 1.0
        #    synaptic weights: 5.0

        conn_dict = {'rule': 'pairwise_bernoulli',
             'p': 1.,
             'mask': {'box':
                          {'lower_left': 1,
                           'upper_right': 1}},
             'allow_autapses': False,
             'allow_multapses': False,
             'allow_oversized_mask': True
             }
        syn_spec = {'weight': np.max(weights * np.multiply(g, alpha_const)) * multiplier}
        
        nest.Connect(layer_vn, layer_io, conn_dict, syn_spec)

#    @staticmethod
#    def vn_to_s(layer_vn, layer_s_vn, kernel=1.0, weights=1.0, rows=1, columns=1):
#        """VNからSpike Detectorへの接続を行う
#
#        Example:
#
#            ::
#
#            Network.vn_to_s(layer_vn, layer_s_vn)
#
#        Args:
#            layer_vn (tuple): VNレイヤー
#            layer_s_vn (tuple): spike detectorのレイヤー
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
#        configuration['sources'] = {'model': 'VN'}
#        configuration['targets'] = {'model': 'SD'}
#        configuration['mask']['grid']['rows'] = rows
#        configuration['mask']['grid']['columns'] = columns
#        print (layer_s_vn)
#        tp.ConnectLayers(layer_vn, layer_s_vn, configuration)
