//
// Created by alexandre on 25/11/2020.
//

#include <assert.h>
#include <string.h>
#include <stdarg.h>
#include "class.h"
#include "new.h"
#include "Point.h"

struct Point {
    const void *class;	/* Doit être en premier */
    int x;
    int y;
};

static void *Point_ctor(void *_self, va_list *app) {
    struct Point *self = _self; // on récupère les arguments
    const int x = va_arg(*app, int);
    const int y = va_arg(*app, int);

    self->x = x;
    self->y = y;
    return self; // on retourne l'instant de variable ainsi crée
}

static void *Point_dtor(void *_self) {
    struct Point *self = _self;
    self->x = 0, self->y = 0;
    return self; // on retourne le pointeur sur l'objet pour le libérer dans delete()
}

static void *Point_clone(const void *_self) {
    const struct Point *self = _self;
    return new(Point, self->x, self->y); // crée une nouvelle instance dynamiquement
}

static int Point_differ(const void *_self, const void *_b) {
    const struct Point *self = _self;
    const struct Point *b = _b;

    if (self == b) // si il s'agit du même objet c'est forcément vrai
        return 0;
    if (!b || b->class != Point) // types différents donc f
        return 1;
    return self->x != b->x || self->y != b->y; // on compare leur contenu
}

static const struct Class _Point = {
        sizeof(struct Point),
        Point_ctor, Point_dtor,
        Point_clone, Point_differ
};
const void *Point = &_Point;