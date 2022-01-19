import pprint
import pandas as pd

pickle_file = pd.read_pickle(r'S1_internal_connection.pickle')

pprint.pprint(pickle_file)

