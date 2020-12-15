#include <stdlib.h>
#include <time.h>

#include "../types/Object.h"
#include "../types/Image.h"


int main() {
    printf("===============IMAGE TEST===============\n");

    struct Image *img, *gray, *sepia;
    clock_t t;
    double time_taken;

    t = clock();
    img = (struct Image *) loadImg("assets/image_res_high.jpg");
    t = clock() - t;
    time_taken = ((double)t) / CLOCKS_PER_SEC;
    printf("Image loaded in %.2fms: ", time_taken * 1000);
    puto(img, stdout);

    gray = (struct Image *) toGray(img);
    sepia = (struct Image *) toSepia(img);

    t = clock();
    saveImg(gray, "assets/gray_res.jpg");
    t = clock() - t;
    time_taken = ((double)t) / CLOCKS_PER_SEC;
    printf("Saving gray img to disk in %.2fms\n", time_taken * 1000);
    t = clock();
    saveImg(sepia, "assets/sepia_res.jpg");
    t = clock() - t;
    time_taken = ((double)t) / CLOCKS_PER_SEC;
    printf("Saving sepia img to disk in %.2fms\n", time_taken * 1000);

    delete(img);
    delete(gray);
    delete(sepia);

    exit(EXIT_SUCCESS);
}