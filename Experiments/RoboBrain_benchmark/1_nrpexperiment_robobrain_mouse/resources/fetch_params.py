#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
## fetch_params.py
##
## This file contains routines that set the parameter files and return an object containing everything required by the instantiate_XYZ functions of ini_all.py

# ideally, functions below should read from parameter files, but it may be easier to hardcode values here as a first try

def read_sim():
  try:
    from runpy import run_path
    file_params = run_path('simParams.py', init_globals=globals())
    sim_params = file_params['simParams']
    return sim_params
  except:
    raise ImportError('The simulation parameters could not be loaded. Please make sure that the file `simParams.py` exists and is a valid python defining the variable "simParams".')


def read_ctx():
    try:
        from runpy import run_path
        file_params = run_path('ctxParams.py', init_globals=globals())
        ctx_params = file_params['ctxParams']
        return ctx_params
    except:
        raise ImportError(
            'The cortex-region parameters could not be loaded. Please make sure that the file `baseCTXParams.py` exists and is a valid python defining the variable "ctxParams".')


def read_ctx_M1():
    try:
        from runpy import run_path
        file_params = run_path('ctxM1Params.py', init_globals=globals())
        ctx_M1_params = file_params['ctxM1Params']
        return ctx_M1_params
    except:
        raise ImportError(
            'The cortex-M1-region parameters could not be loaded. Please make sure that the file `baseCTXM1Params.py` exists and is a valid python defining the variable "ctxM1Params".')
'''
def read_ctx_M2():
    try:
        from runpy import run_path
        file_params = run_path('ctxM2Params.py', init_globals=globals())
        ctx_M2_params = file_params['ctxM2Params']
        return ctx_M2_params
    except:
        raise ImportError(
            'The cortex-M2-region parameters could not be loaded. Please make sure that the file `baseCTXM2Params.py` exists and is a valid python defining the variable "ctxM2Params".')
            
'''
    
def read_th():
    try:
        from runpy import run_path
        file_params = run_path('thParams.py', init_globals=globals())
        th_params = file_params['thParams']
        return th_params
    except:
        raise ImportError(
            'The thalamus-region parameters could not be loaded. Please make sure that the file `baseTHParams.py` exists and is a valid python defining the variable "thParams".')


def read_bg():
  try:
    from runpy import run_path
    file_params = run_path('bgParams.py', init_globals=globals())
    bg_params = file_params['bgParams']
    return bg_params
  except:
    raise ImportError('The BG-region parameters could not be loaded. Please make sure that the file `bgParams.py` exists and is a valid python defining the variable "bgParams".')


def read_conn():
    try:
        from runpy import run_path
        file_params = run_path('connParams.py', init_globals=globals())
        ctx_params = file_params['connParams']
        return ctx_params
    except:
        raise ImportError(
            'The cortex-region parameters could not be loaded. Please make sure that the file `baseCONNParams.py` exists and is a valid python defining the variable "connParams".')

def read_cb():
  mf_hz = 30.
  io_hz = 3.


