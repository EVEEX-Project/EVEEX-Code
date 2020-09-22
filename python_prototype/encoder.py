from huffman import Huffman

DEFAULT_QUANTIZATION_THRESHOLD = 0.5


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
        raise NotImplementedError

    def RGB_to_YCbCr(self, image):
        """
        Convertit une image depuis une représentation RGB (Rouge, Vert, Bleu)
        vers une représentation YCbCr (Luminance, Chrominance)

        Args:
            image: tableau de pixels représentant l'image

        Returns:
            image_ycbcr: tableau de pixels représentant l'image au format YUV
        """
        raise NotImplementedError

    def apply_DCT(self, image):
        """
        Applique la transformée en cosinus discrete à une image au format luminance chrominance.

        Args:
            image: tableau de pixels représentant l'image au format Luminance/Chrominance

        Returns:
            dct_data: tableau de coefficients issu de la transformée en cosinus discrete
        """
        raise NotImplementedError

    def zigzag_linearisation(self, dct_data):
        """
        Parcoure un tableau de coefficients en zig zag de manière à passer d'un
        tableau en deux dimensions à un tableau à une dimension avec par conséquent
        beaucoup de zéros entre les valeurs significatives.

        Args:
            dct_data: tableau de coefficients issus de la transformée en cosinus discrete

        Returns:
            data: tableau à une dimension des coefficients de l'image
        """
        raise NotImplementedError

    def quantization(self, data, threshold=DEFAULT_QUANTIZATION_THRESHOLD):
        """
        Permet de quantifier les coefficients en passant toutes les valeurs sous un certain seuil
        à 0.

        Args:
            data: tableau à une dimension des coefficients de l'image passés par la DCT
            threshold: valeur de seuil à partir de laquelle les valeurs sont mises à zéro

        Returns:

        """
        raise NotImplementedError

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
        raise NotImplementedError

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