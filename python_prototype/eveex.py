# -*- coding: utf-8 -*-
import sys
import numpy as np
from encoder import Encoder
from decoder import Decoder
from pathlib import Path
from bitstream import BitstreamGenerator, BitstreamSender
from image_generator import ImageGenerator, BlankImageGenerator, MosaicImageGenerator, FromJSONImageGenerator
from image_visualizer import ImageVisualizer

from PIL import Image

operateur_DCT = Encoder.DCT_operator(16)
if len(sys.argv) < 2:
    print("""Voici comment utiliser ce programme:  
          
          Liste des actions: \n 
          
              -e img filename: encoder l'image 'img' à l'emplacement 'filename'
              
              -d filename img: decode le bitstream 'filename' en l'image 'img'
              
              -bi sizeX sizeY filename: create a blank image of size (sizeX x sizeY) in the file 'filename'
              
              -mi sizeX sizeY sizeBloc filename: create a mosaic image of size(sizeX x sizeY) in the file 'filename'
              
              -ji inputFile outputFile: create an image from the config file json 'inputFile' in the file 'outputFile'
              
              
    
              
              """)
    sys.exit(1)

action = sys.argv[1]

if action.lower() == "-e":

    ### Vérifie le nombre d'arguments

    if len(sys.argv) != 4:
        print("Error: not the right number of arguments")
        sys.exit(1)

    ### Vérifie que le fichier existe

    path = Path(sys.argv[2])

    if not path.exists():
        print("Error: file doesn't exist")
        sys.exit(1)

    # -----------Encoder-----------#

    image = Image.open(path)
    img_data = np.asarray(image)
    enc = Encoder()
    bs = BitstreamGenerator(1, len(img_data) * len(img_data[0]), 5)
    operateur_DCT = Encoder.DCT_operator(16)

    # On converti de RGB vers YUV
    image_yuv = enc.RGB_to_YUV(img_data)
    # On applique la DCT
    dct_data = enc.apply_DCT(operateur_DCT, image_yuv)
    # zigzag linearisation
    zigzag_data = enc.zigzag_linearisation(dct_data)
    # On quantiife les données
    quanti = enc.quantization(zigzag_data, threshold=1e2)
    # RLE
    rle = enc.run_level(quanti)
    # RLE to Bitstream ( valeurs aléatoires pour le moment)
    Bitstream = bs.encode_frame_RLE(1, len(img_data) * len(img_data[0]), 10, rle, 55)
    fichier = open(sys.argv[3], "w")
    fichier.write(Bitstream)
    fichier.close()

    print('The operation is succesful')

    sys.exit(1)

elif action.lower() == "-d":

    ### Vérifie le nombre d'arguments

    if len(sys.argv) != 4:
        print("Error: not the right number of arguments")
        sys.exit(1)

    ### Vérifie que le fichier existe

    path = Path(sys.argv[2])
    if not path.exists():
        print("Error: file doesn't exist")
        sys.exit(1)

    received_data = open(path, 'r')
    dec = Decoder()

    dec_rle_data = dec.decode_bitstream_RLE(received_data.read())
    received_data.close()
    dec_quantized_data = dec.decode_run_length(dec_rle_data)
    dec_dct_data = dec.decode_zigzag(dec_quantized_data)

    dec_yuv_data = dec.decode_DCT(operateur_DCT, dec_dct_data)

    dec_rgb_data = dec.YUV_to_RGB(dec_yuv_data)
    visu = ImageVisualizer()
    # On enregistre l'image:
    print(dec_rgb_data)
    for i in range(len(dec_rgb_data)):
        for x in range(len(dec_rgb_data[0])):
            for y in range(len(dec_rgb_data[0][0])):
                dec_rgb_data[i][x][y] = dec_rgb_data[i][x][y] / 255

    visu.save_image_to_disk(dec_rgb_data, sys.argv[3])
    sys.exit(1)

elif action == "-ji":

    ### Vérifie le nombre d'arguments

    if len(sys.argv) != 4:
        print("Error: not the right number of arguments")
        sys.exit(1)

    ### Vérifie que le fichier existe

    path = Path(sys.argv[2])
    if not path.exists():
        print("Error: file doesn't exist")
        sys.exit(1)
    file = sys.argv[2]
    gen = FromJSONImageGenerator(file)
    visu = ImageVisualizer()
    # On enregistre l'image:
    visu.save_image_to_disk(gen.generate(), sys.argv[3])
    sys.exit(1)

elif action == "-mi":
    ### Vérifie le nombre d'arguments
    if len(sys.argv) != 6:
        print("Error: not the right number of arguments")
        sys.exit(1)

    size = (int(sys.argv[2]), int(sys.argv[3]))
    gen = BlankImageGenerator(size, (sys.argv[4], sys.argv[4]))
    visu = ImageVisualizer()
    # On enregistre l'image:
    visu.save_image_to_disk(gen.generate(), sys.argv[5])
    sys.exit(1)

elif action == "-bi":
    ### Vérifie le nombre d'arguments
    if len(sys.argv) != 5:
        print("Error: not the right number of arguments")
        sys.exit(1)
    size = (int(sys.argv[2]), int(sys.argv[3]))
    gen = BlankImageGenerator(size, (1, 1, 1))
    visu = ImageVisualizer()
    # On enregistre l'image:
    visu.save_image_to_disk(gen.generate(), sys.argv[4])
    sys.exit(1)

else:
    print("Error: unknown action")
