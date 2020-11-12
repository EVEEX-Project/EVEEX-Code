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
huff_ratios_DCT = {8  : [28.06, 32.06, 32.66, 33.62, 33.98], 
                   16 : [38.50, 43.23, 45.51, 45.61, 45.88], 
                   32 : [46.98, 46.85, 48.65, 49.41, 49.45]}


# Clés : tailles des macroblocs
# Valeurs : tailles relatives (en %) des dictionnaires de Huffman encodés, par 
# rapport à la taille originale de l'image (en bits)
dict_ratios_DCT = {8  : [101.72, 66.96, 37.81, 18.30, 7.49], 
                   16 : [125.91, 70.53, 34.14, 14.27, 6.14], 
                   32 : [122.79, 65.62, 31.16, 13.13, 5.10]}


# Clés : tailles des macroblocs
# Valeurs : tailles relatives (en %) des tailles des métadonnées, par rapport 
# à la taille originale de l'image (en bits)
metadata_ratios_DCT = {8  : [5.99, 5.23, 4.78, 4.53, 4.39], 
                       16 : [2.97, 2.06, 1.52, 1.26, 1.15], 
                       32 : [2.70, 1.69, 1.28, 1.12, 1.03]}


# Clés : tailles des macroblocs
# Valeurs : taux de compression (en %) associés aux images générées aléatoirement
comp_rates_DCT = {8  : [135.77, 104.25, 75.25, 56.45, 45.87], 
                  16 : [167.38, 115.83, 81.17, 61.14, 53.17], 
                  32 : [172.47, 114.16, 81.09, 63.66, 55.57]}


# Clés : tailles des macroblocs
# Valeurs : temps d'exécution (en secondes) de l'algorithme
exec_times_DCT = {8  : [0.875, 2.281, 8.178, 29.929, 107.432], 
                  16 : [0.755, 1.704, 4.678, 14.210,  47.391], 
                  32 : [0.765, 1.500, 4.215, 12.879,  41.067]}


# Clés : colonnes d'affichage des données (j)
# Valeurs : données associées aux images générées aléatoirement
dict_data_DCT = {0 : huff_ratios_DCT, 
                 1 : dict_ratios_DCT, 
                 2 : metadata_ratios_DCT, 
                 3 : comp_rates_DCT, 
                 4 : exec_times_DCT}


# Clés : colonnes d'affichage des données (j)
# Valeurs : types des données
# Ce dictionnaire sera également utilisé par la fonction 'plot_stats_Sunset_DCT'
dict_data_types = {0 : "Huff ratios in %", 
                   1 : "Dict ratios in %", 
                   2 : "Metadata ratios in %", 
                   3 : "Compression rates in %", 
                   4 : "Execution time in seconds"}


#----------------------------------------------------------------------------#


def plot_stats_random_images_DCT():
    """
    Affiche les stats associées aux images générées aléatoirement, et compressées
    en utilisant (en particulier) la DCT.
    """
    plt.close('all')
    fig, axes = plt.subplots(1, 5, figsize=(16, 8))
    
    for j, global_data in dict_data_DCT.items():
        for macroblock_size in macroblock_sizes:
            couleur = colors[macroblock_size]
            data = global_data[macroblock_size]
            
            axes[j].plot(nb_pixels, data, color=couleur, label=f"macroblock size = {macroblock_size}")
            
            if macroblock_size == macroblock_sizes[0]:
                data_type = dict_data_types[j]
                axes[j].set_title(data_type + "\n", color='k', fontsize=10)
        
        axes[j].legend(loc="upper right", fontsize=8)
    
    fig.text(0.5, 0.05, "Axe Ox : Nombre de pixels dans l'image", fontsize=15, ha='center')
    
    fig.suptitle("Stats DCT - Images générées aléatoirement", fontsize=15)
    fig.canvas.set_window_title("Stats EVEEX")
    
    plt.show()


############################# IMAGE PRÉ-EXISTANTE #############################


"""
Image considérée ici : 'Sunset.jpg'
"""


