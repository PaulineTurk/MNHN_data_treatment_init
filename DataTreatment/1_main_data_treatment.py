################################################################################
#                                  Importations                                #    
################################################################################
import sys  
from pathlib import Path 
file = Path(__file__).resolve()
sys.path.append(file.parents[0]) 
import treatment.stockholm as stockholm
import treatment.capitalizer as capitalizer
import treatment.pid as pid
import treatment.redundancy as redundancy
import treatment.split as split
import treatment.description as description
import utils.folder as folder


################################################################################
#                                  Variables                                   #    
################################################################################

DATA                        =  f"{file.parents[2]}/MNHN_RESULT/1_DATA_mini"      # chemin du dossier des données à créer en amont

list_standard_aa            = ["A", "R", "N", "D", "C", "Q", "E", "G", "H", "I", 
                               "L", "K", "M", "F", "P", "S", "T", "W", "Y", "V"]

nom_fichier_multi_stockholm = "Pfam-A.seed"   # ex. Pfam-A.seed
nom_dossier_mono_stockholm  = "Pfam_Stockholm"
nom_dossier_fasta           = "Pfam_FASTA"
nom_dossier_fasta_upper     = "Pfam_Upper"
nom_dossier_PID             = "PID"
nom_dossier_cluster         = "Pfam_nonRedondant"
pid_cluster                 = 99
nom_dossier_data_split      = "Pfam_split"
percentage_train            = 50   # pourcentage de Pfam pour l'entrainement

################################################################################
#                 Séparation du fichier Stockholm multi-alignements            #
#                   en un fichier Stockholm par alignement                     #
################################################################################

path_file_multi_stockholm   = f"{DATA}/{nom_fichier_multi_stockholm}"
path_folder_mono_stockholm  = f"{DATA}/{nom_dossier_mono_stockholm}"
stockholm.stockholm_separator(path_file_multi_stockholm, path_folder_mono_stockholm)


################################################################################
#                   Conversion de chaque fichier Stockholm                     #
#                            en un fichier FASTA                               #
################################################################################

path_folder_fasta = f"{DATA}/{nom_dossier_fasta}"
stockholm.multi_stockholm_to_fasta(path_folder_mono_stockholm, path_folder_fasta)

# residu_count, total_residu, character_count, total_character = description.data_count(path_folder_fasta, list_standard_aa)
# description.bar_plot_data_count(path_folder_fasta, residu_count, total_residu, "Standard amino-acid")
# description.bar_plot_data_count(path_folder_fasta, character_count, total_character , "Character")



################################################################################
#                   Capitalisation des caractères de Pfam                      #
################################################################################

print("\nCapitalisation")
path_folder_fasta_upper = f"{DATA}/{nom_dossier_fasta_upper}" 
capitalizer.multi_capitalization(path_folder_fasta, path_folder_fasta_upper)

residu_count, total_residu, character_count, total_character = description.data_count(path_folder_fasta_upper, list_standard_aa)
description.bar_plot_data_count(path_folder_fasta_upper, residu_count, total_residu, "Standard amino-acid")
description.bar_plot_data_count(path_folder_fasta_upper, character_count, total_character , "Character")



################################################################################
#                   Calcul des pourcentages d'identité                         #
################################################################################

print("\nCalcul de PID")
path_folder_pid = f"{DATA}/{nom_dossier_PID}"   
pid.save_pid(path_folder_fasta_upper, path_folder_pid, list_standard_aa)


################################################################################
#                                    Clustering                                #
################################################################################

print("\nClustering")
path_folder_fasta_nonRedondant = f"{DATA}/{nom_dossier_cluster}" 
redundancy.multi_non_redundancy_correction(path_folder_fasta_upper, path_folder_fasta_nonRedondant, list_standard_aa, pid_cluster)

residu_count, total_residu, character_count, total_character = description.data_count(path_folder_fasta_nonRedondant, list_standard_aa)
description.bar_plot_data_count(path_folder_fasta_nonRedondant, residu_count, total_residu, "Standard amino-acid")
description.bar_plot_data_count(path_folder_fasta_nonRedondant, character_count, total_character , "Character")




################################################################################
#                Split des alignements en entrainement/test                    #
################################################################################

print("\nData split")
path_folder_data_split = f"{DATA}/{nom_dossier_data_split}" 
folder.creat_folder(path_folder_data_split)
split.data_split(path_folder_fasta_nonRedondant, path_folder_data_split, percentage_train, "Pfam_train", "Pfam_test")
