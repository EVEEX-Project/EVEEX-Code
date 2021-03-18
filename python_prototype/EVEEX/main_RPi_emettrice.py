# -*- coding: utf-8 -*-

"""
Main adapté à l'émetteur de données (ici une Raspberry Pi), entièrement séparé
de l'entité réceptrice (ici un PC).

Code fait en conjonction avec "main_PC_recepteur.py".
"""


DEFAULT_QUANTIZATION_THRESHOLD = 10

import numpy as np

from logger import Logger, LogLevel
from encoder import Encoder
from network_transmission import Client
from bitstream_RPi import BitstreamSender

from test_PiCamera import PiCameraObject


# # # ---------------------------USEFUL DATA---------------------------- # # #


generer_fichier_log = False

log = Logger.get_instance()
log.set_log_level(LogLevel.DEBUG)

if generer_fichier_log:
    log.start_file_logging("log_RPi_émettrice.log")

# Valeurs standards de macroblock_size : 8, 16 et 32 (valeur conseillée : 16)
# Doit être <= 63
macroblock_size = 16

# il faut s'assurer que macroblock_size divise bien les 2 dimensions suivantes

# "width" doit être un multiple de 32 (sinon ce sera automatiquement "arrondi"
# au multiple de 32 le plus proche par la PiCamera)
img_width = 96

# "height" doit être un multiple de 16 (sinon ce sera automatiquement "arrondi"
# au multiple de 16 le plus proche par la PiCamera)
img_height = 96

# format standard
img_size = (img_width, img_height)

# création de l'opérateur orthogonal de la DCT
A = Encoder.DCT_operator(macroblock_size)

enc = Encoder()


# # # -------------------------SENDING DATA OVER NETWORK-------------------------- # # #


print("\n")

bufsize = 4096

HOST = "192.168.8.218" # adresse IP du PC récepteur
PORT = 22 # port SSH

cli = Client(HOST, PORT, bufsize, False)
cli.connect_to_server()

affiche_debug = True


def encode_et_envoie_frame(image_BGR, frame_id):
    if frame_id == 1 and affiche_debug:
        print("")
    
    if affiche_debug:
        log.debug(f"{frame_id}")
        log.debug(f"Encodage - Image RGB n°{frame_id}")
    
    # frame RGB --> frame YUV
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

if generer_fichier_log:
    log.stop_file_logging()


log.debug("Fin émetteur")

