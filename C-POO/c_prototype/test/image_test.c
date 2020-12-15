#include <stdlib.h>

#include "../types/Object.h"
#include "../types/Image.h"

int main() {
    printf("===============IMAGE TEST===============\n");

    struct Image *img, *gray, *sepia;

    img = (struct Image *) loadImg("assets/image_res.jpg");
    printf("Image loaded: ");
    puto(img, stdout);

    gray = (struct Image *) toGray(img);
    sepia = (struct Image *) toSepia(img);

    saveImg(gray, "assets/gray_res.jpg");
    printf("Saving gray img to disk\n");
    saveImg(gray, "assets/sepia_res.jpg");
    printf("Saving sepia img to disk\n");

    delete(img);
    delete(gray);
    delete(sepia);

    exit(EXIT_SUCCESS);
}