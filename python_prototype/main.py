"""
Script permettant de tester l'encodage et le décodage d'une image par notre propre algorithme
"""

from encoder import Encoder, DEFAULT_QUANTIZATION_THRESHOLD
from decoder import Decoder
from network_transmission import Server, Client
from image_generator import BlankImageGenerator, MosaicImageGenerator
from image_visualizer import ImageVisualizer
from logger import LogLevel, Logger

# # # ----------------------SETTING UP THE LOGGER------------------------ # # #

log = Logger.get_instance()
log.set_log_level(LogLevel.DEBUG)

# # # -------------------------IMAGE GENERATION-------------------------- # # #

img_gen = BlankImageGenerator()
image = img_gen.generate()


# # # -------------------------IMAGE ENCODING-------------------------- # # #

enc = Encoder()
image_yuv = enc.RGB_to_YUV(image)
dct_data = enc.apply_DCT(image_yuv)
zigzag_data_line = enc.zigzag_linearisation(dct_data)
quantized_data = enc.quantization(zigzag_data_line, threshold=DEFAULT_QUANTIZATION_THRESHOLD)
rle_data = enc.run_level(quantized_data)
compressed_data = enc.huffman_encode(rle_data)


# # # -------------------------SENDING DATA OVER NETWORK-------------------------- # # #

serv = Server()
cli = Client()
received_data = None


def on_received_data(data):
    """
    Fonction appelée lorsque des données sont reçues par le serveur.
    """
    global received_data
    received_data = data


serv.listen_for_packets(callback=on_received_data) # probablement à mettre dans un thread séparé
cli.send_data_to_server(compressed_data)
cli.wait_for_response() # dans le thread actuel pour attendre d'avoir toutes les données


# # # -------------------------DATA DECODING TO IMAGE-------------------------- # # #

dec = Decoder()
dec_rle_data = dec.decode_huffman(*received_data)
dec_quantized_data = dec.decode_run_length(dec_rle_data)
dec_zigzag_data = dec.decode_zigzag(dec_quantized_data)
dec_dct_data = dec.decode_dct(dec_zigzag_data)

# # # -------------------------VISUALIZING THE IMAGE-------------------------- # # #

img_visu = ImageVisualizer()
img_visu.save_image_to_disk(dec_dct_data, "decoded_image.png")
img_visu.show_image_with_matplotlib(dec_dct_data)