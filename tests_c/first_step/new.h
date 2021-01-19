//
// Created by alexandre on 24/11/2020.
//

#ifndef C_POO_NEW_H
#define C_POO_NEW_H

#include <stdlib.h>

void *new(const void *type, ...);
void delete(void *item);
int differ(const void *a, const void *b);
void *clone(const void *object);
size_t sizeOf(const void *self);

#endif //C_POO_NEW_H