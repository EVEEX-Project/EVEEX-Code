#ifndef LIST_H
#define LIST_H

#include "Object.h"

extern const void *List;			/* new(Point, x, y); */

struct Object *addFirst(void *self, const struct Object *element);
struct Object *addLast(void *self, const struct Object *element);
unsigned count(const void *self);
struct Object *lookAt(const void *self, unsigned n);
struct Object *takeFirst(void *self);
struct Object *takeLast(void *self);

extern const void *ListClass;		/* adds draw */

void initList(void);

#endif