# pour l'instant on ne considère qu'une seule image ('Sunset.jpg')
pic_name = "Sunset.jpg"
pic_size = (720, 480)
macroblock_sizes_pic = [8, 16, 24, 48, 60]


# Clés : colonnes d'affichage des données (j)
# Valeurs : couleurs des données affichées dans la colonne d'affichage associée 
colors_pic = {0 : "r", 1 : "g", 2 : "b", 3 : "k", 4 : "m"}


# Clés : tailles des macroblocs
# Valeurs : tailles relatives (en %) des données encodées par l'algo de 
# Huffman, par rapport à la taille originale de l'image (en bits)
huff_ratios_pic = {8  : 9.02, 
                   16 : 6.81, 
                   24 : 7.26, 
                   48 : 7.21, 
                   60 : 7.51}


# Clés : tailles des macroblocs
# Valeurs : tailles relatives (en %) des dictionnaires de Huffman encodés, par 
# rapport à la taille originale de l'image (en bits)
dict_ratios_pic = {8  : 6.79, 
                   16 : 4.18, 
                   24 : 3.37, 
                   48 : 2.86, 
                   60 : 2.84}


# Clés : tailles des macroblocs
# Valeurs : tailles relatives (en %) des tailles des métadonnées, par rapport 
# à la taille originale de l'image (en bits)
metadata_ratios_pic = {8  : 4.38, 
                       16 : 1.13, 
                       24 : 0.52, 
                       48 : 0.22, 
                       60 : 0.20}


# Clés : tailles des macroblocs
# Valeurs : taux de compression (en %) associées à l'image 'Sunset.jpg'
comp_rates_pic = {8  : 20.18, 
                  16 : 12.12, 
                  24 : 11.15, 
                  48 : 10.29, 
                  60 : 10.54}


# Clés : tailles des macroblocs
# Valeurs : temps d'exécution (en secondes) de l'algorithme
exec_times_pic = {8  : 143.472, 
                  16 :  51.514, 
                  24 :  35.132, 
                  48 :  27.712, 
                  60 :  27.692}


# Clés : colonnes d'affichage des données (j)
# Valeurs : données associées à l'image 'Sunset.jpg'
dict_data_pic = {0 : huff_ratios_pic, 
                 1 : dict_ratios_pic, 
                 2 : metadata_ratios_pic, 
                 3 : comp_rates_pic, 
                 4 : exec_times_pic}


#----------------------------------------------------------------------------#


def plot_stats_Sunset_DCT():
    """
    Affiche les stats associées à l'image 'Sunset.jpg', et compressée en utilisant
    (en particulier) la DCT.
    """
    fig, axes = plt.subplots(1, 5, figsize=(16, 8))
    
    for j, global_data in dict_data_pic.items():
        data = list(global_data.values())
        couleur = colors_pic[j]
        
        axes[j].plot(macroblock_sizes_pic, data, color=couleur)
        
        data_type = dict_data_types[j]
        axes[j].set_title(data_type + "\n", color='k', fontsize=10)
    
    fig.text(0.5, 0.05, "Axe Ox : Taille des côtés des macroblocs", fontsize=15, ha='center')
    
    fig.suptitle(f"Stats DCT - Image pré-existante - {pic_name}, taille : {pic_size[0]}x{pic_size[1]}", fontsize=15)
    fig.canvas.set_window_title("Stats EVEEX")
    
    plt.show()


################################## DÉBUGGAGE ##################################


if __name__ == "__main__":
    plot_stats_random_images_DCT()
    
    plot_stats_Sunset_DCT()
    
    """
    Conclusion :
    
    Étant donné que la qualité de l'image RGB décodée ne semble pas être affectée 
    par macroblock_size, on a tout intérêt à considérer un macroblock_size maximal 
    afin d'optimiser les performances de l'algorithme. 
    
    Parmi les valeurs standards de macroblock_size (ie 8, 16 et 32), on considère 
    donc 16 et 32 comme des candidats potentiels.
    
    Pour du 480p (ie du 720x480), 32 étant une valeur illicite de macroblock_size
    (car 32 ne divise pas 720), on considèrera donc macroblock_size = 16.
    """

