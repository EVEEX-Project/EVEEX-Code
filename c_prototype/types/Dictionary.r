#ifndef DICTIONARY_R
#define DICTIONARY_R

#include "Object.r"
#include "List.r"

struct Dictionary {
    const struct Object _;
    const struct List *items;
};

struct DictionaryClass {
    const struct Class _;

    struct Object *(*set) (const void *self, const char *key, const struct Object *value);
    unsigned (*size) (const void *self);
    struct Object *(*get) (const void *self, const char *key);
    struct List *(*getKeys) (const void *self);
};

#endif