#include <math.h>
#include <stdlib.h>

#include "../lib/decoder.h"
#include "../types/Image.h"
#include "../types/Image.r"

void IDCT(const double *coeffs, void *_macrobloc, int channel)
{
    struct Image *macrobloc = cast(Image(), _macrobloc);

    // intermediate
    double *tmp = calloc(sizeof(double), macrobloc->width * macrobloc->height);

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

            double coef = cos((s_col * M_PI * (col + 0.5)) / macrobloc->width) * cos((s_line * M_PI * (line + 0.5)) / macrobloc->height);
            *(tmp + idx) += *(coeffs + s_idx) * coef;

            // orthogonal factors
            if (col == 0) m_col = 1 / sqrt(2);
            else m_col = 1;

            if (line == 0) m_line = 1 / sqrt(2);
            else m_line = 1;

            *(p + channel) += *(coeffs + idx) * m_col * m_line * coef;
        }
        *(tmp + idx) *= 0.25;
        *(p + channel) = floor(*(tmp + idx) + 0.5);
    }

    free(tmp);
}