# -*- coding: utf-8 -*-

"""
Script permettant de tester l'encodage et le décodage d'une image par notre 
propre algorithme.

Version utilisant la DCT (Discrete Cosine Transform).
"""

DEFAULT_QUANTIZATION_THRESHOLD = 10

import sys
from os import getcwd
from PIL import Image
import numpy as np
from time import time, sleep
from random import randint

from logger import LogLevel, Logger
from image_generator import MosaicImageGenerator
from image_visualizer import ImageVisualizer
from encoder import Encoder
from network_transmission import Server, Client
from bitstream import BitstreamSender
from decoder import Decoder


# # # ----------------------SETTING UP THE LOGGER------------------------ # # #


t_debut_algo = time()

generer_fichier_log = False
sauvegarder_image_decodee = False

log = Logger.get_instance()
log.set_log_level(LogLevel.DEBUG)

if generer_fichier_log:
    log.start_file_logging("log_main_DCT.log")

print("\n")
log.debug("Algorithme de compression utilisant la DCT classique\n\n")


# # # -------------------------IMAGE GENERATION-------------------------- # # #


"""
On a ici 2 méthodes. Choisir celle à utiliser (cf. dico_methodes).
"""

dico_methodes = {1 : "considérer une image pré-existante",
                 2 : "générer une image aléatoirement"}


numero_methode_choisie = 1 # ∈ [1, 2]


#----------------------------------------------------------------------------#


"""
Méthode n°1 : Si l'on veut considérer une image pré-existante
"""

if numero_methode_choisie == 1:
    dico_noms_images = {1 : "Autumn.png", 
                        2 : "Bridge_BW.bmp", 
                        3 : "Ferrari.jpg", 
                        4 : "Lykan.jpg", 
                        5 : "Sunset.jpg"}
    
    numero_image = 4 # ∈ [1, 5]
    nom_image = dico_noms_images[numero_image]
    
    path_image = getcwd() + "\\assets\\" + nom_image
    
    # Valeurs standards de macroblock_size : 8, 16 et 32
    # Ici, 24, 48 et 60 fonctionnent aussi très bien
    # Doit être <= 63
    macroblock_size = 16
    
    # il faut s'assurer d'avoir les bonnes dimensions de l'image, ET que macroblock_size
    # divise bien ses 2 dimensions
    img_width = 720
    img_height = 480
    
    # format standard
    img_size = (img_width, img_height)
    
    image = Image.open(path_image)
    image_intermediaire = image.getdata()
    
    image_rgb = np.array(image_intermediaire).reshape((img_height, img_width, 3))


#----------------------------------------------------------------------------#


"""
Méthode n°2 : Si l'on veut générer une image aléatoirement
"""

if numero_methode_choisie == 2:
    # Valeurs standards de macroblock_size : 8, 16 et 32
    # Doit être <= 63
    macroblock_size = 16
    
    num_macroblocks_per_line = 45
    num_macroblocks_per_column = 30
    
    img_width = num_macroblocks_per_line * macroblock_size
    img_height = num_macroblocks_per_column * macroblock_size
    
    # format standard
    img_size = (img_width, img_height)
    
    # pour MosaicGenerator
    taille_image = (img_height, img_width)
    
    # doit être comprise entre 1 et img_height
    hauteur_blocs_aleatoires = 4
    
    # doit être comprise entre 1 et img_width
    epaisseur_blocs_aleatoires = 4
    
    taille_blocs_aleatoires = (hauteur_blocs_aleatoires, epaisseur_blocs_aleatoires)
    
    img_gen = MosaicImageGenerator(size=taille_image, bloc_size=taille_blocs_aleatoires)
    image_rgb = np.round(255 * img_gen.generate()).astype(dtype=int)


#----------------------------------------------------------------------------#


if numero_methode_choisie not in list(dico_methodes.keys()):
    log.error("Numéro de méthode invalide.\n\n")
    sys.exit()


# # # -------------------------IMAGE ENCODING-------------------------- # # #


# création de l'opérateur orthogonal de la DCT
A = Encoder.DCT_operator(macroblock_size)


img_visu = ImageVisualizer()
enc = Encoder()


t_debut_premier_affichage = time()
print("\nEncodage - Image RGB :\n")
img_visu.show_image_with_matplotlib(image_rgb)
print("\n\n")
t_fin_premier_affichage = time()
duree_premier_affichage = t_fin_premier_affichage - t_debut_premier_affichage

# 'extraction' ou 'génération' de la frame RGB, selon la méthode choisie
t_fin_extraction_frame_RGB = time()
duree_extraction_frame_RGB = t_fin_extraction_frame_RGB - t_debut_algo - duree_premier_affichage

# frame RGB --> frame YUV
image_yuv = enc.RGB_to_YUV(np.array(image_rgb, dtype=float))
t_fin_conversion_RGB_YUV = time()
duree_conversion_RGB_YUV = t_fin_conversion_RGB_YUV - t_fin_extraction_frame_RGB

