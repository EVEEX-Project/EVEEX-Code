
#include <stdlib.h>
#include "types/Image.h"
#include "types/Image.r"
#include "types/List.h"


int main() {
    struct Image *img;

    img = (struct Image *) loadImg("assets/image_res.png");
    puto(img, stdout);

    const struct List *macroBlocks = splitInMacroblocs(img, 10);

    for (int k = 0; k < count(macroBlocks); k++) {
        char filename[64];
        sprintf(filename, "out/out_%u.png", k);
        saveImg(cast(Image(), lookAt(macroBlocks, k)), filename);
    }

    delete((void *) macroBlocks);
    delete(img);

    exit(EXIT_SUCCESS);
}