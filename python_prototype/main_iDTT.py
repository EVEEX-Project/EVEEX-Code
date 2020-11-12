# -*- coding: utf-8 -*-

"""
Script permettant de tester l'encodage et le décodage d'une image par notre 
propre algorithme.

Ici : version avec la iDTT (integer Discrete Tchebychev Transform), qui est
analogue à la DCT entière.
--> cf. iDTT.py
"""

DEFAULT_QUANTIZATION_THRESHOLD = 10

from iDTT import DTT_operator, generer_decomp, round_matrix
from time import time, sleep
import numpy as np
from random import randint
from encoder import Encoder
from decoder import Decoder
from network_transmission import Server, Client
from bitstream import BitstreamSender
from image_visualizer import ImageVisualizer
from logger import LogLevel, Logger


# # # ----------------------SETTING UP THE LOGGER------------------------ # # #


t_debut_algo = time()

log = Logger.get_instance()
log.set_log_level(LogLevel.DEBUG)
#log.start_file_logging("log_iDTT.log")

print("\n")
log.debug("iDTT (ou iDCT)\n\n")


# # # -------------------------IMAGE GENERATION-------------------------- # # #


"""
On a ici 2 méthodes. Décommenter celle qui a été choisie et commenter l'autre.
"""


"""
Méthode n°1 : Si l'on veut considérer une image pré-existante
"""


from PIL import Image

nom_image = "Sunset.jpg"

# Valeurs standards de macroblock_size : 8, 16 et 32
# Ici, 24 et 48 fonctionnent aussi très bien
# Doit être <= 63 (pour la iDTT, doit être <= 20 sinon le temps de calcul de
# l'opérateur orthogonal de la DTT devient trop élevé)
macroblock_size = 16

# il faut s'assurer d'avoir les bonnes dimensions de l'image, ET que macroblock_size
# divise bien ses 2 dimensions
img_width = 720
img_height = 480

# format standard
img_size = (img_width, img_height)

image = Image.open(nom_image)
image_intermediaire = image.getdata()

image_rgb = np.array(image_intermediaire).reshape((img_height, img_width, 3))


#----------------------------------------------------------------------------#


"""
Méthode n°2 : Si l'on veut générer une image aléatoirement
"""


#from image_generator import MosaicImageGenerator
#
## Valeurs standards de macroblock_size : 8, 16 et 32
## Doit être <= 63 (pour la iDTT, doit être <= 20 sinon le temps de calcul de
## l'opérateur orthogonal de la DTT devient trop élevé)
#macroblock_size = 16
#
#num_macroblocks_per_line = 45
#num_macroblocks_per_column = 30
#
#img_width = num_macroblocks_per_line * macroblock_size
#img_height = num_macroblocks_per_column * macroblock_size
#
## format standard
#img_size = (img_width, img_height)
#
## pour MosaicGenerator
#taille_image = (img_height, img_width)
#
## doit être comprise entre 1 et img_height
#hauteur_blocs_aleatoires = 4
#
## doit être comprise entre 1 et img_width
#epaisseur_blocs_aleatoires = 4
#
#taille_blocs_aleatoires = (hauteur_blocs_aleatoires, epaisseur_blocs_aleatoires)
#
#img_gen = MosaicImageGenerator(size=taille_image, bloc_size=taille_blocs_aleatoires)
#image_rgb = round_matrix(255 * img_gen.generate())


# # # -------------------------IMAGE ENCODING-------------------------- # # #


"""
Pour tester une sorte de "DCT entière" en recyclant la méthode de la iDTT,
remplacer "A = DTT_operator(macroblock_size)" par "A = Encoder.DCT_operator(macroblock_size)"
"""
A = DTT_operator(macroblock_size)
#A = Encoder.DCT_operator(macroblock_size)

# génération de la décomposition de A en SERMs (--> cf. iDTT.py)
(P, S) = generer_decomp(A)


img_visu = ImageVisualizer()
enc = Encoder()


print("\n\nEncodage - Image RGB :\n")
img_visu.show_image_with_matplotlib(image_rgb)
print("\n\n")

# frame RGB --> frame YUV
image_yuv = round_matrix(enc.RGB_to_YUV(image_rgb))

# frame YUV --> frame RLE
rle_data = enc.decompose_frame_en_macroblocs_via_iDTT(image_yuv, img_size, macroblock_size, DEFAULT_QUANTIZATION_THRESHOLD, P, S)


# # # -------------------------SENDING DATA OVER NETWORK-------------------------- # # #


