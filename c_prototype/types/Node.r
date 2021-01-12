#ifndef NODE_R
#define NODE_R

#include "Object.r"

struct Node {
    const struct Object _;
    struct Object *value;
    unsigned long frequency;
    struct Node *left;
    struct Node *right;
};

struct NodeClass {
	const struct Class _;
};


#endif