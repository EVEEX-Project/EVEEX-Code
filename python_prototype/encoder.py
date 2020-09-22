from huffman import Huffman

DEFAULT_QUANTIZATION_THRESHOLD = 0.5
import numpy as np 

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

        Args:
            image: tableau de pixels représentant l'image au format Luminance/Chrominance

        Returns:
            dct_data: tableau de coefficients issu de la transformée en cosinus discrete
        """
        dct_data = np.zeros(image.shape)

        def compute_energy(image, k1, k2, k3):
            """
            Permet de calculer l'énerge au point k1, k2 sur le canal k3
            """
            res = 0
            for n1 in range(image.shape[0]):
                for n2 in range(image.shape[1]):
                    res += image[n1, n2, k3] * \
                           np.cos(np.pi / image.shape[0] * (n1 + 1/2) * k1) * \
                           np.cos(np.pi / image.shape[1] * (n2 + 1/2) * k2)
            return res

        # On itere sur les 3 canaux
        # puis sur les pixels de l'image
        for k in range(3):
            for i in range(image.shape[0]):
                for j in range(image.shape[1]):
                    dct_data[i, j, k] = compute_energy(image, i, j, k)
        return dct_data

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
        for t in range(dct_data.size):
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
                    # Sinon on parcoure la diagonale
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
                    # Sinon on parcoure la diagonale
                    j -= 1
                    i += 1
            
        return np.array(res)

    def quantization(self, data, threshold=DEFAULT_QUANTIZATION_THRESHOLD):
        """
        Permet de quantifier les coefficients en passant toutes les valeurs sous un certain seuil
        à 0.

        Args:
            data: tableau à une dimension des coefficients de l'image passés par la DCT
            threshold: valeur de seuil à partir de laquelle les valeurs sont mises à zéro

        Returns:

        """
        # Pour chaque élément de la liste
        for i in range(data.shape[0]):
            # Si la valeur est en dessous du seuil
            if data[i] <= threshold:
                # On la met à 0
                data[i] = 0
                
        return data

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
            # Si on a un non-nul
            if x != 0:
                # On enregistre le couple
                pairs.append((n, x))
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
    enc = Encoder()
    tab = np.zeros((5,5))
    tab[2, 1] = 6
    tab[0, 1] = 3
    tab[4, 2] = 9
    tab[3, 3] = 0.2
    print("Tableau original : \n", tab)
    zigzag = enc.zigzag_linearisation(tab)
    print("Zig zag : \n", zigzag)
    quanti = enc.quantization(zigzag)
    print("Quantifié : \n", quanti)
    rle = enc.run_level(quanti)
    print("Run-length encoding : \n", rle)
