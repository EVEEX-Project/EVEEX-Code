# -*- coding: utf-8 -*-

"""
Main adapté à la réception de données vidéo. Code fait en conjonction avec
"main_emetteur_video.py".
"""

from time import time
import numpy as np

from video_handler import VideoHandler
from logger import Logger, LogLevel
from network_transmission import Server
from encoder import Encoder
from decoder import Decoder


# # # ---------------------------USEFUL DATA---------------------------- # # #


generer_fichier_log = False
enregistrer_frames_recues = False
affiche_debug = True

log = Logger.get_instance()
log.set_log_level(LogLevel.DEBUG)

if generer_fichier_log:
    log.start_file_logging("log_récepteur_vidéo.log")

# Valeurs standards de macroblock_size : 8, 16 et 32
# Doit être <= 63
macroblock_size = 16

# il faut s'assurer que macroblock_size divise bien ces 2 dimensions
global img_width
global img_height

global img_size

# création de l'opérateur orthogonal de la DCT
A = Encoder.DCT_operator(macroblock_size)

dec = Decoder()

global frames_recues
frames_recues = []


# # # -------------------RECEIVING DATA OVER NETWORK-------------------- # # #


print("\n")

bufsize = 4096

HOST = "localhost"
PORT = 3456

serv = Server(HOST, PORT, bufsize, affiche_messages=False)

global received_data
received_data = ""

global compteur_images_recues
compteur_images_recues = 0

global t_debut_algo


def corrige_erreurs(decoded_image):
    global img_width
    global img_height
    
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
    
    return decoded_image


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
    global img_size
    dec_yuv_data = dec.recompose_frame_via_DCT(dec_rle_data, img_size, macroblock_size, A)
    
    # frame YUV --> frame BGR (/!\ ET NON RGB /!\)
    dec_bgr_data = dec.YUV_to_RGB(dec_yuv_data, mode_RPi=True)
    
    # correction des erreurs potentielles
    dec_bgr_data = corrige_erreurs(dec_bgr_data)
    
    if affiche_debug:
        log.debug(f"La frame n°{compteur_images_recues} a bien été décodée")
    
    global frames_recues
    frames_recues.append(dec_bgr_data)


def on_received_data(data):
    if data[0] == "S":
        global img_width
        global img_height
        global img_size
        global t_debut_algo
        
        t_debut_algo = time()
        
        splitted_data = data.split(".")
        # splitted_data[0] = "SIZE_INFO"
        img_width = int(splitted_data[1])
        img_height = int(splitted_data[2])
        
        # format standard
        img_size = (img_width, img_height)
        
        log.debug(f"Taille reçue : {img_size}")
        print("")
    
    else:
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

t_fin_algo = time()

duree_algo = t_fin_algo - t_debut_algo
nb_fps_moyen = compteur_images_recues / duree_algo

print("\n")
log.debug(f"Durée de l'algorithme : {duree_algo:.3f} s")
log.debug(f"Nombre moyen de FPS (réception / décodage) : {nb_fps_moyen:.2f}")

if enregistrer_frames_recues:
    log.info("Enregistrement de la vidéo en cours ...")
    saved_video_filename = "test2.mp4"
    VideoHandler.frames2vid(frames_recues, saved_video_filename)
    log.info("Enregistrement terminé !")

log.debug("Fin récepteur vidéo")

if generer_fichier_log:
    log.stop_file_logging()

