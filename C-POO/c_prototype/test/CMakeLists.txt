cmake_minimum_required(VERSION 3.16)

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

add_test(NAME PointTest COMMAND point_testing)
add_test(NAME ListTest COMMAND list_testing)
add_test(NAME DictionaryTest COMMAND dico_testing)