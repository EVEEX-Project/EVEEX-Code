import matplotlib.pyplot as plt
import os
import numpy as np

from logger import Logger


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
        plt.imsave(file_name, np.array(data, dtype="uint8"), format="png")
        Logger.get_instance().info(f"Saving image to {os.getcwd()}/{file_name}")

    def open_image_with_native_viewer(self, data):
        """
        Affiche l'image en utilisant le visionneur d'image natif de la machine.

        Args:
            data: tableau de pixels représentant l'image
        """
        raise NotImplementedError

if __name__ == "__main__":
    from PIL import Image
    import numpy as np
    visu = ImageVisualizer()

    img = Image.open("test_img.png")
    visu.show_image_with_matplotlib(img)
    Logger.get_instance().debug(np.asarray(img)[0, 0])