# le bufsize doit impérativement être >= 67 (en pratique : OK)
bufsize = 4096

HOST = 'localhost'
PORT = randint(5000, 15000)

# booléen indiquant si l'on veut afficher les messages entre le client et
# le serveur
affiche_messages = False

# On désactive les messages par défaut si on sait qu'il va y avoir beaucoup de
# données à afficher
if img_width * img_height > 10000:
    affiche_messages = False

serv = Server(HOST, PORT, bufsize, affiche_messages)
cli = Client(serv)

global received_data
received_data = ""

def on_received_data(data):
    global received_data 
    received_data += data

serv.listen_for_packets(cli, callback=on_received_data)

frame_id = randint(0, 65535) # 65535 = 2**16 - 1

# frame RLE --> bitstream
bit_sender = BitstreamSender(frame_id, img_size, macroblock_size, rle_data, cli, bufsize)
bit_sender.send_frame_RLE()


# # # -------------------------DATA DECODING TO IMAGE-------------------------- # # #


dec = Decoder()

# bitstream --> frame RLE
dec_rle_data = dec.decode_bitstream_RLE(received_data)

sleep(0.01)

if not(affiche_messages):
    print("\n")
    log.debug("\nLes messages entre le client et le serveur n'ont ici pas été affichés pour plus de lisibilité.")

print("\n\n")
log.debug(f"\nTransmission réseau réussie : {rle_data == dec_rle_data}\n")

# frame RLE --> frame YUV
dec_yuv_data = dec.recompose_frame_via_iDTT(dec_rle_data, img_size, macroblock_size, P, S)

# frame YUV --> frame RGB
dec_rgb_data = dec.YUV_to_RGB(dec_yuv_data)


# Vérification des valeurs de la frame RGB décodée (on devrait les avoir entre
# 0 et 255)
# Les "valeurs illégales" sont ici en forte minorité (heureusement)
(num_low_values, num_high_values) = (0, 0)
for k in range(3):
    for i in range(img_height):
        for j in range(img_width):
            pixel_component = dec_rgb_data[i, j, k]
            
            # On remet 'pixel_component' entre 0 (inclus) et 255 (inclus) si besoin
            
            if pixel_component < 0:
                dec_rgb_data[i, j, k] = 0
                num_low_values += 1
            
            if pixel_component > 255:
                dec_rgb_data[i, j, k] = 255
                num_high_values += 1


dec_rgb_data = np.round(dec_rgb_data).astype(dtype=np.uint8)

print("\n\nDécodage - Image RGB :\n")
img_visu.show_image_with_matplotlib(dec_rgb_data)

#print("\n\n")
#img_visu.save_image_to_disk(dec_rgb_data, "decoded_image.png")

t_fin_algo = time()
duree_algo = round(t_fin_algo - t_debut_algo, 3)


# # # ----------------------------STATISTICS------------------------------ # # #


taille_originale_en_bits = 8 * 3 * img_width * img_height

taille_donnees_compressees_huffman = bit_sender.taille_donnees_compressees_huffman
taille_dico_encode_huffman = len(bit_sender.dict_huffman_encode)
taille_bitstream_total = len(received_data) # = len(bit_sender.bit_generator.bitstream)

# on considère que le header et le tail font partie des métadonnees du bitstream
taille_metadonnees = taille_bitstream_total - taille_donnees_compressees_huffman - taille_dico_encode_huffman

taux_donnees_huffman = round(100 * taille_donnees_compressees_huffman / taille_originale_en_bits, 2)
taux_dico_huffman = round(100 * taille_dico_encode_huffman / taille_originale_en_bits, 2)
taux_bitstream_total = round(100 * taille_bitstream_total / taille_originale_en_bits, 2)
taux_metadonnees = round(100 * taille_metadonnees / taille_originale_en_bits, 2)

print("\n\n")
log.debug(f"\nTailles relatives par rapport à la taille originale de l'image (en bits) :\n")

log.debug(f"\nDonnées encodées par l'algo de Huffman : {taux_donnees_huffman}%")
log.debug(f"\nDictionnaire de Huffman encodé : {taux_dico_huffman}%")
log.debug(f"\nMétadonnées du bitstream : {taux_metadonnees}%")
log.debug(f"\nBitstream total : {taux_bitstream_total}% --> taux de compression\n")

log.debug(f"\nTemps d'exécution de tout l'algorithme : {duree_algo} s\n")


cli.connexion.close()

