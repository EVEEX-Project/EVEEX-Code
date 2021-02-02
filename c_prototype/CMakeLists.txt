cmake_minimum_required(VERSION 3.16)
set(CMAKE_C_STANDARD 99)

project(C_PROTOTYPE C)

# Tells CMake that there are testing files
enable_testing()

# Loading CMakeLists.txt from the test folder
add_subdirectory (${PROJECT_SOURCE_DIR}/test)

# Copying image file
configure_file(assets/image_res.png assets/image_res.png COPYONLY)

add_executable(C_PROTOTYPE
        types/Object.c
        types/Point.c
        types/List.c
        types/DictionaryItem.c
        types/Dictionary.c
        types/Node.c
        types/Native.c
        types/Image.c
        lib/encoder.c
        lib/decoder.c
        lib/huffman.c
        lib/logger.c

        main.c)

target_link_libraries(C_PROTOTYPE m)