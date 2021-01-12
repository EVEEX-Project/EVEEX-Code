#include <stdlib.h>

#include "../types/Object.h"
#include "../types/Pixel.h"

int main() {
    printf("/* -------- TEST PIXELS -------- */\n");

    void *rgb = new(RGBPixel(), 15, 255, 16);
    void *yuv = new(YUVPixel(), 252, 15, 15);

    puto(rgb, stdout);
    puto(yuv, stdout);

    delete(rgb);
    delete(yuv);

    exit(EXIT_SUCCESS);
}