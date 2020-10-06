# -*- coding: utf-8 -*-

from random import randint
from huffman import Huffman

# définition des variables globales (= différents types de messages à encoder)
from logger import Logger

global HEADER_MSG
HEADER_MSG = 0

global DICT_MSG
DICT_MSG = 1

global BODY_MSG
BODY_MSG = 2

global TAIL_MSG
TAIL_MSG = 3


###############################################################################


# fonction auxiliaire

# retourne une chaîne de caractères correspondant à la représentation binaire
# d'un entier positif ou nul, codé sur un nombre de bits prédéfini
# on suppose ici que entier <= 2**nb_bits - 1
def int2bin(entier, nb_bits):
    if entier == 0:
        return("0".zfill(nb_bits))
    
    chaine_binaire = ""
    while entier != 0:
        entier, reste = divmod(entier, 2)
        chaine_binaire = "01"[reste] + chaine_binaire
    
    return(chaine_binaire.zfill(nb_bits))


###############################################################################


class BitstreamGenerator:
    """
    Classe permettant de générer un bitstream à partir des infos d'une frame 
    en entrée (après RLE).
    Concrètement, le bistream d'une frame est constituée de 4 éléments :
        - header: en-tête
        - dict: relatif au dictionnaire de Huffman de la frame encodée (construit itérativement)
        - body: relatif à la frame encodée (construit itérativement)
        - tail: fin du bitstream
    """
    
    def __init__(self, frame_id, img_size, macroblock_size):
        self.frame_id = frame_id
        self.img_size = img_size # multiple de macroblock_size**2
        self.macroblock_size = macroblock_size
        
        self.index_dict = 0
        self.index_body = 0
        
        self.header = None
        self.dict = ""
        self.body = ""
        self.tail = None
        
        self.bitstream = ""
    
    
    def construct_header(self):
        """
        Construit le bitstream d'en-tête de l'image à partir des informations 
        entrées lors de l'instanciation de la classe.
        Returns:
            bitstream (string): le bitstream représentant le header de la frame
        """
        # header = frame_id + type_msg + taille image + taille macroblocs
        self.header = int2bin(self.frame_id, 16) + int2bin(HEADER_MSG, 2) + \
                      int2bin(self.img_size, 16) + int2bin(self.macroblock_size, 5)
        
        self.bitstream += self.header
        
        return(self.header)
    
    
    def construct_dict(self, dict_huffman_packet):
        """
        Construit le bitstream représentant le dictionnaire de huffman associé
        à la frame (après RLE), converti en binaire.
        Args:
            dict_huffman_packet: paquet d'un dictionnaire de huffman encodé en binaire
        Returns:
            bitstream (string): le bitstream représentant le dictionnaire de huffman
        """
        # nouv_contenu_dict = frame_id + type_msg + index + taille dico encodé + dico encodé
        nouv_contenu_dict = int2bin(self.frame_id, 16) + int2bin(DICT_MSG, 2) + \
                            int2bin(self.index_dict, 16) + \
                            int2bin(len(dict_huffman_packet), 16) + dict_huffman_packet
        
        self.dict += nouv_contenu_dict
        self.bitstream += nouv_contenu_dict
        self.index_dict += 1
        
        return(nouv_contenu_dict)
    
    
    def construct_body(self, huffman_packet):
        """
        Construit le bitstream représentant le contenu d'un paquet encodé 
        par huffman.
        Args:
            huffman_packet: contenu du paquet encodé par huffman
        Returns:
            bitstream (string): le bitstream représentant le paquet
        """
        # nouveau contenu = frame_id + type_msg + index + taille contenu + contenu
        nouv_contenu_body = int2bin(self.frame_id, 16) + int2bin(BODY_MSG, 2) + \
                            int2bin(self.index_body, 16) + \
                            int2bin(len(huffman_packet), 16) + huffman_packet
        
        self.body += nouv_contenu_body
        self.bitstream += nouv_contenu_body
        self.index_body += 1
        
        return(nouv_contenu_body)
    
    
    def construct_end_message(self):
        """
        Construit le bitstream représentant le message de fin d'une frame.
        Returns:
            bitstream (string): le bitstream représentant le message de fin
        """
        # tail = frame_id + type_msg
        self.tail = int2bin(self.frame_id, 16) + int2bin(TAIL_MSG, 2)
        self.bitstream += self.tail
        
        return(self.tail)
    
    
    @staticmethod
    def decode_bitstream_RLE(bitstream):
        """
        Permet de décoder un bitstream associé une frame RLE avec seulement 
        les méthodes statiques de la classe Huffman. Fonction très pratique au
        moment du décodage global.
        Args:
            bitstream (string): bitstream complet associé à une frame, généré grâce 
                                à la classe BitstreamGenerator
        Returns:
            frame_RLE_decodee: frame RLE (liste de tuples d'entiers) associée au 
                               bitstream mis en entrée
        """
        
        #--------------------------------------------------------------------#
        
        # récupération des données utiles du dict
        
        donnees_utiles_dict = ""
        
        # détermination de la taille du paquet utile dans la partie actuelle
        # (chaque partie contient exactement un paquet utile)
        indice_debut_partie = 39 
        indice_debut_taille = indice_debut_partie + 34
        indice_fin_taille = indice_debut_taille + 16
        taille_donnees_paquet = int(bitstream[indice_debut_taille : indice_fin_taille], 2)
        
        # récupération des données utiles du dictionnaire dans la partie actuelle
        indice_fin_partie = indice_debut_partie + 50 + taille_donnees_paquet
        partie = bitstream[indice_debut_partie : indice_fin_partie]
        type_msg = int(partie[16 : 18], 2)
        donnees_utiles_dict += partie[50 : 50 + taille_donnees_paquet]
        
        while type_msg == DICT_MSG:
            indice_debut_partie += 50 + taille_donnees_paquet
            
            # détermination de la taille du paquet utile dans la partie actuelle
            indice_debut_taille = indice_debut_partie + 34
            indice_fin_taille = indice_debut_taille + 16
            taille_donnees_paquet = int(bitstream[indice_debut_taille : indice_fin_taille], 2)
            
            # récupération des données utiles du dictionnaire dans la partie actuelle
            indice_fin_partie = indice_debut_partie + 50 + taille_donnees_paquet
            partie = bitstream[indice_debut_partie : indice_fin_partie]
            type_msg = int(partie[16 : 18], 2)
            
            # si cette condition n'est pas vérifiée, c'est que type_msg = BODY_MSG = 2,
            # et donc que l'on est en train de considérer les données du body, et non
            # celles du dict
            # en outre, si cette condition n'est pas vérifiée, cela signifie que
            # indice_debut_partie désigne l'indice du 1er élément du body 
            if type_msg == DICT_MSG:
                donnees_utiles_dict += partie[50 : 50 + taille_donnees_paquet]
        
        #--------------------------------------------------------------------#
        
        # on décode le dictionnaire de huffman associé à la frame
        dict_huffman_decode = Huffman.binToDict(donnees_utiles_dict)
        
        #--------------------------------------------------------------------#
        
        # on récupère le body associé à la frame (sans avoir trié les parties utiles)
        body_bitstream = bitstream[indice_debut_partie : -18]
        len_body_bitstream = len(body_bitstream)
        
        #--------------------------------------------------------------------#
        
        # récupération des données utiles du body
        
        donnees_utiles_body = ""
        indice_debut_partie = 0 # ré-initialisation de indice_debut_partie
        
        while indice_debut_partie < len_body_bitstream:
            # détermination de la taille du paquet utile dans la partie actuelle
            indice_debut_taille = indice_debut_partie + 34
            indice_fin_taille = indice_debut_taille + 16
            taille_donnees_paquet = int(body_bitstream[indice_debut_taille : indice_fin_taille], 2)
            
            # récupération des données utiles du body dans la partie actuelle
            indice_debut_donnees = indice_fin_taille
            indice_fin_donnees = indice_debut_donnees + taille_donnees_paquet
            donnees_paquet = body_bitstream[indice_debut_donnees : indice_fin_donnees]
            
            donnees_utiles_body += donnees_paquet
            
            # on met à jour indice_debut_partie pour pouvoir ré-itérer ce processus
            indice_debut_partie += 50 + taille_donnees_paquet
        
        #--------------------------------------------------------------------#
        
        # on décode les données utiles du body
        frame_RLE_decodee = Huffman.decode_frame_RLE(donnees_utiles_body, dict_huffman_decode)
        
        return(frame_RLE_decodee)


