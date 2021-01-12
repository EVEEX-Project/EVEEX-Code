//
// Created by alexandre on 24/11/2020.
//

#include <assert.h>
#include <string.h>
#include <stdarg.h>
#include "class.h"
#include "new.h"
#include "String.h"

struct String {
    const void *class;	/* Doit être en premier */
    char *text;
};

static void *String_ctor(void *_self, va_list *app) {
    struct String *self = _self; // on récupère les arguments
    const char *text = va_arg(*app, const char *);

    self->text = malloc(strlen(text) + 1); // allocation de mémoire pour la string
    assert(self->text); // on vérifie qu'il n'y a pas eu d'erreur
    strcpy(self->text, text); // copie de la chaine dans la variable
    return self; // on retourne l'instant de variable ainsi crée
}

static void *String_dtor(void *_self) {
    struct String *self = _self;
    free(self->text), self->text = 0; // on libère l'espace alloué
    return self; // on retourne le pointeur sur l'objet pour le libérer dans delete()
}

static void *String_clone(const void *_self) {
    const struct String *self = _self;
    return new(String, self->text); // crée une nouvelle instance dynamiquement
}

static int String_differ(const void *_self, const void *_b) {
    const struct String *self = _self;
    const struct String *b = _b;

    if (self == b) // si il s'agit du même objet c'est forcément vrai
        return 0;
    if (!b || b->class != String) // types différents donc f
        return 1;
    return strcmp(self->text, b->text); // on compare leur contenu
}

static const struct Class _String = {
        sizeof(struct String),
        String_ctor, String_dtor,
        String_clone, String_differ
};
const void *String = &_String;