#include <malloc.h>

#include "Bitstream.r"
#include "Bitstream.h"

/**************************************************************************/
/*							  CLASSE BITSTREAM							  */
/**************************************************************************/

/* Constructeur avec arguments */
static void *Bitstream_ctor (void *_self, va_list *app) {
    struct Bitstream *self = super_ctor(Bitstream(), _self, app);

    // On récupère les arguments dynamiques
    self->frame_id = va_arg(*app, int);
    self->type = va_arg(*app, int );
    self->size = va_arg(*app, unsigned long);
    self->data = va_arg(*app, char *);

    return self;
}

/* Destructeur */
static void *Bitstream_dtor (void *_self) {
    struct Bitstream *self = cast(Bitstream(), _self);

    // freeing the buffer
    //free(self->data);
    // returning a reference to the structure to be freed
    return self;
}

static void Bitstream_puto(void *_self, FILE *fp) {
    struct Bitstream *self = cast(Bitstream(), _self);
    fprintf(fp, "Bitstream: size=%ld, buffer=%s", self->size, self->data);
}

/**************************************************************************/
/*							MÉTACLASSE BITSTREAMCLASS					  */
/**************************************************************************/

/* Constructeur */
static void * BitstreamClass_ctor (void * _self, va_list * app) {
    // on appelle le constructeur du parent (appel en chaîne jusqu'à objet)
    struct BitstreamClass * self = super_ctor(BitstreamClass(), _self, app);
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
static const void *_Bitstream, *_BitstreamClass; // références internes

// référence externe dans le projet
const void *const BitstreamClass(void) {
    return _BitstreamClass ?
           _BitstreamClass : (_BitstreamClass = new(Class(), "BitstreamClass",
                                            Class(), sizeof(struct BitstreamClass),
                                            ctor, BitstreamClass_ctor,	// constructeur de classe
                                            (void *) 0));
}

// référence externe dans le projet
const void *const Bitstream(void) {
    return _Bitstream ?
           _Bitstream : (_Bitstream = new(BitstreamClass(), "Bitstream",
                                  Object(), sizeof(struct Bitstream),
                                  ctor, Bitstream_ctor,		// contructeur de classe
                                  dtor, Bitstream_dtor,		// méthodes de classe (obligatoire)
                                  puto, Bitstream_puto,
                                  (void *) 0));
}