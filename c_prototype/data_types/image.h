//
// Created by alexandre on 03/11/2020.
//

#ifndef C_PROTOTYPE_IMAGE_H
#define C_PROTOTYPE_IMAGE_H

#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

/*
 * Enum: Allocation_type
 * ---------------------
 * Enum used to describe how an image has been created
 * by telling how its memory has been allocated
 */
enum allocation_type {
    NO_ALLOCATION, SELF_ALLOCATED, STB_ALLOCATED
};

/*
 * Structure: Image
 * ---------------------
 * Structure that describes an image with its basic properties
 * for example a JPG image has 3 channels and a PNG has 4 (transparency)
 * all the pixels are in the data variable and the allocationType variable
 * is used to tell how the image has been created.
 */
typedef struct {
    int width;
    int height;
    int channels;
    size_t size;
    uint8_t *data;
    enum allocation_type allocationType;
} Image;

/* Creation and deletion functions */
int Image_create(Image *img, int width, int height, int channels, bool init_with_zeros);
void Image_free(Image *img);

/* Loading and saving functions */
int Image_load(Image *img, const char *file_name);
void Image_save(Image *img, const char *file_name);

/* Filtering functions */
void Image_to_gray(const Image *orig, Image *gray);
void Image_to_sepia(const Image *orig, Image *sepia);

#endif //C_PROTOTYPE_IMAGE_H
