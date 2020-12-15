#include "Object.r"

struct RGBPixel {
    const struct Object _;
    int r, g, b, a;
};

struct YUVPixel {
    const struct Object _;
    int y, cb, cr, a;
};

struct PixelClass {
    const struct Class _;
    void (*draw) (const void *self);
};
