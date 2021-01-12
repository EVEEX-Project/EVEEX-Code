cmake_minimum_required(VERSION 3.16)

configure_file(assets/image_res_low.jpg assets/image_res_low.jpg COPYONLY)
configure_file(assets/image_res_high.jpg assets/image_res_high.jpg COPYONLY)

add_executable(point_testing
        ../types/Object.c
        ../types/Point.c
        point_test.c)

add_executable(list_testing
        ../types/Object.c
        ../types/Point.c
        ../types/List.c
        list_test.c)

add_executable(dico_testing
        ../types/Object.c
        ../types/Native.c
        ../types/Point.c
        ../types/List.c
        ../types/DictionaryItem.c
        ../types/Dictionary.c
        dico_test.c)

add_executable(pixel_testing
        ../types/Object.c
        ../types/Pixel.c
        pixel_test.c)

add_executable(image_testing
        ../types/Object.c
        ../types/Image.c
        image_test.c)
target_link_libraries(image_testing m)

add_executable(bitstream_testing
        ../types/Object.c
        ../types/Bitstream.c
        bitstream_test.c)

add_executable(node_testing
        ../types/Object.c
        ../types/Point.c
        ../types/Node.c
        node_test.c)

add_executable(huffman_testing
        ../types/Object.c
        ../types/Node.c
        ../types/Native.c
        ../types/List.c
        ../types/Dictionary.c
        ../types/DictionaryItem.c
        ../lib/huffman.c
        huffman_test.c)

add_test(NAME PointTest COMMAND point_testing)
add_test(NAME ListTest COMMAND list_testing)
add_test(NAME DictionaryTest COMMAND dico_testing)
add_test(NAME PixelTest COMMAND pixel_testing)
add_test(NAME ImageTest COMMAND image_testing)
add_test(NAME BitstreamTest COMMAND bitstream_testing)
add_test(NAME NodeTest COMMAND node_testing)
add_test(NAME HuffmanTest COMMAND huffman_testing)

