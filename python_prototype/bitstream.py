class BitstreamGenerator:

    HEADER_MSG = 0
    DICT_MSG = 1
    BODY_MDG = 2

    def __init__(self, frame_id, img_size, macrobloc_size):
        self.img_size = img_size
        self.macrobloc_size = macrobloc_size
        self.frame_id = frame_id
        self.index = 0

    def construct_header_bitstream(self):
        """
        Construit le bitstream d'en-tête de l'image à partir des informations entrées
        lors de l'instanciation de la classe

        Returns:
            bitstream (string): le bitstream représentant le header de la frame
        """
        raise NotImplementedError

    def construct_body(self, huffman_data):
        """
        Construit le bitstream représentant le contenu d'un macrobloc, encodé par huffman

        Args:
            huffman_data: contenu du macrobloc encodé par huffman

        Returns:
            bitstream (string): le bitstream représentant le macrobloc
        """
        raise NotImplementedError

    def construct_end_message(self):
        """
        Construit le bitstream représentant le message de fin d'une frame

        Returns:
            bitstream (string): le bitstream représentant le message de fin
        """