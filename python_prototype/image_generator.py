from abc import ABCMeta, abstractmethod
import json
import numpy as np


class ColorDecoder:

    colors = {
        "red" : [255, 0, 0],
        "green" : [0, 255, 0],
        "blue" : [0, 0, 255],
        "black" : [0, 0, 0],
        "white" : [255, 255, 255]
    }

    @staticmethod
    def fromString(color_name):
        return np.array(ColorDecoder.colors[color_name.lower()])

    @staticmethod
    def toString(color_int):
        raise NotImplementedError


class ImageGenerator(metaclass=ABCMeta):
    """
    Classe de base permettant de générer des images de synthèse pour
    tester les algorithmes d'encodage et de décodage.
    """

    def __init__(self):
        super().__init__()
        self.img_data = np.zeros((100, 100, 3))

    def addCircle(self, position, size, color):
        # si la forme dépasse du canevas on lance une erreur
        if position[0] - size < 0 or position[1] - size < 0 or \
                position[0] + size >= self.img_data.shape[0] or \
                position[1] + size >= self.img_data.shape[1]:
            raise Exception(f"Le cercle à la position {position} dépasse du canevas !")

        # on change les bits en question
        c = 0
        for i in range(position[0] - size + 1, position[0] + size):
            for j in range(position[1] - size + 1, position[1] + size):
                # si le pixel est dans le cercle
                if (i - position[0]) ** 2 + (j - position[1]) ** 2 <= size ** 2:
                    c += 1
                    self.img_data[i, j] = color
        print(f"addCircle : {c} pixels changés")

    def addRectangle(self, position, size, color):
        # si la forme dépasse du canevas on lance une erreur
        if position[0] < 0 or position[1] < 0 or \
                position[0] + size[0] > self.img_data.shape[0] or \
                position[1] + size[1] > self.img_data.shape[1]:
            raise Exception(f"Le rectangle à la position {position} dépasse du canevas !")

        # on change les bits en question
        c = 0
        for i in range(position[0], position[0] + size[0]):
            for j in range(position[1], position[1] + size[1]):
                c += 1
                self.img_data[i, j] = color
        print(f"addRectangle : {c} pixels changés")

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


class FromJSONImageGenerator(ImageGenerator):
    """
    Générateur d'image à partir d'un scénario dans un fichier JSON.
    """

    def __init__(self, filename):
        super().__init__()
        data = None
        with open(filename, "r") as f:
            data = json.loads(f.read())
        self.json_data = data

        self.parse_json()

    def parse_json(self):
        # Parsing header
        header = self.json_data["header"]
        self.img_size = (int(header["size"][0]), int(header["size"][1]), 3)
        print(f"Img size : {self.img_size}")
        # on recrée l'image à la bonne taille
        self.img_data = np.zeros(self.img_size)

        # si on a définit une couleur de fond
        if "background_color" in header:
            self.addRectangle((0, 0),
                              self.img_size,
                              ColorDecoder.fromString(header["background_color"]))

        content = self.json_data["content"]
        # pour chaque forme que l'on ajoute à l'image
        for i in range(len(content)):
            element = content[i]
            print(f"Detected shape : {element['type']}")
            if element['type'] == "circle":
                s_position = element["position"]
                position = (int(s_position[0]), int(s_position[1]))
                size = int(element["size"])
                print(f"with position : {position} and size {size}")
                self.addCircle(position,
                               size,
                               ColorDecoder.fromString(element["color"]))
            elif element['type'] == "rectangle":
                s_position = element["position"]
                position = (int(s_position[0]), int(s_position[1]))
                size = int(element["size"][0]), int(element["size"][1])
                print(f"with position : {position} and size {size}")
                self.addRectangle(position,
                                  size,
                                  ColorDecoder.fromString(element["color"]))

    def generate(self):
        return self.img_data


if __name__ == "__main__":
    from image_visualizer import ImageVisualizer

    visu = ImageVisualizer()
    gen = FromJSONImageGenerator("image_desc.json")

    visu.show_image_with_matplotlib(gen.generate())
    visu.save_image_to_disk(gen.generate(), "image_desc_res.png")
