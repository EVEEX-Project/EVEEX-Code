# -*- coding: utf-8 -*-

import numpy as np
from bitstream import BitstreamGenerator
from iDTT import decode_iDTT

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
    
    
    def decode_run_length(self, rle_data):
        """
        Décode les paires de valeurs issues de la RLE et retourne
        une liste corrspondant aux valeurs quantifiées.
        
        Args:
            rle_data: paires de valeurs issues de la RLE
        
        Returns:
            quantized_data: liste de valeurs quantifiées
        """
        tab = np.array([], dtype=int)
        
        for x in rle_data:
            tab = np.concatenate((tab, np.zeros((x[0],), dtype=int)))
            tab = np.concatenate((tab, np.array([x[1]], dtype=int)))
        
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
        res2 = np.zeros((n, n, 3), dtype=int)
        
        k = 0 # numéro de la couche actuelle (0 <= k <= 2)
        
        # normalement len(split_quantized_data) = 3
        for data in split_quantized_data:
            up = False
            # Position du curseur
            i, j = 0, 0
            # couche qui va être mise à jour
            res = np.zeros((n, n), dtype=int)
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
    
    
    def decode_DCT(self, operateur_DCT, dct_data):
        """
        Decode un tableau de valeurs passées par la transformée discrète en
        cosinus. Il s'agit d'appliquer la DCT inverse.
        
        Source pour la formule **exacte** que l'on utilise ici :
        https://www.chireux.fr/mp/cours/Compression%20JPEG.pdf (page 5/24)
        
        Args:
            operateur_DCT : matrice orthogonale qui sert d'opérateur à la DCT
            dct_data: tableau de valeurs issues de la DCT
        
        Returns:
            yuv_data: tableau de valeurs représentant l'image
        """
        yuv_data = np.zeros(dct_data.shape)
        
        # NB : On aurait très bien pu générer l'opérateur ici via la méthode
        # DCT_operator de Encoder, mais comme cet opérateur est amené à être réutilisé,
        # autant le mettre en argument (pour éviter de le générer plus d'une fois)
        
        for k in range(3):
            yuv_data[:, :, k] = operateur_DCT.T @ dct_data[:, :, k] @ operateur_DCT
        
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
    
    
    def recompose_frame_via_DCT(self, frame_RLE, img_size, macroblock_size, A):
        """
        Recompose une frame YUV à partir des données encodées d'une frame RLE,
        grâce à la DCT classique.
        
        Args:
            frame_RLE: frame entière encodée (liste de listes de tuples RLE)
            img_size: tuple égal à (img_width, img_height)
            macroblock_size: taille (d'un côté) d'un macrobloc
            A: opérateur orthogonal de la DCT, de taille (macroblock_size, macroblock_size)
        
        Returns:
            image_yuv_decodee: tableau représentant l'image YUV décodée, de 
                               taille (img_height, img_width, 3)
        """
        
        # définition des paramètres de l'image
        img_width = img_size[0]
        img_height = img_size[1]
        total_num_of_macroblocks = (img_width * img_height) // macroblock_size**2
        num_macroblocks_per_line = img_width // macroblock_size
        
        image_yuv_decodee = np.zeros((img_height, img_width, 3), dtype=float)
        
        for num_macrobloc in range(total_num_of_macroblocks):
            (i_macrobloc, j_macrobloc) = divmod(num_macrobloc, num_macroblocks_per_line)
            
            i_debut_macrobloc = i_macrobloc * macroblock_size
            i_fin_macrobloc = i_debut_macrobloc + macroblock_size
            
            j_debut_macrobloc = j_macrobloc * macroblock_size
            j_fin_macrobloc = j_debut_macrobloc + macroblock_size
            
            macrobloc = np.copy(frame_RLE[num_macrobloc])
            
            # c'est ici que l'on décode les données du macrobloc
            dec_quantized_data = self.decode_run_length(macrobloc)
            dec_DCT_data = self.decode_zigzag(dec_quantized_data)
            dec_yuv_data = self.decode_DCT(A, dec_DCT_data)
            
            image_yuv_decodee[i_debut_macrobloc : i_fin_macrobloc, j_debut_macrobloc : j_fin_macrobloc, :] = dec_yuv_data
        
        return(image_yuv_decodee)
    
    
    def recompose_frame_via_iDTT(self, frame_RLE, img_size, macroblock_size, P, S):
        """
        Recompose une frame YUV à partir des données encodées d'une frame RLE.
        
        Args:
            frame_RLE: frame entière encodée (liste de listes de tuples RLE)
            img_size: tuple égal à (img_width, img_height)
            macroblock_size: taille (d'un côté) d'un macrobloc
            P et S: matrices contenant les infos de la décomposition de l'opérateur 
                    (de la DCT ou la DTT) en SERMs, de taille (macroblock_size, macroblock_size)
        
        Returns:
            image_yuv_decodee: tableau représentant l'image YUV décodée, de 
                               taille (img_height, img_width, 3)
        """
        
        # définition des paramètres de l'image
        img_width = img_size[0]
        img_height = img_size[1]
        total_num_of_macroblocks = (img_width * img_height) // macroblock_size**2
        num_macroblocks_per_line = img_width // macroblock_size
        
        image_yuv_decodee = np.zeros((img_height, img_width, 3), dtype=int)
        
        for num_macrobloc in range(total_num_of_macroblocks):
            (i_macrobloc, j_macrobloc) = divmod(num_macrobloc, num_macroblocks_per_line)
            
            i_debut_macrobloc = i_macrobloc * macroblock_size
            i_fin_macrobloc = i_debut_macrobloc + macroblock_size
            
            j_debut_macrobloc = j_macrobloc * macroblock_size
            j_fin_macrobloc = j_debut_macrobloc + macroblock_size
            
            macrobloc = np.copy(frame_RLE[num_macrobloc])
            
            # c'est ici que l'on décode les données du macrobloc
            dec_quantized_data = self.decode_run_length(macrobloc)
            dec_iDTT_data = self.decode_zigzag(dec_quantized_data)
            dec_yuv_data = decode_iDTT(P, S, dec_iDTT_data)
            
            image_yuv_decodee[i_debut_macrobloc : i_fin_macrobloc, j_debut_macrobloc : j_fin_macrobloc, :] = dec_yuv_data
        
        return(image_yuv_decodee)

