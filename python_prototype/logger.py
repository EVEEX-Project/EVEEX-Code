import datetime
from colorama import Fore

def get_time():
    """
    Retourne l'heure, les minutes et les secondes actuelles
    """
    now = datetime.datetime.now()
    return str(now.hour).zfill(2), str(now.minute).zfill(2), str(now.second).zfill(2)


class LogLevel:
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
            return Fore.RESET + "[" + Fore.RED + "CRIT " + Fore.RESET + "]"
        elif log_level == LogLevel.ERROR:
            return Fore.RESET + "[" + Fore.RED + "ERROR" + Fore.RESET + "]"
        elif log_level == LogLevel.WARNING:
            return Fore.RESET + "[" + Fore.YELLOW + "WARN " + Fore.RESET + "]"
        elif log_level == LogLevel.INFO:
            return Fore.RESET + "[" + Fore.BLUE + "INFO " + Fore.RESET + "]"
        elif log_level == LogLevel.DEBUG:
            return Fore.RESET + "[" + Fore.MAGENTA + "DEBUG" + Fore.RESET + "]"

        return ""


class Logger:

    def __init__(self, log_level=None, log_file=None):
        self.log_level = LogLevel.INFO
        self.log_file = None
        self.is_logging_to_file = False

        if log_level is not None:
            self.log_level = log_level

        if log_file is not None:
            self.log_file = log_file
            self.is_logging_to_file = True

    def set_log_level(self, log_level):
        self.log_level = log_level

    def start_file_logging(self, filename):
        self.is_logging_to_file = True
        self.log_file = filename

    def stop_file_logging(self):
        self.is_logging_to_file = False
        self.log_file = None

    def debug(self, message):
        self._print_message(LogLevel.DEBUG, message)

    def info(self, message):
        self._print_message(LogLevel.INFO, message)

    def warn(self, message):
        self._print_message(LogLevel.WARNING, message)

    def error(self, message):
        self._print_message(LogLevel.ERROR, message)

    def critical(self, message):
        self._print_message(LogLevel.CRITICAL, message)

    def _construct_line(self, msg_level, message):
        date = Fore.RESET + "[" + Fore.GREEN + "{}:{}:{}".format(*get_time()) + Fore.RESET + "]"
        line = f"{date}{LogLevel.to_string(msg_level)} {message}"
        return line

    def _print_message(self, msg_level, message):
        # Si on peut afficher le message (car paramétré comme)
        if LogLevel.can_be_printed(msg_level, self.log_level):
            line = self._construct_line(msg_level, message)
            print(line)

        # Si on a prévu de logger le message dans un fichier on le fait
        if self.is_logging_to_file:
            self._save_message_to_file(msg_level, message)

    def _save_message_to_file(self, msg_level, message):
        if self.log_file is None:
            raise Exception("No logging file specified!")

        line = self._construct_line(msg_level, message)
        with open(self.log_file, "a") as f:
            f.write(line)


if __name__ == "__main__":
    log = Logger(log_level=LogLevel.DEBUG)
    log.debug("Hello world")
    log.error("Ceci est une erreur")
    log.info("Et ceci est une information")
    log.warn("Alors que ce message est un avertissement")