# -*- coding: utf-8 -*-

"""
Script permettant de tester l'encodage et le décodage d'une image par notre 
propre algorithme.

Ici : version avec la iDTT (integer Discrete Tchebychev Transform), qui est
analogue à la DCT entière.
--> cf. iDTT.py
"""

from iDTT import DTT_operator, generer_decomp, apply_iDTT, decode_iDTT, round_matrix

"""
Si DEFAULT_QUANTIZATION_THRESHOLD = 0, il n'y a pas de perte entre l'image YUV 
(arrondie) de départ et l'image YUV décodée (cela n'est pas vrai pour l'image RGB, 
car au début on a dû arrondir la matrice YUV après conversion de RGB à YUV).

DEFAULT_QUANTIZATION_THRESHOLD doit être un entier >= 0 du coup.
"""
DEFAULT_QUANTIZATION_THRESHOLD = 1


from time import sleep
import numpy as np
from random import randint
from encoder import Encoder
from decoder import Decoder
from network_transmission import Server, Client
from bitstream import BitstreamSender
from image_generator import MosaicImageGenerator
from image_visualizer import ImageVisualizer
from logger import LogLevel, Logger

# # # ----------------------SETTING UP THE LOGGER------------------------ # # #


log = Logger.get_instance()
log.set_log_level(LogLevel.DEBUG)


# # # -------------------------IMAGE GENERATION-------------------------- # # #

# ATTENTION : N est typiquement de la taille d'un macrobloc, donc idéalement
# il faudrait que N ne soit pas trop élevé (N <= 10 par exemple)
# Les erreurs sur les flottants deviennent soudainement monstrueueses entre
# N = 12 et N = 13 (erreurs cumulées sur les flottants ?)
N = 8

img_gen = MosaicImageGenerator(size=(N, N), bloc_size=(4, 4))

image_rgb = 255 * img_gen.generate()

A = DTT_operator(N)

# S : matrice contenant l'information des SERMs (--> cf. iDTT.py)
(P, S) = generer_decomp(A)


# # # -------------------------IMAGE ENCODING-------------------------- # # #


img_visu = ImageVisualizer()
enc = Encoder()

# affichage n°1
print("\n\n\nEncodage - Image RGB :\n")
img_visu.show_image_with_matplotlib(image_rgb[:, :, 0])

image_yuv = round_matrix(enc.RGB_to_YUV(image_rgb))

# affichage n°2
print(f"\n\n\nEncodage - Image YUV (juste avant iDTT) :\n")
img_visu.show_image_with_matplotlib(image_yuv[:, :, 0])

iDTT_data = apply_iDTT(P, S, image_yuv)

# affichage n°3
print(f"\n\n\nEncodage - Image juste après iDTT :\n")
img_visu.show_image_with_matplotlib(iDTT_data[:, :, 0])
print("\n\n\n")

zigzag_data_line = enc.zigzag_linearisation(iDTT_data)
quantized_data = enc.quantization(zigzag_data_line, threshold=DEFAULT_QUANTIZATION_THRESHOLD)
rle_data = enc.run_level(quantized_data)
#compressed_data = enc.huffman_encode(rle_data)


# # # -------------------------SENDING DATA OVER NETWORK-------------------------- # # #


puiss_2_random = randint(10, 12)
bufsize = 2 ** puiss_2_random # doit impérativement être >= 51 (en pratique : OK)

HOST = 'localhost'
PORT = randint(5000, 15000)

serv = Server(HOST, PORT, bufsize)
cli = Client(serv)

global received_data
received_data = ""

def on_received_data(data):
    global received_data 
    received_data += data

serv.listen_for_packets(cli, callback=on_received_data)

frame_id = randint(0, 65535)
img_size = image_rgb.shape[0] * image_rgb.shape[1]
macroblock_size = 5 # par exemple

bit_sender = BitstreamSender(frame_id, img_size, macroblock_size, rle_data, cli, bufsize)
bit_sender.send_frame_RLE()

cli.connexion.close()


# # # -------------------------DATA DECODING TO IMAGE-------------------------- # # #


dec = Decoder()

dec_rle_data = dec.decode_bitstream_RLE(received_data)
dec_quantized_data = dec.decode_run_length(dec_rle_data)
dec_iDTT_data = dec.decode_zigzag(dec_quantized_data)

# affichage n°4
sleep(0.01)
print(f"\n\nTransmission réseau réussie : {rle_data == dec_rle_data}\n\n")
print(f"\n\n\nDécodage - Données iDTT de l'image :\n")
img_visu.show_image_with_matplotlib(dec_iDTT_data[:, :, 0])

dec_yuv_data = decode_iDTT(P, S, dec_iDTT_data)

# affichage n°5
print("\n\n\nDécodage - Image YUV :\n")
img_visu.show_image_with_matplotlib(dec_yuv_data[:, :, 0])

dec_rgb_data = dec.YUV_to_RGB(dec_yuv_data)

# affichage n°6
print("\n\n\nDécodage - Image RGB :\n")
img_visu.show_image_with_matplotlib(dec_rgb_data[:, :, 0])


# Preuve que la iDTT et la iDTT inverse sont bien cohérentes
test1 = decode_iDTT(P, S, apply_iDTT(P, S, image_yuv))
epsilon1 = np.linalg.norm(test1 - image_yuv)
test2 = apply_iDTT(P, S, decode_iDTT(P, S, iDTT_data))
epsilon2 = np.linalg.norm(test2 - iDTT_data)
print(f"\n\n\nTest de précision (iDTT & iDTT inverse) : {epsilon1}, {epsilon2}\n")
# --> plus les 2 valeurs obtenues ici sont proches de 0, plus ces 2 fonctions
# sont précises --> OK


# # # -------------------------VISUALIZING THE IMAGE-------------------------- # # #


#img_visu = ImageVisualizer()
#img_visu.save_image_to_disk(dec_yuv_image, "decoded_image.png")
#img_visu.show_image_with_matplotlib(dec_yuv_image)

