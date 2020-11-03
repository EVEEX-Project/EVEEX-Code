// Needed to use the library
#ifndef STB_IMAGE_IMPLEMENTATION
    #define STB_IMAGE_IMPLEMENTATION
    #include "lib/stb_image.h"
#endif
#ifndef STB_IMAGE_WRITE_IMPLEMENTATION
    #define STB_IMAGE_WRITE_IMPLEMENTATION
    #include "lib/stb_image_write.h"
#endif

#include "image.h"
#include "utils.h"

int Image_load(Image *img, const char *file_name) {
    // loading the data into the data variable
    img->data = stbi_load(file_name, &img->width, &img->height, &img->channels, 0);

    // if the data is null there was a problem during the loading
    if(img->data == NULL)
        return 1;

    // else we load the rest of the infos
    img->size = img->width * img->height * img->channels;
    img->allocationType = STB_ALLOCATED;

    // returning 0 to say it's done
    return 0;
}

int Image_create(Image *img, int width, int height, int channels, bool init_with_zeros) {
    // calc the size of the image
    size_t size = width * height * channels;
    // if the image has to be init with zeros, calloc instead of malloc
    if(init_with_zeros) {
        img->data = calloc(size, 1);
    } else {
        img->data = malloc(size);
    }

    // if the data is null, there was a problem allocating the data
    if(img->data != NULL)
        return 1;

    // else we set the rest of the infos
    img->width = width;
    img->height = height;
    img->size = size;
    img->channels = channels;
    img->allocationType = SELF_ALLOCATED;

    // returning 0 to day everything went fine
    return 0;
}

void Image_save(Image *img, const char *file_name) {
    // Check if the file name ends in one of the .jpg/.JPG/.jpeg/.JPEG or .png/.PNG
    if(str_ends_in(file_name, ".jpg")
        || str_ends_in(file_name, ".JPG")
        || str_ends_in(file_name, ".jpeg")
        || str_ends_in(file_name, ".JPEG")) {
        stbi_write_jpg(file_name, img->width, img->height, img->channels, img->data, 100);
    }
    else if(str_ends_in(file_name, ".png")
        || str_ends_in(file_name, ".PNG")) {
        stbi_write_png(file_name, img->width, img->height, img->channels, img->data, img->width * img->channels);
    } else {
        char message[100];
        sprintf(message, "Bad extension (or no extension at all) for the filename : '%s'", file_name);
        ON_ERROR_EXIT(false, message);
    }
}

void Image_free(Image *img) {
    // we check that the image is valid before doing anything else
    if(img->allocationType != NO_ALLOCATION && img->data != NULL) {
        // if the image was loaded and not created
        if(img->allocationType == STB_ALLOCATED) {
            // then we unload the image
            stbi_image_free(img->data);
        } else {
            // else we only free the data
            free(img->data);
        }
        // then it's just a matter of resetting everything
        img->data = NULL;
        img->width = 0;
        img->height = 0;
        img->size = 0;
        img->allocationType = NO_ALLOCATION;
    }
}

void Image_to_gray(const Image *orig, Image *gray) {
    ON_ERROR_EXIT(!(orig->allocationType != NO_ALLOCATION && orig->channels >= 3), "The input image must have at least 3 channels.");
    int channels = orig->channels == 4 ? 2 : 1;
    Image_create(gray, orig->width, orig->height, channels, false);
    ON_ERROR_EXIT(gray->data == NULL, "Error in creating the image");

    for(unsigned char *p = orig->data, *pg = gray->data; p != orig->data + orig->size; p += orig->channels, pg += gray->channels) {
        *pg = (uint8_t)((*p + *(p + 1) + *(p + 2))/3.0);
        if(orig->channels == 4) {
            *(pg + 1) = *(p + 3);
        }
    }
}

void Image_to_sepia(const Image *orig, Image *sepia) {
    ON_ERROR_EXIT(!(orig->allocationType != NO_ALLOCATION && orig->channels >= 3), "The input image must have at least 3 channels.");
    Image_create(sepia, orig->width, orig->height, orig->channels, false);
    ON_ERROR_EXIT(sepia->data == NULL, "Error in creating the image");

    // Sepia filter coefficients from https://stackoverflow.com/questions/1061093/how-is-a-sepia-tone-created
    for(unsigned char *p = orig->data, *pg = sepia->data; p != orig->data + orig->size; p += orig->channels, pg += sepia->channels) {
        *pg       = (uint8_t)fmin(0.393 * *p + 0.769 * *(p + 1) + 0.189 * *(p + 2), 255.0);         // red
        *(pg + 1) = (uint8_t)fmin(0.349 * *p + 0.686 * *(p + 1) + 0.168 * *(p + 2), 255.0);         // green
        *(pg + 2) = (uint8_t)fmin(0.272 * *p + 0.534 * *(p + 1) + 0.131 * *(p + 2), 255.0);         // blue
        if(orig->channels == 4) {
            *(pg + 3) = *(p + 3);
        }
    }
}