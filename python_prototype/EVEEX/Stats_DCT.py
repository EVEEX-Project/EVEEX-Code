# -*- coding: utf-8 -*-

"""
Regroupement de quelques statistiques concernant l'algorithme de compression
utilisé. Ici, il vaut mieux visualiser les graphes dans une fenêtre à part.

On ne considère pour l'instant que les stats de la DCT (sans celles de la iDCT ni 
de la iDTT), parce que les stats de la iDCT et de la iDTT sont sensiblement les 
mêmes que celles de la DCT, à la différence près qu'elles prennent en moyenne un 
peu plus de temps à s'exécuter.

Données communes :
DEFAULT_QUANTIZATION_THRESHOLD = 10
bufsize = 4096
"""

import matplotlib.pyplot as plt


######################## IMAGES GÉNÉRÉES ALÉATOIREMENT ########################


# à titre informatif (donnée commune à toutes les images générées aléatoirement)
dimensions_blocs_aleatoires = (4, 4)

macroblock_sizes = [8, 16, 32]

# tailles associées : [(32, 32), (64, 64), (128, 128), (256, 256), (512, 512)]
nb_pixels = [32**2, 64**2, 128**2, 256**2, 512**2]


# Clés : tailles des macroblocs
# Valeurs : couleurs des données associées aux macroblocs de la taille correspondante
colors = {8 : "r", 16 : "g", 32 : "b"}


# Clés : tailles des macroblocs
# Valeurs : tailles relatives (en %) des données encodées par l'algo de 
# Huffman, par rapport à la taille originale de l'image (en bits)
huff_ratios_random_images = {8  : [28.06, 32.06, 32.66, 33.62, 33.98],
                             16 : [38.50, 43.23, 45.51, 45.61, 45.88],
                             32 : [46.98, 46.85, 48.65, 49.41, 49.45]}


# Clés : tailles des macroblocs
# Valeurs : tailles relatives (en %) des dictionnaires de Huffman encodés, par 
# rapport à la taille originale de l'image (en bits)
dict_ratios_random_images = {8  : [101.72, 66.96, 37.81, 18.30, 7.49],
                             16 : [125.91, 70.53, 34.14, 14.27, 6.14],
                             32 : [122.79, 65.62, 31.16, 13.13, 5.10]}


# Clés : tailles des macroblocs
# Valeurs : tailles relatives (en %) des tailles des métadonnées, par rapport 
# à la taille originale de l'image (en bits)
metadata_ratios_random_images = {8  : [5.99, 5.23, 4.78, 4.53, 4.39],
                                 16 : [2.97, 2.06, 1.52, 1.26, 1.15],
                                 32 : [2.70, 1.69, 1.28, 1.12, 1.03]}


# Clés : tailles des macroblocs
# Valeurs : taux de compression (en %) associés aux images générées aléatoirement
comp_rates_random_images = {8  : [135.77, 104.25, 75.25, 56.45, 45.87],
                            16 : [167.38, 115.83, 81.17, 61.14, 53.17],
                            32 : [172.47, 114.16, 81.09, 63.66, 55.57]}


# Clés : tailles des macroblocs
# Valeurs : temps d'exécution (en secondes) de l'algorithme
exec_times_random_images = {8  : [0.391, 0.735, 3.303, 11.451, 57.513],
                            16 : [0.266, 0.734, 2.479,  7.597, 28.735],
                            32 : [0.297, 0.750, 2.287,  6.431, 22.962]}


# Clés : colonnes d'affichage des données (j)
# Valeurs : données associées aux images générées aléatoirement
dict_data_random_images = {0 : huff_ratios_random_images, 
                           1 : dict_ratios_random_images, 
                           2 : metadata_ratios_random_images, 
                           3 : comp_rates_random_images, 
                           4 : exec_times_random_images}


# Clés : colonnes d'affichage des données (j)
# Valeurs : types des données
# Ce dictionnaire sera également utilisé par la fonction 'plot_stats_existing_image_DCT'
dict_data_types = {0 : "Huff ratios in %", 
                   1 : "Dict ratios in %", 
                   2 : "Metadata ratios in %", 
                   3 : "Compression rates in %", 
                   4 : "Execution time in seconds"}


#----------------------------------------------------------------------------#


