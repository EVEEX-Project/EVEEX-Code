
#include <stdlib.h>
#include "types/Image.h"
#include "types/Image.r"
#include "types/List.h"
#include "lib/huffman.h"
#include "lib/encoder.h"

void saveMacroBlocksToDisk(const struct List *macroBlocks) {
    for (int k = 0; k < count(macroBlocks); k++) {
        char filename[64];
        sprintf(filename, "out/out_%u.png", k);
        saveImg(cast(Image(), lookAt(macroBlocks, k)), filename);
    }
}

int main() {
    // Loading the image
    struct Image *img;
    img = (struct Image *) loadImg("assets/image_res.png");

    // Conversion to YUV
    const struct Image *yuv = toYUVImage(img);

    // Splitting in macroblocs
    const struct List *macroBlocks = splitInMacroblocs(yuv, 25);
    // saveMacroBlocksToDisk(macroBlocks);

    //const struct Image *test = cast(Image(), lookAt(macroBlocks, 5));

    delete((void *) macroBlocks);
    delete((void *) yuv);
    delete(img);

    exit(EXIT_SUCCESS);
}