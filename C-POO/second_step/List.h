#ifndef LIST_H
#define LIST_H

#include "Object.h"

extern const void * const List(void);			/* new(Point, x, y); */

struct Object *addFirst(void *self, const struct Object *element);
struct Object *addLast(void *self, const struct Object *element);
unsigned count(const void *self);
struct Object *lookAt(const void *self, unsigned n);
struct Object *takeFirst(void *self);
struct Object *takeLast(void *self);
unsigned indexOf(const void *self, const struct Object *element);

extern const void * const ListClass(void);		/* adds draw */

#endif