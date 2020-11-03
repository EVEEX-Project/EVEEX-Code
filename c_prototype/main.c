#include <stdio.h>
#include "image.c"
#include "utils.h"

void loadImageTest() {
    Image img, gray;

    Image_load(&img, "image_res.jpg");
    ON_ERROR_EXIT( img.data == NULL, "Error while loading the image");
    Image_to_gray(&img, &gray);
    Image_save(&gray, "gray_res.jpg");

    printf("Image loaded with a width of %dpx and height of %dpx with %d channels\n", img.width, img.height, img.channels);

    Image_free(&gray);
    Image_free(&img);
}

int main() {
    Image blank;
    Image_create(&blank, 100, 100, 3, true);

    ON_ERROR_EXIT( blank.data == NULL, "Error while creating the image");
    Image_save(&blank, "blank.jpg");
    Image_free(&blank);

    return 0;
}
