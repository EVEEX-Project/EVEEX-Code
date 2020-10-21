# -*- coding: utf-8 -*-

import numpy as np
from bitstream import BitstreamGenerator

###############################################################################


class Decoder:

    def __init__(self):
        pass
    
    def decode_bitstream_RLE(self, bitstream):
        """
        Permet de décoder un bitstream associé une frame RLE avec seulement 
        les méthodes statiques de la classe Huffman.
        
        Args:
            bitstream (string): bitstream complet associé à une frame RLE
        
        Returns:
            rle_data: paires de données issues de la RLE
        """
        rle_data = BitstreamGenerator.decode_bitstream_RLE(bitstream)
        return rle_data
    
    def decode_run_length(self, rle_data, scale=1):
        """
        Décode les paires de valeurs issues de la RLE et retourne
        une liste corrspondant aux valeurs quantifiées.
        
        Args:
            rle_data: paires de valeurs issues de la RLE
        
        Returns:
            quantized_data: liste de valeurs quantifiées
        """
        tab = np.array([], dtype=float)
        
        for x in rle_data:
            tab = np.concatenate((tab, np.zeros(x[0])))
            tab = np.concatenate((tab, np.array([x[1]], dtype=float)))
        
        return tab
    
    def decode_zigzag(self, quantized_data):
        """
        Decode une liste de valeurs quantifiées en un tableau de valeurs
        en respectant le principe de l'encodage en zig zag.
        
        Args:
            quantized_data: liste de valeurs quantifiées
        
        Returns:
            dct_tab: tableau de valeurs issues de la transformation en cosinus
        """
        # On divise en 3 la suite de valeurs quantifiées pour avoir les 3 couches
        split_quantized_data = np.array_split(quantized_data, 3)
        
        n = int(split_quantized_data[0].size ** (1 / 2))
        
        # tableau de sortie
        res2 = np.zeros((n, n, 3), dtype=float)
        
        k = 0 # numéro de la couche actuelle (0 <= k <= 2)
        
        # normalement len(split_quantized_data) = 3
        for data in split_quantized_data:
            up = False
            # Position du curseur
            i, j = 0, 0
            # couche qui va être mise à jour
            res = np.zeros((n, n), dtype=float)
            # Pour chacun des points qui constituent l'image
            for t in range(data.size):
                # On ajoute le point courant
                if data[t] != 0:
                    res[i, j] = data[t]
                
                # Si on parcoure l'image vers le haut
                if up:
                    if j == (n - 1):
                        i += 1
                        up = False  # On change de direction
                    elif i == 0:
                        j += 1
                        up = False  # On change de direction
                    else:
                        # Sinon on parcoure la diagonale
                        i -= 1
                        j += 1
                # Si on parcoure l'image vers le bas
                else:
                    if i == (n - 1):
                        j += 1
                        up = True  # On change de direction
                    elif j == 0:
                        i += 1
                        up = True  # On change de direction
                    else:
                        # Sinon on parcoure la diagonale
                        j -= 1
                        i += 1
            
            # on veut renvoyer un tableau comprenant les 3 tableaux des couches
            res2[:, :, k] = res
            
            k += 1 # mise à jour du numéro de la couche à mettre à jour
        
        return res2
    
    def decode_DCT(self, dct_data):
        """
        Decode un tableau de valeurs passées par la transformée discrète en
        cosinus. Il s'agit d'appliquer la DCT inverse.
        
        Source pour la formule **exacte** que l'on utilise ici :
        https://www.chireux.fr/mp/cours/Compression%20JPEG.pdf (page 5/24)
        
        Args:
            dct_data: tableau de valeurs issues de la DCT
        
        Returns:
            yuv_data: tableau de valeurs représentant l'image
        """
        yuv_data = np.zeros(dct_data.shape)
        
        def C(w):
            """
            Fonction auxiliaire.
            """
            if w == 0:
                return(1 / np.sqrt(2))
            return(1)
        
        # ici on suppose que height = width (ie image carrée)
        (height, width) = (dct_data.shape[0], dct_data.shape[1])
        
        def compute_yuv_pixel_component(i_ref, j_ref, k):
            """
            Permet de calculer la valeur du pixel au point (i_ref, j_ref) sur le canal k
            """
            res = 0
            for i in range(height):
                for j in range(width):
                    res += C(i) * C(j) * dct_data[i, j, k] * \
                           np.cos((np.pi / height) * i * (i_ref + 1 / 2)) * \
                           np.cos((np.pi / width) * j * (j_ref + 1 / 2))
            return((2 / height) * res)
        
        # on itere sur les 3 canaux, puis sur les pixels de l'image
        for k in range(3):
            for i_ref in range(height):
                for j_ref in range(width):
                    yuv_data[i_ref, j_ref, k] = compute_yuv_pixel_component(i_ref, j_ref, k)
        
        return(yuv_data)
    
    def YUV_to_RGB(self, yuv_data):
        """
        Convertit une image depuis une représentation YUV (Luminance, Chrominance)
        vers une représentation RGB (Rouge, Vert, Bleu)
        
        Args:
            image: tableau de pixels représentant l'image au format YUV
        
        Returns:
            image_rgb: tableau de pixels représentant l'image au format RGB
        """
        rgb_data = np.zeros(yuv_data.shape)
        
        # Pour chaque pixel de l'image
        for i in range(yuv_data.shape[0]):
            for j in range(yuv_data.shape[1]):
                y, u, v = yuv_data[i, j]
                # On recalcule les coefficients RGB
                # Source : https://fr.wikipedia.org/wiki/YUV
                r = y + 1.13983 * v
                g = y - 0.39465 * u - 0.5806 * v
                b = y + 2.03211 * u
                rgb_data[i, j] = [r, g, b]
        
        # On retourne l'image ainsi constituée
        return rgb_data

