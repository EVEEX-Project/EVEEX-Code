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
    self->key = malloc(sizeof(*key));
    strcpy((char *) self->key, key);
    assert(self->key);
    self->value = va_arg(*app, struct Object *);
    assert(self->value);

    return self;
}

static void *DictionaryItem_dtor(struct DictionaryItem *self) {
    delete((void *) self->value);
    free((void *) self->key);

    return super_dtor(DictionaryItem(), self);
}

/* Initialisation */
static const void *_DictionaryItem;

const void * const DictionaryItem(void) {
    return _DictionaryItem ? _DictionaryItem : (_DictionaryItem = new(Class(), "DictionaryItem",
          Object(), sizeof(struct DictionaryItem),
          ctor, DictionaryItem_ctor,
          dtor, DictionaryItem_dtor,
          (void *) 0));
}