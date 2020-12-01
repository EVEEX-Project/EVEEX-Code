#include <assert.h>
#include <stdlib.h>
#include <string.h>

#include "List.r"
#include "List.h"

#ifndef	MIN
#define	MIN	32		// minimal buffer dimension
#endif

/* LIST */
static void *List_ctor (void *_self, va_list *app) {
    struct List *self = super_ctor(List, _self, app);

    if (! (self->dim = va_arg(*app, unsigned)))
        self->dim = MIN;
    self->buf = malloc(self->dim * sizeof * self->buf);
    assert(self->buf);
    
    return self;
}

static void *List_dtor(struct List *self) {
    free(self->buf), self->buf = 0;
    return super_dtor(List, self);
}

static void *add1(struct List *self, const void *element)
{
    self->end = self->count = 1;
    return (void *) (self->buf[self->begin = 0] = element);
}

static void extend(struct List *self)	// one more element
{
    if (self->count >= self->dim)
    {
        self->buf = realloc(self->buf, 2 * self->dim* sizeof * self->buf);

        assert(self->buf);
        if (self->begin && self->begin != self->dim)
        {
            memcpy(self->buf + self->dim + self->begin,
                    self->buf + self->begin,
                    (self->dim - self->begin) * sizeof * self->buf);
            self->begin += self->dim;
        }
        else
            self->begin = 0;
        self->dim *= 2;
    }
    ++self->count;
}

static struct Object *List_addFirst(void *_self, const struct Object *element) {
    struct List *self = _self;

    if (!self->count)
        return add1(self, element);
    extend(self);
    if (self->begin == 0)
        self->begin = self->dim;
    self->buf[-- self->begin] = element;
    return (void *) element;
}

static struct Object *List_addLast(void *_self, const struct Object *element) {
    struct List *self = _self;

    if (!self->count)
        return add1(self, element);
    extend(self);
    if (self->end >= self->dim)
        self->end = 0;
    self->buf[self->end ++] = element;
    return (void *) element;
}

static unsigned List_count(const void *_self) {
    const struct List *self = _self;
    return self->count;
}

static struct Object *List_lookAt(const void *_self, unsigned n) {
    const struct List *self = _self;

    return (void *) (n >= self->count ? 0 :
                     self->buf[(self->begin + n) % self->dim]);
}

static struct Object *List_takeFirst(void *_self) {
    struct List *self = _self;

    if (! self->count)
        return 0;
    --self->count;
    if (self->begin >= self->dim)
        self->begin = 0;
    return (void *) self->buf[self->begin++];
}

static struct Object *List_takeLast(void *_self) {
    struct List *self = _self;

    if (!self->count)
        return 0;
    --self->count;
    if (self->end == 0)
        self->end = self->dim;
    return (void *) self->buf[--self->end];
}

/* added methods */
struct Object *addFirst(void *_self, const struct Object *element) {
    const struct ListClass *class = classOf(_self);

    assert(class->addFirst);
    return class->addFirst(_self, element);
}

struct Object *addLast(void *_self, const struct Object *element) {
    const struct ListClass *class = classOf(_self);

    assert(class->addLast);
    return class->addLast(_self, element);
}

unsigned count(const void *_self) {
    const struct ListClass *class = classOf(_self);

    assert(class->count);
    return class->count(_self);
}

struct Object *lookAt(const void *_self, unsigned n) {
    const struct ListClass *class = classOf(_self);

    assert(class->lookAt);
    return class->lookAt(_self, n);
}

struct Object *takeFirst(void *_self) {
    const struct ListClass *class = classOf(_self);

    assert(class->takeFirst);
    return class->takeFirst(_self);
}

struct Object *takeLast(void *_self) {
    const struct ListClass *class = classOf(_self);

    assert(class->takeLast);
    return class->takeLast(_self);
}


/* ListClass */
static void * ListClass_ctor (void *_self, va_list *app) {
    struct ListClass * self
            = super_ctor(ListClass, _self, app);
    typedef void (*voidf) ();
    voidf selector;
#ifdef va_copy
    va_list ap; va_copy(ap, *app);
#else
    va_list ap = *app;
#endif

    while ((selector = va_arg(ap, voidf)))
    {
        voidf method = va_arg(ap, voidf);

        if (selector == (voidf) addFirst)
            *(voidf *) &self->addFirst = method;
        else if (selector == (voidf) addLast)
            *(voidf *) &self->addLast = method;
        else if (selector == (voidf) count)
            *(voidf *) &self->count = method;
        else if (selector == (voidf) lookAt)
            *(voidf *) &self->lookAt = method;
        else if (selector == (voidf) takeFirst)
            *(voidf *) &self->takeFirst = method;
        else if (selector == (voidf) takeLast)
            *(voidf *) &self->takeLast = method;
    }
#ifdef va_copy
    va_end(ap);
#endif

    return self;
}

/* Initialisation */
const void *ListClass, *List;

void initList(void)
{
    if (!ListClass)
        ListClass = new(Class, "ListClass",
                         Class, sizeof(struct ListClass),
                         ctor, ListClass_ctor,
                         0);
    if (!List)
        List = new(ListClass, "List",
                    Object, sizeof(struct List),
                    ctor, List_ctor,
                    addFirst, List_addFirst,
                    addLast, List_addLast,
                    count, List_count,
                    lookAt, List_lookAt,
                    takeFirst, List_takeFirst,
                    takeLast, List_takeLast,
                    0);
}