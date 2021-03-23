# -*- coding: utf-8 -*-

"""
Main adapté à l'émetteur de données (ici une Raspberry Pi), entièrement séparé
de l'entité réceptrice (ici un PC).

Code fait en conjonction avec "main_PC_recepteur.py".
"""

DEFAULT_QUANTIZATION_THRESHOLD = 10

import sys
from time import time
import numpy as np

from logger import Logger, LogLevel
from encoder import Encoder
from network_transmission import Client
from bitstream_RPi import BitstreamSender

from test_PiCamera import PiCameraObject


# # # ---------------------------USEFUL DATA---------------------------- # # #


generer_fichier_log = False
affiche_debug = True

log = Logger.get_instance()
log.set_log_level(LogLevel.DEBUG)

if generer_fichier_log:
    log.start_file_logging("log_RPi_émettrice.log")

# Valeurs standards de macroblock_size : 8, 16 et 32 (valeur conseillée : 16)
# Doit être <= 63
macroblock_size = 16

# il faut s'assurer que macroblock_size divise bien img_width et img_height

# "width" doit être un multiple de 32 (sinon ce sera automatiquement "arrondi"
# au multiple de 32 le plus proche par la PiCamera)
img_width = 96

# "height" doit être un multiple de 16 (sinon ce sera automatiquement "arrondi"
# au multiple de 16 le plus proche par la PiCamera)
img_height = 96

if (img_width % macroblock_size != 0 or img_height % macroblock_size != 0) or (img_width % 32 !=0 or img_height % 16 != 0):
    log.error("Dimensions des frames invalides !")
    sys.exit()

# format standard
img_size = (img_width, img_height)

# création de l'opérateur orthogonal de la DCT
A = Encoder.DCT_operator(macroblock_size)

enc = Encoder()


# # # -------------------------SENDING DATA OVER NETWORK-------------------------- # # #


print("\n")
t_debut_demo = time()

bufsize = 4096

HOST = "192.168.8.218" # adresse IP du PC récepteur
PORT = 22 # port SSH

cli = Client(HOST, PORT, bufsize, affiche_messages=False)
cli.connect_to_server()

# on envoie d'abord les dimensions de la vidéo au récepteur (+ la taille des macroblocs)
cli.send_data_to_server(f"SIZE_INFO.{img_width}.{img_height}.{macroblock_size}")


def encode_et_envoie_frame(image_BGR, frame_id):
    if frame_id == 1 and affiche_debug:
        print("")
    
    if affiche_debug:
        log.debug(f"{frame_id}")
        log.debug(f"Encodage - Image BGR n°{frame_id}")
    
    # frame BGR --> frame YUV
    image_yuv = enc.RGB_to_YUV(np.array(image_BGR, dtype=float), mode_RPi=True)
    
    # frame YUV --> frame RLE
    rle_data = enc.decompose_frame_en_macroblocs_via_DCT(image_yuv, img_size, macroblock_size, DEFAULT_QUANTIZATION_THRESHOLD, A)
    
    if affiche_debug:
        log.debug(f"Envoi n°{frame_id} en cours ...")
    
    # frame RLE --> bitstream --> réseau
    bit_sender = BitstreamSender(frame_id, img_size, macroblock_size, rle_data, cli, bufsize)
    bit_sender.send_frame_RLE()
    
    if affiche_debug:
        log.debug(f"Envoi n°{frame_id} réussi")
        log.debug(f"Fin de l'encodage n°{frame_id}")
        print("")


# nombre de FPS de la PiCamera
framerate = 2 # stonks

piCameraObject = PiCameraObject(img_width, img_height, framerate, callback=encode_et_envoie_frame)

# pour tester si la PiCamera fonctionne bien
nb_secondes_preview = 1
piCameraObject.launch_simple_preview(nb_secondes_preview, close_camera=False)

# ==> LANCEMENT DE LA PICAMERA (GÉNÉRATION DE FRAMES)
piCameraObject.start_generating_frames()

# on indique au serveur que l'on a fini d'envoyer les données
cli.send_data_to_server("FIN_ENVOI")

cli.connexion.shutdown(2) # 2 = socket.SHUT_RDWR
cli.connexion.close()

t_fin_demo = time()

duree_demo = t_fin_demo - t_debut_demo
nb_fps_moyen = piCameraObject.compteur_images_generees / duree_demo

print("")
log.debug(f"Durée de la démonstration : {duree_demo:.3f} s")
log.debug(f"Macroblock size : {macroblock_size}x{macroblock_size}")
log.debug(f"Nombre moyen de FPS (émission / encodage) : {nb_fps_moyen:.2f}")

print("")
log.debug("Fin émetteur")

if generer_fichier_log:
    log.stop_file_logging()

