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
struct Object *removeItem(void *self, const struct Object *element);
unsigned indexOf(const void *self, const struct Object *element);

struct List *copyList(const void *self);
void deleteChildren(const void *self);

extern const void * const ListClass(void);		/* adds draw */

#endif