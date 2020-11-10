# -*- coding: utf-8 -*-
import sys
import numpy as np
from encoder import Encoder
from iDTT import DTT_operator, generer_decomp, round_matrix
from decoder import Decoder
from pathlib import Path
from bitstream import BitstreamGenerator, BitstreamSender
from image_generator import ImageGenerator, BlankImageGenerator, MosaicImageGenerator, FromJSONImageGenerator
from image_visualizer import ImageVisualizer

from PIL import Image
DEFAULT_QUANTIZATION_THRESHOLD = 10

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

    nom_image = path

    # Valeurs standards de macroblock_size : 8, 16 et 32
    # Ici, 24 et 48 fonctionnent aussi très bien
    # Doit être <= 63
    macroblock_size = 16

    # il faut s'assurer d'avoir les bonnes dimensions de l'image, ET que macroblock_size
    # divise bien ses 2 dimensions
    img_width = 720
    img_height = 480

    # format standard
    img_size = (img_width, img_height)

    image = Image.open(nom_image)
    image_intermediaire = image.getdata()

    image_rgb = np.array(image_intermediaire).reshape((img_height, img_width, 3))

    frame_id = 0  # 65535 = 2**16 - 1

    # le bufsize doit impérativement être >= 67 (en pratique : OK)
    bufsize = 4096

    # création de l'opérateur orthogonal de la DCT
    A = Encoder.DCT_operator(macroblock_size)

    enc = Encoder()

    # frame RGB --> frame YUV
    image_yuv = enc.RGB_to_YUV(image_rgb)

    # frame YUV --> frame RLE
    rle_data = enc.decompose_frame_en_macroblocs_via_DCT(image_yuv, img_size, macroblock_size, DEFAULT_QUANTIZATION_THRESHOLD, A)

    # frame RLE --> bitstream
    bitstream_genere = BitstreamGenerator.encode_frame_RLE(frame_id, img_size, macroblock_size, rle_data, bufsize)


    fichier = open(sys.argv[3], "w")
    fichier.write(bitstream_genere)
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

    img_visu = ImageVisualizer()
    dec = Decoder()
    macroblock_size = 16
    # bitstream --> frame RLE
    dec_rle_data = dec.decode_bitstream_RLE(received_data.read())
    A = DTT_operator(macroblock_size)
    (P, S) = generer_decomp(A)
    # frame RLE --> frame YUV
    img_width, img_height = (720,480)
    dec_yuv_data = dec.recompose_frame_via_iDTT(dec_rle_data, (720,480), macroblock_size, P, S)

    # frame YUV --> frame RGB
    dec_rgb_data = dec.YUV_to_RGB(dec_yuv_data)

    # Vérification des valeurs de la frame RGB décodée (on devrait les avoir entre
    # 0 et 255)
    # Les "valeurs illégales" sont ici en forte minorité (heureusement)
    (num_low_values, num_high_values) = (0, 0)
    for k in range(3):
        for i in range(img_height):
            for j in range(img_width):
                pixel_component = dec_rgb_data[i, j, k]

                # On remet 'pixel_component' entre 0 (inclus) et 255 (inclus) si besoin

                if pixel_component < 0:
                    dec_rgb_data[i, j, k] = 0
                    num_low_values += 1

                if pixel_component > 255:
                    dec_rgb_data[i, j, k] = 255
                    num_high_values += 1

    dec_rgb_data = np.round(dec_rgb_data).astype(dtype=np.uint8)

    img_visu = ImageVisualizer()
    # On enregistre l'image:

    img_visu.save_image_to_disk(dec_rgb_data, sys.argv[3])
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
