# -*- coding: utf-8 -*-

import sys
from os import getcwd
import cv2

from logger import Logger

###############################################################################


class VideoHandler:
    """
    Classe permettant de gérer les conversions entre liste de frames et vidéo mp4
    (et vice-versa).
    """
    def __init__(self):
        pass
    
    
    @staticmethod
    def vid2frames(video):
        """
        Convertit une vidéo (pré-enregistrée) en une liste d'arrays au format BGR.
        """
        
        vidcap = cv2.VideoCapture(video)
        success, image = vidcap.read()
        sortie = []
        
        while success:
            sortie.append(image)
            success, image = vidcap.read()
        
        return sortie
    
    
    @staticmethod
    def frames2vid(frames, saved_video_filename):
        """
        Convertit une liste de frames au format BGR en une vidéo au format mp4.
        """
        
        height, width, channels = frames[0].shape
        frame_size = (width, height)
        nb_fps = 30
        
        out = cv2.VideoWriter(saved_video_filename, cv2.VideoWriter_fourcc(*"mp4v"), nb_fps, frame_size)
        
        for i in range(len(frames)):
            out.write(frames[i])
        
        out.release()


###############################################################################


if __name__ == "__main__":
    # saved video --> list of frames
    
    video_name = "video_test.mp4"
    
    OS = sys.platform
    if OS == "win32":
        video_path = getcwd() + "\\assets\\" + video_name
    elif OS == "linux" or OS == "linux2":
        video_path = getcwd() + "/assets/" + video_name
    else:
        Logger.get_instance().error(f"Unrecognized platform : {OS}")
        sys.exit()
    
    frames = VideoHandler.vid2frames(video_path)
    
    #------------------------------------------------------------------------#
    
    # list of frames --> (new) saved video
    
    saved_video_filename = "test2.mp4"
    VideoHandler.frames2vid(frames, saved_video_filename)

