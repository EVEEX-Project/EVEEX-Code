//
// Created by alexandre on 24/11/2020.
//

#include <assert.h>
#include <stdarg.h>

#include "class.h"
#include "new.h"

void *new(const void *_class, ...) {
    const struct Class *class = _class;
    void *p = calloc(1, class->size);

    assert(p); // on vérifie que la mémoire à bien été allouée
    *(const struct Class **)p = class; // quelque soit l'objet on lui donne sa classe

    // si la classe possède un constructeur
    if (class->ctor) {
        va_list ap; // liste variable d'arguments
        va_start(ap, _class); // init de la liste variable d'arguments
        p = class->ctor(p, &ap); // on appelle le constructeur de la classe
        va_end(ap); // on termine son utilisation
    }
    return p; // on retourne l'instance de classe ainsi crée
}

void delete(void *self) {
    const struct Class **cp = self;

    // si l'objet existe et qu'il possède un destructeur
    if (self && *cp && (*cp)->dtor)
        self = (*cp)->dtor(self); // on appelle le destructeur
    free(self); // on libère enfin l'objet
}

int differ(const void *self, const void *b) {
    const struct Class *const *cp = self;

    // on s'assure que l'objet existe bien et qu'il possède une fct de comparaison
    assert(self && *cp && (*cp)->differ);
    return (*cp)->differ(self, b); // on appelle la méthode de la classe
}

void *clone(const void * self)
{
    const struct Class * const * cp = self;

    // on s'assure que la reférence existe et la fonction de clonage aussi
    assert(self && *cp && (* cp)->clone);
    return (*cp)->clone(self);
}

size_t sizeOf(const void *self) {
    const struct Class *const *cp = self;
    assert(self && *cp); // on s'assure que l'objet existe ainsi que son contenu
    return (*cp)->size; // on retourne la taille de l'objet
}