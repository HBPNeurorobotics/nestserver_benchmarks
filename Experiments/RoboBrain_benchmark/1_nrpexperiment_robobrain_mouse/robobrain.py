#!/usr/bin/env python
# -*- coding: utf-8 -*-
  
import nest

# Resetting Nest Kernel 
nest.ResetKernel()  


# Initializing Neurons, Brain connections and FrequencyDetectors
ctx_M1_layers = stim_all_model.main()

#-------------------------------------------------------------------------------
# ctx_M1_Layers are:
# 'M1_L1_ENGC', NodeCollection(metadata=spatial, model=M1_L1_ENGC, size=512, first=1, last=512)),
# ('M1_L1_SBC', NodeCollection(metadata=spatial, model=M1_L1_SBC, size=1200, first=514, last=1713)),
# ('M1_L23_CC', NodeCollection(metadata=spatial, model=M1_L23_CC, size=14256, first=1715, last=15970)), 
# ('M1_L23_PV', NodeCollection(metadata=spatial, model=M1_L23_PV, size=1280, first=15972, last=17251)),
# ('M1_L23_SST', NodeCollection(metadata=spatial, model=M1_L23_SST, size=1125, first=17253, last=18377)), 
# ('M1_L23_VIP', NodeCollection(metadata=spatial, model=M1_L23_VIP, size=1280, first=18379, last=19658)), 
# ('M1_L5A_CC', NodeCollection(metadata=spatial, model=M1_L5A_CC, size=1600, first=19660, last=21259)),
# ('M1_L5A_CS', NodeCollection(metadata=spatial, model=M1_L5A_CS, size=1600, first=21261, last=22860)),
# ('M1_L5A_CT', NodeCollection(metadata=spatial, model=M1_L5A_CT, size=1600, first=22862, last=24461)),
# ('M1_L5A_PV', NodeCollection(metadata=spatial, model=M1_L5A_PV, size=675, first=24463, last=25137)), 
# ('M1_L5A_SST', NodeCollection(metadata=spatial, model=M1_L5A_SST, size=675, first=25139, last=25813)),
# ('M1_L5B_CC', NodeCollection(metadata=spatial, model=M1_L5B_CC, size=3249, first=25815, last=29063)), 
# ('M1_L5B_CS', NodeCollection(metadata=spatial, model=M1_L5B_CS, size=3249, first=29065, last=32313)),
# ('M1_L5B_PT', NodeCollection(metadata=spatial, model=M1_L5B_PT, size=5819, first=32315, last=38133)),
# ('M1_L5B_PV', NodeCollection(metadata=spatial, model=M1_L5B_PV, size=1575, first=38135, last=39709)),
# ('M1_L5B_SST', NodeCollection(metadata=spatial, model=M1_L5B_SST, size=1575, first=39711, last=41285)),
# ('M1_L6_CT', NodeCollection(metadata=spatial, model=M1_L6_CT, size=13690, first=41287, last=54976)),
# ('M1_L6_PV', NodeCollection(metadata=spatial, model=M1_L6_PV, size=1445, first=54978, last=56422)), 
# ('M1_L6_SST', NodeCollection(metadata=spatial, model=M1_L6_SST, size=2400, first=56424, last=58823))])
#-------------------------------------------------------------------------------


print('\n\n BFFFFFF test from brain \n\n')
population_2 = nest.Create('iaf_cond_alpha', 8)

populations = ctx_M1_layers

#               {'circuit' : population_2,
#               'actors_bf' : population_2,
#               'actors_bfe' : population_2}
                          
#circuit = nest.Create('iaf_cond_alpha', 3)

