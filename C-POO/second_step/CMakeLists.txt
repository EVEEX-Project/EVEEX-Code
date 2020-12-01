cmake_minimum_required(VERSION 3.18)
project(SECOND_STEP C)

set(CMAKE_C_STANDARD 99)

add_executable(SECOND_STEP
        Object.c
        Point.c
        List.c
        main.c)