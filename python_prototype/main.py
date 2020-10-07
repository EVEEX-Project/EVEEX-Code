# -*- coding: utf-8 -*-

"""
Script permettant de tester l'encodage et le décodage d'une image par notre 
propre algorithme
"""

from random import randint
from encoder import Encoder, DEFAULT_QUANTIZATION_THRESHOLD
from decoder import Decoder
from network_transmission import Server, Client
from bitstream import BitstreamGenerator, BitstreamSender
from image_generator import BlankImageGenerator, MosaicImageGenerator
from image_visualizer import ImageVisualizer
from logger import LogLevel, Logger

# # # ----------------------SETTING UP THE LOGGER------------------------ # # #


log = Logger.get_instance()
log.set_log_level(LogLevel.DEBUG)


# # # -------------------------IMAGE GENERATION-------------------------- # # #


#img_gen = BlankImageGenerator(size=(10, 10))
img_gen = MosaicImageGenerator(size=(10, 10), bloc_size=(2, 2))
image = img_gen.generate()


# # # -------------------------IMAGE ENCODING-------------------------- # # #


enc = Encoder()

image_yuv = enc.RGB_to_YUV(image)
dct_data = enc.apply_DCT(image_yuv)
zigzag_data_line = enc.zigzag_linearisation(dct_data[:, :, 0])
quantized_data = enc.quantization(zigzag_data_line, threshold=DEFAULT_QUANTIZATION_THRESHOLD)
rle_data = enc.run_level(quantized_data)
compressed_data = enc.huffman_encode(rle_data)


# # # -------------------------SENDING DATA OVER NETWORK-------------------------- # # #


puiss_2_random = randint(10, 12)
bufsize = 2 ** puiss_2_random

HOST = 'localhost'
PORT = randint(5000, 15000)

serv = Server(HOST, PORT, bufsize)
cli = Client(serv)

global received_data
received_data = ""

def on_received_data(data):
    global received_data 
    received_data += data

serv.listen_for_packets(cli, callback=on_received_data)

frame_id = randint(0, 65535)
img_size = image.shape[0] * image.shape[1]
macroblock_size = 5

bit_sender = BitstreamSender(frame_id, img_size, macroblock_size, rle_data, cli, bufsize)
bit_sender.send_frame_RLE()


# # # -------------------------DATA DECODING TO IMAGE-------------------------- # # #


dec = Decoder()

dec_rle_data = dec.decode_bitstream_RLE(received_data)
dec_quantized_data = dec.decode_run_length(dec_rle_data)
dec_zigzag_data = dec.decode_zigzag(dec_quantized_data)
#dec_dct_data = dec.decode_dct(dec_zigzag_data)


# # # -------------------------VISUALIZING THE IMAGE-------------------------- # # #


#img_visu = ImageVisualizer()
#img_visu.save_image_to_disk(dec_dct_data, "decoded_image.png")
#img_visu.show_image_with_matplotlib(dec_dct_data)

