# -*- coding: utf-8 -*-

"""
Script permettant d'extraire chacune des frames d'un flux vidéo provenant d'une
PiCamera, et de les convertir en arrays Numpy.
"""

from io import BytesIO
from picamera import PiCamera
import numpy as np
import cv2
from time import sleep

from logger import Logger

##############################################################################


class PiCameraObject:
    """
    Classe permettant d'effectuer des fonctionnalités de base avec une PiCamera.
    """
    def __init__(self, img_width, img_height, framerate, callback):
        self.img_width = img_width
        self.img_height = img_height
        
        self.resolution = (self.img_width, self.img_height)
        
        self.framerate = framerate
        
        # formatage initial de la PiCamera
        self.camera = PiCamera()
        self.camera.resolution = self.resolution
        self.camera.framerate = self.framerate
        
        # buffer/stream contenant les données d'une frame
        self.stream = BytesIO()
        
        self.frame = None
        self.array_image_a_envoyer = None # /!\ array au format BGR, et non RGB /!\
        
        self.compteur_images_generees = None
        self.callback = callback
    
    
    def launch_simple_preview(self, nb_secondes_preview, close_camera=True):
        """
        Permet simplement de faire une preview de "nb_secondes_preview" secondes.
        """
        
        self.camera.start_preview()
        sleep(nb_secondes_preview)
        self.camera.stop_preview()
        
        if close_camera:
            self.camera.close()
    
    
    def start_generating_frames(self, display_frames_on_RPi=True):
        """
        Méthode permettant de convertir chaque frame d'un flux vidéo provenant
        d'une PiCamera en arrays Numpy (au format BGR).
        """
        
        if display_frames_on_RPi:
            window_name = "Test RPi emettrice (appuyez sur la touche \"q\" pour quitter)"
            cv2.namedWindow(window_name)
            nb_millisecondes_attente = 1 # doit être > 0
        
        self.compteur_images_generees = 0
        
        while True:
            # "remise à zéro" du buffer
            self.stream.seek(0)
            self.stream.truncate(0)
            
            # récupération du flux vidéo associé à la frame actuelle
            self.camera.capture(self.stream, format="jpeg", use_video_port=True)
            
            # conversion du flux en array Numpy tridimensionnel (au format BGR)
            self.frame = cv2.imdecode(np.frombuffer(self.stream.getvalue(), dtype=np.uint8), cv2.IMREAD_COLOR)
            
            # envoi de la frame au PC récepteur (cela dépend de la fonction de
            # callback utilisée)
            self.callback(self.frame, self.compteur_images_generees + 1)
            
            self.compteur_images_generees += 1
            
            if display_frames_on_RPi:
                # /!\ la fonction "cv2.imshow" affiche les images au format BGR, et non RGB /!\
                cv2.imshow(window_name, self.frame)
                
                pressed_key = cv2.waitKey(nb_millisecondes_attente)
                
                # on arrête le flux vidéo si on appuie sur la touche "q" du clavier
                if pressed_key == ord("q"):
                    self.camera.close()
                    Logger.get_instance().debug("La PiCamera a bien été arrêtée")
                    break
        
        if display_frames_on_RPi:
            cv2.destroyAllWindows()


##############################################################################


if __name__ == "__main__":
    # "width" doit être un multiple de 32 (sinon ce sera automatiquement "arrondi"
    # au multiple de 32 le plus proche par la PiCamera)
    img_width = 720
    
    # "height" doit être un multiple de 16 (sinon ce sera automatiquement "arrondi"
    # au multiple de 16 le plus proche par la PiCamera)
    img_height = 480
    
    # nombre de FPS
    framerate = 24
    
    # pour cet exemple-ci (ie une démo simple) la fonction de callback ne fera rien
    def do_nothing(image_BGR, frame_id):
        pass
    
    piCameraObject = PiCameraObject(img_width, img_height, framerate, callback=do_nothing)
    
    #------------------------------------------------------------------------#
    
    # pour tester si la PiCamera fonctionne bien
    nb_secondes_preview = 1
    piCameraObject.launch_simple_preview(nb_secondes_preview, close_camera=False)
    
    piCameraObject.start_generating_frames()

