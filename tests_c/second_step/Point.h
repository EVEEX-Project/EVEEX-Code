#ifndef POINT_H
#define POINT_H

#include "Object.h"

extern const void * const Point(void);			/* new(Point, x, y); */

void draw (const void *self);
void move (void *point, int dx, int dy);

extern const void * const PointClass(void);		/* adds draw */

#endif