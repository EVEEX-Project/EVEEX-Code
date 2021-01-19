#include <malloc.h>
#include <memory.h>

#include "Native.h"
#include "Native.r"

/**************************************************************************/
/*							  CLASSE NATIVE   							  */
/**************************************************************************/

/* Constructeur avec arguments */
static void *Native_ctor (void *_self, va_list *app) {
    struct Native *self = super_ctor(Native(), _self, app);

    // On récupère les arguments dynamiques
    self->value = va_arg(*app, void *);
    self->size = va_arg(*app, size_t);

    return self;
}

/* Destructeur */
static void *Native_dtor (void *_self) {
    struct Native *self = cast(Native(), _self);
    if (self->value) {
        free((void *) self->value);
        self->value = NULL;
    }

    return self;
}

static void Native_puto(void *_self, FILE *fp) {
    struct Native *self = cast(Native(), _self);
    puto(self->value, fp);
}

static void *Native_clone(const void *_self) {
    const struct Native *self = _self;

    void *copy = malloc(self->size);
    memcpy(copy, self->value, self->size);
    return new(Native(), copy, self->size);
}

/**************************************************************************/
/*							MÉTACLASSE NODECLASS    					  */
/**************************************************************************/

/* Constructeur */
static void * NativeClass_ctor (void * _self, va_list * app) {
    // on appelle le constructeur du parent (appel en chaîne jusqu'à objet)
    struct NativeClass * self = super_ctor(NativeClass(), _self, app);
    typedef void (*voidf) ();
    voidf selector;
#ifdef va_copy
    va_list ap; va_copy(ap, *app);
#else
    va_list ap = *app;
#endif

    while ((selector = va_arg(ap, voidf))) {
        voidf method = va_arg(ap, voidf);

        // on ajoute ici les méthodes de classe
        // 1 if par méthode
    }
#ifdef va_copy
    va_end(ap);
#endif

    return self;
}

/**************************************************************************/
/*				  INITIALISATION BITSTREAM,BITSTREAMCLASS   			  */
/**************************************************************************/
static const void *_Native, *_NativeClass; // références internes

// référence externe dans le projet
const void *const NativeClass(void) {
    return _NativeClass ?
           _NativeClass : (_NativeClass = new(Class(), "NativeClass",
                                          Class(), sizeof(struct NativeClass),
                                          ctor, NativeClass_ctor,	// constructeur de classe
                                          (void *) 0));
}

// référence externe dans le projet
const void *const Native(void) {
    return _Native ?
           _Native : (_Native = new(NativeClass(), "Native",
                                Object(), sizeof(struct Native),
                                ctor, Native_ctor,		// contructeur de classe
                                dtor, Native_dtor,		// méthodes de classe (obligatoire)
                                puto, Native_puto,
                                clone, Native_clone,
                                (void *) 0));
}