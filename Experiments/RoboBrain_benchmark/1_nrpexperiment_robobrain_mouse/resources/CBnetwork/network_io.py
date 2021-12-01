# coding: utf-8

import numpy as np
import nest

class Network(object):

    @staticmethod
    def io_to_pkj(layer_io, layer_pkj, kernel=1.0, weights=1.0, g=[0.7, 1.0], alpha_const=[1.0, 1.0], rows=1, columns=16, anchor_row=0, anchor_column=8):
        """IOからPKJへの接続を行う

        Example:

            ::

            Network.io_to_pkj(layer_io, layer_pkj)

        Args:
            layer_io (tuple): IOレイヤー
            layer_pkj (tuple): PKJレイヤー
            kernel (float): 接続確率
            weights (float): 接続の重み。負だと抑制、正だと興奮性となる。
            g (list): 各ゲートのg
            alpha_const (list): 各ゲートのアルファ関数にかけられる係数
            rows (int): ニューロンの接続範囲の行
            columns (int): ニューロンの接続範囲の列
            anchor_row (int): rowsとcolumnsの中心座標の行をシフトする
            anchor_columns (int): rowsとcolumnsの中心座標の列をシフトする
        """
        # io to pkj
        #    excitatory inputs from 1x1 nearby model IO cells with probability 1.0
        #    synaptic weights: 1.0
        configuration = {'connection_type': 'divergent', 'mask': {'grid': {}, 'anchor': {}}}
        configuration['kernel'] = kernel
        configuration['sources'] = {'model': 'IO'}
        configuration['targets'] = {'model': 'PKJ'}
        configuration['mask']['grid']['rows'] = rows
        configuration['mask']['grid']['columns'] = columns
        configuration['mask']['anchor']['row'] = anchor_row
        configuration['mask']['anchor']['column'] = anchor_column
        weights = weights * np.multiply(g, alpha_const)
        configuration['weights'] = np.max(weights)
        tp.ConnectLayers(layer_io, layer_pkj, configuration)

    @staticmethod
    def io_to_s(layer_io, layer_s_io, kernel=1.0, weights=1.0, rows=1, columns=1):
        """IOからSpike Detectorへの接続を行う

        Example:

            ::

            Network.io_to_pkj(layer_io, layer_s_io)

        Args:
            layer_io (tuple): IOレイヤー
            layer_s_io (tuple): spike detectorのレイヤー
            kernel (float): 接続確率
            weights (float): 接続の重み。負だと抑制、正だと興奮性となる。
            rows (int): ニューロンの接続範囲の行
            columns (int): ニューロンの接続範囲の列
        """
        # io to spike_detector
        #    connections are confirmed
        configuration = {'connection_type': 'convergent', 'mask': {'grid': {}}}
        configuration['kernel'] = kernel
        configuration['weights'] = weights
        configuration['sources'] = {'model': 'IO'}
        configuration['targets'] = {'model': 'SD'}
        configuration['mask']['grid']['rows'] = rows
        configuration['mask']['grid']['columns'] = columns
        tp.ConnectLayers(layer_io, layer_s_io, configuration)
