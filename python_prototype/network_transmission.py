class Server:

    """
    Classe permettant à une entité d'écouter et d'attendre
    de recevoir des packets depuis un correspondant connu ou inconnu
    """

    def __init__(self):
        pass

    def listen_for_packets(self, callback):
        """
        Se met en mode écoute dans un thread séparé et attend de recevoir
        des informations par le réseau.

        Args:
            callback: fonction à appeler dès que l'on reçoit des données
        """
        raise NotImplementedError

    def send_response_to_client(self):
        """
        Réponse à retourner au client dès lors que l'on recoit des données.
        Nécessaire à une communication en tunnel.
        """
        raise NotImplementedError


class Client:

    """
    Permet d'envoyer par le réseau des données à une entité connue.
    """

    def __init__(self):
        pass

    def send_data_to_server(self, data):
        """
        Envoie les données au serveur en ouvrant un tunnel TCP avec ce dernier.

        Args:
            data: les données à transmettre
        """
        raise NotImplementedError

    def wait_for_response(self):
        """
        Fonction outil permettant d'attendre que le serveur réponde avant de poursuivre
        le traitement des données.
        """
        raise NotImplementedError