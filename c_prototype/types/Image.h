#ifndef IMAGE_H
#define IMAGE_H

#include "Object.h"

extern const void * const Image(void);
extern const void * const ImageClass(void);

const struct Image *loadImg(const char *fileName);

void saveImg(const void *self, const char *fileName);
const struct Image *toGray(const void *self);
const struct Image *toSepia(const void *self);

const struct List *splitInMacroblocs(const void *self, int size);

#endif