//
// Created by alexandre on 12/01/2021.
//

#ifndef C_PROTOTYPE_ENCODER_H
#define C_PROTOTYPE_ENCODER_H

#define PI 3.141592653589793
#define N 16

double *DCT(const void *macrobloc, int channel);
void IDCT_N(float C[N][N], int reconstructed_matrix[N][N]);

const struct Image *toYUVImage(const void *self);
const struct List *splitInMacroblocs(const void *self, int size);

#endif //C_PROTOTYPE_ENCODER_H
