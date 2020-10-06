# -*- coding: utf-8 -*-

import socket, sys, threading
from time import sleep
from logger import Logger

#############################################################################


class ThreadListen(threading.Thread):
    """
    Thread pour gérer le mode écoute du serveur.
    """
    def __init__(self, socket_server, callback, bufsize):
        threading.Thread.__init__(self)
        
        self.callback = callback
        
        self.socket_server = socket_server
        self.bufsize = bufsize
    
    
    @staticmethod
    def generer_description_paquet(msgClient):
        """
        Permet de générer la description d'un paquet reçu par le serveur.
        Args:
            msgClient: paquet (str) reçu par le serveur
        Returns:
            desc_paquet: str décrivant le paquet reçu
        """
        type_msg = int(msgClient[16 : 18], 2)
        
        # 'dict_types_msg' est une variable globale créée au moment de l'instanciation
        # de la classe Server
        desc_type_msg = dict_types_msg[type_msg]
        
        if type_msg in [1, 2]:
            index_ref = int(msgClient[18 : 34], 2)
            msg_index = "index_" + desc_type_msg + " = " + str(index_ref)
            desc_paquet = desc_type_msg + ", " + msg_index
        
        else:
            desc_paquet = desc_type_msg
        
        return(desc_paquet)
    
    
    def run(self):
        """
        Cette méthode définit le code qui va s'exécuter automatiquement dès
        que l'instance de ThreadListen en question aura été démarrée avec 
        la méthode 'start' de threading.Thread.
        """
        self.socket_server.listen(5)
        while True:
            # établissement de la connexion
            connexion, adresse = self.socket_server.accept()
            Server.safe_print("\nServeur> Client connecté, adresse IP %s, port %s.\n\n" % (adresse[0], adresse[1]))
            
            # dialogue avec le client            
            msgClient = connexion.recv(self.bufsize)
            msgClient = msgClient.decode("utf8")
            while True:     
                # au cas où
                if msgClient.upper() == "FIN" or msgClient == "":
                    break
                
                msgClient = connexion.recv(self.bufsize)
                msgClient = msgClient.decode("utf8")
                
                try:
                    if msgClient[0] in ['0', '1']:
                        self.callback(msgClient)
                        
                        desc_paquet = self.generer_description_paquet(msgClient)
                        msgServeur = "Données bien reçues : " + desc_paquet
                        
                        Server.safe_print("\nServeur> " + msgServeur)
                        msgServeur = msgServeur.encode("utf8")
                        connexion.send(msgServeur)
                        
                        # INDISPENSABLE pour permettre le traitement de l'information
                        # envoyée + son affichage dans la console
                        # Ici, sans cette commande, les messages sont affichés dans le
                        # mauvais ordre dans la console (bien qu'ils ne soient plus
                        # entremêlés grâce à la fonction safe_print)
                        # 'temps_pause_apres_envoi' est une variable globale créée
                        # au moment de l'instanciation de la classe Server
                        # --> Même remarque pour tous les autres 'sleep(temps_pause_envoi)' 
                        # du code
                        sleep(temps_pause_apres_envoi)
                
                except:
                    # si msgClient[0] n'existe pas (ou si c'est mal défini), 
                    # on passe simplement à la suite
                    pass
            
            connexion.close()    # on ferme la connexion côté serveur
            Server.safe_print("\nServeur> Client déconnecté.")


#############################################################################


class Server:
    """
    Classe permettant à une entité d'écouter et d'attendre de recevoir des 
    paquets depuis un correspondant connu ou inconnu.
    """
    def __init__(self, HOST, PORT, bufsize):
        self.HOST = HOST
        self.PORT = PORT
        self.bufsize = bufsize
        
        global verrou
        verrou = threading.RLock()
        
        self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.mySocket.bind((self.HOST, self.PORT))
        except socket.error:
            self.safe_print("\nServeur> La liaison du socket à l'adresse choisie a échoué.")
            sys.exit()
        self.safe_print("\nServeur> Serveur prêt, en attente de requêtes ...")
        
        global temps_pause_apres_envoi
        temps_pause_apres_envoi = 0.01 # en secondes
        
        global dict_types_msg
        dict_types_msg = {0 : "header", 1 : "dict", 2 : "body", 3 : "tail"}
    
    
    @staticmethod
    def safe_print(texte):
        """
        Permet de print sans se soucier des autres prints 'quasiment simultanés' dans
        d'autres threads. 
        Ici, sans cette fonction, les blocs de str s'entremêleront lors de leur
        affichage dans la console.
        Il s'agit en fait d'une sorte de 'print bloquant'.
        """
        # 'verrou' est une variable globale qui sera créée au moment de
        # l'instanciation de la classe Server
        try:
            verrou.acquire()
            Logger.get_instance().debug(texte)
        finally:
            verrou.release()
    
    
    def listen_for_packets(self, client, callback):
        """
        Se met en mode écoute dans un thread séparé et attend de recevoir
        des informations par le réseau. 
        Permet également au client de se
        connecter au serveur.
        Args:
            client: client qui va interagir avec le serveur
            callback: fonction à appeler dès que le serveur reçoit des données
        """
        th_Listen = ThreadListen(self.mySocket, callback, self.bufsize)
        th_Listen.start()
        
        client.connect_to_server()


#############################################################################


class Client:
    """
    Permet d'envoyer par le réseau des données à une entité connue.
    Args:
        server: serveur auquel le client veut se connecter
    """
    def __init__(self, server):        
        self.HOST = server.HOST        
        self.PORT = server.PORT
        self.bufsize = server.bufsize
        
        self.connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.premier_message_envoye = True
    
    
    def connect_to_server(self):
        """
        Connecte le client au serveur.
        """
        try:
            self.connexion.connect((self.HOST, self.PORT))
        except socket.error:
            Server.safe_print("\nClient> La connexion a échoué.")
            sys.exit()
        Server.safe_print("\nClient> Connexion établie avec le serveur.")
    
    
    def send_data_to_server(self, data):
        """
        Envoie les données au serveur en ouvrant un tunnel TCP avec ce dernier.
        Args:
            data: les données à transmettre (type: str)
        """
        if self.premier_message_envoye:
            # pour 'activer' le dialogue avec le client, on a besoin d'un premier
            # message
            msg_filler = "filler"
            msg_filler = msg_filler.encode("utf8")
            self.connexion.send(msg_filler)
            sleep(temps_pause_apres_envoi)
            self.premier_message_envoye = False
        
        Server.safe_print("\nClient> " + data)
        data = data.encode("utf8")
        self.connexion.send(data)
        sleep(temps_pause_apres_envoi)
    
    
    def wait_for_response(self):
        """
        Fonction outil permettant d'attendre que le serveur réponde avant de poursuivre
        le traitement des données.
        """
        msgServeur = self.connexion.recv(self.bufsize)
        msgServeur = msgServeur.decode("utf8")
        while True:
            # au cas où
            if msgServeur.upper() == "FIN" or msgServeur == "":
                self.connexion.close()
                break
            
            else:
                try:
                    if msgServeur[ : 19] == "Données bien reçues":
                        desc_paquet = msgServeur[22 : ]
                        Server.safe_print("\nClient> Réponse du serveur reçue : " + desc_paquet + "\n\n")
                        break
                except:
                    pass
            
            msgServeur = self.connexion.recv(self.bufsize)
            msgServeur = msgServeur.decode("utf8")