def plot_stats_random_images_DCT(save_graph=False):
    """
    Affiche les stats associées aux images générées aléatoirement, et compressées
    en utilisant (en particulier) la DCT.
    """
    plt.close('all')
    fig, axes = plt.subplots(1, 5, figsize=(16, 8))
    
    for j, global_data in dict_data_random_images.items():
        for macroblock_size in macroblock_sizes:
            couleur = colors[macroblock_size]
            data = global_data[macroblock_size]
            
            axes[j].plot(nb_pixels, data, color=couleur, label=f"macroblock size = {macroblock_size}")
            
            if macroblock_size == macroblock_sizes[0]:
                data_type = dict_data_types[j]
                axes[j].set_title(data_type + "\n", color='k', fontsize=10)
        
        axes[j].legend(loc="upper right", fontsize=8)
    
    fig.text(0.5, 0.05, "Axe Ox : Nombre de pixels (largeur x hauteur) dans l'image", fontsize=15, ha='center')
    
    fig.suptitle("Stats DCT - Images générées aléatoirement - Récapitulatif", fontsize=15)
    fig.canvas.set_window_title("Stats EVEEX")
    
    if save_graph:
        plt.savefig("Stats DCT - Images générées aléatoirement - Récapitulatif.png", dpi=300, format="png")
    
    plt.show()


############################ IMAGES PRÉ-EXISTANTES ############################


"""
Pour l'instant on ne travaille que sur un échantillon de 5 images en 480p
"""


dico_noms_images = {1 : "Autumn.png", 
                    2 : "Bridge_BW.bmp", 
                    3 : "Ferrari.jpg", 
                    4 : "Lykan.jpg", 
                    5 : "Sunset.jpg"}

pic_size = (720, 480)
macroblock_sizes_pics = [8, 16, 24, 48, 60]


# Clés : colonnes d'affichage des données (j)
# Valeurs : couleurs des données affichées dans la colonne d'affichage associée 
colors_pics = {0 : "r", 1 : "g", 2 : "b", 3 : "k", 4 : "m"}


# Clés : tailles des macroblocs
# Valeurs : tailles relatives (en %) des données encodées par l'algo de 
# Huffman, par rapport à la taille originale de l'image (en bits)
huff_ratios_pics = {8  : [46.14, 10.53, 6.67, 13.85, 9.02],
                    16 : [45.58, 10.87, 5.41, 14.19, 6.81],
                    24 : [45.64, 10.96, 6.03, 14.39, 7.26],
                    48 : [46.79, 11.79, 6.86, 15.49, 7.21],
                    60 : [47.21, 12.35, 7.25, 16.01, 7.51]}


# Clés : tailles des macroblocs
# Valeurs : tailles relatives (en %) des dictionnaires de Huffman encodés, par 
# rapport à la taille originale de l'image (en bits)
dict_ratios_pics = {8  : [7.65, 2.11, 4.12, 4.66, 6.79],
                    16 : [4.80, 2.75, 3.39, 3.94, 4.18],
                    24 : [3.75, 2.51, 3.04, 3.43, 3.37],
                    48 : [3.11, 2.20, 2.62, 2.76, 2.86],
                    60 : [3.04, 2.15, 2.53, 2.63, 2.84]}


# Clés : tailles des macroblocs
# Valeurs : tailles relatives (en %) des tailles des métadonnées, par rapport 
# à la taille originale de l'image (en bits)
metadata_ratios_pics = {8  : [4.39, 4.32, 4.35, 4.36, 4.38],
                        16 : [1.15, 1.11, 1.12, 1.12, 1.13],
                        24 : [1.02, 0.51, 0.52, 0.52, 0.52],
                        48 : [0.86, 0.29, 0.24, 0.35, 0.22],
                        60 : [0.85, 0.27, 0.21, 0.33, 0.20]}


# Clés : tailles des macroblocs
# Valeurs : taux de compression (en %) associées à l'image considérée
comp_rates_pics = {8  : [58.18, 16.96, 15.13, 22.86, 20.18],
                   16 : [51.53, 14.73,  9.91, 19.25, 12.12],
                   24 : [50.42, 13.99,  9.60, 18.34, 11.15],
                   48 : [50.76, 14.29,  9.71, 18.60, 10.29],
                   60 : [51.10, 14.78,  9.99, 18.97, 10.54]}


# Clés : tailles des macroblocs
# Valeurs : temps d'exécution (en secondes) de l'algorithme
exec_times_pics = {8  : [87.779, 20.345, 30.631, 40.857, 57.405],
                   16 : [34.290, 15.302, 16.838, 23.100, 20.877],
                   24 : [27.478, 14.270, 14.479, 20.437, 16.274],
                   48 : [25.744, 13.088, 13.442, 17.520, 14.643],
                   60 : [25.484, 13.266, 13.686, 15.411, 14.460]}


