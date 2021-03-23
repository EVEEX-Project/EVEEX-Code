# -*- coding: utf-8 -*-

"""
Main adapté au récepteur de données (ici un PC), entièrement séparé de l'entité
émettrice (ici une Raspberry Pi).

Code fait en conjonction avec "main_RPi_emettrice.py".
"""

import numpy as np
import cv2

from logger import Logger, LogLevel
from image_visualizer import ImageVisualizer
from network_transmission import Server
from encoder import Encoder
from decoder import Decoder


# # # ---------------------------USEFUL DATA---------------------------- # # #


generer_fichier_log = False
affiche_debug = True

log = Logger.get_instance()
log.set_log_level(LogLevel.DEBUG)

if generer_fichier_log:
    log.start_file_logging("log_PC_récepteur.log")

# Valeurs standards de macroblock_size : 8, 16 et 32
# Doit être <= 63
macroblock_size = 16

# il faut s'assurer d'avoir les bonnes dimensions de l'image, ET que macroblock_size
# divise bien ces 2 dimensions
img_width = 96
img_height = 96

# format standard
img_size = (img_width, img_height)

# création de l'opérateur orthogonal de la DCT
A = Encoder.DCT_operator(macroblock_size)

img_visu = ImageVisualizer()
dec = Decoder()


# # # -------------------RECEIVING DATA OVER NETWORK-------------------- # # #


print("\n")

bufsize = 4096

HOST = "192.168.8.218" # adresse IP du PC récepteur
PORT = 22 # port SSH

serv = Server(HOST, PORT, bufsize, affiche_messages=False)

global received_data
received_data = ""

global compteur_images_recues
compteur_images_recues = 0


def corrige_erreurs(decoded_image):
    # Vérification des valeurs de la frame RGB décodée (on devrait les avoir entre
    # 0 et 255)
    # Les "valeurs illégales", en forte minorité (heureusement), sont ici 
    # principalement dues au passage aux entiers lors de la RLE (à l'encodage)
    for k in range(3):
        for i in range(img_height):
            for j in range(img_width):
                pixel_component = decoded_image[i, j, k]
                
                # On remet 'pixel_component' entre 0 (inclus) et 255 (inclus) si besoin
                
                if pixel_component < 0:
                    decoded_image[i, j, k] = 0
                
                if pixel_component > 255:
                    decoded_image[i, j, k] = 255
    
    decoded_image = np.round(decoded_image).astype(dtype=np.uint8)
    
    # au passage on convertit l'image de BGR à RGB
    return decoded_image[:, :, ::-1]


def decode_frame_entierement():
    global compteur_images_recues
    compteur_images_recues += 1
    
    if affiche_debug:
        print("")
        log.debug(f"{compteur_images_recues}")
        log.debug(f"Début du décodage de la frame n°{compteur_images_recues} ...")
    
    # bitstream (données reçues) --> frame RLE
    global received_data
    dec_rle_data = dec.decode_bitstream_RLE(received_data)
    
    # frame RLE --> frame YUV
    dec_yuv_data = dec.recompose_frame_via_DCT(dec_rle_data, img_size, macroblock_size, A)
    
    # frame YUV --> frame BGR (/!\ ET NON RGB /!\)
    dec_bgr_data = dec.YUV_to_RGB(dec_yuv_data, mode_RPi=True)
    
    # correction des erreurs potentielles (+ conversion BGR --> RGB)
    dec_rgb_data = corrige_erreurs(dec_bgr_data)
    
    if affiche_debug:
        log.debug(f"La frame n°{compteur_images_recues} a bien été décodée")
    
    # affichage de la frame décodée via matplotlib.pyplot (au format RGB)
    img_visu.show_image_with_matplotlib(dec_rgb_data)


def on_received_data(data):
    global received_data
    
    received_data += data
    
    binary_MSG_TYPE = data[16 : 18]
    
    # "11" est en fait la valeur de TAIL_MSG (= 3) en binaire
    if binary_MSG_TYPE == "11":
        decode_frame_entierement()
        received_data = ""


# en fait tout se fait via la fonction de callback
serv.listen_for_packets(callback=on_received_data)

serv.th_Listen.join()
serv.mySocket.close()

cv2.destroyAllWindows()

log.debug("Fin récepteur")

if generer_fichier_log:
    log.stop_file_logging()

