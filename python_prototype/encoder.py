# -*- coding: utf-8 -*-

import numpy as np
from huffman import Huffman
from logger import Logger

DEFAULT_QUANTIZATION_THRESHOLD = 0.5

###############################################################################


class Encoder:

    def __init__(self, **params):
        pass

    def RGB_to_YUV(self, image):
        """
        Convertit une image depuis une représentation RGB (Rouge, Vert, Bleu)
        vers une représentation YUV (Luminance, Chrominance)
        
        Args:
            image: tableau de pixels représentant l'image
        
        Returns:
            image_yuv: tableau de pixels représentant l'image au format YUV
        """
        image_yuv = np.zeros(image.shape)

        # Pour chaque pixel de l'image
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                r, g, b = image[i, j]
                # On recalcule les coefficients YUV
                # Source : https://fr.wikipedia.org/wiki/YUV
                y = 0.299 * r + 0.587 * g + 0.114 * b
                u = -0.14713 * r - 0.28886 * g + 0.436 * b
                v = 0.615 * r - 0.51498 * g - 0.10001 * b
                image_yuv[i, j] = [y, u, v]

        # On retourne l'image ainsi constituée
        return image_yuv

    def RGB_to_YCbCr(self, image):
        """
        Convertit une image depuis une représentation RGB (Rouge, Vert, Bleu)
        vers une représentation YCbCr (Luminance, Chrominance)
        
        Args:
            image: tableau de pixels représentant l'image
        
        Returns:
            image_ycbcr: tableau de pixels représentant l'image au format YUV
        """
        image_ycbcr = np.zeros(image.shape)

        # Pour chaque pixel de l'image
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                r, g, b = image[i, j]
                # On recalcule les coefficients YCbCr
                # Source : https://fr.wikipedia.org/wiki/YCbCr
                y = 0.299 * r + 0.587 * g + 0.114 * b
                cb = -0.1687 * r - 0.3313 * g + 0.5 * b + 128
                cr = 0.5 * r - 0.4187 * g - 0.0813 * b + 128
                image_ycbcr[i, j] = [y, cb, cr]

        # On retourne l'image ainsi constituée
        return image_ycbcr
    
    def apply_DCT(self, image):
        """
        Applique la transformée en cosinus discrete à une image au format luminance chrominance.
        On veillera bien à implémenter la DCT-II : https://fr.wikipedia.org/wiki/Transform%C3%A9e_en_cosinus_discr%C3%A8te#DCT-II
        
        Source pour la formule **exacte** que l'on utilise ici :
        https://www.chireux.fr/mp/cours/Compression%20JPEG.pdf (page 5/24)
        
        Args:
            image: tableau de pixels représentant l'image au format Luminance/Chrominance
        
        Returns:
            dct_data: tableau de coefficients issu de la transformée en cosinus discrete
        """
        dct_data = np.zeros(image.shape)
        
        def C(w):
            """
            Coefficient permettant de rendre chacune des matrices dct_data[:, :, k]
            orthogonales, avec 0 <= k <= 2. Fonction auxiliaire.
            """
            if w == 0:
                return(1 / np.sqrt(2))
            return(1)
        
        # ici on suppose que height = width (ie image carrée)
        (height, width) = (image.shape[0], image.shape[1])
        
        def compute_energy(i_ref, j_ref, k):
            """
            Permet de calculer l'énerge au point (i_ref, j_ref) sur le canal k
            """
            res = 0
            for i in range(height):
                for j in range(width):
                    res += image[i, j, k] * \
                           np.cos((np.pi / height) * i_ref * (i + 1 / 2)) * \
                           np.cos((np.pi / width) * j_ref * (j + 1 / 2))
            return((2 / height) * C(i_ref) * C(j_ref) * res)
        
        # on itere sur les 3 canaux, puis sur les pixels de l'image
        for k in range(3):
            for i_ref in range(height):
                for j_ref in range(width):
                    dct_data[i_ref, j_ref, k] = compute_energy(i_ref, j_ref, k)
        
        return(dct_data)
    
    def zigzag_linearisation(self, dct_data):
        """
        Parcourt un tableau de coefficients en zig zag de manière à passer d'un
        tableau en deux dimensions à un tableau à une dimension avec par conséquent
        beaucoup de zéros entre les valeurs significatives.
        
        Args:
            dct_data: tableau de coefficients issus de la transformée en cosinus discrete
        
        Returns:
            data: tableau à une dimension des coefficients de l'image
        """
        # Directon
        up = False
        # Position du curseur
        i, j = 0, 0
        # Tableau de sortie
        res = []
        # Pour chacun des points qui constituent l'image
        for t in range(dct_data[:, :, 0].size):
            # On ajoute le point courant
            res.append(dct_data[i, j])
            # Si on parcoure l'image vers le haut
            if up:
                if j == (dct_data.shape[1] - 1):
                    i += 1
                    up = False  # On change de direction
                elif i == 0:
                    j += 1
                    up = False  # On change de direction
                else:
                    # Sinon on parcourt la diagonale
                    i -= 1
                    j += 1
            # Si on parcoure l'image vers le bas
            else:
                if i == (dct_data.shape[0] - 1):
                    j += 1
                    up = True  # On change de direction
                elif j == 0:
                    i += 1
                    up = True  # On change de direction
                else:
                    # Sinon on parcourt la diagonale
                    j -= 1
                    i += 1
        
        # On transforme le tableau à 3 'couches' en un tableau à une dimension
        res2 = []
        for k in range(3):
            for pixel_dct in res:
                res2.append(pixel_dct[k])
        
        return np.array(res2)

    def quantization(self, data, threshold=DEFAULT_QUANTIZATION_THRESHOLD):
        """
        Permet de quantifier les coefficients en passant toutes les valeurs sous un certain seuil
        à 0.
        
        Args:
            data: tableau à une dimension des coefficients de l'image passés par la DCT
            threshold: valeur de seuil à partir de laquelle les valeurs sont mises à zéro
        
        Returns:
            data: tableau modifié 
        """
        quantized_data = np.copy(data)
        
        # Pour chaque élément de la liste
        for i in range(quantized_data.shape[0]):
            # Si la valeur est en dessous du seuil
            if abs(quantized_data[i]) <= threshold:
                # On la met à 0
                quantized_data[i] = 0
        
        return quantized_data
    
    def run_level(self, data):
        """
        Permet de transformer un tableau de coefficients dont les valeurs significatives sont séparées par des
        zéros, à un ensemble de paires décrivants les mêmes données mais de façon plus concise.
        
        Examples:
            (5, 18) : veut dire qu'il y a 5 zéros avant de tomber sur la valeur 18
        
        Args:
            data: tableau quantifié à une dimension des coefficients de l'image
        
        Returns:
            pairs: ensemble de paires décrivants les données de l'image
        """
        n = 0
        pairs = []
        
        # Pour chaque élément de la liste
        for x in data:
            # Dans un premier temps, on considèrera que les 2èmes valeurs
            # des tuples RLE sont des entiers, et non des flottants
            # --> "entier" correspond à l'entier le plus proche de x
            if x > 0:
                entier = int(x + 0.5)
            else:
                entier = int(x - 0.5)
            
            # Si on a entier un non-nul
            if entier != 0:
                # On enregistre le couple
                pairs.append((n, entier))
                n = 0
            else:
                # Sinon, on compte les zéros
                n += 1
        
        # Si la chaîne se termine par 00000 (cinq zéros) on enregistre (4,0)
        if n != 0:
            pairs.append((n - 1, 0))
        
        return pairs
    
    def huffman_encode(self, pairs):
        """
        Encode par l'algorithme de Huffman les donnéees. Attribue un identifiant en binaire à chaque symbole
        de sorte que les symboles récurrents soient exprimés avec le minimum de bits possibles.
        
        Args:
            pairs: paires décrivant les données de l'image
        
        Returns:
            bitstream: le bitstream compressé correspondant à l'image
        """
        huff_enc = Huffman(pairs)
        # TODO : Construire le bitstream (structure, données)

        return huff_enc.encode_phrase(), huff_enc.symbols


