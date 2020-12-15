cmake_minimum_required(VERSION 3.16)

configure_file(assets/image_res.jpg assets/image_res.jpg COPYONLY)

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

add_test(NAME PointTest COMMAND point_testing)
add_test(NAME ListTest COMMAND list_testing)
add_test(NAME DictionaryTest COMMAND dico_testing)
add_test(NAME PixelTest COMMAND pixel_testing)
add_test(NAME ImageTest COMMAND image_testing)

