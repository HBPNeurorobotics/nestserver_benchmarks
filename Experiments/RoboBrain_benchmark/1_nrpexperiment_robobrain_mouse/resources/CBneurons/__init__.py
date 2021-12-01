import CBneurons.gr as gr
import CBneurons.go as go
import CBneurons.pkj as pkj
import CBneurons.bs as bs
import CBneurons.vn as vn
import CBneurons.io as io
#import CBneurons.mf as mf
#import CBneurons.spike_detector as sd
import CBneurons.pons as pons

def create_neurons(subCB):
    #mf_hz = 30.
    #io_hz = 3.
    #frequency = 0.5
    gr.create_GR(subCB)
    go.create_GO(subCB)
    pkj.create_PKJ(subCB)
    bs.create_BS(subCB)
    vn.create_VN(subCB)
    io.create_IO(subCB)
    #mf.create_MF(mf_hz=mf_hz, io_hz=io_hz, frequency=frequency)
    #sd.create_SD()
    pons.create_PONS(subCB)