###############################################################################


# génération aléatoire de frame RLE
# on suppose que macroblock_size >= 8 et nb_macroblocs >= 4
def generer_frame_RLE(macroblock_size, nb_macroblocks):
    frame = []
    
    img_size = nb_macroblocks * macroblock_size**2
    
    # techniquement, ce nombre maximal vaut img_size // 2, mais en pratique les
    # premières valeurs des tuples seront relativement élevées, donc on divise 
    # img_size par 20 (par exemple ; on suppose ici que img_size est >= 20)
    # cette fonction marchera quand même si nb_tuples_RLE_max = img_size // 2
    nb_tuples_RLE_max = img_size // 20
    
    nb_tuples_RLE = randint(1, nb_tuples_RLE_max)
    nb_zeros = img_size - nb_tuples_RLE
    
    # on cherche donc à trouver nb_tuples_RLE entiers aléatoires dont la somme 
    # est nb_zeros
    
    moyenne = nb_zeros // nb_tuples_RLE + 1
    
    nb_zeros_partiel = 0
    for num_tuple_RLE in range(nb_tuples_RLE):
        if num_tuple_RLE != nb_tuples_RLE - 1:
            a = randint(1, moyenne)
            nb_zeros_partiel += a
            
            # on met à jour la moyenne du nombre de zeros par tuple RLE restant
            # afin d'avoir les coefficients les plus homogènes possibles
            moyenne = (nb_zeros - nb_zeros_partiel) // (nb_tuples_RLE - num_tuple_RLE - 1) + 1
        
        else:
            a = nb_zeros - nb_zeros_partiel # = nombre de zéros restants
        
        if a != 0:
            b = randint(1, 30)
            frame.append((a, b))
        
        else:
            # il est possible que 'a' soit nul à la toute dernière étape (et
            # uniquement à cette étape)
            # dans ce cas, on rajoute 1 au nombre de zéros du dernier tuple
            # de la frame
            dernier_tuple = frame[-1]
            (dernier_a, dernier_b) = (dernier_tuple[0], dernier_tuple[1])
            frame = frame[ : -1]
            frame.append((dernier_a + 1, dernier_b))
    
    return(frame)


