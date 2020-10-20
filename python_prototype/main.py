# -*- coding: utf-8 -*-

"""
Script permettant de tester l'encodage et le décodage d'une image par notre 
propre algorithme
"""

from time import sleep
import numpy as np
from random import randint
from encoder import Encoder, DEFAULT_QUANTIZATION_THRESHOLD
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


img_gen = MosaicImageGenerator(size=(10, 10), bloc_size=(4, 4))

image = img_gen.generate()


# # # -------------------------IMAGE ENCODING-------------------------- # # #


img_visu = ImageVisualizer()
enc = Encoder()

# affichage n°1
print("\n\n\nEncodage - Image RGB :\n")
img_visu.show_image_with_matplotlib(image[:, :, 0])

image_yuv = enc.RGB_to_YUV(image)

# affichage n°2
print("\n\n\nEncodage - Image YUV (juste avant DCT) :\n")
img_visu.show_image_with_matplotlib(image_yuv[:, :, 0])

dct_data = enc.apply_DCT(image_yuv)

# affichage n°3
print("\n\n\nEncodage - Image juste après DCT :\n")
img_visu.show_image_with_matplotlib(dct_data[:, :, 0])
print("\n\n\n")

zigzag_data_line = enc.zigzag_linearisation(dct_data)
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
img_size = image.shape[0] * image.shape[1]
macroblock_size = 5 # par exemple

bit_sender = BitstreamSender(frame_id, img_size, macroblock_size, rle_data, cli, bufsize)
bit_sender.send_frame_RLE()

cli.connexion.close()


# # # -------------------------DATA DECODING TO IMAGE-------------------------- # # #


dec = Decoder()

dec_rle_data = dec.decode_bitstream_RLE(received_data)
dec_quantized_data = dec.decode_run_length(dec_rle_data)
dec_dct_data = dec.decode_zigzag(dec_quantized_data)

# affichage n°4
sleep(0.01)
print("\n\n\nDécodage - Données DCT  de l'image :\n")
img_visu.show_image_with_matplotlib(dec_dct_data[:, :, 0])

dec_yuv_data = dec.decode_DCT(dec_dct_data)

# affichage n°5
print("\n\n\nDécodage - Image YUV :\n")
img_visu.show_image_with_matplotlib(dec_yuv_data[:, :, 0])

dec_rgb_data = dec.YUV_to_RGB(dec_yuv_data)

# affichage n°6
print("\n\n\nDécodage - Image RGB :\n")
img_visu.show_image_with_matplotlib(dec_rgb_data[:, :, 0])
print("\n")


"""
NB : Ici, la perte d'informations est exclusivement dûe au passage aux entiers
     (lors de l'application de la RLE) et au seuillage (quantization).
     Cependant, même avec un seuil de 0, la perte d'informations semble
     tout de même assez importante, **même en considérant des entiers négatifs**.
"""


# Preuve que la DCT et la DCT_inverse sont bien cohérentes
test1 = dec.decode_DCT(enc.apply_DCT(image_yuv))
epsilon1 = np.linalg.norm(test1 - image_yuv)
test2 = enc.apply_DCT(dec.decode_DCT(dct_data))
epsilon2 = np.linalg.norm(test2 - dct_data)
print(f"\nTest de précision (DCT & DCT inverse) : {epsilon1}, {epsilon2}\n")
# --> plus les 2 valeurs obtenues ici sont proches de 0, plus ces 2 fonctions
# sont précises --> OK


# # # -------------------------VISUALIZING THE IMAGE-------------------------- # # #


#img_visu = ImageVisualizer()
#img_visu.save_image_to_disk(dec_yuv_image, "decoded_image.png")
#img_visu.show_image_with_matplotlib(dec_yuv_image)

