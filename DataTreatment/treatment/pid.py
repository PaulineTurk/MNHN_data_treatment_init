################################################################################
#                                  Importations                                #    
################################################################################

import numpy as np
import os
from tqdm import tqdm


import sys  
from pathlib import Path 
file = Path(__file__).resolve()
sys.path.append(file.parents[1]) 
from utils.timer import Timer
import utils.fastaReader as fastaReader
import utils.folder as folder



################################################################################
#                                  Fonctions                                   #    
################################################################################

def pid(seq_1, seq_2, list_inclusion):  
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


def pid_two_seq(path_fasta_file, path_file_pId, list_inclusion):  
    liste_seq = fastaReader.read_multi_fasta(path_fasta_file)
    pid_couple = {}
    nb_seq = len(liste_seq)

    # intialisation dico
    for i in range(nb_seq):
        pid_couple[liste_seq[i][0]] = {}
    
    for i in range(nb_seq):
        for j in range(i, nb_seq):
            current_pid = pid(liste_seq[i][1], liste_seq[j][1], list_inclusion)
            pid_couple[liste_seq[i][0]][liste_seq[j][0]] = current_pid
            pid_couple[liste_seq[j][0]][liste_seq[i][0]] = current_pid

    np.save(path_file_pId, pid_couple) 


def save_pid(path_folder_fasta, path_folder_pid, list_inclusion):
    """
    For each fasta file in path_folder_fasta, compute the dictionary of pid 
    for each couple of sequences and save it in path_folder_pid
    """

    folder.creat_folder(path_folder_pid)

    path, dirs, files = next(os.walk(path_folder_fasta))
    nb_files = len(files)

    # liste des PosixPath des alignements d'apprentissage
    files = [x for x in Path(path_folder_fasta).iterdir()]

    for file_counter in tqdm(range(nb_files), desc = "pid"):
        file = files[file_counter]
        accession_num = folder.get_accession_number(file)
        path_file_pid = f"{path_folder_pid}/{accession_num}.pid"
        pid_two_seq(file, path_file_pid, list_inclusion)