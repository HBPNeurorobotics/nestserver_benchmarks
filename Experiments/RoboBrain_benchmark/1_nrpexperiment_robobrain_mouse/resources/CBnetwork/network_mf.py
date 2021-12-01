# coding: utf-8

import numpy as np
import nest

class Network(object):

    @staticmethod
    def mf_to_gr(layer_mf_gr, layer_gr, kernel=1.0, weights=4.0, g=[0.18, 0.025, 0.028, 0.028], alpha_const=[1.0, 1.0, 0.43, 0.57], rows=1, columns=1, multiplier=0.225):
        """MFからGRへの接続を行う

        Example:

            ::

            Network.mf_to_gr(layer_mf_gr, layer_gr)

        Args:
            layer_mf_gr (tuple): mf_grレイヤー
            layer_gr (tuple): grレイヤー
            kernel (float): 接続確率
            weights (float): 接続の重み。負だと抑制、正だと興奮性となる。
            g (list): 各ゲートのg
            alpha_const (list): 各ゲートのアルファ関数にかけられる係数
            lower_left (list): 長方形の範囲で、ニューロンが接続される。lower_leftは長方形の左下の相対座標となる。
            upper_right (list): 長方形の範囲で、ニューロンが接続される。upper_rightは長方形の右上の相対座標となる。
            multiplier (float): 重みにかけられる係数で、調整用
        """
        # mf to granule
        #    excitatory inputs from 1x1 nearby mf inputs with probability 1.0
        #    synaptic weights: 4.0
        configuration = {'connection_type': 'divergent', 'mask': {'grid': {}}}
        configuration['kernel'] = kernel
        configuration['sources'] = {'model': 'MF'}
        configuration['targets'] = {'model': 'GR'}
        configuration['mask']['grid']['rows'] = rows
        configuration['mask']['grid']['columns'] = columns
        weights = multiplier * weights * np.multiply(g, alpha_const)
        configuration['weights'] = np.max(weights)
        tp.ConnectLayers(layer_mf_gr, layer_gr, configuration)
        configuration['sources'] = {'model': 'MF_Constant'}
        tp.ConnectLayers(layer_mf_gr, layer_gr, configuration)

    @staticmethod
    def mf_to_vn(layer_mf_vn, layer_vn, kernel=1.0, weights=0.002, g=[50.0, 25.8, 30.0], alpha_const=[1.0, 1.0, 1.0], rows=1, columns=1, multiplier=0.3):
        """MFからGRへの接続を行う

        Example:

            ::

            Network.mf_to_vn(layer_mf_vn, layer_vn)

        Args:
            layer_mf_vn (tuple): mf_vnレイヤー
            layer_vn (tuple): vnレイヤー
            kernel (float): 接続確率
            weights (float): 接続の重み。負だと抑制、正だと興奮性となる。
            g (list): 各ゲートのg
            alpha_const (list): 各ゲートのアルファ関数にかけられる係数
            lower_left (list): 長方形の範囲で、ニューロンが接続される。lower_leftは長方形の左下の相対座標となる。
            upper_right (list): 長方形の範囲で、ニューロンが接続される。upper_rightは長方形の右上の相対座標となる。
            multiplier (float): 重みにかけられる係数で、調整用
        """
        # mf to vn
        #    excitatory inputs from 1x1 nearby mf_vn inputs with probability 1.0
        #    synaptic weights: 0.002
        configuration = {'connection_type': 'divergent', 'mask': {'grid': {}}}
        configuration['kernel'] = kernel
        configuration['sources'] = {'model': 'MF'}
        configuration['targets'] = {'model': 'VN'}
        configuration['mask']['grid']['rows'] = rows
        configuration['mask']['grid']['columns'] = columns
        weights = weights * np.multiply(g, alpha_const) * multiplier
        configuration['weights'] = np.max(weights)
        tp.ConnectLayers(layer_mf_vn, layer_vn, configuration)

    @staticmethod
    def mf_to_io(layer_io_input, layer_io, kernel=1.0, weights=1.0, g=[1.0, 0.18], alpha_const=[1.0, 1.0], rows=1, columns=1):
        """CFからIOへの接続を行う

        Example:

            ::

            Network.mf_to_io(layer_io_input, layer_io)

        Args:
            layer_io_input(tuple): CFレイヤー
            layer_io (tuple): IOレイヤー
            kernel (float): 接続確率
            weights (float): 接続の重み。負だと抑制、正だと興奮性となる。
            rows (int): ニューロンの接続範囲の行
            columns (int): ニューロンの接続範囲の列
        """
        # input to io
        #    excitatory inputs from 1x1 nearby inputs with probability 1.0
        #    synaptic weights: 1.0
        configuration = {'connection_type': 'divergent', 'mask': {'grid': {}}}
        configuration['kernel'] = kernel
        configuration['sources'] = {'model': 'MF_IO'}
        configuration['targets'] = {'model': 'IO'}
        configuration['mask']['grid']['rows'] = rows
        configuration['mask']['grid']['columns'] = columns
        weights = weights * np.multiply(g, alpha_const)
        configuration['weights'] = np.max(weights)
        tp.ConnectLayers(layer_io_input, layer_io, configuration)
