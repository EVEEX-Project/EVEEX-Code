# -*- coding: utf-8 -*-

"""
Script permettant de tester notre algorithme sur plusieurs images pré-enregistrées.
Contrairement à "Stats_DCT.py", nous testons ici une petite quarantaine d'images,
au lieu de (seulement) 5.
"""

DEFAULT_QUANTIZATION_THRESHOLD = 10

import sys
from os import getcwd
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from time import time, sleep

from logger import LogLevel, Logger
from encoder import Encoder
from network_transmission import Server, Client
from bitstream import BitstreamSender
from decoder import Decoder


##############################################################################


# déclaration des variables globales

global img_width
global img_height
global img_size
global macroblock_size
global possible_macroblock_sizes
global A
global log
global dec
global rle_data
global img_counter
global bit_sender
global dico_huff_ratios
global dico_dict_ratios
global dico_metadata_ratios
global dico_comp_rates


def decode_frame_entierement():
    global received_data
    
    global img_width
    global img_height
    global img_size
    
    global macroblock_size
    
    global A
    global rle_data
    
    global log
    global dec
    
    global img_counter
    global bit_sender
    
    # bitstream (données reçues) --> frame RLE
    dec_rle_data = dec.decode_bitstream_RLE(received_data)
    
    # booléen qui indique si la transmission réseau a été réussie ou non
    bool_test = (rle_data == dec_rle_data)
    
    if bool_test:
        # frame RLE --> frame YUV
        dec_yuv_data = dec.recompose_frame_via_DCT(dec_rle_data, img_size, macroblock_size, A)
        
        # frame YUV --> frame RGB
        dec_rgb_data = dec.YUV_to_RGB(dec_yuv_data)
        
        
        # Vérification des valeurs de la frame RGB décodée (on devrait les avoir entre
        # 0 et 255)
        for k in range(3):
            for i in range(img_height):
                for j in range(img_width):
                    pixel_component = dec_rgb_data[i, j, k]
                    
                    # On remet 'pixel_component' entre 0 (inclus) et 255 (inclus) si besoin
                    
                    if pixel_component < 0:
                        dec_rgb_data[i, j, k] = 0
                    
                    if pixel_component > 255:
                        dec_rgb_data[i, j, k] = 255
        
        
        dec_rgb_data = np.round(dec_rgb_data).astype(dtype=np.uint8)
        
        
        # # # -----------------------STATISTICS------------------------- # # #
        
        
        taille_originale_en_bits = 8 * 3 * img_width * img_height
        
        taille_donnees_compressees_huffman = bit_sender.th_WriteInBitstreamBuffer.taille_donnees_compressees_huffman
        taille_dico_encode_huffman = len(bit_sender.th_WriteInBitstreamBuffer.dict_huffman_encode)
        taille_bitstream_total = len(received_data) # = len(bit_sender.th_WriteInBitstreamBuffer.bit_generator.bitstream)
        
        # on considère que le header et le tail font partie des métadonnees du bitstream
        taille_metadonnees = taille_bitstream_total - taille_donnees_compressees_huffman - taille_dico_encode_huffman
        
        # calcul des taux de tailles de données
        taux_donnees_huffman = 100 * taille_donnees_compressees_huffman / taille_originale_en_bits
        taux_dico_huffman = 100 * taille_dico_encode_huffman / taille_originale_en_bits
        taux_metadonnees = 100 * taille_metadonnees / taille_originale_en_bits
        taux_bitstream_total = 100 * taille_bitstream_total / taille_originale_en_bits # taux de compression
        
        global dico_huff_ratios
        dico_huff_ratios[macroblock_size].append(taux_donnees_huffman)
        
        global dico_dict_ratios
        dico_dict_ratios[macroblock_size].append(taux_dico_huffman)
        
        global dico_metadata_ratios
        dico_metadata_ratios[macroblock_size].append(taux_metadonnees)
        
        global dico_comp_rates
        dico_comp_rates[macroblock_size].append(taux_bitstream_total)
    
    else:
        log.error(f"Transmission réseau non réussie (macroblock size : {macroblock_size}, image counter : {img_counter})")
        sys.exit()


