# -*- coding: utf-8 -*-

import threading
from random import randint
from time import time, sleep


from EVEEX.network_transmission import Server, Client
from EVEEX.huffman import Huffman

###############################################################################

# définition des variables globales (ici : les différents types de messages à encoder)

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
        les méthodes statiques de la classe Huffman. Fonction essentielle au début
        de la phase de décodage.
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


class ThreadWriteInBitstreamBuffer(threading.Thread):
    """
    Thread qui va permettre d'append le bitstream à la fin d'un buffer, paquet
    par paquet.
    """
    def __init__(self, frame_id, img_size, macroblock_size, frame, bufsize):
        threading.Thread.__init__(self)
        
        self.bit_generator = BitstreamGenerator(frame_id, img_size, macroblock_size)
        
        # liste de listes de tuples
        # chacune des sous-listes (qui sont ici des listes de tuples) correspond 
        # en fait à la représentation RLE d'un macrobloc
        self.frame = frame
        
        # c'est aussi égal à (img_size[0] * img_size[1]) // macroblock_size**2
        self.total_num_of_macroblocks = len(self.frame)
        
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
        
        # initialisation du nombre de paquets qui seront envoyés du client au 
        # serveur, et qui sont associés au dict (resp. au body)
        self.nb_paquets_dict = None
        self.nb_paquets_body = None
        
        # génération puis encodage du dictionnaire de huffman associé à la 
        # frame **entière**
        t_debut_generation_dico_huffman = time()
        self.huff = Huffman([tuple_RLE for macrobloc in self.frame for tuple_RLE in macrobloc])
        t_fin_generation_dico_huffman = time()
        self.duree_generation_dico_huffman = t_fin_generation_dico_huffman - t_debut_generation_dico_huffman
        self.dict_huffman_encode = self.huff.dictToBin()
        
        # définit la taille des données compressées **utiles** du body
        self.taille_donnees_compressees_huffman = 0
        
        # buffer qui se remplit si jamais verrou_buffer_bitstream est déjà acquis
        # par le thread principal
        self.buffer_interne = ""
    
    
    def add_header_to_buffer(self):
        """
        Permet d'ajouter le bitstream associé au header à la fin du buffer.
        """
        header_bitstream = self.bit_generator.construct_header()
        
        global bitstream_buffer
        global verrou_bitstream_buffer
        
        if not(verrou_bitstream_buffer.locked()):
            # ajout des données à la fin du buffer
            verrou_bitstream_buffer.acquire() # opération bloquante par défaut
            bitstream_buffer += header_bitstream
            verrou_bitstream_buffer.release()
        
        else:
            self.buffer_interne += header_bitstream
    
    
    def add_dict_to_buffer(self):
        """
        Permet d'ajouter le bitstream associé au dict à la fin du buffer.
        """
        global bitstream_buffer
        global verrou_bitstream_buffer
        
        # définition du nombre de paquets qui vont être générés à partir du dictionnaire
        # de huffman encodé
        len_dict_bitstream = len(self.dict_huffman_encode)
        if len_dict_bitstream % self.taille_paquet_elementaire_dict == 0:
            self.nb_paquets_dict = len_dict_bitstream // self.taille_paquet_elementaire_dict
        else:
            self.nb_paquets_dict = len_dict_bitstream // self.taille_paquet_elementaire_dict + 1
        
        # construction du dict, paquet par paquet
        for num_paquet_dict in range(self.nb_paquets_dict):
            indice_initial = num_paquet_dict * self.taille_paquet_elementaire_dict
            
            if num_paquet_dict != self.nb_paquets_dict - 1:
                indice_final = indice_initial + self.taille_paquet_elementaire_dict
                donnees_paquet = self.dict_huffman_encode[indice_initial : indice_final]
            
            else:
                # dernier paquet
                donnees_paquet = self.dict_huffman_encode[indice_initial : ]
            
            nouv_paquet_dict = self.bit_generator.construct_dict(donnees_paquet)
            
            #-----------------------------------------------------------------#
            
            if not(verrou_bitstream_buffer.locked()):
                # ajout des données à la fin du buffer
                verrou_bitstream_buffer.acquire() # opération bloquante par défaut
                bitstream_buffer += self.buffer_interne + nouv_paquet_dict
                verrou_bitstream_buffer.release()
                
                # ré-initialisation du buffer interne
                self.buffer_interne = ""
            
            else:
                self.buffer_interne += nouv_paquet_dict
    
    
    def add_macrobloc_to_buffer(self, num_macrobloc, macrobloc_encode):
        """
        Permet d'ajouter le bitstream associé à un macrobloc encodé à la fin du 
        buffer.
        """
        global bitstream_buffer
        global verrou_bitstream_buffer
        
        # réinitialisation de l'index du paquet associé au macrobloc actuel
        self.bit_generator.index_paquet_macrobloc = 0
        
        # définition du nombre de paquets qui vont être générés à partir du
        # macrobloc encodé
        len_macrobloc_encode = len(macrobloc_encode)
        if len_macrobloc_encode % self.taille_paquet_elementaire_body == 0:
            nb_paquets_macrobloc = len_macrobloc_encode // self.taille_paquet_elementaire_body
        else:
            nb_paquets_macrobloc = len_macrobloc_encode // self.taille_paquet_elementaire_body + 1
        
        self.nb_paquets_body += nb_paquets_macrobloc
        
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
            
            #-----------------------------------------------------------------#
            
            if not(verrou_bitstream_buffer.locked()):
                # ajout des données à la fin du buffer
                verrou_bitstream_buffer.acquire() # opération bloquante par défaut
                bitstream_buffer += self.buffer_interne + nouv_paquet_macrobloc
                verrou_bitstream_buffer.release()
                
                # ré-initialisation du buffer interne
                self.buffer_interne = ""
            
            else:
                self.buffer_interne += nouv_paquet_macrobloc
    
    
    def add_body_to_buffer(self):
        """
        Permet d'ajouter le bitstream associé au body à la fin du buffer.
        """
        self.nb_paquets_body = 0
        
        for num_macrobloc in range(self.total_num_of_macroblocks):
            macrobloc = self.frame[num_macrobloc]
            macrobloc_encode = self.huff.encode_phrase(phrase=macrobloc)
            self.taille_donnees_compressees_huffman += len(macrobloc_encode)
            self.add_macrobloc_to_buffer(num_macrobloc, macrobloc_encode)
    
    
    def add_tail_to_buffer(self):
        """
        Permet d'ajouter le bitstream associé au tail à la fin du buffer.
        """
        tail_bitstream = self.bit_generator.construct_end_message()
        
        global bitstream_buffer
        global verrou_bitstream_buffer
        
        # ajout des données à la fin du buffer
        # ici, on ne teste pas si le verrou est verrouillé ou non, car on va dans
        # tous les cas rajouter les dernières données au buffer du bitstream (comme
        # il s'agit du dernier paquet que l'on va envoyer)
        verrou_bitstream_buffer.acquire() # opération bloquante par défaut
        bitstream_buffer += self.buffer_interne + tail_bitstream
        verrou_bitstream_buffer.release()
        
        # ré-initialisation du buffer interne (pas obligatoire, car on ne 
        # l'utilise plus)
        self.buffer_interne = ""
    
    
    def run(self):
        """
        Cette méthode définit le code qui va s'exécuter automatiquement dès
        que l'instance de ThreadWriteInBitstreamBuffer en question aura été 
        démarrée avec la méthode 'start' de threading.Thread.
        
        Méthode de synthèse.
        Permet d'écrire toutes les composantes du bitstream dans le buffer.
        """
        self.add_header_to_buffer()
        self.add_dict_to_buffer()
        self.add_body_to_buffer()
        self.add_tail_to_buffer()


