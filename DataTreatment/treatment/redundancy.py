################################################################################
#                                  Importations                                #    
################################################################################

import sys  
from pathlib import Path  
import os
from tqdm import tqdm

import sys  
from pathlib import Path 
file = Path(__file__).resolve()
sys.path.append(file.parents[1]) 
from utils.timer import Timer
from treatment.pid import pid                        # check si vraiment besoin
import utils.fastaReader as fastaReader
import utils.folder as folder


################################################################################
#                                  Fonctions                                   #    
################################################################################

def len_seq_corrected(seq, list_residu):
    """
    Return the number of residus in seq that are included in list_residu
    """
    len_seq_corrected = 0
    for aa in seq:
        if aa in list_residu:
            len_seq_corrected += 1
    return len_seq_corrected


def pid_redundant(seq_1, seq_2, list_inclusion):  
    """
    Return the percentage of identity between the two sequences: seq_1 and seq_2
    list_inclusion: liste des caractères inclus
    """
    pid = 0
    nb_included_character_seq_1 = 0
    nb_included_character_seq_2 = 0

    len_seq = len(seq_1)
    for indice_aa in range(len_seq):
        if seq_1[indice_aa] in list_inclusion:
            nb_included_character_seq_1 += 1
        if seq_2[indice_aa] in list_inclusion:
            nb_included_character_seq_2 += 1
            
        if seq_1[indice_aa] in list_inclusion and seq_2[indice_aa] in list_inclusion and seq_1[indice_aa] == seq_2[indice_aa]:
                pid += 1

    return 100*pid/min(nb_included_character_seq_1, nb_included_character_seq_2)


def clustering_non_redundant(liste_seq, file_seq_non_redondant, list_inclusion, pid_sup):    
    """
    Return a partition of liste_seq of sequences with a percentage of identity greater or equal than pid_sup
    """
    cluster = {}
    if liste_seq:   # if the list is not empty
        name_0, seq_0 = liste_seq[0] 
        len_seq_real_0 = len_seq_corrected(seq_0, list_inclusion)
        cluster[0] = [(name_0, seq_0, len_seq_real_0)]

        for name_1, seq_1 in liste_seq:
            len_seq_real_1 = len_seq_corrected(seq_1, list_inclusion)
            group = 0
            indice = 0

            while group <= len(cluster) - 1 and indice <= len(cluster[group]) - 1:
                seq_2 = cluster[group][indice][1]
                pourcentage_id = pid_redundant(seq_1, seq_2, list_inclusion) 
                if pourcentage_id < pid_sup:
                    group += 1
                    indice = 0
                else:
                    if indice == len(cluster[group]) - 1:
                        cluster[group].append((name_1, seq_1, len_seq_real_1))
                        indice += 2 # avoid infinite loop
                    else:
                        indice += 1
            if group == len(cluster):
                cluster[group] = [(name_1, seq_1, len_seq_real_1)]
    else:
        print(file_seq_non_redondant)
    return cluster



def cluster_representative(cluster):
    """
    Select the first sequence with the longest length in the cluster as the cluster representative
    """
    seq_non_redundant = []
    for group in cluster:
        current_group = cluster[group]
        representative = current_group[0]   
        for elem in current_group:
            if elem[2] > representative[2]: # 2 stands for the corrected lenght of a sequence
                representative = elem
        seq_non_redundant.append(representative[0])   # 0 stands for the name of the sequence
    return seq_non_redundant




def non_redundancy_correction(path_file_fasta, path_file_seq_non_redundant, list_residu, pid_sup):
    """
    Rewrite the fasta file by correcting the issue of redundancy according to pid_sup.o
    """
    seed = fastaReader.read_multi_fasta(path_file_fasta)
    cluster = clustering_non_redundant(seed, path_file_seq_non_redundant, list_residu, pid_sup)
    seq_non_redundant = cluster_representative(cluster)

    with open(path_file_fasta, "r") as file:
        with open(path_file_seq_non_redundant, "w") as file_corrected:
            flag_write = False
            for line in file:
                if line[0] == ">":   
                    if line[1:-1].split(" ")[0] in seq_non_redundant:    # keep the name only 
                        flag_write = True
                    else:
                        flag_write = False
                if flag_write == True:
                    file_corrected.write(line)





def multi_non_redundancy_correction(path_folder_fasta, path_folder_fasta_non_redondant, list_residu, pid_sup = 99):
    """
    Create a folder of fasta files with the redondant issue corrected

    path_folder_fasta: original fasta folder
    path_folder_fasta_non_redondant: fasta folder corrected
    list_residu: list of valid residu to evaluate the corrected len of each sequence
    pid_sup: percentage of identity for the clustering
    """

    folder.creat_folder(path_folder_fasta_non_redondant)
    
    path, dirs, files = next(os.walk(path_folder_fasta))
    nb_files = len(files)

    # liste des PosixPath des alignements d'apprentissage
    files = [x for x in Path(path_folder_fasta).iterdir()]

    for file_counter in tqdm(range(nb_files), desc = "non-redundant"):
        file = files[file_counter]
        accession_num = folder.get_accession_number(file)
        path_fasta_non_redondant = f"{path_folder_fasta_non_redondant}/{accession_num}.fasta.nonRedundant"
        non_redundancy_correction(file, path_fasta_non_redondant, list_residu, pid_sup)