def on_received_data(data):
    global received_data
    
    received_data += data
    
    binary_MSG_TYPE = data[16 : 18]
    
    # "11" est en fait la valeur de TAIL_MSG (= 3) en binaire
    if binary_MSG_TYPE == "11":
        decode_frame_entierement()
        received_data = ""


def execute_main(total_nb_of_images):
    """
    Exécute le programme principal "total_nb_of_images" fois afin d'extraire des
    statistiques sur notre algorithme de compression (du coup sur un total de
    "total_nb_of_images" images).
    """
    
    # # # -------------------------USEFUL DATA-------------------------- # # #
    
    
    t_debut_analyse = time()
    
    global log
    log = Logger.get_instance()
    log.set_log_level(LogLevel.DEBUG)
    
    print("")
    log.debug(f"Début de l'analyse des {total_nb_of_images} images\n")
    
    global img_width
    global img_height
    global img_size
    img_width, img_height = 96, 64
    img_size = (img_width, img_height)
    
    
    global possible_macroblock_sizes
    possible_macroblock_sizes = [8, 16, 32]
    
    global dico_huff_ratios
    dico_huff_ratios = {8  : [],
                        16 : [],
                        32 : []}
    
    global dico_dict_ratios
    dico_dict_ratios = {8  : [],
                        16 : [],
                        32 : []}
    
    global dico_metadata_ratios
    dico_metadata_ratios = {8  : [],
                            16 : [],
                            32 : []}
    
    global dico_comp_rates
    dico_comp_rates = {8  : [],
                       16 : [],
                       32 : []}
    
    
    global dec
    enc = Encoder()
    dec = Decoder()
    
    bufsize = 4096
    
    HOST = "localhost"
    PORT = 3456
    
    serv = Server(HOST, PORT, bufsize, affiche_messages=False)
    cli = Client(HOST, PORT, bufsize, affiche_messages=False)
    
    global received_data
    received_data = ""
    
    serv.listen_for_packets(callback=on_received_data)
    cli.connect_to_server()
    
    frame_id = 0
    
    for possible_macroblock_size in possible_macroblock_sizes:
        global macroblock_size
        macroblock_size = possible_macroblock_size
        
        # création de l'opérateur orthogonal de la DCT
        global A
        A = Encoder.DCT_operator(macroblock_size)
        
        
        for image_nb in range(1, total_nb_of_images + 1):
            frame_id += 1
            
            global img_counter
            img_counter = image_nb
            
            
            # # # --------------------IMAGE GENERATION---------------------- # # #
            
            
            nom_image = f"image_{image_nb}.jpg"
            
            OS = sys.platform
            if OS == "win32":
                path_image = getcwd() + "\\assets\\image_testing\\" + nom_image
            elif OS == "linux" or OS == "linux2":
                path_image = getcwd() + "/assets/image_testing/" + nom_image
            else:
                log.error(f"Unrecognized platform : {OS}")
                sys.exit()
            
            image = Image.open(path_image)
            image_intermediaire = image.getdata()
            
            image_rgb = np.array(image_intermediaire).reshape((img_height, img_width, 3))
            
            
            # # # ----------------------IMAGE ENCODING---------------------- # # #
            
            
            # frame RGB --> frame YUV
            image_yuv = enc.RGB_to_YUV(np.array(image_rgb, dtype=float))
            
            # frame YUV --> frame RLE
            global rle_data
            rle_data = enc.decompose_frame_en_macroblocs_via_DCT(image_yuv, img_size, macroblock_size, DEFAULT_QUANTIZATION_THRESHOLD, A)
            
            
            # # # ----------------SENDING DATA OVER NETWORK----------------- # # #
            
            
            # frame RLE --> bitstream --> réseau
            global bit_sender
            bit_sender = BitstreamSender(frame_id, img_size, macroblock_size, rle_data, cli, bufsize)
            bit_sender.start_sending_messages()
            
            # on termine le thread d'écriture dans le buffer du bitstream
            bit_sender.th_WriteInBitstreamBuffer.join()
    
    
    cli.send_data_to_server("FIN_ENVOI")
    
    # fermeture du socket créé, du côté serveur ET du côté client
    # on termine également le thread d'écoute du serveur
    cli.connexion.shutdown(2) # 2 = socket.SHUT_RDWR
    cli.connexion.close()
    serv.th_Listen.join()
    serv.mySocket.close()
    
    # pour laisser le temps au message associé à la fermeture de la connexion du 
    # client de se print correctement
    sleep(0.1)
    
    log.debug("Thread d'écoute du serveur supprimé.")
    log.debug("Serveur supprimé.")
    
    print("")
    log.debug(f"Fin de l'analyse des {total_nb_of_images} images")
    
    t_fin_analyse = time()
    duree_analyse = t_fin_analyse - t_debut_analyse
    log.info(f"Durée de l'analyse : {duree_analyse:.3f} s")


