#ifndef LIST_R
#define LIST_R

#include "Object.r"

struct List {
    const struct Object _;
    const void **buf;
    unsigned dim;
    unsigned count;
    unsigned begin;
    unsigned end;
};

struct ListClass {
    const struct Class _;

    struct Object *(*addFirst) (const void *self, const struct Object *element);
    struct Object *(*addLast) (const void *self, const struct Object *element);
    unsigned (*count) (const void *self);
    struct Object *(*lookAt) (const void *self, unsigned n);
    struct Object *(*takeFirst) (const void *self);
    struct Object *(*takeLast) (const void *self);
    unsigned (*indexOf) (const void *self, const struct Object *element);
    struct Object *(*removeItem) (void *self, const struct Object *element);
};

#endif