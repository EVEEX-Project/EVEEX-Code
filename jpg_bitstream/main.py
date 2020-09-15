from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from color_utils import *

im = Image.open("source.jpg")

pixels = np.asarray(im)
pixels_ycbcr = np.zeros(pixels.shape, dtype=np.uint8)

"""
for i in range(pixels.shape[0]):
    for j in range(pixels.shape[1]):
        pixels_ycbcr[i, j] = rgb2ycbcr(*pixels[i, j])"""

pixels_ycbcr = np.asarray(im.convert("YCbCr"))
pixels_ycbcr = np.ndarray((im.size[1], im.size[0], 3), 'u1', pixels_ycbcr.tostring())

print(np.min(pixels_ycbcr), np.max(pixels_ycbcr))

#plt.imshow(pixels_ycbcr.astype(np.int64))
plt.imshow(pixels_ycbcr)
plt.show()
plt.imsave("dest.jpg", pixels_ycbcr)

"""
Les étapes : 
1 - prendre l'image JPEG et convertir en YCbCr
2 - appliquer la DCT sur des macroblocs de 8x8
3 - Quantization matrix pour échelonner les valeurs de la DCT
4 - Les blocs sont transformés en chaine de caractère en utilisant un pattern en zig zag
5 - On encode avec Huffman pour l'envoyer sous forme de bitstream
"""