# -*- coding: utf-8 -*-

import socket, sys, threading
from time import sleep
from logger import Logger


#############################################################################


class ThreadListen(threading.Thread):
    """
    Thread pour gérer le mode écoute du serveur.
    """
    def __init__(self, socket_server, callback, bufsize, affiche_messages):
        threading.Thread.__init__(self)
        
        self.callback = callback
        
        self.socket_server = socket_server
        self.bufsize = bufsize
        self.affiche_messages = affiche_messages
    
    
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
        
        # dict
        if type_msg == 1:
            index_paquet_dict = int(msgClient[18 : 34], 2)
            desc_paquet = f"dict, index_paquet_dict = {index_paquet_dict}"
        
        # body
        elif type_msg == 2:
            num_macrobloc = int(msgClient[18 : 34], 2)
            index_paquet_macrobloc = int(msgClient[34 : 50], 2)
            desc_paquet = f"body, numero_macrobloc = {num_macrobloc}, index_paquet_macrobloc = {index_paquet_macrobloc}"
        
        # header et tail (ie type_msg = 0 ou 3)
        else:
            if type_msg == 0:
                desc_paquet = "header"
            
            else:
                # ici, on a nécessairement type_msg = 3
                desc_paquet = "tail"
        
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
            Server.safe_print(f"Serveur> Client connecté, adresse IP {adresse[0]}, port {adresse[1]}.\n\n")
            
            while True:
                # dialogue avec le client            
                msgClient = connexion.recv(self.bufsize)
                msgClient = msgClient.decode("utf8")
                
                # si le client se déconnecte
                if msgClient == "FIN_ENVOI":
                    break
                
                try:
                    if msgClient[0] in ["0", "1"]:
                        self.callback(msgClient)
                        
                        desc_paquet = self.generer_description_paquet(msgClient)
                        msgServeur = f"Données bien reçues : {desc_paquet}"
                        
                        if self.affiche_messages:
                            Server.safe_print(f"Serveur> {msgServeur}")
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
                        if self.affiche_messages:
                            sleep(temps_pause_apres_envoi)
                    
                    elif msgClient[0] == "S":
                        self.callback(msgClient)
                
                except:
                    # si msgClient[0] n'existe pas (ou si c'est mal défini), 
                    # on passe simplement à la suite
                    pass
            
            connexion.shutdown(2) # 2 = socket.SHUT_RDWR
            connexion.close() # on ferme la connexion côté serveur
            Server.safe_print("Serveur> Client déconnecté.")
            
            # il n'y a qu'un seul client, donc s'il se déconnecte, on n'a plus
            # besoin de ce thread
            break


#############################################################################


class Server:
    """
    Classe permettant à une entité d'écouter et d'attendre de recevoir des 
    paquets depuis un correspondant connu ou inconnu.
    """
    def __init__(self, HOST, PORT, bufsize, affiche_messages):
        self.HOST = HOST
        self.PORT = PORT
        self.bufsize = bufsize
        self.affiche_messages = affiche_messages
        
        if "verrou" not in globals():
            global verrou
            verrou = threading.Lock()
            
            # pour éviter certains bugs
            verrou.acquire()
            verrou.release()
        
        self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.mySocket.bind((self.HOST, self.PORT))
        except socket.error:
            self.safe_print("Serveur> La liaison du socket à l'adresse choisie a échoué.")
            sys.exit()
        self.safe_print("Serveur> Serveur prêt, en attente de requêtes ...\n")
        
        # cette variable globale ne sera utile QUE si l'on affiche les messages
        # entre le client et le serveur
        if "temps_pause_apres_envoi" not in globals():
            global temps_pause_apres_envoi
            temps_pause_apres_envoi = 0.01 # en secondes
        
        # désigne le thread d'écoute du serveur
        self.th_Listen = None
    
    
    @staticmethod
    def safe_print(texte):
        """
        Permet de print sans se soucier des autres prints 'quasiment simultanés' dans
        d'autres threads. 
        Ici, sans cette fonction, les blocs de str s'entremêleront lors de leur
        affichage dans la console.
        Il s'agit en fait d'une sorte de 'print bloquant'.
        """
        global verrou
        
        # 'verrou' est une variable globale qui sera créée au moment de
        # l'instanciation de la classe Server
        verrou.acquire()
        Logger.get_instance().debug(texte)
        verrou.release()
    
    
    def listen_for_packets(self, callback):
        """
        Se met en mode écoute dans un thread séparé et attend de recevoir
        des informations par le réseau. 
        Permet également au client de se
        connecter au serveur.
        Args:
            client: client qui va interagir avec le serveur
            callback: fonction à appeler dès que le serveur reçoit des données
        """
        self.th_Listen = ThreadListen(self.mySocket, callback, self.bufsize, self.affiche_messages)
        self.th_Listen.start()


#############################################################################


class Client:
    """
    Permet d'envoyer par le réseau des données à une entité connue.
    """
    def __init__(self, HOST, PORT, bufsize, affiche_messages):
        self.HOST = HOST
        self.PORT = PORT
        self.bufsize = bufsize
        self.affiche_messages = affiche_messages
        
        self.connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        if "verrou" not in globals():
            global verrou
            verrou = threading.Lock()
            
            # pour éviter certains bugs
            verrou.acquire()
            verrou.release()
        
        # cette variable globale ne sera utile QUE si l'on affiche les messages
        # entre le client et le serveur
        if "temps_pause_apres_envoi" not in globals():
            global temps_pause_apres_envoi
            temps_pause_apres_envoi = 0.01 # en secondes
    
    
    def connect_to_server(self):
        """
        Connecte le client au serveur.
        """
        
        try:
            self.connexion.connect((self.HOST, self.PORT))
        except socket.error:
            Server.safe_print("Client> La connexion a échoué.")
            sys.exit()
        
        Server.safe_print("Client> Connexion établie avec le serveur.")
    
    
    def send_data_to_server(self, data):
        """
        Envoie les données au serveur en ouvrant un tunnel TCP avec ce dernier.
        Args:
            data: les données à transmettre (type: str)
        """
        
        if self.affiche_messages:
            Server.safe_print(f"Client> {data}")
        data = data.encode("utf8")
        self.connexion.send(data)
        if self.affiche_messages:
            sleep(temps_pause_apres_envoi)
    
    
    def wait_for_response(self):
        """
        Fonction outil permettant d'attendre que le serveur réponde avant de poursuivre
        le traitement des données.
        """
        msgServeur = self.connexion.recv(self.bufsize)
        msgServeur = msgServeur.decode("utf8")
        while True:
            try:
                if msgServeur[ : 19] == "Données bien reçues":
                    desc_paquet = msgServeur[22 : ]
                    if self.affiche_messages:
                        Server.safe_print(f"Client> Réponse du serveur reçue : {desc_paquet}\n\n")
                    break
            except:
                pass
            
            msgServeur = self.connexion.recv(self.bufsize)
            msgServeur = msgServeur.decode("utf8")

