#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

#include "Object.h"

#include "DictionaryItem.r"
#include "DictionaryItem.h"

/* DICTIONARYITEM */
static void *DictionaryItem_ctor (void *_self, va_list *app) {
    struct DictionaryItem *self = super_ctor(DictionaryItem(), _self, app);

    char *key = va_arg(*app, char *);
    assert(key);
    self->key = malloc(strlen(key) + 1);
    strcpy((char *) self->key, key);
    assert(self->key);
    self->value = clone(va_arg(*app, struct Object *));
    assert(self->value);

    return self;
}

static int DictionaryItem_differ (const void *_self, const void *_other) {
    const struct DictionaryItem *self = cast(DictionaryItem(), _self);

    if (classOf(self) != classOf(_other)) return 1;

    const struct DictionaryItem *otherObj = cast(DictionaryItem(), _other);
    if (strcmp(otherObj->key, self->key) != 0) return 1;

    return differ(self->value, otherObj->value);
}

static void *DictionaryItem_dtor(struct DictionaryItem *self) {
    if (self->key) {
        free((void *) self->key);
        self->key = NULL;
    }
    if (self->value) {
        delete((void *) self->value);
    }

    return super_dtor(DictionaryItem(), self);
}

static void *DictionaryItem_clone(const void *_self) {
    const struct DictionaryItem *self = _self;
    return new(DictionaryItem(), self->key, self->value);
}

/* Initialisation */
static const void *_DictionaryItem;

const void * const DictionaryItem(void) {
    return _DictionaryItem ? _DictionaryItem : (_DictionaryItem = new(Class(), "DictionaryItem",
          Object(), sizeof(struct DictionaryItem),
          ctor, DictionaryItem_ctor,
          dtor, DictionaryItem_dtor,
          clone, DictionaryItem_clone,
          differ, DictionaryItem_differ,
          (void *) 0));
}