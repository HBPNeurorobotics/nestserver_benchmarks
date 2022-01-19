import pprint
import pandas as pd


pickle_file = pd.read_pickle(r'S1_internal_connection.pickle')


# Print all the Pickle file
pprint.pprint(pickle_file)


# Print all sigma = 0 layers
for a in pickle_file:
    print("region: ", a)
    for b in pickle_file[a]:
        
        for c in pickle_file[a][b]:
            if c == "sigma":
                if pickle_file[a][b][c] == 0:
                    
                    print("  layer:", b)
                    print("    sigma:", pickle_file[a][b][c])
