# -*- coding: utf-8 -*-
import sys
import numpy as np
from encoder import Encoder
from pathlib import Path
from bitstream import BitstreamGenerator

from PIL import Image

if len(sys.argv) < 2:
    print("""Voici comment utiliser ce programme:  
          
          Liste des actions: \n 
          
              -e img filename: encoder l'image 'img' à l'emplacement 'filename'
              
              -d filename img: decode le bitstream 'filename' en l'image 'img'
              
              -bi sizeX sizeY filename: create a blank image of size (sizeX x sizeY) in the file 'filename'
              
              -mi sizeX sizeY filename: create a mosaic image of size(sizeX x sizeY) in the file 'filename'
              
              -ji inputFile outputFile: create an image from the config file json 'inputFile' in the file 'outputFile'
              
              
    
              
              """)
    sys.exit(1)
    


action = sys.argv[1]


if action.lower() == "-e":
    
    ### Vérifie le nombre d'arguments
    
    if len(sys.argv)!= 4:
        print("Error: not the right number of arguments")
        sys.exit(1)
    
    ### Vérifie que le fichier existe
    
    path =Path(sys.argv[2])

    if not path.exists():
        print("Error: file doesn't exist")
        sys.exit(1)
        
        
    #-----------Encoder-----------#

    image = Image.open("test_img.png")
    img_data = np.asarray(image)
    enc = Encoder()
    bs=BitstreamGenerator(1, len(img_data)*len(img_data[0]),5)

    # On converti de RGB vers YUV
    yuv_data = enc.RGB_to_YUV(img_data)
    # On applique la DCT
    dct_data = enc.apply_DCT(yuv_data)
    # zigzag linearisation de la luminance
    zigzag_data = enc.zigzag_linearisation(dct_data[:, :, 0])
    # On quantiife les données
    quanti = enc.quantization(zigzag_data, threshold=1e2)
    # RLE
    rle = enc.run_level(quanti)
    #RLE to Bitstream ( valeurs aléatoires pour le moment)
    Bitstream=bs.encode_frame_RLE(1, len(img_data)*len(img_data[0]), 10, rle, 55)
    fichier = open(sys.argv[3],"w")
    fichier.write(Bitstream)
    fichier.close()
    
    print('The operation is succesful')
    
    sys.exit(1)
    
elif action.lower() == "-d":
    
    ### Vérifie le nombre d'arguments
    
    if len(sys.argv)!= 4:
        print("Error: not the right number of arguments")
        sys.exit(1)
    
    ### Vérifie que le fichier existe
    
    path =Path(sys.argv[2])
    if not path.exists():
        print("Error: file doesn't exist")
        sys.exit(1)
    
    print("decode")
    sys.exit(1)
    
elif action =="-ji":
    
    ### Vérifie le nombre d'arguments
    
    if len(sys.argv)!= 4:
        print("Error: not the right number of arguments")
        sys.exit(1)
    
    ### Vérifie que le fichier existe
    
    path = Path(sys.argv[2])
    if not path.exists():
        print("Error: file doesn't exist")
        sys.exit(1)
    
    print("ji")
    sys.exit(1)
    
elif action == "-mi":
    ### Vérifie le nombre d'arguments
    if len(sys.argv)!= 5:
        print("Error: not the right number of arguments")
        sys.exit(1)
        
    print('mi')
    sys.exit(1)
    
elif action == "-bi":
    ### Vérifie le nombre d'arguments
    if len(sys.argv)!= 5:
        print("Error: not the right number of arguments")
        sys.exit(1)
        
    print('-bi')
    sys.exit(1)
    
else :
    print("Error: unknown action")