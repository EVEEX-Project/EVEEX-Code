
class Decoder:

    def __init__(self):
        raise NotImplementedError

    def decode_huffman(self, dictionary, enc_data):
        """
        Permet de décoder des données encodées par huffman et de retourner
        les couples de valeurs RLE issues de l'encodage

        Args:
            dictionary (dict): dico des symboles d'encodage
            enc_data (string): chaine de caractères encodée

        Returns:
            rle_data : paires de données issues de la RLE
        """
        raise NotImplementedError

    def decode_run_length(self, rle_data):
        """
        Décode les paires de valeurs issues de la RLE et retourne
        une liste corrspondant aux valeurs quantifiées.

        Args:
            rle_data: paires de valeurs issues de la RLE

        Returns:
            quantized_data: liste de valeurs quantifiées
        """

        return NotImplementedError

    def decode_zigzag(self, quantized_data):
        """
        Decode une liste de valeurs quantifiées en un tableau de valeurs
        en respectant le principe de l'encodage en zig zag.

        Args:
            quantized_data: liste de valeurs quantifiées

        Returns:
            dct_tab: tableau de valeurs issues de la transformation en cosinus
        """

        return NotImplementedError

    def decode_dct(self, dct_data):
        """
        Decode un tableau de valeurs passées par la transformée discrète en
        cosinus. Il s'agit d'appliquer la DCT inverse.

        Args:
            dct_data: tableau de valeurs issues de la DCT

        Returns:
            img_data: tableau de valeurs représentant l'image
        """

        return NotImplementedError