if __name__ == '__main__':
    from PIL import Image
    from image_visualizer import ImageVisualizer

    image = Image.open("test_img.png")
    img_data = np.asarray(image)
    enc = Encoder()
    visu = ImageVisualizer()

    # On converti de RGB vers YUV
    yuv_data = enc.RGB_to_YUV(img_data)
    # On affiche la luminance
    visu.show_image_with_matplotlib(yuv_data[:, :, 0])
    # On applique la DCT
    dct_data = enc.apply_DCT(yuv_data)
    # On affiche la carte d'énergie
    visu.show_image_with_matplotlib(dct_data[:, :, 0])
    # zigzag linearisation
    zigzag_data = enc.zigzag_linearisation(dct_data)
    # On quantiife les données
    quanti = enc.quantization(zigzag_data, threshold=1e2)
    # On affiche le résultat de la quantification de la luminance
    visu.show_image_with_matplotlib(np.reshape(quanti[:100], (img_data.shape[0], img_data.shape[1])))
    # RLE
    rle = enc.run_level(quanti)
    Logger.get_instance().debug("RLE\n" + str(rle))
    # Encodage avec huffman
    huff_enc = enc.huffman_encode(rle)
    Logger.get_instance().debug("Huffman\n" + str(huff_enc))

    originale = 3 * 8 * img_data.shape[0] * img_data.shape[1]
    compressee = len(huff_enc[0])
    Logger.get_instance().debug("Taille originale en bits : " + str(originale))
    Logger.get_instance().debug("Taille compressée : " + str(compressee))
    Logger.get_instance().debug(f"Taux de compression : {round(compressee / originale * 100, 2)}%")

