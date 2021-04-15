
#include <stdlib.h>
#include <time.h>
#include "types/Image.h"
#include "types/Image.r"
#include "types/List.h"
#include "lib/huffman.h"
#include "lib/encoder.h"
#include "lib/logger.h"

void saveMacroBlocksToDisk(const struct List *macroBlocks) {
    for (int k = 0; k < count(macroBlocks); k++) {
        char filename[64];
        sprintf(filename, "out/out_%u.png", k);
        saveImg(cast(Image(), lookAt(macroBlocks, k)), filename);
    }
}

int main(int argc, char *argv[]) {
    clock_t t;
    t = clock();

    shouldLogToFile = 0;
    currentLogLevel = DEBUG;

    // Printing pretty hello world
    helloWorld("1.2.0");
    //testLog();

    // Loading the image
    struct Image *img;
    img = (struct Image *) loadImg(argv[1]);

    // Conversion to YUV
    const struct Image *yuv = toYUVImage(img);

    // Splitting in macroblocs
    const struct List *macroBlocks = splitInMacroblocs(yuv, 16);
    // saveMacroBlocksToDisk(macroBlocks);

    for (int i=0; i < count(macroBlocks); i++) {
        const struct Image *test = cast(Image(), lookAt(macroBlocks, i));
        for (int j=0; j < 3; j++) {
            DCT(test, j);
        }
    }

    delete((void *) macroBlocks);
    delete((void *) yuv);
    delete(img);

    t = clock() - t;
    double time_taken = ((double)t)/CLOCKS_PER_SEC; // in seconds

    printf("L'algorithme a mis %f secondes à s'éxécuter\n", time_taken);

    exit(EXIT_SUCCESS);
}