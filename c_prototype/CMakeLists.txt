cmake_minimum_required(VERSION 3.18)
project(c_prototype C)

set(CMAKE_C_STANDARD 99)

configure_file(assets/image_res.jpg assets/image_res.jpg COPYONLY)

add_executable(c_prototype
        dictionary.c
        huffman.c
        image.c
        main.c)

target_link_libraries(c_prototype m)