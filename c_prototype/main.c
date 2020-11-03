#include <stdio.h>
#include "image.c"
#include "utils.h"


int main() {
    Image img, gray, sepia;

    Image_load(&img, "image_res.jpg");
    ON_ERROR_EXIT( img.data == NULL, "Error while loading the image");
    Image_to_gray(&img, &gray);
    //Image_to_sepia(&img, &sepia);
    Image_save(&gray, "gray_res.jpg");
    //Image_save(&sepia, "sepia_res.jpg");

    printf("Image loaded with a width of %dpx and height of %dpx with %d channels\n", img.width, img.height, img.channels);

    Image_free(&img);
    Image_free(&gray);
    //Image_free(&sepia);

    return 0;
}
