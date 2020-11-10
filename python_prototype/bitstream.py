# -*- coding: utf-8 -*-

from random import randint
from huffman import Huffman
from network_transmission import Server, Client
from logger import Logger

###############################################################################

# définition des variables globales (ie les différents types de messages à encoder)

global HEADER_MSG
HEADER_MSG = 0

global DICT_MSG
DICT_MSG = 1

global BODY_MSG
BODY_MSG = 2

global TAIL_MSG
TAIL_MSG = 3

###############################################################################


class BitstreamGenerator:
    """
    Classe permettant de générer un bitstream à partir des infos d'une frame 
    en entrée (après RLE). Chaque instance de cette classe servira à créer le 
    bitstream d'une seule image (pour le moment).
    
    Concrètement, le bitstream d'une frame est constitué de 4 éléments :
        - header: en-tête
        - dict: relatif au dictionnaire de Huffman de la frame encodée (construit itérativement)
        - body: relatif à la frame encodée (construit itérativement)
        - tail: fin du bitstream
    """
    
    def __init__(self, frame_id, img_size, macroblock_size):
        self.frame_id = frame_id
        
        # img_size = (w, h), où w (= width = largeur) et h (= height = hauteur) 
        # sont **obligatoirement** des multiples de macroblock_size
        # En particulier, cela implique que w*h est un multiple de macroblock_size**2
        self.img_size = img_size
        self.img_width, self.img_height = self.img_size
        
        self.macroblock_size = macroblock_size
        
        # initialisation des index des paquets envoyés (pour le dict et le body)
        self.index_paquet_dict = 0
        self.index_paquet_macrobloc = 0
        
        self.len_dict_bitstream = 0
        self.len_body_bitstream = 0
        
        self.bitstream = ""
    
    
    @staticmethod
    def int2bin(entier, nb_bits):
        """
        Fonction auxiliaire.
        Retourne une chaîne de caractères correspondant à la représentation 
        binaire d'un entier positif ou nul (entier), codé sur un nombre de bits
        prédéfini (nb_bits). 
        On suppose ici que entier <= 2**nb_bits - 1 (ie on suppose que cet entier
        est codable sur le nombre de bits défini).
        """
        if entier == 0:
            return("0".zfill(nb_bits))
        
        chaine_binaire = ""
        while entier != 0:
            entier, reste = divmod(entier, 2)
            chaine_binaire = "01"[reste] + chaine_binaire
        
        return(chaine_binaire.zfill(nb_bits))
    
    
    def construct_header(self):
        """
        Construit le bitstream d'en-tête d'une frame à partir des informations 
        entrées lors de l'instanciation de la classe.
        Returns:
            bitstream (string): le bitstream représentant le header de la frame
        """
        
        # header = frame_id + type_msg + largeur de l'image + hauteur de l'image
        # + taille des macroblocs
        header = self.int2bin(self.frame_id, 16) + self.int2bin(HEADER_MSG, 2) + \
                 self.int2bin(self.img_width, 12) + self.int2bin(self.img_height, 12) + \
                 self.int2bin(self.macroblock_size, 6)
        
        self.bitstream += header
        
        return(header)
    
    
    def construct_dict(self, dict_huffman_packet):
        """
        Construit le bitstream représentant le dictionnaire de huffman associé
        à la frame (après RLE), converti en binaire.
        
        Remarque importante : à part pour le tout dernier paquet provenant des données
        utiles du dictionnaire de huffman encodé, on aura toujours la relation 
        suivante : len(dict_huffman_packet) = bufsize - 50 = taille_paquet_elementaire_dict,
        et donc len(nouv_contenu_dict) = taille_paquet_elementaire_dict + 50 = bufsize.
        Pour le tout dernier paquet, on aura juste len(dict_huffman_packet) <= bufsize - 50
        et len(nouv_contenu_dict) <= bufsize.
        La raison pour laquelle on inclut quand même la taille des paquets est précisément
        ce dernier paquet, qui n'est pas nécessairement de la même taille que tous 
        les autres.
        
        --> Cette remarque est aussi valable pour la méthode construct_body (en 
            remplaçant '50' par '66').
        
        Args:
            dict_huffman_packet: paquet d'un dictionnaire de huffman encodé en binaire
        Returns:
            bitstream (string): le bitstream représentant une partie du dictionnaire 
                                de huffman
        """
        # nouv_contenu_dict = frame_id + type_msg + index + taille paquet + paquet
        # --> pas besoin du numéro du macrobloc, car dictionnaire global
        nouv_contenu_dict = self.int2bin(self.frame_id, 16) + self.int2bin(DICT_MSG, 2) + \
                            self.int2bin(self.index_paquet_dict, 16) + \
                            self.int2bin(len(dict_huffman_packet), 16) + dict_huffman_packet
        
        self.bitstream += nouv_contenu_dict
        self.len_dict_bitstream += len(nouv_contenu_dict)
        self.index_paquet_dict += 1
        
        return(nouv_contenu_dict)
    
    
    def construct_body(self, num_macrobloc, huffman_packet):
        """
        Construit le bitstream représentant le contenu d'un paquet encodé 
        par huffman.
        Args:
            num_macrobloc: numéro du macrobloc dont est issu le paquet encodé
            huffman_packet: contenu du paquet encodé par huffman
        Returns:
            bitstream (string): le bitstream représentant le paquet
        """
        # nouveau contenu = frame_id + type_msg + numéro macrobloc + index + 
        # taille paquet + paquet
        nouv_contenu_body = self.int2bin(self.frame_id, 16) + self.int2bin(BODY_MSG, 2) + \
                            self.int2bin(num_macrobloc, 16) + self.int2bin(self.index_paquet_macrobloc, 16) + \
                            self.int2bin(len(huffman_packet), 16) + huffman_packet
        
        self.bitstream += nouv_contenu_body
        self.len_body_bitstream += len(nouv_contenu_body)
        self.index_paquet_macrobloc += 1
        
        return(nouv_contenu_body)
    
    
    def construct_end_message(self):
        """
        Construit le bitstream représentant le message de fin d'une frame.
        Returns:
            bitstream (string): le bitstream représentant le message de fin
        """
        # tail = frame_id + type_msg
        self.tail = self.int2bin(self.frame_id, 16) + self.int2bin(TAIL_MSG, 2)
        
        self.bitstream += self.tail
        
        return(self.tail)
    
    
    @staticmethod
    def encode_frame_RLE(frame_id, img_size, macroblock_size, frame, bufsize):
        """
        Permet de convertir une frame RLE en un bitstream. Il s'agit d'une
        fonction-outil. On reprend en fait tout le processus de la méthode
        'send_frame_RLE' de BitstreamSender, mais SANS passer par un réseau.
        
        Args:
            frame_id: identifiant de la frame (int)
            img_size: tuple égal à (img_width, img_height)
            macroblock_size: longueur des côtés des macroblocs (on suppose que
                             ce sont des carrés), int > 1
            frame: frame_RLE de référence (liste de tuples d'entiers)
            bufsize: taille maximale que peut prendre un paquet (int >= 51)
        
        Returns:
            bitstream_total: bitstream associé à la frame RLE de référence 
        """
        
        #--------------------------------------------------------------------#
        
        # initialisation du constructeur (du bitstream)
        bit_generator = BitstreamGenerator(frame_id, img_size, macroblock_size)
        
        #--------------------------------------------------------------------#
        
        # construction du header
        bit_generator.construct_header()
        
        #--------------------------------------------------------------------#
        
        # dict
        
        taille_metadonnees_dict = 50
        taille_paquet_elementaire_dict = bufsize - taille_metadonnees_dict
        
        # encodage du dictionnaire de huffman associé à la frame **entière**
        huff = Huffman([tuple_RLE for macrobloc in frame for tuple_RLE in macrobloc])
        dict_huffman_encode = huff.dictToBin()
        
        # définition du nombre de paquets qui vont être générés à partir du dictionnaire
        # de huffman encodé
        len_dict_bitstream = len(dict_huffman_encode)
        if len_dict_bitstream % taille_paquet_elementaire_dict == 0:
            nb_paquets_dict = len_dict_bitstream // taille_paquet_elementaire_dict
        else:
            nb_paquets_dict = len_dict_bitstream // taille_paquet_elementaire_dict + 1
        
        # construction du dict, paquet par paquet
        for num_paquet_dict in range(nb_paquets_dict):
            indice_initial = num_paquet_dict * taille_paquet_elementaire_dict
            
            if num_paquet_dict != nb_paquets_dict - 1:
                indice_final = indice_initial + taille_paquet_elementaire_dict
                donnees_paquet = dict_huffman_encode[indice_initial : indice_final]
            
            else:
                # dernier paquet
                donnees_paquet = dict_huffman_encode[indice_initial : ]
            
            bit_generator.construct_dict(donnees_paquet)
        
        #--------------------------------------------------------------------#
        
        # body
        
        taille_metadonnees_body = 66
        taille_paquet_elementaire_body = bufsize - taille_metadonnees_body
        
        total_num_of_macroblocks = len(frame)
        
        for num_macrobloc in range(total_num_of_macroblocks):
            macrobloc = frame[num_macrobloc]
            macrobloc_encode = huff.encode_phrase(phrase=macrobloc)
            
            # création du bitstream associé au macrobloc
            
            # réinitialisation de l'index du paquet associé au macrobloc actuel
            bit_generator.index_paquet_macrobloc = 0
            
            # définition du nombre de paquets qui vont être générés à partir du
            # macrobloc encodé
            len_macrobloc_encode = len(macrobloc_encode)
            if len_macrobloc_encode % taille_paquet_elementaire_body == 0:
                nb_paquets_macrobloc = len_macrobloc_encode // taille_paquet_elementaire_body
            else:
                nb_paquets_macrobloc = len_macrobloc_encode // taille_paquet_elementaire_body + 1
            
            # construction du bitstream associé au macrobloc, paquet par paquet
            for num_paquet_macrobloc in range(nb_paquets_macrobloc):
                indice_initial = num_paquet_macrobloc * taille_paquet_elementaire_body
                
                if num_paquet_macrobloc != nb_paquets_macrobloc - 1:
                    indice_final = indice_initial + taille_paquet_elementaire_body
                    donnees_paquet = macrobloc_encode[indice_initial : indice_final]
                
                else:
                    # dernier paquet
                    donnees_paquet = macrobloc_encode[indice_initial : ]
                
                bit_generator.construct_body(num_macrobloc, donnees_paquet)
        
        #--------------------------------------------------------------------#
        
        # construction du tail du bitstream (message de fin)
        bit_generator.construct_end_message()
        
        #--------------------------------------------------------------------#
        
        bitstream_total = bit_generator.bitstream
        
        return(bitstream_total)
    
    
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
            frame_RLE_decodee: frame RLE (liste de listes de tuples d'entiers) 
                               associée au bitstream mis en entrée
        """
        
        #--------------------------------------------------------------------#
        
        # récupération des données utiles du dict
        
        donnees_utiles_dict = ""
        
        # détermination de la taille du paquet utile dans la partie actuelle
        # (chaque partie contient exactement un paquet utile)
        indice_debut_partie = 48 # 48 = taille du header
        type_msg = int(bitstream[indice_debut_partie + 16 : indice_debut_partie + 18], 2)
        indice_debut_taille = indice_debut_partie + 34
        indice_fin_taille = indice_debut_taille + 16
        taille_donnees_paquet = int(bitstream[indice_debut_taille : indice_fin_taille], 2)
        
        # récupération des données utiles du dictionnaire dans la partie actuelle
        # (ie la 1ère partie)
        donnees_utiles_dict += bitstream[indice_debut_partie + 50 : indice_debut_partie + 50 + taille_donnees_paquet]
        
        while type_msg == DICT_MSG:
            indice_debut_partie += 50 + taille_donnees_paquet
            
            type_msg = int(bitstream[indice_debut_partie + 16 : indice_debut_partie + 18], 2)
            
            if type_msg == DICT_MSG:
                # détermination de la taille du paquet utile dans la partie actuelle
                indice_debut_taille = indice_debut_partie + 34
                indice_fin_taille = indice_debut_taille + 16
                taille_donnees_paquet = int(bitstream[indice_debut_taille : indice_fin_taille], 2)
                
                # récupération des données utiles du dictionnaire dans la partie actuelle
                donnees_utiles_dict += bitstream[indice_debut_partie + 50 : indice_debut_partie + 50 + taille_donnees_paquet]
            
            # Si type_msg != DICT_MSG, c'est nécessairement parce que l'on a 
            # type_msg = BODY_MSG = 2, et donc que l'on est en train de considérer 
            # les données du body, et non celles du dict
            # En outre, si cette condition n'est pas vérifiée, cela signifie que
            # indice_debut_partie désigne l'indice du 1er élément du body 
        
        #--------------------------------------------------------------------#
        
        # on décode le dictionnaire de huffman associé à la frame
        dict_huffman_decode = Huffman.binToDict(donnees_utiles_dict)
        
        #--------------------------------------------------------------------#
        
        # on récupère le body associé à la frame (sans avoir trié les parties utiles)
        body_bitstream = bitstream[indice_debut_partie : -18] # 18 = taille du tail
        len_body_bitstream = len(body_bitstream)
        
        #--------------------------------------------------------------------#
        
        # récupération des données utiles du body
        
        frame_RLE_decodee = []
        
        # on détermine d'abord combien il y a de macroblocs en tout
        header = bitstream[ : 48]
        img_width = int(header[18 : 30], 2)
        img_height = int(header[30 : 42], 2)
        macroblock_size = int(header[42 : ], 2)
        total_num_of_macroblocks = (img_width * img_height) // macroblock_size**2
        
        indice_debut_partie = 0 # ré-initialisation de indice_debut_partie
        
        for num_macrobloc in range(total_num_of_macroblocks):
            donnees_utiles_macrobloc = ""
            
            num_macrobloc_actuel = int(body_bitstream[indice_debut_partie + 18 : indice_debut_partie + 34], 2)
            
            while (num_macrobloc_actuel == num_macrobloc) and (indice_debut_partie < len_body_bitstream):
                # détermination de la taille du paquet utile dans la partie actuelle
                indice_debut_taille = indice_debut_partie + 50
                indice_fin_taille = indice_debut_taille + 16
                taille_donnees_paquet = int(body_bitstream[indice_debut_taille : indice_fin_taille], 2)
                
                # récupération des données utiles du macrobloc dans la partie actuelle
                indice_fin_donnees = indice_fin_taille + taille_donnees_paquet
                donnees_paquet = body_bitstream[indice_fin_taille : indice_fin_donnees]
                
                donnees_utiles_macrobloc += donnees_paquet
                
                # on met à jour indice_debut_partie pour pouvoir ré-itérer ce processus
                indice_debut_partie += 66 + taille_donnees_paquet
                
                if indice_debut_partie < len_body_bitstream:
                    num_macrobloc_actuel = int(body_bitstream[indice_debut_partie + 18 : indice_debut_partie + 34], 2)
            
            # on décode les données utiles du body
            macrobloc_decode = Huffman.decode_frame_RLE(donnees_utiles_macrobloc, dict_huffman_decode)
            
            # on ajoute le macrobloc décodé à la frame
            frame_RLE_decodee.append(macrobloc_decode)
        
        return(frame_RLE_decodee)


###############################################################################


class BitstreamSender:
    """
    Classe permettant de gérer l'envoi d'un bitstream via un réseau, d'un client
    à un serveur.
    """
    
    def __init__(self, frame_id, img_size, macroblock_size, frame, client, bufsize):
        self.bit_generator = BitstreamGenerator(frame_id, img_size, macroblock_size)
        
        # liste de listes de tuples
        # chacune des sous-listes (qui sont ici des listes de tuples) correspond 
        # en fait à la représentation RLE d'un macrobloc
        self.frame = frame
        
        # c'est aussi égal à (img_size[0] * img_size[1]) // macroblock_size**2
        self.total_num_of_macroblocks = len(self.frame)
        
        # comme le client est défini par rapport à un serveur prédéfini, on n'a
        # pas besoin de créer une variable d'instance 'server'
        self.client = client
        
        self.bufsize = bufsize
        
        # concrètement, les métadonnées des paquets envoyés pour former le bitstream
        # du dict font 50 "bits" (50 = 16 + 2 + 16 + 16)
        self.taille_metadonnees_dict = 50
        
        # taille d'un paquet élémentaire du dict avant de l'adjoindre au paquet
        # du bitstream
        self.taille_paquet_elementaire_dict = self.bufsize - self.taille_metadonnees_dict
        
        # les métadonnées des paquets envoyés pour former le bitstream du body
        # ont une taille de 66 "bits" (66 = 16 + 2 + 16 + 16 + 16)
        self.taille_metadonnees_body = 66
        
        # taille d'un paquet élémentaire du dict avant de l'adjoindre au paquet
        # du bitstream (de taille 66 + taille_paquet_elementaire_body, qui vaut 
        # bufsize par définition)
        self.taille_paquet_elementaire_body = self.bufsize - self.taille_metadonnees_body
        
        # encodage du dictionnaire de huffman associé à la frame **entière**
        self.huff = Huffman([tuple_RLE for macrobloc in self.frame for tuple_RLE in macrobloc])
        self.dict_huffman_encode = self.huff.dictToBin()
        
        # définit la taille des données compressées **utiles** du body
        self.taille_donnees_compressees_huffman = 0
    
    
    @staticmethod
    def generer_frame_RLE(macroblock_size, total_num_of_macroblocks):
        """
        Permet de générer une frame RLE aléatoirement.
        Args:
            macroblock_size (int >= 2): taille d'un macrobloc
        Returns:
            frame: frame RLE (liste de listes de tuples d'entiers) générée aléatoirement
        """
        frame = []
        valeur_non_nulle_maximale = 30 # par exemple
        nb_tuples_RLE_max = macroblock_size**2 // 2
        
        for num_macrobloc in range(total_num_of_macroblocks):
            macrobloc = []
            
            nb_tuples_RLE = randint(1, nb_tuples_RLE_max)
            nb_zeros = macroblock_size**2 - nb_tuples_RLE # approximation raisonnable
            
            # on cherche ici à trouver nb_tuples_RLE entiers aléatoires dont la somme 
            # est nb_zeros
            
            moyenne = nb_zeros // nb_tuples_RLE + 1
            
            nb_zeros_partiel = 0
            for num_tuple_RLE in range(nb_tuples_RLE):
                if num_tuple_RLE != nb_tuples_RLE - 1:
                    a = randint(0, moyenne)
                    nb_zeros_partiel += a
                    
                    # on met à jour la moyenne du nombre de zeros par tuple RLE restant
                    # afin d'avoir les coefficients les plus homogènes possibles
                    moyenne = (nb_zeros - nb_zeros_partiel) // (nb_tuples_RLE - num_tuple_RLE - 1) + 1
                
                else:
                    a = nb_zeros - nb_zeros_partiel # = nombre de zéros restants
                
                b = randint(1, valeur_non_nulle_maximale)
                macrobloc.append((a, b))
            
            frame.append(macrobloc)
        
        return(frame)
    
    
    def send_header_bitstream(self):
        """
        Permet d'envoyer le bitstream associé au header du client au serveur. 
        """
        header_bitstream = self.bit_generator.construct_header()
        
        # envoi du paquet en 1 seule fois, car len(header_bitstream) = 48,
        # et 48 <= 67 <= bufsize
        self.client.send_data_to_server(header_bitstream)
        self.client.wait_for_response()
    
    
    def send_dict_bitstream(self):
        """
        Permet d'envoyer le bitstream associé au dict du client au serveur.
        """
        
        # définition du nombre de paquets qui vont être générés à partir du dictionnaire
        # de huffman encodé
        len_dict_bitstream = len(self.dict_huffman_encode)
        if len_dict_bitstream % self.taille_paquet_elementaire_dict == 0:
            nb_paquets_dict = len_dict_bitstream // self.taille_paquet_elementaire_dict
        else:
            nb_paquets_dict = len_dict_bitstream // self.taille_paquet_elementaire_dict + 1
        
        # construction du dict, paquet par paquet
        for num_paquet_dict in range(nb_paquets_dict):
            indice_initial = num_paquet_dict * self.taille_paquet_elementaire_dict
            
            if num_paquet_dict != nb_paquets_dict - 1:
                indice_final = indice_initial + self.taille_paquet_elementaire_dict
                donnees_paquet = self.dict_huffman_encode[indice_initial : indice_final]
            
            else:
                # dernier paquet
                donnees_paquet = self.dict_huffman_encode[indice_initial : ]
            
            nouv_paquet_dict = self.bit_generator.construct_dict(donnees_paquet)
            
            # envoi du paquet en 1 seule fois, car, par construction,
            # len(nouv_paquet_dict) < bufsize 
            self.client.send_data_to_server(nouv_paquet_dict)
            self.client.wait_for_response()
    
    
    def send_macrobloc_bitstream(self, num_macrobloc, macrobloc_encode):
        """
        Permet d'envoyer le bitstream associé à un macrobloc encodé du client 
        au serveur.
        """
        
        # réinitialisation de l'index du paquet associé au macrobloc actuel
        self.bit_generator.index_paquet_macrobloc = 0
        
        # définition du nombre de paquets qui vont être générés à partir du
        # macrobloc encodé
        len_macrobloc_encode = len(macrobloc_encode)
        if len_macrobloc_encode % self.taille_paquet_elementaire_body == 0:
            nb_paquets_macrobloc = len_macrobloc_encode // self.taille_paquet_elementaire_body
        else:
            nb_paquets_macrobloc = len_macrobloc_encode // self.taille_paquet_elementaire_body + 1
        
        # construction du bitstream associé au macrobloc, paquet par paquet
        for num_paquet_macrobloc in range(nb_paquets_macrobloc):
            indice_initial = num_paquet_macrobloc * self.taille_paquet_elementaire_body
            
            if num_paquet_macrobloc != nb_paquets_macrobloc - 1:
                indice_final = indice_initial + self.taille_paquet_elementaire_body
                donnees_paquet = macrobloc_encode[indice_initial : indice_final]
            
            else:
                # dernier paquet
                donnees_paquet = macrobloc_encode[indice_initial : ]
            
            nouv_paquet_macrobloc = self.bit_generator.construct_body(num_macrobloc, donnees_paquet)
            # envoi du paquet en 1 seule fois, car, par construction,
            # len(nouv_paquet_macrobloc) = bufsize, ou bien 
            # len(nouv_paquet_macrobloc) <= bufsize pour le tout dernier paquet
            self.client.send_data_to_server(nouv_paquet_macrobloc)
            self.client.wait_for_response()
    
    
    def send_body_bitstream(self):
        """
        Permet d'envoyer le bitstream associé au body du client au serveur.
        """
        for num_macrobloc in range(self.total_num_of_macroblocks):
            macrobloc = self.frame[num_macrobloc]
            macrobloc_encode = self.huff.encode_phrase(phrase=macrobloc)
            self.taille_donnees_compressees_huffman += len(macrobloc_encode)
            self.send_macrobloc_bitstream(num_macrobloc, macrobloc_encode)
    
    
    def send_tail_bitstream(self):
        """
        Permet d'envoyer le bitstream associé au tail du client au serveur.
        """
        tail_bitstream = self.bit_generator.construct_end_message()
        
        # envoi du paquet en 1 seule fois, car len(tail_bitstream) = 18,
        # et 18 <= 67 <= bufsize
        self.client.send_data_to_server(tail_bitstream)
        self.client.wait_for_response()
    
    
    def send_frame_RLE(self):
        """
        Méthode de synthèse.
        Permet d'envoyer le bitstream total du client au serveur.
        """
        self.send_header_bitstream()
        self.send_dict_bitstream()
        self.send_body_bitstream()
        self.send_tail_bitstream()


###############################################################################


# Exemple concret

if __name__ == "__main__":    
    # on définit une frame
    
    frame_id = randint(0, 65535) # 65535 = 2**16 - 1
    
    macroblock_size = 8
    
    num_of_macroblocks_per_line = 4
    num_of_macroblocks_per_column = 4
    
    total_num_of_macroblocks = num_of_macroblocks_per_line * num_of_macroblocks_per_column
    
    img_width = num_of_macroblocks_per_line * macroblock_size
    img_height = num_of_macroblocks_per_column * macroblock_size
    
    img_size = (img_width, img_height)
    
    # booléen indiquant si l'on veut afficher les messages entre le client et
    # le serveur (+ la frame générée et décodée + le bitstream total)
    affiche_messages = False
    
    # génération aléatoire d'une frame RLE
    frame = BitstreamSender.generer_frame_RLE(macroblock_size, total_num_of_macroblocks)
    log = Logger.get_instance()
    if affiche_messages:
        log.debug(f"\nFrame de référence (générée aléatoirement) :\n{frame}\n")
    
    #------------------------------------------------------------------------#
    
    # définition du bufsize (très important)
    
    # On DOIT avoir bufsize >= 67 (pour que l'on puisse envoyer en 1 seule fois
    # le header et la queue du bitstream, et pour que l'on puisse envoyer correctement 
    # chacun des paquets constituant dict et body
    
    # En effet, la taille maximale des "métadonnées" associées à chacun des 
    # paquets élémentaires de dict et de body est de 66 bits (enfin, pour être 
    # précis, ce sont des chaînes de caractère de taille <= 66 qui sont uniquement 
    # composées de '0' et de '1', mais chacun de ces '0' et '1' est codé sur 8 
    # bits, donc sur un octet, donc en réalité ces métadonnées ont une taille 
    # <= 66 octets, et non <= 66 bits)
    
    # Rappel :
    # taille métadonnées dict = 50 "bits"
    # taille métadonnées body = 66 "bits"
    
    # Le bufsize est souvent une puissance de 2, et désigne le nombre maximal
    # d'octets qui pourront être reçus (resp. être envoyés) par le serveur (resp. 
    # le client)
    
    # Afin de minimiser le temps d'envoi des données via le réseau, on a tout
    # intérêt à maximiser le bufsize
    
    puiss_2_random = randint(10, 12)
    bufsize = 2 ** puiss_2_random # /!\ bufsize >= 67 /!\
    
    #------------------------------------------------------------------------#
    
    # initialisation de la partie réseau
    
    HOST = 'localhost' # localhost ou bien adresse IP
    PORT = randint(5000, 15000)
    
    serv = Server(HOST, PORT, bufsize, affiche_messages)
    cli = Client(serv)
    
    global received_data
    received_data = "" # bitstream reçu par le serveur, construit itérativement
    
    def on_received_data(data):
        """
        Fonction appelée lorsque des données sont reçues par le serveur.
        On suppose que les données en entrée ont déjà été décodées via la 
        méthode decode().
        """
        global received_data 
        received_data += data
    
    # on met le serveur en mode écoute
    serv.listen_for_packets(cli, callback=on_received_data)
    
    #------------------------------------------------------------------------#
    
    # envoi du bitstream de la frame RLE du client au serveur
    
    bit_sender = BitstreamSender(frame_id, img_size, macroblock_size, frame, cli, bufsize)
    bit_sender.send_frame_RLE()
    
    #------------------------------------------------------------------------#
    
    # décodage du bitstream total reçu par le serveur via l'algo de Huffman
    frame_decodee = BitstreamGenerator.decode_bitstream_RLE(received_data)
    
    #------------------------------------------------------------------------#
    
    # prints de synthèse
    
    if affiche_messages:
        log.debug(f"\nBitstream total reçu par le serveur (associé à la frame) :\n{received_data}\n")
        log.debug(f"\nDécodage du bitstream de la frame :\n{frame_decodee}\n")
    
    if not(affiche_messages):
        print("\n")
        log.debug("\nLes messages entre le serveur et le client n'ont ici pas été affichés pour plus de lisibilité.\n\n\n")
    
    # test de cohérence
    bool_test = (frame == frame_decodee)
    log.debug(f"\nFrame décodée == frame de référence : {bool_test}\n")
    
    # à titre informatif
    log.debug("\nINFOS UTILES / SYNTHÈSE :\n")
    log.debug(f"\nImage size : (width, height) = {img_size}")
    log.debug(f"\nMacroblock size : {macroblock_size}x{macroblock_size}")
    log.debug(f"\nNombre total de macroblocs : {total_num_of_macroblocks}")
    log.debug(f"\nBufsize (ici : puissance de 2 aléatoire) : {bufsize}\n")
    
    # taille des parties principales du bitstream comparées à sa taille totale
    # Remarque : len(received_data) = len(bit_sender.bit_generator.bitstream)
    pourcentage_dict_bitstream = round(100 * bit_sender.bit_generator.len_dict_bitstream / len(received_data), 2)
    pourcentage_body_bitstream = round(100 * bit_sender.bit_generator.len_body_bitstream / len(received_data), 2)
    
    # taille des différentes composantes du bitstream (en octets / nombre de '0' et de '1')
    log.debug(f"\nTaille du bitstream total : {len(received_data)}")
    log.debug("\nTaille du header : 48 (taille constante)")
    log.debug(f"\nTaille de dict_bitstream : {bit_sender.bit_generator.len_dict_bitstream} ({pourcentage_dict_bitstream}%)")
    log.debug(f"\nTaille de body_bitstream : {bit_sender.bit_generator.len_body_bitstream} ({pourcentage_body_bitstream}%)")
    log.debug("\nTaille du tail : 18 (taille constante)\n")
    
    # taux de compression
    taille_originale_en_bits = 8 * 3 * img_width * img_height
    taux_compression = round(100 * len(received_data) / taille_originale_en_bits, 2)
    log.debug(f"\nTaux de compression : {taux_compression}%\n")
    
    #------------------------------------------------------------------------#
    
    # test pour encode_frame_RLE
    bitstream_genere = BitstreamGenerator.encode_frame_RLE(frame_id, img_size, macroblock_size, frame, bufsize)
    bool_coherence = (bitstream_genere == bit_sender.bit_generator.bitstream)
    log.debug(f"[Test d'une fonction-outil]\nBitstream généré par encode_frame_RLE == received_data : {bool_coherence}\n")
    
    #------------------------------------------------------------------------#
    
    # pour éviter d'avoir les messages de déconnexion des clients qui n'ont pas
    # été déconnectés des serveurs précédemment associés au même hôte
    # et puis, de toute façon, à ce stade, on n'a plus besoin du client (ni du
    # serveur)
    cli.connexion.close()

