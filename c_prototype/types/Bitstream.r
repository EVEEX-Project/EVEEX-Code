#ifndef BITSTREAM_R
#define BITSTREAM_R

#include "Object.r"
#include "List.r"

enum MessageTypes {
    HEADER_MSG, DICT_MSG, BODY_MSG, TAIL_MSG
};

struct Bitstream {
    const struct Object _;
    int frame_id;
    enum MessageTypes type;
    unsigned long size;
    char *data;
};

struct BitstreamClass {
	const struct Class _;
};

#endif