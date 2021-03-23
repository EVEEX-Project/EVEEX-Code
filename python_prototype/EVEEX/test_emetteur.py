# -*- coding: utf-8 -*-

"""
Test d'un client basique. À tester en conjonction avec "test_recepteur.py" (= serveur).
"""

from logger import Logger
from network_transmission import Client

#----------------------------------------------------------------------------#


log = Logger.get_instance()
log.debug("Début client")

bufsize = 50

HOST = "192.168.8.218" # adresse IP du PC récepteur
PORT = 22 # port SSH

cli = Client(HOST, PORT, bufsize, True)
cli.connect_to_server()

fake_legal_msg = "1" * 18 # on simule l'envoie du tail (avec frame_id = 65535)

cli.send_data_to_server(fake_legal_msg)
cli.wait_for_response()

cli.send_data_to_server("FIN_ENVOI")

cli.connexion.shutdown(2)
cli.connexion.close()

log.debug("Fin client")