# frame YUV --> frame RLE
rle_data = enc.decompose_frame_en_macroblocs_via_DCT(image_yuv, img_size, macroblock_size, DEFAULT_QUANTIZATION_THRESHOLD, A)
t_fin_conversion_YUV_RLE = time()
duree_conversion_YUV_RLE = t_fin_conversion_YUV_RLE - t_fin_conversion_RGB_YUV


# # # -------------------------SENDING DATA OVER NETWORK-------------------------- # # #


# le bufsize doit impérativement être >= 67 (en pratique : OK)
bufsize = 4096

HOST = "localhost"
PORT = 6666

# booléen indiquant si l'on veut afficher les messages entre le client et
# le serveur
affiche_messages = False

# On désactive les messages par défaut si on sait qu'il va y avoir beaucoup de
# données à afficher
if ((affiche_messages == True) and (img_width * img_height > 10000)):
    affiche_messages = False

serv = Server(HOST, PORT, bufsize, affiche_messages)
cli = Client(HOST, PORT, bufsize, affiche_messages)

global received_data
received_data = ""

def on_received_data(data):
    global received_data
    received_data += data

serv.listen_for_packets(callback=on_received_data)
cli.connect_to_server()

frame_id = randint(0, 65535) # 65535 = 2**16 - 1

t_fin_initialisation_reseau = time()
duree_initialisation_reseau = t_fin_initialisation_reseau - t_fin_conversion_YUV_RLE

# frame RLE --> bitstream --> réseau
bit_sender = BitstreamSender(frame_id, img_size, macroblock_size, rle_data, cli, bufsize)
bit_sender.start_sending_messages()
t_fin_conversion_RLE_bitstream_et_passage_reseau = time()
duree_generation_dico_huffman = bit_sender.th_WriteInBitstreamBuffer.duree_generation_dico_huffman
duree_conversion_RLE_bitstream_et_passage_reseau_sans_generation_dico_huffman = t_fin_conversion_RLE_bitstream_et_passage_reseau - t_fin_initialisation_reseau - duree_generation_dico_huffman

# juste à titre informatif (débuggage)
nb_paquets_dict = bit_sender.th_WriteInBitstreamBuffer.nb_paquets_dict
nb_paquets_body = bit_sender.th_WriteInBitstreamBuffer.nb_paquets_body
# header + dict + body + tail
nb_total_paquets_envoyes = 1 + nb_paquets_dict + nb_paquets_body + 1

# pour laisser le temps au message associé au dernier paquet réseau de se print 
# correctement
if affiche_messages:
    sleep(0.1)

else:
    log.debug("Les messages entre le client et le serveur n'ont ici pas été affichés pour plus de lisibilité.\n\n")

# on termine le thread d'écriture dans le buffer du bitstream
bit_sender.th_WriteInBitstreamBuffer.join()
log.debug("Thread d'écriture dans le buffer du bitstream supprimé.\n")

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
log.debug("Serveur supprimé.\n\n")


# # # -------------------------DATA DECODING TO IMAGE-------------------------- # # #


dec = Decoder()

# bitstream (données reçues) --> frame RLE
dec_rle_data = dec.decode_bitstream_RLE(received_data)
t_fin_conversion_bitstream_recu_RLE = time()
duree_conversion_bitstream_recu_RLE = t_fin_conversion_bitstream_recu_RLE - t_fin_conversion_RLE_bitstream_et_passage_reseau

log.debug(f"Transmission réseau réussie : {str(rle_data == dec_rle_data).upper()}\n")

# frame RLE --> frame YUV
dec_yuv_data = dec.recompose_frame_via_DCT(dec_rle_data, img_size, macroblock_size, A)
t_fin_conversion_RLE_YUV = time()
duree_conversion_RLE_YUV = t_fin_conversion_RLE_YUV - t_fin_conversion_bitstream_recu_RLE

# frame YUV --> frame RGB
dec_rgb_data = dec.YUV_to_RGB(dec_yuv_data)
t_fin_conversion_YUV_RGB = time()
duree_conversion_YUV_RGB = t_fin_conversion_YUV_RGB - t_fin_conversion_RLE_YUV


# Vérification des valeurs de la frame RGB décodée (on devrait les avoir entre
# 0 et 255)
# Les "valeurs illégales", en forte minorité (heureusement), sont ici 
# principalement dues au passage aux entiers lors de la RLE (à l'encodage)
(num_illegal_low_values, num_illegal_high_values) = (0, 0) # pour débugger
for k in range(3):
    for i in range(img_height):
        for j in range(img_width):
            pixel_component = dec_rgb_data[i, j, k]
            
            # On remet 'pixel_component' entre 0 (inclus) et 255 (inclus) si besoin
            
            if pixel_component < 0:
                dec_rgb_data[i, j, k] = 0
                num_illegal_low_values += 1
            
            if pixel_component > 255:
                dec_rgb_data[i, j, k] = 255
                num_illegal_high_values += 1


