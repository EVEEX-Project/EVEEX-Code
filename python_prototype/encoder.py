# -*- coding: utf-8 -*-

import numpy as np
from huffman import Huffman

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
    
    @staticmethod
    def DCT_operator(N):
        """
        Génère l'opérateur orthogonal (orthogonal <==> sa transposée = son inverse) 
        de la DCT.
        
        Source pour la formule **exacte** que l'on utilise ici :
        https://www.chireux.fr/mp/cours/Compression%20JPEG.pdf (page 5/24)
        
        En fait, la formule donnée sur ce site pour les termes du tableau (2D)
        encodé définit les coefficients d'une matrice égale à un certain 
        produit "A @ tableau_a_encoder @ A.T", et on définit ici cette matrice A.
        
        De même, la formule donnée pour les termes du tableau (2D) décodé
        définit les coefficients d'une matrice égale à "A.T @ tableau_a_decoder @ A",
        où A est l'opérateur qui a été utilisé pour l'encodage.
        
        Args:
            N: Taille d'un côté de l'image / du macrobloc
        
        Returns:
            A: l'opérateur de la DCT (matrice NxN)
        """
        A = np.zeros((N, N))
        
        # coefficient permettant de rendre l'opérateur de la DCT orthogonal 
        def C(i, N):
            if i == 0:
                return(1 / np.sqrt(N))
            return(np.sqrt(2 / N))
        
        # remplissage de la matrice
        for i in range(N):
            for j in range(N):
                A[i, j] = C(i, N) * np.cos((np.pi / N) * i * (j + 1 / 2))
        
        return(A)
    
    def apply_DCT(self, operateur_DCT, image):
        """
        Applique la transformée en cosinus discrete à une image au format luminance chrominance.
        On veillera bien à implémenter la DCT-II : https://fr.wikipedia.org/wiki/Transform%C3%A9e_en_cosinus_discr%C3%A8te#DCT-II
        
        Args:
            operateur_DCT : matrice orthogonale qui sert d'opérateur à la DCT
            image: tableau de pixels représentant l'image au format Luminance/Chrominance
        
        Returns:
            dct_data: tableau de coefficients issu de la transformée en cosinus discrete
        """
        dct_data = np.zeros(image.shape)
        
        # NB : On aurait très bien pu générer l'opérateur ici via la méthode
        # DCT_operator, mais comme cet opérateur est amené à être réutilisé,
        # autant le mettre en argument (pour éviter de le générer plus d'une fois)
        
        for k in range(3):
            dct_data[:, :, k] = operateur_DCT @ image[:, :, k] @ operateur_DCT.T
        
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
            """
            Dans un premier temps, on considèrera que les 2èmes valeurs
            des tuples RLE sont des entiers, et non des flottants
            --> "entier" correspond à ici l'entier le plus proche de x
            
            /!\ ATTENTION /!\
            Ici, NE PAS UTILISER la fonction round ou np.round (en considérant
            par exemple 'entier = round(x)' ou 'entier = np.round(x)'), car ici
            x est soit de type numpy.int32 ou numpy.float64 (et non int ou float)
            
            Si x est de type numpy.int32 : OK (pas de problème)
            
            Si x est de type numpy.float64 : gros problème
            En effet, quand la fonction round (ou np.round) reçoit un objet de 
            type numpy.float64 en entrée, elle renvoie un objet qui est également 
            de type numpy.float64, et non int (ou numpy.int32) !!
            
            Exemple : Soit a = 24.4, avec type(a) = numpy.float64, et soit
            b = round(a) (ou b = np.round(a)). Alors b = 24.0 (et non 24), et 
            type(b) = numpy.float64 !
            
            Cependant, la fonction int **force** la conversion en int, même si
            l'objet est de type numpy.float64
            
            Autre remarques (moins importantes) : 
            1) Si x est de type float (et non numpy.float64), round renvoie bien
            un int, comme on s'y attendrait
            2) La fonction int n'est pas exactement la partie entière
            Il s'agit en fait de la 'troncature entière', ie le flottant privé de
            sa partie décimale. Ainsi, int et la partie entière coïncident sur
            R+, mais PAS sur R*-. Sur R*-, on a : int(x) = partie_entiere(x) + 1.
            Si int avait été exactement la partie entière, on aurait directement
            pu écrire 'entier = int(x + 0.5)' sans aucune disjonction de cas.
            """
            if x >= 0:
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
        
        return huff_enc.encode_phrase(), huff_enc.symbols, huff_enc.dictToBin()

