from abc import ABCMeta, abstractmethod


class ImageGenerator(ABCMeta):

    """
    Classe de base permettant de générer des images de synthèse pour
    tester les algorithmes d'encodage et de décodage.
    """

    def __init__(self):
        super().__init__(self)

    @abstractmethod
    def generate(self):
        pass


class BlankImageGenerator(ImageGenerator):

    """
    Générateur d'image blanche ou vide. Ne retournera qu'une image
    d'une seule couleur ou bien une image vide.
    """

    def __init__(self):
        super().__init__()

    def generate(self):
        raise NotImplementedError


class MosaicImageGenerator(ImageGenerator):

    """
    Générateur d'image en mosaique. Retournera une mosaique de couleurs
    aléatoires.
    """

    def __init__(self):
        super().__init__()

    def generate(self):
        raise NotImplementedError
