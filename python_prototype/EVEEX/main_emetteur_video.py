# -*- coding: utf-8 -*-

"""
Main adapté à l'émetteur de données vidéo. Code fait en conjonction avec
"main_recepteur_video.py".
"""

DEFAULT_QUANTIZATION_THRESHOLD = 10

import sys
from time import time
from os import getcwd
import numpy as np

from video_handler import VideoHandler
from logger import Logger, LogLevel
from encoder import Encoder
from network_transmission import Client
from bitstream_RPi import BitstreamSender


# # # ---------------------------USEFUL DATA---------------------------- # # #


# nom de la vidéo pré-enregistrée à envoyer (dans le dossier "assets")
# --> l'envoi se fera frame par frame
video_name = "video_test.mp4"

generer_fichier_log = False
affiche_debug = True

log = Logger.get_instance()
log.set_log_level(LogLevel.DEBUG)

if generer_fichier_log:
    log.start_file_logging("log_émetteur_vidéo.log")

# Valeurs standards de macroblock_size : 8, 16 et 32 (valeur conseillée : 16)
# Doit être <= 63
macroblock_size = 16

# création de l'opérateur orthogonal de la DCT
A = Encoder.DCT_operator(macroblock_size)

enc = Encoder()

#----------------------------------------------------------------------------#

"""
Transformation de la vidéo considérée en liste de frames
"""

log.debug(f"Conversion \"vidéo {video_name} --> liste de frames\" en cours ...")

OS = sys.platform
if OS == "win32":
    video_path = getcwd() + "\\assets\\" + video_name
elif OS == "linux" or OS == "linux2":
    video_path = getcwd() + "/assets/" + video_name
else:
    Logger.get_instance().error(f"Unrecognized platform : {OS}")
    sys.exit()

frames = VideoHandler.vid2frames(video_path)
nb_frames = len(frames)

# il faut s'assurer que macroblock_size divise bien les 2 dimensions suivantes
img_width, img_height = frames[0].shape[ : 2]

if img_width % macroblock_size != 0 or img_height % macroblock_size != 0:
    log.error("Dimensions de la vidéo invalides !")
    sys.exit()

# format standard
img_size = (img_width, img_height)

log.debug("Conversion finie")


# # # -------------------------SENDING DATA OVER NETWORK-------------------------- # # #


print("\n")

bufsize = 4096

HOST = "localhost"
PORT = 3456

cli = Client(HOST, PORT, bufsize, affiche_messages=False)
cli.connect_to_server()

# on envoie d'abord les dimensions de la vidéo au récepteur
cli.send_data_to_server(f"SIZE_INFO.{img_width}.{img_height}")


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


t_debut_algo = time()

# envoi effectif des frames
for frame_id in range(1, nb_frames + 1):
    frame = frames[frame_id - 1]
    encode_et_envoie_frame(frame, frame_id)

# on indique au serveur que l'on a fini d'envoyer les données
cli.send_data_to_server("FIN_ENVOI")

cli.connexion.shutdown(2) # 2 = socket.SHUT_RDWR
cli.connexion.close()

t_fin_algo = time()

duree_algo = t_fin_algo - t_debut_algo
nb_fps_moyen = nb_frames / duree_algo

print("")
log.debug(f"Durée de l'algorithme : {duree_algo:.3f} s")
log.debug(f"Nombre moyen de FPS (émission / encodage) : {nb_fps_moyen:.2f}")

log.debug("Fin émetteur vidéo")

if generer_fichier_log:
    log.stop_file_logging()

