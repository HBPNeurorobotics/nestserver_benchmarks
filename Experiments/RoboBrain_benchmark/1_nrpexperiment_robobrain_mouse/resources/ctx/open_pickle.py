import pprint
import pandas as pd
import pickle


file = r'S1_internal_connection.pickle'

pickle_file = []
with open(file, 'rb+') as pf:
    pickle_file = pickle.load(pf)


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
                    pickle_file[a][b][c] = 0.2
                    print(pickle_file[a][b][c])


with open(file, 'wb+') as pf:
    pickle.dump(pickle_file, pf)


#df.to_pickle(r'S1_internal_connection.pickle')


