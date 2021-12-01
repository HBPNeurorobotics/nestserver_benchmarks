# coding: utf-8
import numpy as np
import nest

class Network(object):

    @staticmethod
    def bs_to_pkj(layer_bs, layer_pkj, subCB, kernel=1.0, weights=-1.0, g=[0.7, 1.0], alpha_const=[1.0, 1.0], multiplier=1.5):
        """BSからPKJへの接続を行う

        Example:

            ::

            Network.bs_to_pkj(layer_bs, layer_pkj)

        Args:
            layer_bs (tuple): bsレイヤー
            layer_pkj (tuple): pkjレイヤー
            kernel (float): 接続確率
            weights (float): 接続の重み。負だと抑制、正だと興奮性となる。
            g (list): 各ゲートのg
            alpha_const (list): 各ゲートのアルファ関数にかけられる係数
            lower_left (list): 長方形の範囲で、ニューロンが接続される。lower_leftは長方形の左下の相対座標となる。
            upper_right (list): 長方形の範囲で、ニューロンが接続される。upper_rightは長方形の右上の相対座標となる。
            multiplier (float): 重みにかけられる係数で、調整用
        """
        # bs to pkj
        #    1024. / 16. = 64.0 is the length between basket cells
        #    inhibitory inputs from 1x3 nearby model basket cells with probability 1.0
        #    synaptic weights: 5.3
        #    connections are confirmed

        conn_dict = {'rule': 'pairwise_bernoulli',
             'p': 1.,
             'mask': {'box':
                          {'lower_left': [-0.1, -0.25, -0.5],
                           'upper_right': [0.1, 0.25, 0.5]}},
             'allow_autapses': False,
             'allow_multapses': False,
             'allow_oversized_mask': True
             }
        syn_spec = {'weight': np.max(weights * np.multiply(g, alpha_const)) * multiplier}
        
        nest.Connect(layer_bs, layer_pkj, conn_dict, syn_spec)