###############################################################################


class BitstreamSender:
    """
    Classe permettant de gérer l'envoi d'un bitstream via un réseau, d'un client
    à un serveur.
    """
    def __init__(self, frame_id, img_size, macroblock_size, frame, client, bufsize):
        # comme le client est défini par rapport à un serveur prédéfini, on n'a
        # pas besoin de créer une variable d'instance 'server'
        self.client = client
        
        # concrètement, les métadonnées des paquets envoyés pour former le bitstream
        # du dict font 50 "bits" (50 = 16 + 2 + 16 + 16)
        self.taille_metadonnees_dict = 50
        
        # les métadonnées des paquets envoyés pour former le bitstream du body
        # ont une taille de 66 "bits" (66 = 16 + 2 + 16 + 16 + 16)
        self.taille_metadonnees_body = 66
        
        global bitstream_buffer
        bitstream_buffer = ""
        
        global verrou_bitstream_buffer
        verrou_bitstream_buffer = threading.Lock()
        
        self.th_WriteInBitstreamBuffer = ThreadWriteInBitstreamBuffer(frame_id, img_size, macroblock_size, frame, bufsize)
    
    
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
        
        # pour une frame RLE associée à un seul macrobloc
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
    
    
    def start_sending_messages(self):
        """
        Envoi du bitstream complet du client au serveur, paquet par paquet, à 
        partir des données contenues dans buffer_bitstream (buffer qui est rempli
        par un thread en parallèle).
        """
        self.th_WriteInBitstreamBuffer.start()
        
        global bitstream_buffer
        global verrou_bitstream_buffer
        
        while True:
            verrou_bitstream_buffer.acquire() # opération bloquante par défaut
            
            str_type_msg = bitstream_buffer[16 : 18]
            
            if str_type_msg != "":
                type_msg = int(str_type_msg, 2)
                
                if type_msg == HEADER_MSG:
                    # taille constante
                    data_size = 48
                
                elif type_msg == DICT_MSG:
                    # extraction de la taille du paquet associé au dictionnaire de 
                    # huffman encodé
                    data_size = self.taille_metadonnees_dict + int(bitstream_buffer[34 : 50], 2)
                
                elif type_msg == BODY_MSG:
                    # extraction de la taille du paquet associé au body (ie aux
                    # différents macroblocs)
                    data_size = self.taille_metadonnees_body + int(bitstream_buffer[50 : 66], 2)
                
                # ici, on a nécessairement type_msg = TAIL_MSG
                else:
                    # taille constante
                    data_size = 18
                
                # extraction des données du buffer
                data = bitstream_buffer[ : data_size]
                
                # suppression des données du buffer
                bitstream_buffer = bitstream_buffer[data_size : ]
                
                verrou_bitstream_buffer.release()
                
                # envoi du paquet en 1 seule fois, car par construction on a
                # len(data) = bufsize ou len(data) < bufsize
                self.client.send_data_to_server(data)
                self.client.wait_for_response()
                
                if type_msg == TAIL_MSG:
                    break
            
            else:
                verrou_bitstream_buffer.release()