# Clés : colonnes d'affichage des données (j)
# Valeurs : données associées à l'image considérée
dict_data_pic = {0 : huff_ratios_pics, 
                 1 : dict_ratios_pics, 
                 2 : metadata_ratios_pics, 
                 3 : comp_rates_pics, 
                 4 : exec_times_pics}


#----------------------------------------------------------------------------#


def plot_stats_existing_image_DCT(numero_image, save_graph=False):
    """
    Affiche les stats associées à l'image considérée, et compressée en utilisant
    (en particulier) la DCT.
    """
    fig, axes = plt.subplots(1, 5, figsize=(16, 8))
    
    nom_image = dico_noms_images[numero_image]
    
    for j, global_data in dict_data_pic.items():
        data = [ratio_list[numero_image-1] for ratio_list in list(global_data.values())]
        couleur = colors_pics[j]
        
        axes[j].plot(macroblock_sizes_pics, data, color=couleur)
        
        data_type = dict_data_types[j]
        axes[j].set_title(data_type + "\n", color='k', fontsize=10)
    
    fig.text(0.5, 0.05, "Axe Ox : Taille des côtés des macroblocs", fontsize=15, ha='center')
    
    fig.suptitle(f"Stats DCT - Image pré-existante - {nom_image}, taille : 720x480 (480p)", fontsize=15)
    fig.canvas.set_window_title("Stats EVEEX")
    
    if save_graph:
        plt.savefig(f"Stats DCT - Image pré-existante - '{nom_image}'.png", dpi=300, format="png")
    
    plt.show()


#----------------------------------------------------------------------------#


def plot_stats_all_saved_images_DCT(save_graph=False):
    """
    Affiche les stats associées aux 5 images considérées, et compressées en utilisant
    (en particulier) la DCT.
    """
    fig, axes = plt.subplots(1, 5, figsize=(16, 8))
    
    for j, global_data in dict_data_pic.items():
        for numero_image in range(1, 6):
            nom_image = dico_noms_images[numero_image]
            
            data = [ratio_list[numero_image-1] for ratio_list in list(global_data.values())]
            couleur = colors_pics[numero_image-1]
            
            axes[j].plot(macroblock_sizes_pics, data, color=couleur, label=f"{nom_image}")
            
            data_type = dict_data_types[j]
        
        axes[j].set_title(data_type + "\n", color='k', fontsize=10)
        axes[j].legend(loc="upper right", fontsize=8)
    
    fig.text(0.5, 0.05, "Axe Ox : Taille des côtés des macroblocs", fontsize=15, ha='center')
    
    fig.suptitle("Stats DCT - Images pré-existantes - Récapitulatif - Taille des images : 720x480 (480p)", fontsize=15)
    fig.canvas.set_window_title("Stats EVEEX")
    
    if save_graph:
        plt.savefig("Stats DCT - Images pré-existantes - Récapitulatif.png", dpi=300, format="png")
    
    plt.show()


################################## DÉBUGGAGE ##################################


if __name__ == "__main__":
    sauvegarder_graphe = False
    
    plot_stats_random_images_DCT(save_graph=sauvegarder_graphe)
    
    #------------------------------------------------------------------------#
    
    # rappel des noms des images considérées
    dico_noms_images = {1 : "Autumn.png", 
                        2 : "Bridge_BW.bmp", 
                        3 : "Ferrari.jpg", 
                        4 : "Lykan.jpg", 
                        5 : "Sunset.jpg"}
    
#    for numero_image in range(1, 6):
#        plot_stats_existing_image_DCT(numero_image, save_graph=sauvegarder_graphe)
    
    plot_stats_all_saved_images_DCT(save_graph=sauvegarder_graphe)
    
    #------------------------------------------------------------------------#
    
    """
    Conclusions/constats :
    
    1) Les stats sur les images générées aléatoirement indiquent qu'il faudrait
       choisir un macroblock_size maximal afin de minimiser le taux de compression
    
    2) En pratique, les stats sur les 5 images pré-existantes indiquent qu'il faudrait
       choisir macroblock_size = 16 ou macroblock_size = 24 afin de minimiser
       ce taux de compression
    
    3) Comme 24 n'est pas une taille de macroblocs 'standard', on choisit donc (pour
       des images 480p) macroblock_size = 16.
    
    4) Si on ne compte pas Autumn.png, qui a un taux de compression minimal autour
       de 50%, les taux de compression minimaux des images sont compris entre 10%
       et 20%.
    """

