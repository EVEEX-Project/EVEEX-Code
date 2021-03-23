# -*- coding: utf-8 -*-

"""
Test d'un serveur basique. À tester en conjonction avec "test_emetteur.py" (= client).
"""

from logger import Logger
from network_transmission import Server

#----------------------------------------------------------------------------#


log = Logger.get_instance()
log.debug("Début serveur")

bufsize = 50

HOST = "192.168.8.218" # adresse IP du PC récepteur
PORT = 22 # port SSH

serv = Server(HOST, PORT, bufsize, True)

def do_nothing(data):
    pass

serv.listen_for_packets(callback=do_nothing)

serv.th_Listen.join()
serv.mySocket.close()

log.debug("Fin serveur")

