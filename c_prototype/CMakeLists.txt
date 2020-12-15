cmake_minimum_required(VERSION 3.16)
project(c_prototype C)

set(CMAKE_C_STANDARD 99)

configure_file(assets/image_res.jpg assets/image_res.jpg COPYONLY)

add_executable(c_prototype
        data_types/dictionary.c
        data_types/image.c
        data_types/list.c
        data_types/bitstream.c
        huffman.c
        main.c)

target_link_libraries(c_prototype m)