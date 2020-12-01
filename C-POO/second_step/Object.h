#ifndef OBJECT_H
#define OBJECT_H

#include <stdarg.h>
#include <stddef.h>
#include <stdio.h>

#include "Object.r"

extern const void * Object;						/* new(Object); */

void *new (const void *class, ...);
void delete (void * self);

const void *classOf (const void *self);
size_t sizeOf (const void *self);

void *ctor (void *self, va_list * app);
void *dtor (void *self);
int differ (const void *self, const void *b);
int puto (const void *self, FILE *fp);

int isA(const void *self, const struct Class *class);
int isOf(const void *self, const struct Class *class);
void *cast(const void *self, const struct Class *class);

extern const void * Class;						/* new(Class, "name", super, size
															sel, meth, ... 0); */

const void * super (const void * self);			/* Superclasse de la classe */

#endif