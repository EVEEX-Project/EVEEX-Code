#include <assert.h>
#include <stdlib.h>
#include <string.h>

#include "Dictionary.r"
#include "Dictionary.h"

#include "List.h"
#include "DictionaryItem.r"
#include "DictionaryItem.h"
#include "Native.h"

#ifndef	MIN
#define	MIN	32		// minimal buffer dimension
#endif

/* DICTIONARY */
static void *Dictionary_ctor (void *_self, va_list *app) {
    struct Dictionary *self = super_ctor(Dictionary(), _self, app);

    unsigned dim = va_arg(*app, unsigned);
    // garbage detection
    if (dim > 1024 * 16)
        dim = MIN;

    self->items = new(List(), dim);
    assert(self->items);

    return self;
}

static void *Dictionary_dtor(struct Dictionary *self) {
    /*while (count(self->items) != 0) {
        void *objToFree = takeLast((void *) self->items);
        delete(objToFree);
    }*/
    delete((void *) self->items);
    return super_dtor(Dictionary(), self);
}

static struct Object *Dictionary_set(struct Dictionary *_self, const char *key, const struct Object *value) {
    struct Dictionary *self = _self;

    // looking for the entry in the dictionary
    unsigned found = -1;
    for (unsigned i = 0; i < count(self->items); i++) {
        struct DictionaryItem *item = cast(DictionaryItem(), lookAt(self->items, i));
        if (strcmp(item->key, key) == 0) {
            found = i;
            break;
        }
    }

    // if this is a new entry
    if (found == -1) {
        void *newItem = new(DictionaryItem(), key, value);
        addLast((void *) self->items, newItem);
        return newItem;
    }
    // else there is already an entry
    else {
        struct DictionaryItem *existingItem = cast(DictionaryItem(), lookAt(self->items, found));
        existingItem->value = value;
        return (void *) existingItem;
    }
}

static unsigned Dictionary_size(const struct Dictionary *_self) {
    const struct Dictionary *self = _self;
    assert(self->items);

    return count(self->items);
}

static struct Object *Dictionary_get(const struct Dictionary *_self, const char *key) {
    const struct Dictionary *self = _self;

    for (unsigned i = 0; i < count(self->items); i++) {
        struct DictionaryItem *item = cast(DictionaryItem(), lookAt(self->items, i));
        if (strcmp(item->key, key) == 0) {
            return (void *) item->value;
        }
    }

    // not found
    return NULL;
}

static struct List *Dictionary_getKeys(const struct Dictionary *_self) {
    const struct Dictionary *self = _self;

    struct List *keys = new(List());

    for (unsigned i = 0; i < size(self); i++) {
        struct DictionaryItem *item = cast(DictionaryItem(), lookAt(self->items, i));
        char *newKey = malloc(strlen(item->key) + 1);
        strcpy(newKey, item->key);
        addLast(keys, new(Native(), newKey, strlen(item->key) + 1));
    }

    return keys;
}

/* added methods */
struct Object *set(void *_self, const char *key, const struct Object *value) {
    struct Dictionary *self = cast(Dictionary(), _self);
    const struct DictionaryClass *class = classOf(self);

    assert(class->set);
    return class->set(self, key, value);
}

struct Object *get(const void *_self, const char *key) {
    struct Dictionary *self = cast(Dictionary(), _self);
    const struct DictionaryClass *class = classOf(self);

    assert(class->get);
    return class->get(self, key);
}

unsigned size(const void *_self) {
    struct Dictionary *self = cast(Dictionary(), _self);
    const struct DictionaryClass *class = classOf(self);

    assert(class->size);
    return class->size(self);
}

struct List *getKeys(const void *_self) {
    struct Dictionary *self = cast(Dictionary(), _self);
    const struct DictionaryClass *class = classOf(self);

    assert(class->getKeys);
    return class->getKeys(self);
}

/* DictionaryClass */
static void * DictionaryClass_ctor (void *_self, va_list *app) {
    struct DictionaryClass * self
            = super_ctor(DictionaryClass(), _self, app);
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

        if (selector == (voidf) get)
            *(voidf *) &self->get = method;
        else if (selector == (voidf) set)
            *(voidf *) &self->set = method;
        else if (selector == (voidf) size)
            *(voidf *) &self->size = method;
        else if (selector == (voidf) getKeys)
            *(voidf *) &self->getKeys = method;
    }
#ifdef va_copy
    va_end(ap);
#endif

    return self;
}

/* Initialisation */
static const void *_DictionaryClass, *_Dictionary;

const void * const DictionaryClass(void) {
    return _DictionaryClass ? _DictionaryClass : (_DictionaryClass = new(Class(), "DictionaryClass",
             Class(), sizeof(struct DictionaryClass),
             ctor, DictionaryClass_ctor,
             (void *) 0));
}

const void * const Dictionary(void) {
    return _Dictionary ? _Dictionary : (_Dictionary = new(DictionaryClass(), "Dictionary",
          Object(), sizeof(struct Dictionary),
          ctor, Dictionary_ctor,
          dtor, Dictionary_dtor,
          set, Dictionary_set,
          get, Dictionary_get,
          size, Dictionary_size,
          getKeys, Dictionary_getKeys,
          (void *) 0));
}