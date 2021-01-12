cmake_minimum_required(VERSION 3.16)
set(CMAKE_C_STANDARD 99)

project(C_PROTOTYPE C)

# Tells CMake that there are testing files
enable_testing()

# Loading CMakeLists.txt from the test folder
add_subdirectory (${PROJECT_SOURCE_DIR}/test)

add_executable(C_PROTOTYPE
        types/Object.c
        types/Point.c
        types/List.c
        types/DictionaryItem.c
        types/Dictionary.c
        types/Node.c
        types/Native.c
        lib/encoder.c
        lib/decoder.c
        lib/huffman.c

        main.c)