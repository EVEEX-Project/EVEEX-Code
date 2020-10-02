# -*- coding: utf-8 -*-

# définition des variables globales (= différents types de messages à encoder)

global HEADER_MSG
HEADER_MSG = 0

global DICT_MSG
DICT_MSG = 1

global BODY_MSG
BODY_MSG = 2

global TAIL_MSG
TAIL_MSG = 3

########################################################################################

# fonction auxiliaire

# retourne une chaîne de caractères correspondant à la représentation binaire
# d'un entier positif, codé sur un nombre de bits prédéfini
def int2bin(entier, nb_bits):
    if entier == 0:
        return("0".zfill(nb_bits))
    chaine_binaire = ""
    while entier != 0:
        entier, reste = divmod(entier, 2)
        chaine_binaire = "01"[reste] + chaine_binaire
    return(chaine_binaire.zfill(nb_bits))

########################################################################################

class BitstreamGenerator:
    """
    Classe permettant de générer un bitsream à partir des infos d'une frame 
    en entrée.
    Frame = header + dict huffman encodé + body (en plusieurs incréments) + tail.
    """
    def __init__(self, frame_id, img_size, macroblock_size):
        self.frame_id = frame_id
        self.img_size = img_size
        self.macroblock_size = macroblock_size
        
        self.index = 0
        
        self.header = ""
        self.dict = ""
        self.body = ""
        self.tail = ""
        
        self.bitstream = ""
    
    def construct_header_bitstream(self):
        """
        Construit le bitstream d'en-tête de l'image à partir des informations 
        entrées lors de l'instanciation de la classe.
        Returns:
            bitstream (string): le bitstream représentant le header de la frame
        """
        # header = frame_id + type_msg + taille image + taille macroblocs
        self.header += int2bin(self.frame_id, 16) + int2bin(HEADER_MSG, 2) + int2bin(self.img_size, 16) + int2bin(self.macroblock_size, 5)
        
        self.bitstream += self.header
    
    def construct_dict_bitstream(self, dict_huffman_encode):
        """
        Rajoute le dictionnaire de huffman (encodé) au bitstream.
        Returns:
            bitstream (string): le bitstream représentant le dictionnaire de huffman
        """
        # dict = frame_id + type_msg + taille dico encodé + dico encodé
        self.dict += int2bin(self.frame_id, 16) + int2bin(DICT_MSG, 2) + int2bin(len(dict_huffman_encode), 16) + dict_huffman_encode
        
        self.bitstream += self.dict
    
    def construct_body(self, huffman_data):
        """
        Construit le bitstream représentant le contenu d'un macrobloc, encodé 
        par huffman.
        Args:
            huffman_data: contenu du macrobloc encodé par huffman
        Returns:
            bitstream (string): le bitstream représentant le macrobloc
        """
        # body = frame_id + type_msg + index + taille contenu + contenu
        nouv_contenu_body = int2bin(self.frame_id, 16) + int2bin(BODY_MSG, 2) + int2bin(self.index, 16) + int2bin(len(huffman_data), 16) + huffman_data
        
        self.body += nouv_contenu_body
        
        self.index += 1
        
        self.bitstream += nouv_contenu_body
    
    def construct_end_message(self):
        """
        Construit le bitstream représentant le message de fin d'une frame.
        Returns:
            bitstream (string): le bitstream représentant le message de fin
        """
        self.tail += int2bin(self.frame_id, 16) + int2bin(TAIL_MSG, 2)
        
        self.bitstream += self.tail        

########################################################################################

if __name__ == "__main__":
    # à tester
    pass
