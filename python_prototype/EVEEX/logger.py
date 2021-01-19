import datetime
from colorama import Fore, Back


def get_time():
    """
    Retourne l'heure, les minutes et les secondes actuelles
    """
    now = datetime.datetime.now()
    return str(now.hour).zfill(2), str(now.minute).zfill(2), str(now.second).zfill(2)


class LogLevel:
    """
    Classe outil décrivant les différents niveaux de log
    allant du débug à l'erreur critique. Cette façon d'afficher les
    messages devra être celle à privilégier.
    """
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

    @staticmethod
    def can_be_printed(msg_log_level, threshold):
        if not (isinstance(msg_log_level, int) and isinstance(threshold, int)):
            raise Exception("Not a LogLevel")

        return msg_log_level >= threshold

    @staticmethod
    def to_string(log_level):
        if log_level == LogLevel.CRITICAL:
            return "[" + "CRI" + "]"
        elif log_level == LogLevel.ERROR:
            return "[" + "ERR" + "]"
        elif log_level == LogLevel.WARNING:
            return "[" + "WAR" + "]"
        elif log_level == LogLevel.INFO:
            return "[" + "INF" + "]"
        elif log_level == LogLevel.DEBUG:
            return "[" + "DEB" + "]"

        return ""

    @staticmethod
    def to_color_string(log_level):
        if log_level == LogLevel.CRITICAL:
            return Fore.RESET + "[" + Fore.BLACK + Back.RED + "CRI" + Fore.RESET + Back.RESET + "]"
        elif log_level == LogLevel.ERROR:
            return Fore.RESET + "[" + Fore.RED + "ERR" + Fore.RESET + "]"
        elif log_level == LogLevel.WARNING:
            return Fore.RESET + "[" + Fore.YELLOW + "WAR" + Fore.RESET + "]"
        elif log_level == LogLevel.INFO:
            return Fore.RESET + "[" + Fore.BLUE + "INF" + Fore.RESET + "]"
        elif log_level == LogLevel.DEBUG:
            return Fore.RESET + "[" + Fore.MAGENTA + "DEB" + Fore.RESET + "]"

        return ""


class Logger:

    _instance = None

    @staticmethod
    def get_instance():
        """
        Permet de retourner une instance du logger pour avoir une seule référence
        commune au travers du projet.
        """
        # si on a pas encore crée l'instance on le fait
        if Logger._instance is None:
            Logger._instance = Logger()
        return Logger._instance

    def __init__(self, log_level=None, log_file=None):
        self.log_level = LogLevel.DEBUG
        self.log_file = None
        self.is_logging_to_file = False

        if log_level is not None:
            self.log_level = log_level

        if log_file is not None:
            self.log_file = log_file
            self.is_logging_to_file = True

    def set_log_level(self, log_level):
        """
        Permet de définir le seuil à partir duquel les messages seront affichés dans
        le terminal de commande

        Args:
            log_level (int): le niveau de log seuil à paramétrer
        """
        self.log_level = log_level

    def start_file_logging(self, filename):
        """
        Permet d'indiquer au logger de démarrer l'enregistrement des messages dans un fichier
        externe (ici filename).

        Args:
            filename: chemin vers le fichier qui contiendra les logs
        """
        self.is_logging_to_file = True
        self.log_file = filename

    def stop_file_logging(self):
        """
        Permet d'indiquer au logger d'arrêter d'enregistrer les messages dans un fichier externe.
        """
        self.is_logging_to_file = False
        self.log_file = None

    def debug(self, message):
        """
        Permet de logger un message de debug sur le terminal si les conditions sont réunies
        de plus si le logger a été configuré pour, les messages seront enregistrés dans
        un fichier externe.

        Args:
            message (str): message à afficher
        """
        self._print_message(LogLevel.DEBUG, message)

    def info(self, message):
        """
        Permet de logger un message d'information sur le terminal si les conditions sont réunies
        de plus si le logger a été configuré pour, les messages seront enregistrés dans
        un fichier externe.

        Args:
            message (str): message à afficher
        """
        self._print_message(LogLevel.INFO, message)

    def warn(self, message):
        """
        Permet de logger un message d'avertissement sur le terminal si les conditions sont réunies
        de plus si le logger a été configuré pour, les messages seront enregistrés dans
        un fichier externe.

        Args:
            message (str): message à afficher
        """
        self._print_message(LogLevel.WARNING, message)

    def error(self, message):
        """
        Permet de logger un message d'erreur sur le terminal si les conditions sont réunies
        de plus si le logger a été configuré pour, les messages seront enregistrés dans
        un fichier externe.

        Args:
            message (str): message à afficher
        """
        self._print_message(LogLevel.ERROR, message)

    def critical(self, message):
        """
        Permet de logger un message critique sur le terminal si les conditions sont réunies
        de plus si le logger a été configuré pour, les messages seront enregistrés dans
        un fichier externe.

        Args:
            message (str): message à afficher
        """
        self._print_message(LogLevel.CRITICAL, message)

    def _construct_line(self, msg_level, message):
        """
        Fonction outil permettant de construire la ligne qui sera soit affichée
        dans le terminal, soit enregistrée dans le fichier.

        Args:
            msg_level (int): le niveau du message à traiter
            message (str): le message à traiter

        Returns:
            line (str): la ligne ainsi construite avec une date et le niveau de log
        """
        date = Fore.RESET + "[" + Fore.GREEN + "{}:{}:{}".format(*get_time()) + Fore.RESET + "]"
        line = f"{date}{LogLevel.to_color_string(msg_level)} {message}"
        return line

    def _print_message(self, msg_level, message):
        """
        Fonction outil permettant d'afficher le message de log en fonction
        du niveau de celui-ci.

        Args:
            msg_level (int): le niveau du message à traiter
            message (str): le message à traiter
        """
        # Si on peut afficher le message (car paramétré comme)
        if LogLevel.can_be_printed(msg_level, self.log_level):
            line = self._construct_line(msg_level, message)
            print(line)

        # Si on a prévu de logger le message dans un fichier on le fait
        if self.is_logging_to_file:
            self._save_message_to_file(msg_level, message)

    def _save_message_to_file(self, msg_level, message):
        """
        Fonction outil permettant d'enregistrer le message de log si
        le logger a été parametré pour

        Args:
            msg_level (int): le niveau du message à traiter
            message (str): le message à traiter
        """
        if self.log_file is None:
            raise Exception("No logging file specified!")

        date = "[" + "{}:{}:{}".format(*get_time()) + "]"
        line = f"{date}{LogLevel.to_string(msg_level)} {message}\n"
        with open(self.log_file, "a") as f:
            f.write(line)


if __name__ == "__main__":
    log = Logger.get_instance()
    log.set_log_level(LogLevel.DEBUG)
    log.start_file_logging("log.log")
    log.debug("Hello world")
    log.error("Ceci est une erreur")
    log.info("Et ceci est une information")
    log.warn("Alors que ce message est un avertissement")
    log.critical("Et ce message on croise les doigts pour ne jamais le voir")