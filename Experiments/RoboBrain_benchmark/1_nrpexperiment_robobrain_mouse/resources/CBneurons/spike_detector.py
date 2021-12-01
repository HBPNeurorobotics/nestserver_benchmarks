import nest


def create_SD():
    """spike detector

    Example:

    ::

        create_SD()
    """
    configuration = {'to_file': False, 'to_memory': True}
    nest.CopyModel('spike_detector', 'SD', configuration)
