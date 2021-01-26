//
// Created by alexandre on 12/01/2021.
//

#ifndef C_PROTOTYPE_ENCODER_H
#define C_PROTOTYPE_ENCODER_H

const struct Image *toYUVImage(const void *self);
const struct List *splitInMacroblocs(const void *self, int size);

#endif //C_PROTOTYPE_ENCODER_H
