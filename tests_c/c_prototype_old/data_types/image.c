#include "image.h"
#include "../utils.h"

// Needed to use the library
#define STB_IMAGE_IMPLEMENTATION
#include "../lib/stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "../lib/stb_image_write.h"

/*
 * Function: Image_create
 * ---------------------
 * Allocate the memory for a new image and returns the status of the memory allocation.
 * Allocate the memory for the data and can init with zeros (using calloc instead of malloc)
 *
 *  img: pointer to the image to create
 *  width: width of the new image in pixels
 *  height: height of the new image in pixels
 *  channels: number of channels in the image (3 for RGB, 4 with transparency)
 *  init_with_zeros: use calloc instead of malloc
 *
 *  returns: status of the creation
 */
int Image_create(Image *img, int width, int height, int channels, bool init_with_zeros) {
    // calculate the size of the image
    size_t size = width * height * channels;
    // if the image has to be init with zeros, calloc instead of malloc
    if(init_with_zeros) {
        img->data = (uint8_t *) calloc(size, 1);
    } else {
        img->data = (uint8_t *) malloc(size);
    }

    // if the data is null, there was a problem allocating the data
    if(img->data == NULL)
        return 1;

    // else we set the rest of the properties
    img->width = width;
    img->height = height;
    img->size = size;
    img->channels = channels;
    img->allocationType = SELF_ALLOCATED;

    // returning 0 to say everything went fine
    return 0;
}

/*
 * Function: Image_free
 * --------------------
 * Free the memory used by each attributes of the image then frees the image.
 *
 *  img: image to free
 */
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

/*
 * Function: Image_load
 * --------------------
 * Load an image as a file (JPG or PNG) and loads it into an image structure
 * to be used in the program.
 *
 *  img: pointer to the destination image
 *  file_name: path to the file containing the image
 *
 *  returns: status of the loading (0 for success, 1 for failure)
 */
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

/*
 * Function: Image_save
 * --------------------
 * Saves the image onto the disk provided there is a file name.
 *
 *  img: image to save
 *  file_name: path to where to save the image
 */
void Image_save(Image *img, const char *file_name) {
    // Check if the file name ends in one of the .jpg/.JPG/.jpeg/.JPEG or .png/.PNG
    if(str_ends_in(file_name, ".jpg")
        || str_ends_in(file_name, ".JPG")
        || str_ends_in(file_name, ".jpeg")
        || str_ends_in(file_name, ".JPEG")) {
        // then we write the image
        stbi_write_jpg(file_name, img->width, img->height, img->channels, img->data, img->width * img->channels);
    }
    else if(str_ends_in(file_name, ".png")
        || str_ends_in(file_name, ".PNG")) {
        // then we write the image
        stbi_write_png(file_name, img->width, img->height, img->channels, img->data, img->width * img->channels);
    } else {
        // the format is not recognized
        char message[100];
        sprintf(message, "Bad extension (or no extension at all) for the filename : '%s'", file_name);
        ON_ERROR_EXIT(false, message);
    }
}

/*
 * Function: Image_to_gray
 * -----------------------
 * Takes an image and store its grayscaled version in another image.
 *
 *  orig: original image
 *  gray: destination image containing the grayscaled version
 */
void Image_to_gray(const Image *orig, Image *gray) {
    // check for a valid image
    ON_ERROR_EXIT(!(orig->allocationType != NO_ALLOCATION && orig->channels >= 3), "The input image must have at least 3 channels.");
    // setting the correct number of channels
    int channels = orig->channels == 4 ? 2 : 1;
    // creating the destination image
    int creation_result = Image_create(gray, orig->width, orig->height, channels, false);
    ON_ERROR_EXIT((gray->data == NULL) || (creation_result != 0), "Error in creating the gray image");

    // values of each RGB pixel
    uint8_t p0, p1, p2;
    // iteration over the pixels of the image
    for(uint8_t *p = orig->data, *pg = gray->data; p != orig->data + orig->size; p += orig->channels, pg += gray->channels) {
        // updating the pixels value
        p0 = *p, p1 = *(p + 1), p2 = *(p + 2);
        // updating the target pixel
        *pg = (uint8_t)((p0 + p1 + p2)/3.0);
        // if there was transparency
        if(orig->channels == 4) {
            // update the transparency pixel
            *(pg + 1) = *(p + 3);
        }
    }
}

/*
 * Function: Image_to_sepia
 * ------------------------
 * Takes an image and applies the sepia filter over the image's pixels.
 *
 *  orig: the original image
 *  sepia: the destination image that will contain the modified data
 */
void Image_to_sepia(const Image *orig, Image *sepia) {
    // check for a valid image
    ON_ERROR_EXIT(!(orig->allocationType != NO_ALLOCATION && orig->channels >= 3), "The input image must have at least 3 channels.");
    // creating the destination image
    int creation_result = Image_create(sepia, orig->width, orig->height, orig->channels, false);
    ON_ERROR_EXIT((sepia->data == NULL) || (creation_result != 0), "Error in creating the sepia image");

    // Sepia filter coefficients from https://stackoverflow.com/questions/1061093/how-is-a-sepia-tone-created
    // iteration over the pixels of the image
    for(unsigned char *p = orig->data, *pg = sepia->data; p != orig->data + orig->size; p += orig->channels, pg += sepia->channels) {
        // updating the RGB pixel values
        *pg       = (uint8_t)fmin(0.393 * *p + 0.769 * *(p + 1) + 0.189 * *(p + 2), 255.0);         // red
        *(pg + 1) = (uint8_t)fmin(0.349 * *p + 0.686 * *(p + 1) + 0.168 * *(p + 2), 255.0);         // green
        *(pg + 2) = (uint8_t)fmin(0.272 * *p + 0.534 * *(p + 1) + 0.131 * *(p + 2), 255.0);         // blue
        // updating the transparency channel
        if(orig->channels == 4) {
            *(pg + 3) = *(p + 3);
        }
    }
}