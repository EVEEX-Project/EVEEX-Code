//
// Created by alexandre on 12/01/2021.
//

#ifndef C_PROTOTYPE_ENCODER_H
#define C_PROTOTYPE_ENCODER_H

#define PI 3.141592653589793
#define N 16

double *DCT(const void *macrobloc, int channel);

const struct Image *toYUVImage(const void *self);
const struct List *splitInMacroblocs(const void *self, int size);
struct List *zigzagLinearisation(const void *macroBloc);
void quantization(void *zigzagList, double threshold);
struct List *runLevel(const void *quantizedList);

#endif //C_PROTOTYPE_ENCODER_H
