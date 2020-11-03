cmake_minimum_required(VERSION 3.18)
project(c_prototype C)

set(CMAKE_C_STANDARD 99)

add_executable(c_prototype main.c)

target_link_libraries(c_prototype m)