###############################################################################


# Exemple concret

if __name__ == "__main__":    
    # on définit une frame
    
    frame_id = randint(0, 65535) # 65535 = 2**16 - 1
    
    macroblock_size = 8
    nb_macroblocks = 4
    img_size = nb_macroblocks * macroblock_size**2
    
    # génération aléatoire d'une frame RLE
    frame = generer_frame_RLE(macroblock_size, nb_macroblocks)
    
    #------------------------------------------------------------------------#
    
    # autres données utiles
    
    # on DOIT avoir bufsize >= 51 (pour que l'on puisse envoyer en 1 seule fois
    # le header et la queue du bitstream, et pour que l'on puisse envoyer correctement 
    # chacun des paquets constituant dict et body
    # en effet, les "métadonnées" associées à chacun des paquets élémentaires
    # de dict et de body font exactement 50 bits
    puiss_2_random = randint(6, 12)
    bufsize = 2 ** puiss_2_random
    
    # taille d'un paquet élémentaire du dict ou du body avant de l'adjoindre
    # au paquet du bitstream (de taille 50 + taille_paquet_elementaire, qui
    # vaut bufsize par définition)
    # concrètement, les métadonnées des paquets envoyés pour former le bistream
    # du dict et du body font exactement 50 bits (50 = 16 + 2 + 16 + 16)
    taille_paquet_elementaire = bufsize - 50
    
    # encodage de la frame et du dictionnaire de huffman associé
    huff = Huffman(frame)
    frame_encodee = huff.encode_phrase()
    dict_huffman_encode = huff.dictToBin()
    
    #------------------------------------------------------------------------#
    
    # génération du header
    
    gen = BitstreamGenerator(frame_id, img_size, macroblock_size)
    
    header_bitstream = gen.construct_header()
    # --> puis : send header_bitstream (en 1 seule fois, car len(header_bitstream) = 39)
    
    #------------------------------------------------------------------------#
    
    # génération du dict du bitstream
    
    # définition du nombre de paquets vont être générés à partir du dictionnaire
    # de huffman encodé
    len_dict_bitstream = len(dict_huffman_encode)
    if len_dict_bitstream % taille_paquet_elementaire == 0:
        nb_paquets_dict = len_dict_bitstream // taille_paquet_elementaire
    else:
        nb_paquets_dict = len_dict_bitstream // taille_paquet_elementaire + 1
    
    # construction du dict, paquet par paquet
    # (normalement, ces paquets seront envoyés un par un, d'un client à un serveur)
    for num_paquet_dict in range(nb_paquets_dict):
        indice_initial = num_paquet_dict * taille_paquet_elementaire
        
        if num_paquet_dict != nb_paquets_dict - 1:
            indice_final = indice_initial + taille_paquet_elementaire
            donnees_paquet = dict_huffman_encode[indice_initial : indice_final]
        
        else:
            donnees_paquet = dict_huffman_encode[indice_initial : ]
        
        nouv_paquet_dict = gen.construct_dict(donnees_paquet)
        # --> puis : send nouv_paquet_dict (en 1 seule fois, car, par construction,
        # len(nouv_paquet_dict) = bufsize, ou bien len(nouv_paquet_dict) <= bufsize
        # pour le tout dernier paquet)
    
    #------------------------------------------------------------------------#
    
    # génération du body
    
    # définition du nombre de paquets vont être générés à partir de la frame
    # encodée
    len_frame_encodee = len(frame_encodee)
    if len_frame_encodee % taille_paquet_elementaire == 0:
        nb_paquets_body = len_frame_encodee // taille_paquet_elementaire
    else:
        nb_paquets_body = len_frame_encodee // taille_paquet_elementaire + 1
    
    # construction du body, paquet par paquet
    # (normalement, ces paquets seront envoyés un par un, d'un client à un serveur)
    for num_paquet_body in range(nb_paquets_body):
        indice_initial = num_paquet_body * taille_paquet_elementaire
        
        if num_paquet_body != nb_paquets_body - 1:
            indice_final = indice_initial + taille_paquet_elementaire
            donnees_paquet = frame_encodee[indice_initial : indice_final]
        
        else:
            donnees_paquet = frame_encodee[indice_initial : ]
        
        nouv_paquet_body = gen.construct_body(donnees_paquet)
        # --> puis : send nouv_paquet_body (en 1 seule fois, car, par construction,
        # len(nouv_paquet_body) = bufsize, ou bien len(nouv_paquet_body) <= bufsize
        # pour le tout dernier paquet)
    
    #------------------------------------------------------------------------#
    
    # génération de la queue du message
    
    tail_bitstream = gen.construct_end_message()
    # --> puis : send tail_bitstream (en 1 seule fois, car len(tail_bitstream) = 18)
    
    #------------------------------------------------------------------------#
    
    # décodage du bitstream 
    # normalement, 'bitstream' correspondra aux données reçues par le serveur, 
    # et interceptées par la méthode on_received_data (cf. network_transmission.py)
    
    bitstream = gen.bitstream
    frame_decodee = BitstreamGenerator.decode_bitstream_RLE(bitstream)
    
    #------------------------------------------------------------------------#
    
    # prints de synthèse
    
    Logger.get_instance().debug("\nFrame :\n" + str(frame))
    Logger.get_instance().debug("\nBitstream associé à la frame :\n" + bitstream)
    Logger.get_instance().debug("\nDécodage du bitstream de la frame :\n" + str(frame_decodee))
    
    # test de cohérence
    bool_test = (frame == frame_decodee)
    Logger.get_instance().debug("\nFrame décodée == frame de référence :", bool_test)
    
    # à titre informatif
    Logger.get_instance().debug("\nBufsize :", bufsize)
