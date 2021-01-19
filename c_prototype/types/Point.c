#include <assert.h>

#include "Point.r"
#include "Point.h"

/* Point */
static void *Point_ctor (void *_self, va_list *app) {
    struct Point *self = super_ctor(Point(), _self, app);

    self->x = va_arg(*app, int); // On récupère les arguments dynamiques
    self->y = va_arg(*app, int);
    return self;
}

static int Point_differ(const void *_self, const void *_other) {
    const struct Point *self = cast(Point(), _self);

    if (classOf(self) != classOf(_other)) return 1;

    const struct Point *otherObj = cast(Point(), _other);
    return !(self->x == otherObj->x && self->y == otherObj->y);
}

static void Point_draw (const void *_self) {
    const struct Point *self = _self;
    printf("\".\" at %d,%d\n", self->x, self->y);
}

static void Point_puto(const void * _self, FILE * fp) {
    const struct Point *self = _self;
    printf("Point (x, y): (%d, %d)\n", self->x, self->y);
}

static void *Point_clone(const void *_self) {
    const struct Point *self = _self;
    return new(Point(), self->x, self->y);
}

void draw (const void *_self) {
    const struct PointClass *class = classOf(_self);

    assert(class->draw);
    class->draw(_self);
}

void super_draw (const void *_class, const void *_self) {
    const struct PointClass *superclass = super(_class);

    assert(_self && superclass->draw);
    superclass->draw(_self);
}

void move (void *_self, int dx, int dy)
{	struct Point *self = _self;

    self->x += dx, self->y += dy;
}

/* PointClass */
static void * PointClass_ctor (void * _self, va_list * app) {
    struct PointClass * self
            = super_ctor(PointClass(), _self, app);
    typedef void (*voidf) ();
    voidf selector;
#ifdef va_copy
    va_list ap; va_copy(ap, *app);
#else
    va_list ap = *app;
#endif

    while ((selector = va_arg(ap, voidf)))
    {	voidf method = va_arg(ap, voidf);

        if (selector == (voidf) draw)
            *(voidf *) &self->draw = method;
    }
#ifdef va_copy
    va_end(ap);
#endif

    return self;
}

/* Initialisation */
static const void *_Point, *_PointClass;

const void *const PointClass(void) {
    return _PointClass ? _PointClass : (_PointClass = new(Class(), "PointClass",
            Class(), sizeof(struct PointClass),
            ctor, PointClass_ctor,
            (void *) 0));
}

const void *const Point(void) {
    return _Point ? _Point : (_Point = new(PointClass(), "Point",
           Object(), sizeof(struct Point),
           ctor, Point_ctor,
           draw, Point_draw,
           clone, Point_clone,
           differ, Point_differ,
           (void *) 0));
}