##############################################################################


def plot_stats(save_graph=False):
    """
    Cette méthode doit être exécutée après la méthode "execute_main"
    """
    
    global dico_huff_ratios
    global dico_dict_ratios
    global dico_metadata_ratios
    global dico_comp_rates
    
    global img_width
    global img_height
    
    dico_global_data = {0 : dico_huff_ratios,
                        1 : dico_dict_ratios,
                        2 : dico_metadata_ratios,
                        3 : dico_comp_rates}
    
    total_nb_of_images = len(dico_huff_ratios[8])
    
    dico_couleurs = {0 : "r", # huff_ratios
                     1 : "g", # dict_ratios
                     2 : "b", # metadata_ratios
                     3 : "k"} # comp_rates
    
    dico_titres = {0 : "Mean Huffman data ratios (in %)",
                   1 : "Mean dict ratios (in %)",
                   2 : "Mean metadata ratios (in %)",
                   3 : "Mean compression rates (in %)"}
    
    global possible_macroblock_sizes
    
    fig, ax = plt.subplots(1, 4, figsize=(16, 8))
    fig.canvas.set_window_title(f"Stats DCT - Test avec {total_nb_of_images} images")
    
    # j = numéro de la colonne d'affichage
    for j in range(4):
        data = dico_global_data[j]
        
        moyennes = [np.array(data[macroblock_size]).mean() for macroblock_size in possible_macroblock_sizes]
        ecarts_types = [np.array(data[macroblock_size]).std() for macroblock_size in possible_macroblock_sizes]
        
        # on affiche les proportions moyennes + les écarts-types associés
        couleur = dico_couleurs[j]
        ax[j].errorbar(possible_macroblock_sizes, moyennes, yerr=ecarts_types, fmt="-o", color=couleur, capsize=3)
        
        ax[j].set_xlim(0, 40)
        ax[j].set_xticks(possible_macroblock_sizes)
        
        titre = dico_titres[j]
        ax[j].set_title(titre)
    
    fig.text(0.5, 0.05, "Axe Ox : Taille des côtés des macroblocs", fontsize=15, ha="center")
    fig.suptitle(f"Stats DCT - {total_nb_of_images} images considérées - Taille des images : {img_width}x{img_height} pixels", fontsize=15)
    
    if save_graph:
        saved_image_name = f"GrapheStatsDCT_avec_{total_nb_of_images}_images.png"
        plt.savefig(saved_image_name, dpi=300, format="png")


##############################################################################


if __name__ == "__main__":
    total_nb_of_images = 37 # ∈ [1, 37]
    
    execute_main(total_nb_of_images)
    plot_stats(save_graph=False)

