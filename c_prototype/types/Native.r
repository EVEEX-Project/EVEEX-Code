#ifndef NATIVE_R
#define NATIVE_R

#include "Object.r"

struct Native {
    const struct Object _;
    const void *value;
};

struct NativeClass {
    const struct Class _;
};


#endif