# -*- coding: utf-8 -*-

from random import randint
from huffman import Huffman
from network_transmission import Server, Client
from logger import Logger

###############################################################################


class BitstreamGenerator:
    """
    Classe permettant de générer un bitstream à partir des infos d'une frame 
    en entrée (après RLE).
    Concrètement, le bitstream d'une frame est constitué de 4 éléments :
        - header: en-tête
        - dict: relatif au dictionnaire de Huffman de la frame encodée (construit itérativement)
        - body: relatif à la frame encodée (construit itérativement)
        - tail: fin du bitstream
    """
    
    def __init__(self, frame_id, img_size, macroblock_size):
        # définition des variables globales (= différents types de messages à encoder)
        
        global HEADER_MSG
        HEADER_MSG = 0
        
        global DICT_MSG
        DICT_MSG = 1
        
        global BODY_MSG
        BODY_MSG = 2
        
        global TAIL_MSG
        TAIL_MSG = 3
        
        # variables d'instance
        
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
        Construit le bitstream d'en-tête de l'image à partir des informations 
        entrées lors de l'instanciation de la classe.
        Returns:
            bitstream (string): le bitstream représentant le header de la frame
        """
        # header = frame_id + type_msg + taille image + taille macroblocs
        self.header = self.int2bin(self.frame_id, 16) + self.int2bin(HEADER_MSG, 2) + \
                      self.int2bin(self.img_size, 16) + self.int2bin(self.macroblock_size, 5)
        
        self.bitstream += self.header
        
        return(self.header)
    
    
    def construct_dict(self, dict_huffman_packet):
        """
        Construit le bitstream représentant le dictionnaire de huffman associé
        à la frame (après RLE), converti en binaire.
        
        Remarque importante : à part pour le tout dernier paquet provenant des données
        utiles du dictionnaire de huffman encodé, on aura toujours la relation 
        suivante : len(dict_huffman_packet) = bufsize - 50 = taille_paquet_elementaire,
        et donc len(nouv_contenu_dict) = taille_paquet_elementaire + 50 = bufsize.
        Pour le tout dernier paquet, on aura juste len(dict_huffman_packet) <= bufsize - 50
        et len(nouv_contenu_dict) <= bufsize.
        La raison pour laquelle on inclut quand même la taille des paquets est précisément
        ce dernier paquet, qui n'est pas nécessairement de la même taille que tous 
        les autres.
        
        --> Cette remarque est aussi valable pour la méthode construct_body.
        
        Args:
            dict_huffman_packet: paquet d'un dictionnaire de huffman encodé en binaire
        Returns:
            bitstream (string): le bitstream représentant une partie du dictionnaire 
                                de huffman
        """
        # nouv_contenu_dict = frame_id + type_msg + index + taille paquet + paquet 
        nouv_contenu_dict = self.int2bin(self.frame_id, 16) + self.int2bin(DICT_MSG, 2) + \
                            self.int2bin(self.index_dict, 16) + \
                            self.int2bin(len(dict_huffman_packet), 16) + dict_huffman_packet
        
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
        # nouveau contenu = frame_id + type_msg + index + taille paquet + paquet
        nouv_contenu_body = self.int2bin(self.frame_id, 16) + self.int2bin(BODY_MSG, 2) + \
                            self.int2bin(self.index_body, 16) + \
                            self.int2bin(len(huffman_packet), 16) + huffman_packet
        
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
        self.tail = self.int2bin(self.frame_id, 16) + self.int2bin(TAIL_MSG, 2)
        self.bitstream += self.tail
        
        return(self.tail)
    
    
    @staticmethod
    def encode_frame_RLE(frame_id, img_size, macroblock_size, frame, bufsize):
        """
        Permet de convertir une frame RLE en un bitstream.
        Args:
            frame_id: identifiant de la frame (int)
            img_size: nombre de pixels de l'image (int > 0)
            macroblock_size: longueur des côtés des macroblocs (on suppose que
                             ce sont des carrés), int > 1
            frame: frame_RLE de référence (liste de tuples d'entiers)
            bufsize: taille maximale que peut prendre un paquet (int >= 51)
        Returns:
            bitstream_total: bitstream associé à la frame RLE de référence 
        """
        
        taille_paquet_elementaire = bufsize - 50
        
        # encodage de la frame et du dictionnaire de huffman associé à la frame
        huff = Huffman(frame)
        frame_encodee = huff.encode_phrase()
        dict_huffman_encode = huff.dictToBin()
        
        #--------------------------------------------------------------------#
        
        # initialisation du constructeur
        bit_generator = BitstreamGenerator(frame_id, img_size, macroblock_size)
        
        #--------------------------------------------------------------------#
        
        # construction du header
        bit_generator.construct_header()
        
        #--------------------------------------------------------------------#
                
        # définition du nombre de paquets qui vont être générés à partir du 
        # dictionnaire de huffman encodé
        len_dict_bitstream = len(dict_huffman_encode)
        if len_dict_bitstream % taille_paquet_elementaire == 0:
            nb_paquets_dict = len_dict_bitstream // taille_paquet_elementaire
        else:
            nb_paquets_dict = len_dict_bitstream // taille_paquet_elementaire + 1
        
        # construction du dict, paquet par paquet
        for num_paquet_dict in range(nb_paquets_dict):
            indice_initial = num_paquet_dict * taille_paquet_elementaire
            
            if num_paquet_dict != nb_paquets_dict - 1:
                indice_final = indice_initial + taille_paquet_elementaire
                donnees_paquet = dict_huffman_encode[indice_initial : indice_final]
            
            else:
                # dernier paquet
                donnees_paquet = dict_huffman_encode[indice_initial : ]
            
            bit_generator.construct_dict(donnees_paquet)
        
        #--------------------------------------------------------------------#
                
        # définition du nombre de paquets qui vont être générés à partir de la
        # frame encodée
        len_frame_encodee = len(frame_encodee)
        if len_frame_encodee % taille_paquet_elementaire == 0:
            nb_paquets_body = len_frame_encodee // taille_paquet_elementaire
        else:
            nb_paquets_body = len_frame_encodee // taille_paquet_elementaire + 1
        
        # construction du body, paquet par paquet
        for num_paquet_body in range(nb_paquets_body):
            indice_initial = num_paquet_body * taille_paquet_elementaire
            
            if num_paquet_body != nb_paquets_body - 1:
                indice_final = indice_initial + taille_paquet_elementaire
                donnees_paquet = frame_encodee[indice_initial : indice_final]
            
            else:
                # dernier paquet
                donnees_paquet = frame_encodee[indice_initial : ]
            
            bit_generator.construct_body(donnees_paquet)
        
        #--------------------------------------------------------------------#
        
        # construction de la queue du bitstream
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


class BitstreamSender:
    """
    Classe permettant de gérer l'envoi d'un bitstream via un réseau, d'un client
    à un serveur.
    """
    
    def __init__(self, frame_id, img_size, macroblock_size, frame, client, bufsize):
        self.bit_generator = BitstreamGenerator(frame_id, img_size, macroblock_size)
        
        self.frame = frame
        
        # comme le client est défini par rapport à un serveur prédéfini, on n'a
        # pas besoin de créer une variable d'instance 'server'
        self.client = client
        
        self.bufsize = bufsize
        
        # taille d'un paquet élémentaire du dict ou du body avant de l'adjoindre
        # au paquet du bitstream (de taille 50 + taille_paquet_elementaire, qui
        # vaut bufsize par définition)
        # concrètement, les métadonnées des paquets envoyés pour former le bitstream
        # du dict et du body font exactement 50 bits (50 = 16 + 2 + 16 + 16)
        self.taille_paquet_elementaire = self.bufsize - 50
        
        # encodage de la frame et du dictionnaire de huffman associé
        huff = Huffman(self.frame)
        self.frame_encodee = huff.encode_phrase()
        self.dict_huffman_encode = huff.dictToBin()
    
    
    @staticmethod
    def generer_frame_RLE(img_size):
        """
        Permet de générer une frame RLE aléatoirement.
        Args:
            img_size (int >= 3): taille de l'image (= nombre de pixels)
        Returns:
            frame: frame RLE (liste de tuples d'entiers) générée aléatoirement
        """
        frame = []
        valeur_non_nulle_maximale = 30 # par exemple
        
        nb_tuples_RLE_max = img_size // 2
        
        nb_tuples_RLE = randint(1, nb_tuples_RLE_max)
        nb_zeros = img_size - nb_tuples_RLE # approximation raisonnable
        
        # on cherche donc à trouver nb_tuples_RLE entiers aléatoires dont la somme 
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
            frame.append((a, b))
        
        return(frame)
    
    
    def send_header_bitstream(self):
        """
        Permet d'envoyer le bitstream associé au header du client au serveur. 
        """
        header_bitstream = self.bit_generator.construct_header()
        
        # envoi du paquet en 1 seule fois, car len(header_bitstream) = 39,
        # et 39 <= 51 <= bufsize
        self.client.send_data_to_server(header_bitstream)
        self.client.wait_for_response()
    
    
    def send_dict_bitstream(self):
        """
        Permet d'envoyer le bitstream associé au dict du client au serveur.
        """
        
        # définition du nombre de paquets qui vont être générés à partir du dictionnaire
        # de huffman encodé
        len_dict_bitstream = len(self.dict_huffman_encode)
        if len_dict_bitstream % self.taille_paquet_elementaire == 0:
            nb_paquets_dict = len_dict_bitstream // self.taille_paquet_elementaire
        else:
            nb_paquets_dict = len_dict_bitstream // self.taille_paquet_elementaire + 1
        
        # construction du dict, paquet par paquet
        for num_paquet_dict in range(nb_paquets_dict):
            indice_initial = num_paquet_dict * self.taille_paquet_elementaire
            
            if num_paquet_dict != nb_paquets_dict - 1:
                indice_final = indice_initial + self.taille_paquet_elementaire
                donnees_paquet = self.dict_huffman_encode[indice_initial : indice_final]
            
            else:
                # dernier paquet
                donnees_paquet = self.dict_huffman_encode[indice_initial : ]
            
            nouv_paquet_dict = self.bit_generator.construct_dict(donnees_paquet)
            
            # envoi du paquet en 1 seule fois, car, par construction,
            # len(nouv_paquet_dict) = bufsize, ou bien len(nouv_paquet_dict) <= bufsize 
            # pour le tout dernier paquet
            self.client.send_data_to_server(nouv_paquet_dict)
            self.client.wait_for_response()
    
    
    def send_body_bitstream(self):
        """
        Permet d'envoyer le bitstream associé au body du client au serveur.
        """
        
        # définition du nombre de paquets qui vont être générés à partir de la frame
        # encodée
        len_frame_encodee = len(self.frame_encodee)
        if len_frame_encodee % self.taille_paquet_elementaire == 0:
            nb_paquets_body = len_frame_encodee // self.taille_paquet_elementaire
        else:
            nb_paquets_body = len_frame_encodee // self.taille_paquet_elementaire + 1
        
        # construction du body, paquet par paquet
        for num_paquet_body in range(nb_paquets_body):
            indice_initial = num_paquet_body * self.taille_paquet_elementaire
            
            if num_paquet_body != nb_paquets_body - 1:
                indice_final = indice_initial + self.taille_paquet_elementaire
                donnees_paquet = self.frame_encodee[indice_initial : indice_final]
            
            else:
                # dernier paquet
                donnees_paquet = self.frame_encodee[indice_initial : ]
            
            nouv_paquet_body = self.bit_generator.construct_body(donnees_paquet)
            # envoi du paquet en 1 seule fois, car, par construction,
            # len(nouv_paquet_body) = bufsize, ou bien len(nouv_paquet_body) <= bufsize 
            # pour le tout dernier paquet
            self.client.send_data_to_server(nouv_paquet_body)
            self.client.wait_for_response()
    
    
    def send_tail_bitstream(self):
        """
        Permet d'envoyer le bitstream associé au tail du client au serveur.
        """
        tail_bitstream = self.bit_generator.construct_end_message()
        
        # envoi du paquet en 1 seule fois, car len(tail_bitstream) = 18,
        # et 18 <= 51 <= bufsize
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
    nb_macroblocks = 4
    img_size = nb_macroblocks * macroblock_size**2
    
    # génération aléatoire d'une frame RLE
    frame = BitstreamSender.generer_frame_RLE(img_size)
    Logger.get_instance().debug("\nFrame (générée aléatoirement) :\n" + str(frame) + "\n")
    
    #------------------------------------------------------------------------#
    
    # définition du bufsize (très important)
    
    # On DOIT avoir bufsize >= 51 (pour que l'on puisse envoyer en 1 seule fois
    # le header et la queue du bitstream, et pour que l'on puisse envoyer correctement 
    # chacun des paquets constituant dict et body
    
    # En effet, les "métadonnées" associées à chacun des paquets élémentaires
    # de dict et de body font exactement 50 bits
    
    # Le bufsize est souvent une puissance de 2, et désigne le nombre maximal
    # d'octets qui pourront être reçus (resp. être envoyés) par le serveur (resp. 
    # le client)
    
    # Afin de minimiser le temps d'envoi des données via le réseau, on a tout
    # intérêt à maximiser le bufsize
    
    puiss_2_random = randint(6, 12)
    bufsize = 2 ** puiss_2_random # /!\ bufsize >= 51 /!\
    
    #------------------------------------------------------------------------#
    
    # initialisation de la partie réseau
    
    HOST = 'localhost' # localhost ou bien adresse IP
    PORT = randint(5000, 15000)
    
    serv = Server(HOST, PORT, bufsize)
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
    
    Logger.get_instance().debug("\nBitstream total reçu par le serveur (associé à la frame) :\n" + received_data + "\n")
    Logger.get_instance().debug("\nDécodage du bitstream de la frame :\n" + str(frame_decodee) + "\n")
    
    # test de cohérence
    bool_test = (frame == frame_decodee)
    Logger.get_instance().debug("\nFrame décodée == frame de référence : " + str(bool_test) + "\n")
    
    # à titre informatif
    Logger.get_instance().debug("\nINFOS UTILES / SYNTHÈSE :\n")
    Logger.get_instance().debug("\nImage size : " + str(img_size))
    Logger.get_instance().debug("\nNombre de tuples RLE : " + str(len(frame)))
    Logger.get_instance().debug("\nBufsize (ici : puissance de 2 aléatoire) : " + str(bufsize) + "\n")
    
    # taille des différentes composantes du bitstream
    Logger.get_instance().debug("\nTaille du bitstream total : " + str(len(received_data)))
    Logger.get_instance().debug("\nTaille de header_bitstream : " + str(len(bit_sender.bit_generator.header)) + " (taille constante)")
    Logger.get_instance().debug("\nTaille de dict_bitstream : " + str(len(bit_sender.bit_generator.dict)))
    Logger.get_instance().debug("\nTaille de body_bitstream : " + str(len(bit_sender.bit_generator.body)))
    Logger.get_instance().debug("\nTaille de tail_bitstream : " + str(len(bit_sender.bit_generator.tail)) + " (taille constante)" + "\n")
    
    #------------------------------------------------------------------------#
    
    # pour éviter d'avoir les messages de déconnexion des clients qui n'ont pas
    # été déconnectés des serveurs précédemment associés au même hôte
    # et puis, de toute façon, à ce stade, on n'a plus besoin du client (ni du
    # serveur)
    cli.connexion.close()

