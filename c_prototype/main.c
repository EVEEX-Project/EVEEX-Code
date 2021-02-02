
#include <stdlib.h>
#include "types/Image.h"
#include "types/Image.r"
#include "types/List.h"
#include "lib/huffman.h"
#include "lib/encoder.h"

void helloWorld(char* version) {
    printf("\033[1;35m            _______    _______________  __\n");
    printf("           / ____/ |  / / ____/ ____/ |/ /\n");
    printf("          / __/  | | / / __/ / __/  |   /\n");
    printf("         / /___  | |/ / /___/ /___ /   |\n");
    printf("        /_____/  |___/_____/_____//_/|_|\n");
    printf("          ___  ___  / __/ _ \\/ ___/ _ |\n");
    printf("         / _ \\/ _ \\/ _// ___/ (_ / __ |\n");
    printf("         \\___/_//_/_/ /_/   \\___/_/ |_|\n\n");
    printf("\033[0;36m32-bit RISC-V Open Source video compression program\n");
    printf("                version \033[0;31m%s\033[0m\n\n", version);
    printf("─────────────────────\033[1;37m LOGS \033[0m────────────────────────\n");
}

void saveMacroBlocksToDisk(const struct List *macroBlocks) {
    for (int k = 0; k < count(macroBlocks); k++) {
        char filename[64];
        sprintf(filename, "out/out_%u.png", k);
        saveImg(cast(Image(), lookAt(macroBlocks, k)), filename);
    }
}

int main() {
    // Printing pretty hello world
    helloWorld("1.2.0");

    // Loading the image
    struct Image *img;
    img = (struct Image *) loadImg("assets/image_res.png");

    // Conversion to YUV
    const struct Image *yuv = toYUVImage(img);

    // Splitting in macroblocs
    const struct List *macroBlocks = splitInMacroblocs(yuv, 10);
    // saveMacroBlocksToDisk(macroBlocks);

    const struct Image *test = cast(Image(), lookAt(macroBlocks, 5));
    double *coeffs = DCT(test, 0);

    delete((void *) macroBlocks);
    delete((void *) yuv);
    delete(img);

    exit(EXIT_SUCCESS);
}