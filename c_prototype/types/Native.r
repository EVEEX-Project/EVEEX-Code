#ifndef NATIVE_R
#define NATIVE_R

#include "Object.r"

struct Native {
    const struct Object _;
    void *value;
    size_t size;
};

struct NativeClass {
    const struct Class _;
};


#endif