# coding: utf-8

import numpy as np
import nest


class Network(object):

    @staticmethod
    def go_to_gr(layer_go, layer_gr, subCB, kernel=0.025, weights=-10.0, g=[0.18, 0.025, 0.028, 0.028], alpha_const=[1.0, 1.0, 0.43, 0.57], multiplier=2.0):
        """GOからGRへの接続を行う

        Example:

            ::

            save_path = './picture/'
            load_path = './result/'
            figure(save_path, load_path)

        Args:
            layer_go (tuple): GOレイヤー
            layer_gr (tuple): GRレイヤー
            kernel (float): 接続確率
            weights (float): 接続の重み。負だと抑制、正だと興奮性となる。
            g (list): 各ゲートのg
            alpha_const (list): 各ゲートのアルファ関数にかけられる係数
            lower_left (list): 長方形の範囲で、ニューロンが接続される。lower_leftは長方形の左下の座標となる。
            upper_right (list): 長方形の範囲で、ニューロンが接続される。upper_rightは長方形の右上の座標となる。
            multiplier (float): 重みにかけられる係数で、調整用
        """
        # define connections
        #    golgi to granule
        #    1024. / 32. = 32. is the length between golgi cells
        #    inhibitory inputs from 9x9 nearby model golgi cells with probability 0.025
        #    synaptic weights: 10.0

        conn_dict = {'rule': 'pairwise_bernoulli',
             'p': 1.,
             'mask': {'box':
                          {'lower_left': [-0.15, -0.15, -0.5],
                           'upper_right': [0.15, 0.15, 0.5]}},
             'allow_autapses': False,
             'allow_multapses': False,
             'allow_oversized_mask': True
             }
        syn_spec = {'weight': np.max(weights * np.multiply(g, alpha_const)) * multiplier}
        
        nest.Connect(layer_go, layer_gr, conn_dict, syn_spec)
