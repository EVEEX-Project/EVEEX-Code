#ifndef DICTIONARY_H
#define DICTIONARY_H

#include "Object.h"

extern const void * const Dictionary(void);

struct Object *set(void *self, const char *key, const struct Object *value);
unsigned size(const void *self);
struct Object *get(const void *self, const char *key);

struct List *getKeys(const void *self);

extern const void * const DictionaryClass (void);

#endif