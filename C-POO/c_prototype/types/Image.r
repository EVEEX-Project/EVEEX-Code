#include "Object.r"

enum allocation_type {
    NO_ALLOCATION, SELF_ALLOCATED, STB_ALLOCATED
};

struct Image {
    const struct Object _;
    int width;
    int height;
    int channels;
    size_t size;
    uint8_t *data;
    enum allocation_type allocationType;
};

struct ImageClass {
	const struct Class _;
	void (*saveImg) (const void *self, const char *fileName);
	const struct Image *(*toGray) (const void *self);
    const struct Image *(*toSepia) (const void *self);
};