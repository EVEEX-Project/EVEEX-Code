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
    struct List *self = super_ctor(List(), _self, app);

    self->dim = va_arg(*app, int);
    // Garbage detection
    if (self->dim > 1024 * 16) {
        // printf("No size given, default to min..\n");
        self->dim = MIN;
    } // else printf("Found a size : %u\n", self->dim);

    self->buf = malloc(self->dim * sizeof * self->buf);
    assert(self->buf);
    
    return self;
}

static void *List_dtor(struct List *self) {
    free(self->buf), self->buf = 0;
    return super_dtor(List(), self);
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

static struct Object *List_addFirst(struct List *_self, const struct Object *element) {
    struct List *self = _self;

    if (!self->count)
        return add1(self, element);
    extend(self);
    if (self->begin == 0)
        self->begin = self->dim;
    self->buf[-- self->begin] = element;
    return (void *) element;
}

static struct Object *List_addLast(struct List *_self, const struct Object *element) {
    struct List *self = _self;

    if (!self->count)
        return add1(self, element);
    extend(self);
    if (self->end >= self->dim)
        self->end = 0;
    self->buf[self->end ++] = element;
    return (void *) element;
}

static unsigned List_count(const struct List *_self) {
    const struct List *self = _self;
    return self->count;
}

static struct Object *List_lookAt(const struct List *_self, unsigned n) {
    const struct List *self = _self;

    return (void *) (n >= self->count ? 0 :
                     self->buf[(self->begin + n) % self->dim]);
}

static struct Object *List_takeFirst(struct List *_self) {
    struct List *self = _self;

    if (! self->count)
        return 0;
    --self->count;
    if (self->begin >= self->dim)
        self->begin = 0;
    return (void *) self->buf[self->begin++];
}

static struct Object *List_takeLast(struct List *_self) {
    struct List *self = _self;

    if (!self->count)
        return 0;
    --self->count;
    if (self->end == 0)
        self->end = self->dim;
    return (void *) self->buf[--self->end];
}

static unsigned List_indexOf(const struct List *_self, const struct Object *element) {
    const struct List *self = _self;

    // iteration over the elements
    for (unsigned i = 0; i < self->count; i++) {
        // if it's the same object
        if (!differ(lookAt(self, i), element))
            return i;
    }
    // not found
    return -1;
}

static struct Object *List_removeItem(struct List *_self, const struct Object *element) {
    struct List *self = _self;

    struct List *tmp = new(List());
    unsigned index = indexOf(self, element);
    if (index == -1) return NULL;

    struct Object *item;
    struct Object *toReturn;
    if (index < self->count) {
        while (differ(item = takeFirst(self), element))
            addFirst(tmp, item);
        toReturn = item;
        while (count(tmp) > 0) {
            item = takeFirst(tmp);
            addFirst(self, item);
        }
    }
    else {
        while (differ(item = takeLast(self), element))
            addLast(tmp, item);
        toReturn = item;
        while (count(tmp) > 0) {
            item = takeLast(tmp);
            addLast(self, item);
        }
    }

    return toReturn;
}

/* added methods */
struct Object *addFirst(void *_self, const struct Object *element) {
    struct List *self = cast(List(), _self);
    const struct ListClass *class = classOf(self);

    assert(class->addFirst);
    return class->addFirst(self, element);
}

struct Object *addLast(void *_self, const struct Object *element) {
    struct List *self = cast(List(), _self);
    const struct ListClass *class = classOf(self);

    assert(class->addLast);
    return class->addLast(self, element);
}

unsigned count(const void *_self) {
    struct List *self = cast(List(), _self);
    const struct ListClass *class = classOf(self);

    assert(class->count);
    return class->count(self);
}

struct Object *lookAt(const void *_self, unsigned n) {
    struct List *self = cast(List(), _self);
    const struct ListClass *class = classOf(self);

    assert(class->lookAt);
    return class->lookAt(self, n);
}

struct Object *takeFirst(void *_self) {
    struct List *self = cast(List(), _self);
    const struct ListClass *class = classOf(self);

    assert(class->takeFirst);
    return class->takeFirst(self);
}

struct Object *takeLast(void *_self) {
    struct List *self = cast(List(), _self);
    const struct ListClass *class = classOf(self);

    assert(class->takeLast);
    return class->takeLast(self);
}

struct Object *removeItem(void *_self, const struct Object *element) {
    struct List *self = cast(List(), _self);
    const struct ListClass *class = classOf(self);

    assert(class->removeItem);
    return class->removeItem(self, element);
}

unsigned indexOf(const void *_self, const struct Object *element) {
    struct List *self = cast(List(), _self);
    const struct ListClass *class = classOf(self);

    assert(class->indexOf);
    return class->indexOf(self, element);
}

/* ListClass */
static void * ListClass_ctor (void *_self, va_list *app) {
    struct ListClass * self
            = super_ctor(ListClass(), _self, app);
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
        else if (selector == (voidf) indexOf)
            *(voidf *) &self->indexOf = method;
        else if (selector == (voidf) removeItem)
            *(voidf *) &self->removeItem = method;
    }
#ifdef va_copy
    va_end(ap);
#endif

    return self;
}

/* Initialisation */
static const void *_ListClass, *_List;

const void * const ListClass(void) {
    return _ListClass ? _ListClass :  (_ListClass = new(Class(), "ListClass",
            Class(), sizeof(struct ListClass),
            ctor, ListClass_ctor,
            (void *) 0));
}

const void * const List(void) {
    return _List ? _List : (_List = new(ListClass(), "List",
            Object(), sizeof(struct List),
            ctor, List_ctor,
            dtor, List_dtor,
            addFirst, List_addFirst,
            addLast, List_addLast,
            count, List_count,
            lookAt, List_lookAt,
            takeFirst, List_takeFirst,
            takeLast, List_takeLast,
            indexOf, List_indexOf,
            removeItem, List_removeItem,
           (void *) 0));
}