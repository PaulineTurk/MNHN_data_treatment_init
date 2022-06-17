import numpy as np
import pandas as pd

def dico_visualizer(path_dico):
    dico = np.load(path_dico, allow_pickle='TRUE').item()    
    df_dico = np.transpose(pd.DataFrame.from_dict(dico))  
    print(path_dico)
    print(df_dico)
    return df_dico



#dico_visualizer("/Users/pauline/Desktop/Projet_MNHN/PF00198.26.pid_v2.npy")
#dico_visualizer("/Users/pauline/Desktop/Projet_MNHN/PF00198.26.pid.npy")