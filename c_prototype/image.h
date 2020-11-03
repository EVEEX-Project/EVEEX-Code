//
// Created by alexandre on 03/11/2020.
//

#ifndef C_PROTOTYPE_IMAGE_H
#define C_PROTOTYPE_IMAGE_H

#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

enum allocation_type {
    NO_ALLOCATION, SELF_ALLOCATED, STB_ALLOCATED
};

typedef struct {
    int width;
    int height;
    int channels;
    size_t size;
    uint8_t *data;
    enum allocation_type allocationType;
} Image;

int Image_load(Image *img, const char *file_name);
int Image_create(Image *img, int width, int height, int channels, bool init_with_zeros);
void Image_save(Image *img, const char *file_name);
void Image_free(Image *img);

#endif //C_PROTOTYPE_IMAGE_H
