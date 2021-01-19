#ifndef DICTIONARYITEM_R
#define DICTIONARYITEM_R

#include "Object.r"

struct DictionaryItem {
    const struct Object _;
    const char *key;
    const struct Object *value;
};

#endif