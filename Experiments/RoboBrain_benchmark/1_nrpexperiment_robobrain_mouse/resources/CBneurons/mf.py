import nest


def create_MF(mf_hz=30, io_hz=3, frequency=0.5, constant=5.0):
    
 
    configuration = {}
    configuration['rate'] = mf_hz / 2.0
    configuration['amplitude'] = mf_hz / 2.0
    configuration['frequency'] = frequency
    configuration['phase'] = -90.0
    nest.CopyModel('sinusoidal_poisson_generator', 'MF', configuration)
    configuration = {}
    configuration['rate'] = float(constant)
    nest.CopyModel('poisson_generator', 'MF_Constant', configuration)
    configuration = {}
    configuration['rate'] = io_hz / 2.0
    configuration['amplitude'] = io_hz / 2.0
    configuration['frequency'] = frequency
    configuration['phase'] = -90.0
    nest.CopyModel('sinusoidal_poisson_generator', 'MF_IO', configuration)
    configuration = {}
    configuration['rate'] = float(constant)
    nest.CopyModel('poisson_generator', 'MF_IO_Constant', configuration)
