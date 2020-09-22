import matplotlib.pyplot as plt

class ImageVisualizer:
    """
    Classe permettant d'afficher une image à partir d'un tableau de pixels ou bien
    de sauvegarder cette image sur le disque.
    """

    def __init__(self):
        pass

    def show_image_with_matplotlib(self, data):
        """
        Affiche l'image en utilisant la bibliothèque matplotlib.

        Args:
            data: tableau de pixels représentant l'image
        """
        plt.imshow(data)
        plt.show()

    def show_image_with_opencv(self, data):
        """
        Affiche l'image en utilisant la bibliothèque opencv.

        Args:
            data: tableau de pixels représentant l'image
        """
        raise NotImplementedError

    def save_image_to_disk(self, data, file_name):
        """
        Sauvegarde l'image sur le disque avec le nom file_name.

        Args:
            data: tableau de pixels représentant l'image
            file_name: nom du fichier sous lequel sauvegrder l'image
        """
        raise NotImplementedError

    def open_image_with_native_viewer(self, data):
        """
        Affiche l'image en utilisant le visionneur d'image natif de la machine.

        Args:
            data: tableau de pixels représentant l'image
        """
        raise NotImplementedError