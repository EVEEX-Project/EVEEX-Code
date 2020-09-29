# -*- coding: utf-8 -*-

import socket, sys, threading
from random import randint
from time import sleep
from huffman import Huffman

##########################################################################################


verrou = threading.RLock()

def safe_print(*a, **b):
    """
    Permet de print sans se soucier des autres prints 'quasiment simultanés' dans
    d'autres threads. 
    Ici, sans cette fonction, les blocs de str s'entremêleront lors de leur
    affichage dans la console.
    Il s'agit en fait d'une sorte de 'print bloquant'.
    """
    try:
        verrou.acquire()
        print(*a, **b)
    finally:
        verrou.release()


##########################################################################################


class ThreadListen(threading.Thread):
    """
    Thread pour gérer le mode écoute du serveur.
    """
    def __init__(self, socket_server, callback, bufsize):
        threading.Thread.__init__(self)
        self.socket_server = socket_server
        self.callback = callback
        self.bufsize = bufsize
    
    def run(self):
        self.socket_server.listen(5)
        while True:
            # établissement de la connexion
            connexion, adresse = self.socket_server.accept()
            safe_print("\nServeur> Client connecté, adresse IP %s, port %s." % (adresse[0], adresse[1]))
            
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
                        
                        msgServeur = "Données bien reçues."
                        safe_print("\nServeur>", msgServeur)
                        msgServeur = msgServeur.encode("utf8")
                        connexion.send(msgServeur)
                        
                        # INDISPENSABLE pour permettre le traitement de l'information
                        # envoyée + son affichage dans la console
                        # Ici, sans cette commande, les messages sont affichés dans le
                        # mauvais ordre dans la console (bien qu'ils ne soient plus
                        # entremêlés grâce à la fonction safe_print)
                        # --> Même remarque pour tous les autres 'sleep(0.01)' du code
                        sleep(0.01)
                
                except:
                    # si msgClient[0] n'existe pas (ou si c'est mal défini), 
                    # on passe simplement à la suite
                    pass
            
            connexion.close()    # on ferme la connexion côté serveur
            safe_print("\nServeur> Client déconnecté.")


class Server:
    """
    Classe permettant à une entité d'écouter et d'attendre de recevoir des 
    paquets depuis un correspondant connu ou inconnu.
    """
    def __init__(self, HOST, PORT, bufsize):
        self.HOST = HOST
        self.PORT = PORT
        self.bufsize = bufsize
        
        self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.mySocket.bind((self.HOST, self.PORT))
        except socket.error:
            safe_print("\nServeur> La liaison du socket à l'adresse choisie a échoué.")
            sys.exit()
        safe_print("\nServeur> Serveur prêt, en attente de requêtes ...")
    
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


##########################################################################################


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
            safe_print("\nClient> La connexion a échoué.")
            sys.exit()
        safe_print("\nClient> Connexion établie avec le serveur.")
    
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
            sleep(0.01)
            self.premier_message_envoye = False
        
        safe_print("\nClient>", data)
        data = data.encode("utf8")
        self.connexion.send(data)
        sleep(0.01)
    
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
            
            elif msgServeur == "Données bien reçues.":
                safe_print("\nClient> Réponse du serveur reçue.")
                break
            
            msgServeur = self.connexion.recv(self.bufsize)
            msgServeur = msgServeur.decode("utf8")


##########################################################################################


# simulation des commandes du main relatives à cette partie

if __name__ == "__main__":
    message_initial = "J'aime manger des citrons."
    print("Message initial :", message_initial)
    
    # encodage du message de référence via l'algo de Huffman
    huff = Huffman(message_initial)
    compressed_data = huff.encode_phrase()
    
    HOST = 'localhost'    # localhost ou bien adresse IP
    PORT = randint(5000, 15000)
    bufsize = 1024
    
    serv = Server(HOST, PORT, bufsize)
    cli = Client(serv)
    received_data = None
    
    
    def on_received_data(data):
        """
        Fonction appelée lorsque des données sont reçues par le serveur.
        On suppose que les données en entrée ont déjà été décodées via la 
        méthode decode().
        """
        global received_data
        received_data = data
    
    
    serv.listen_for_packets(cli, callback=on_received_data)    # dans un thread séparé
    cli.send_data_to_server(compressed_data)
    cli.wait_for_response()    # dans le thread actuel pour attendre d'avoir toutes les données
    
    # pour éviter d'avoir les messages de déconnexion des clients qui n'ont pas
    # été déconnectés des serveurs précédemment associés au même hôte
    cli.connexion.close()
    
    # décodage des données reçues par le serveur via l'algo de Huffman
    if received_data is not None:
        message_final = huff.decode_phrase(received_data)
    else:
        message_final = None
    
    safe_print("\nMessage final :", message_final)
    # Objectif : avoir message_initial == message_final --> OK

