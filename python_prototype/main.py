# -*- coding: utf-8 -*-

"""
Script permettant de tester l'encodage et le décodage d'une image par notre 
propre algorithme
"""

from time import sleep
from random import randint
from numpy.linalg  import norm
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
#log.start_file_logging("log.log")


# # # -------------------------IMAGE GENERATION-------------------------- # # #


N = 16
img_gen = MosaicImageGenerator(size=(N, N), bloc_size=(4, 4))

image = img_gen.generate()

operateur_DCT = Encoder.DCT_operator(N)

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

dct_data = enc.apply_DCT(operateur_DCT, image_yuv)

# affichage n°3
print("\n\n\nEncodage - Image juste après DCT :\n")
img_visu.show_image_with_matplotlib(dct_data[:, :, 0])
print("\n\n\n")

zigzag_data_line = enc.zigzag_linearisation(dct_data)
quantized_data = enc.quantization(zigzag_data_line, threshold=DEFAULT_QUANTIZATION_THRESHOLD)
rle_data = enc.run_level(quantized_data)
compressed_data = enc.huffman_encode(rle_data)


# # # -------------------------SENDING DATA OVER NETWORK-------------------------- # # #


# le bufsize doit impérativement être >= 51 (en pratique : OK)
bufsize = 4096 

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

frame_id = randint(0, 65535) # 65535 = 2**16 -1
img_size = N**2
macroblock_size = 4 # par exemple

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
print("\n\n\n")
log.debug(f"\nTransmission réseau réussie (ie rle_data == decoded_rle_data) : {rle_data == dec_rle_data}\n\n")
print("\n\n\nDécodage - Données DCT  de l'image :\n")
img_visu.show_image_with_matplotlib(dec_dct_data[:, :, 0])

dec_yuv_data = dec.decode_DCT(operateur_DCT, dec_dct_data)

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
     tout de même assez importante, ce qui démontre de l'impact "violent" du
     passage aux entiers lors de l'encodage.
"""


# Preuve que la DCT et la DCT_inverse sont bien cohérentes
test1 = dec.decode_DCT(operateur_DCT, enc.apply_DCT(operateur_DCT, image_yuv))
epsilon1 = norm(test1 - image_yuv)
test2 = enc.apply_DCT(operateur_DCT, dec.decode_DCT(operateur_DCT, dct_data))
epsilon2 = norm(test2 - dct_data)
print("\n")
log.debug(f"\nTest de précision (DCT & DCT inverse) : {epsilon1:.2e}, {epsilon2:.2e}")
# Plus les 2 valeurs obtenues ici sont proches de 0, plus ces 2 fonctions sont
# précises --> OK


# Stats :

taille_originale_en_bits = 8 * 3 * img_size # = 24 * N**2

taille_donnees_compressees_huffman = len(compressed_data[0])
taille_body_bitstream = len(bit_sender.bit_generator.body)
taille_dico_encode_huffman = len(compressed_data[2])
taille_dico_bitstream = len(bit_sender.bit_generator.dict)
taille_bitstream_total = len(received_data) # = len(bit_sender.bit_generator.bitstream)

taux_donnees_huffman = round(100 * taille_donnees_compressees_huffman / taille_originale_en_bits, 2)
taux_body_bitstream = round(100 * taille_body_bitstream / taille_originale_en_bits, 2)
taux_dico_huffman = round(100 * taille_dico_encode_huffman / taille_originale_en_bits, 2)
taux_dico_bitstream = round(100 * taille_dico_bitstream / taille_originale_en_bits, 2)
taux_bitstream_total = round(100 * taille_bitstream_total / taille_originale_en_bits, 2)

print("\n\n")
log.debug(f"Quelques taux de compression (pour un bufsize de {bufsize}) :\n")

log.debug(f"Données encodées par l'algo de Huffman : {taux_donnees_huffman}%")
log.debug(f"Bitstream associé aux données encodées par l'algo de Huffman : {taux_body_bitstream}%\n")
log.debug(f"Dictionnaire de Huffman encodé : {taux_dico_huffman}%")
log.debug(f"Bitstream associé au dictionnaire de Huffman encodé : {taux_dico_bitstream}%\n")
log.debug(f"Bitstream total : {taux_bitstream_total}%\n")


# # # -------------------------VISUALIZING THE IMAGE-------------------------- # # #


#img_visu = ImageVisualizer()
#img_visu.save_image_to_disk(dec_yuv_image, "decoded_image.png")
#img_visu.show_image_with_matplotlib(dec_yuv_image)