dec_rgb_data = np.round(dec_rgb_data).astype(dtype=np.uint8)
t_fin_correction_frame_RGB_decodee = time()
duree_correction_frame_RGB_decodee = t_fin_correction_frame_RGB_decodee - t_fin_conversion_YUV_RGB

t_debut_deuxieme_affichage_et_sauvegarde = time()

print("\n\nDécodage - Image RGB :\n")
img_visu.show_image_with_matplotlib(dec_rgb_data)

if sauvegarder_image_decodee:
    print("\n\n")
    img_visu.save_image_to_disk(dec_rgb_data, "decoded_image.png")

t_fin_deuxieme_affichage_et_sauvegarde = time()
duree_deuxieme_affichage_et_sauvegarde = t_fin_deuxieme_affichage_et_sauvegarde - t_debut_deuxieme_affichage_et_sauvegarde

t_fin_algo = time()
duree_algo = t_fin_algo - t_debut_algo - duree_premier_affichage - duree_deuxieme_affichage_et_sauvegarde


# # # ----------------------------STATISTICS------------------------------ # # #


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
taux_bitstream_total = 100 * taille_bitstream_total / taille_originale_en_bits

expression_standard_taux_compression = taille_originale_en_bits / taille_bitstream_total


# calcul des taux de durées d'exécution
taux_extraction_frame_RGB = 100 * duree_extraction_frame_RGB / duree_algo
taux_conversion_RGB_YUV = 100 * duree_conversion_RGB_YUV / duree_algo
taux_conversion_YUV_RLE = 100 * duree_conversion_YUV_RLE / duree_algo
taux_initialisation_reseau = 100 * duree_initialisation_reseau / duree_algo
taux_generation_dico_huffman = 100 * duree_generation_dico_huffman / duree_algo
taux_conversion_RLE_bitstream_et_passage_reseau_sans_generation_dico_huffman = 100 * duree_conversion_RLE_bitstream_et_passage_reseau_sans_generation_dico_huffman / duree_algo
taux_conversion_bitstream_recu_RLE = 100 * duree_conversion_bitstream_recu_RLE / duree_algo
taux_conversion_RLE_YUV = 100 * duree_conversion_RLE_YUV / duree_algo
taux_conversion_YUV_RGB = 100 * duree_conversion_YUV_RGB / duree_algo
taux_correction_frame_RGB_decodee = 100 * duree_correction_frame_RGB_decodee / duree_algo


print("\n\n")
log.debug(f"Tailles relatives par rapport à la taille originale de l'image (en bits) :\n")

log.debug(f"Données encodées via l'algo de Huffman : {taux_donnees_huffman:.2f}%")
log.debug(f"Dictionnaire de Huffman encodé : {taux_dico_huffman:.2f}%")
log.debug(f"Métadonnées du bitstream : {taux_metadonnees:.2f}%\n")
log.debug(f"Bitstream total : {taux_bitstream_total:.2f}% --> taux de compression \"{expression_standard_taux_compression:.2f} : 1\"\n")


print("\n")
log.debug("Durée de chacune des étapes de l'algorithme :\n")

log.debug(f"Extraction/génération de la frame RGB : {duree_extraction_frame_RGB:.3f} s ({taux_extraction_frame_RGB:.2f}%)")
log.debug(f"Conversion de la frame RGB en frame YUV : {duree_conversion_RGB_YUV:.3f} s ({taux_conversion_RGB_YUV:.2f}%)")
log.debug(f"Conversion de la frame YUV en frame RLE : {duree_conversion_YUV_RLE:.3f} s ({taux_conversion_YUV_RLE:.2f}%)")
log.debug(f"Initialisation des paramètres réseau : {duree_initialisation_reseau:.3f} s ({taux_initialisation_reseau:.2f}%)")
log.debug(f"Génération du dictionnaire de Huffman : {duree_generation_dico_huffman:.3f} s ({taux_generation_dico_huffman:.2f}%)")
log.debug(f"Conversion de la frame RLE en bitstream + passage réseau : {duree_conversion_RLE_bitstream_et_passage_reseau_sans_generation_dico_huffman:.3f} s ({taux_conversion_RLE_bitstream_et_passage_reseau_sans_generation_dico_huffman:.2f}%)")
log.debug(f"Conversion du bitstream reçu en frame RLE : {duree_conversion_bitstream_recu_RLE:.3f} s ({taux_conversion_bitstream_recu_RLE:.2f}%)")
log.debug(f"Conversion de la frame RLE en frame YUV : {duree_conversion_RLE_YUV:.3f} s ({taux_conversion_RLE_YUV:.2f}%)")
log.debug(f"Conversion de la frame YUV en frame RGB : {duree_conversion_YUV_RGB:.3f} s ({taux_conversion_YUV_RGB:.2f}%)")
log.debug(f"Correction de la frame RGB décodée : {duree_correction_frame_RGB_decodee:.3f} s ({taux_correction_frame_RGB_decodee:.2f}%)\n")

log.debug(f"Temps d'exécution de tout l'algorithme : {duree_algo:.3f} s\n")

if generer_fichier_log:
    log.stop_file_logging()

