//
// Created by alexandre on 12/01/2021.
//

#include <stdlib.h>
#include <assert.h>
#include <stdio.h>
#include <math.h>
#include "encoder.h"
#include "huffman.h"
#include "../types/Image.h"
#include "../types/Image.r"
#include "../types/Native.h"
#include "../types/Native.r"

const struct Image *toYUVImage(const void *_self) {
    const struct Image *self = cast(Image(), _self);

    struct Image *yuv = new(Image(), self->width, self->height, self->channels, 1);

    for (uint8_t *p = self->data, *yp = yuv->data; p != self->data + self->size; p += self->channels, yp += yuv->channels) {
        uint8_t red = *p, green = *(p+1), blue = *(p+2);
        uint8_t y = 0.299 * red + 0.587 * green + 0.114 * blue;
        uint8_t u = -0.147 * red + -0.289 * green + 0.436 * blue;
        uint8_t v = 0.615 * red + -0.515 * green + -0.100 * blue;

        *yp = y, *(yp+1) = u, *(yp+2) = v;

        // if there is transparency
        if (self->channels == 4) {
            *(yp+3) = *(p+3);
        }
    }

    return yuv;
}

const struct List *splitInMacroblocs(const void *_self, int size) {
    const struct Image *self = cast(Image(), _self);

    // check for a valid image
    if(self->allocationType == NO_ALLOCATION || self->channels < 3) {
        perror("The input image must have at least 3 channels.");
        exit(EXIT_FAILURE);
    }

    // Checking if picture size if compatible
    assert(self->width % size == 0);
    assert(self->height % size == 0);

    // number of blocks
    long widthMB = self->width / size;
    long heightMB = self->height / size;

    // Populating the macroblocs list
    struct List* macroblocs = new(List(), widthMB * heightMB);
    for (int k = 0; k < widthMB * heightMB ; k++) {
        struct Image *block = new(Image(), size, size, self->channels, 1);
        addLast(macroblocs, (void *) block);
        //puto(block, stdout);
    }
    printf("Created %u blocks\n", count(macroblocs));

    // Iterating over the pixels
    struct Image *mBlock;
    for (uint8_t *p = self->data; p != self->data + self->size; p += self->channels) {
        unsigned idx = (p - self->data) / self->channels;
        unsigned line = idx / self->width;
        unsigned col = idx - (line * self->width);
        unsigned blockId = col / size + (line / size) * widthMB;

        // switching to the correct macroblock
        if (col % size == 0) {
            mBlock = cast(Image(), lookAt(macroblocs, blockId));
        }


        // getting coordinates on the macrobloc
        unsigned mbLine = line - (blockId / widthMB) * size;
        unsigned mbCol = col - (blockId % widthMB) * size;
        unsigned mbIdx = mbLine * size + mbCol;

        uint8_t *c_p = mBlock->data + (mbIdx * self->channels);
        *(c_p) = *p;
        *(c_p + 1) = *(p+1);
        *(c_p + 2) = *(p+2);
        // if there was transparency
        if(self->channels == 4) {
            // update the transparency pixel
            *(c_p + 3) = *(p+3);
        }
    }

    return macroblocs;
}

double *DCT(const void *_macrobloc, int channel)
{
    const struct Image *macrobloc = cast(Image(), _macrobloc);
    double *coeffs = calloc(sizeof(double), macrobloc->width * macrobloc->height);

    unsigned idx, line, col;
    double m_line, m_col;
    for (uint8_t *p = macrobloc->data; p != macrobloc->data + macrobloc->size; p += macrobloc->channels) {
        idx = (p - macrobloc->data) / macrobloc->channels;
        line = idx / macrobloc->width;
        col = idx - (line * macrobloc->width);

        // double sum
        unsigned s_idx, s_line, s_col;
        for (uint8_t *sp = macrobloc->data; sp != macrobloc->data + macrobloc->size; sp += macrobloc->channels) {
            s_idx = (p - macrobloc->data) / macrobloc->channels;
            s_line = s_idx / macrobloc->width;
            s_col = idx - (s_line * macrobloc->width);

            double coef = cos((M_PI * (s_col + 0.5) * col) / macrobloc->width) * cos((M_PI * (s_line + 0.5) * line) / macrobloc->height);
            *(coeffs + idx) += *(p + channel) * coef;
        }

        // orthogonal factors
        if (col == 0) m_col = 1 / sqrt(2);
        else m_col = 1;

        if (line == 0) m_line = 1 / sqrt(2);
        else m_line = 1;

        *(coeffs + idx) *= 0.25 * m_col * m_line;
    }

    return coeffs;
}

struct List *zigzagLinearisation(const void *_macroBloc) {
    const struct Image *macroBloc = cast(Image(), _macroBloc);

    // init the final list
    struct List *res = new(List());

    int i = 0, j = 0;

    // while we are not at the end of the bloc
    while (i < macroBloc->height && j < macroBloc->width) {
        // code
        addLast(res, new(Native(), 15, sizeof(unsigned)));
    }

    return res;
}

void quantization(void *_zigzagList, double threshold) {
    struct List *zigzagList = cast(List(), _zigzagList);

    struct Native *ptr;
    for (int k = 0; k < count(zigzagList); k++) {
        ptr = cast(Native(), lookAt(zigzagList, k));
        if (*((double *) ptr->value) <= threshold)
            *((double *) ptr->value) = 0;
    }
}

struct List *runLevel(const void *_quantizedList) {
    const struct List *quantizedList = cast(List(), _quantizedList);

    struct List *pairs = new(List());

    // exemple
    int pair[2] = {4, 15};
    addLast(pairs, new(Native(), pair, sizeof(int) * 2));

    return pairs;
}