###############################################################################


# Exemple concret

if __name__ == "__main__":
    from logger import Logger, LogLevel
    log = Logger.get_instance()
    log.set_log_level(LogLevel.DEBUG)
    #log.start_file_logging("log_bitstream.log")
    
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
    
    # On désactive les messages par défaut si on sait qu'il va y avoir beaucoup de
    # données à afficher
    if img_width * img_height > 10000:
        affiche_messages = False
    
    # génération aléatoire d'une frame RLE
    frame = BitstreamSender.generer_frame_RLE(macroblock_size, total_num_of_macroblocks)
    
    if affiche_messages:
        print("\n")
        log.debug(f"Frame de référence (générée aléatoirement) :\n{frame}\n")
    
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
    
    print("\n")
    
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
    bit_sender.start_sending_messages()
    
    # pour laisser le temps au message associé au dernier paquet réseau de se print 
    # correctement
    if affiche_messages:
        sleep(0.1)
    
    else:
        log.debug("Les messages entre le serveur et le client n'ont ici pas été affichés pour plus de lisibilité.\n\n")
    
    # on termine le thread d'écriture dans le buffer du bitstream
    bit_sender.th_WriteInBitstreamBuffer.join()
    log.debug("Thread d'écriture dans le buffer du bitstream supprimé.\n")
    
    # fermeture du socket créé, du côté serveur ET du côté client
    # on termine également le thread d'écoute du serveur
    cli.connexion.close()
    serv.th_Listen.join()
    serv.mySocket.close()
    
    # pour laisser le temps au message associé à la fermeture de la connexion du 
    # client de se print correctement
    sleep(0.1)
    
    log.debug("Thread d'écoute du serveur supprimé.")
    log.debug("Serveur supprimé.\n\n")
    
    #------------------------------------------------------------------------#
    
    # décodage du bitstream total reçu par le serveur via l'algo de Huffman
    frame_decodee = BitstreamGenerator.decode_bitstream_RLE(received_data)
    
    #------------------------------------------------------------------------#
    
    # prints de synthèse / débuggage
    
    if affiche_messages:
        log.debug(f"Bitstream total reçu par le serveur (associé à la frame) :\n{received_data}\n\n")
        log.debug(f"Décodage du bitstream de la frame :\n{frame_decodee}\n\n")
    
    # test de cohérence
    bool_test = (frame == frame_decodee)
    log.debug(f"Frame décodée == frame de référence : {str(bool_test).upper()}\n\n")
    
    # à titre informatif
    log.debug("INFOS UTILES / SYNTHÈSE :\n")
    log.debug(f"Image size : (width, height) = {img_size}")
    log.debug(f"Macroblock size : {macroblock_size}x{macroblock_size}")
    log.debug(f"Nombre total de macroblocs : {total_num_of_macroblocks}")
    log.debug(f"Bufsize (ici : puissance de 2 aléatoire) : {bufsize}\n")
    
    # taille des parties principales du bitstream comparées à sa taille totale
    # Remarque : len(received_data) = len(bit_sender.th_WriteInBitstreamBuffer.bit_generator.bitstream)
    len_dict_bitstream = bit_sender.th_WriteInBitstreamBuffer.bit_generator.len_dict_bitstream
    len_body_bitstream = bit_sender.th_WriteInBitstreamBuffer.bit_generator.len_body_bitstream
    len_received_data = len(received_data)
    pourcentage_dict_bitstream = round(100 * len_dict_bitstream / len_received_data, 2)
    pourcentage_body_bitstream = round(100 * len_body_bitstream / len_received_data, 2)
    
    # taille des différentes composantes du bitstream (en octets / "bits" / nombre de '0' et de '1')
    log.debug(f"Taille du bitstream total : {len_received_data} \"bits\"")
    log.debug("Taille du header : 48 (taille constante)")
    log.debug(f"Taille de dict_bitstream : {len_dict_bitstream} ({pourcentage_dict_bitstream:.2f}%)")
    log.debug(f"Taille de body_bitstream : {len_body_bitstream} ({pourcentage_body_bitstream:.2f}%)")
    log.debug("Taille du tail : 18 (taille constante)\n")
    
    # taux de compression (il n'a pas de réel sens physique ici, mais c'est toujours
    # intéressant de le calculer)
    taille_originale_en_bits = 8 * 3 * img_width * img_height
    taux_compression = round(100 * len(received_data) / taille_originale_en_bits, 2)
    log.debug(f"Taux de compression : {taux_compression:.2f}%\n")
    
    #------------------------------------------------------------------------#
    
    # test pour encode_frame_RLE
    bitstream_genere = BitstreamGenerator.encode_frame_RLE(frame_id, img_size, macroblock_size, frame, bufsize)
    bool_coherence = (bitstream_genere == bit_sender.th_WriteInBitstreamBuffer.bit_generator.bitstream)
    log.debug(f"[Test d'une fonction-outil] Bitstream généré par encode_frame_RLE == received_data : {str(bool_coherence).upper()}\n")
    
    #log.stop_file_logging()

