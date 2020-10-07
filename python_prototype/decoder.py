import numpy as np 
from huffman import Huffman

class Decoder:

    def __init__(self):
        pass

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
        huff= Huffman()
        return huff.decode_phrase(enc_data,dictionary)

    def decode_run_length(self, rle_data):
        """
        Décode les paires de valeurs issues de la RLE et retourne
        une liste corrspondant aux valeurs quantifiées.

        Args:
            rle_data: paires de valeurs issues de la RLE

        Returns:
            quantized_data: liste de valeurs quantifiées
        """
    
        tab = np.int_([])
        for x in rle_data:
            tab=np.concatenate((tab,np.int_(np.zeros(x[0]))))
            tab=np.concatenate((tab,np.array([x[1]])))
        
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

        up = False
        # Position du curseur
        i, j = 0, 0
        # Tableau de sortie
        n=int(quantized_data.size**(1/2))
        res = np.int_(np.zeros((n,n)))
        # Pour chacun des points qui constituent l'image
        for t in range(quantized_data.size):
            # On ajoute le point courant
            if quantized_data[t]!=0:
                res[i,j]=quantized_data[t]
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
            
        return res

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