#include "Pixel.r"
#include "Pixel.h"

/**************************************************************************/
/*							  CLASSE PIXEL								  */
/**************************************************************************/

/* Constructeur avec arguments */
static void *RGBPixel_ctor (void *_self, va_list *app) {
    struct RGBPixel *self = super_ctor(RGBPixel(), _self, app);

    // On récupère les arguments dynamiques
    self->r = va_arg(*app, int);
    self->g = va_arg(*app, int);
    self->b = va_arg(*app, int);
    return self;
}

static void *YUVPixel_ctor (void *_self, va_list *app) {
    struct YUVPixel *self = super_ctor(YUVPixel(), _self, app);

    // On récupère les arguments dynamiques
    self->y = va_arg(*app, int);
    self->cb = va_arg(*app, int);
    self->cr = va_arg(*app, int);
    return self;
}

/* Destructeur */
static void *RGBPixel_dtor (void *_self) {
    struct RGBPixel *self = cast(RGBPixel(), _self);
    return self;
}

static void *YUVPixel_dtor (void *_self) {
    struct YUVPixel *self = cast(YUVPixel(), _self);
    return self;
}

/* Override d'une méthode de classe parente */
static void RGBPixel_puto(const void * _self, FILE * fp) {
    const struct RGBPixel *self = _self;
    fprintf(fp, "RGBPixel (r, g, b): (%d, %d, %d)\n", self->r, self->g, self->b);
}

static void YUVPixel_puto(const void * _self, FILE * fp) {
    const struct YUVPixel *self = _self;
    fprintf(fp, "YUVPixel (y, cb, cr): (%d, %d, %d)\n", self->y, self->cb, self->cr);
}

static void *RGBPixel_clone(const void *_self) {
    const struct RGBPixel *self = _self;
    return new(RGBPixel(), self->r, self->g, self->b);
}

static void *YUVPixel_clone(const void *_self) {
    const struct YUVPixel *self = _self;
    return new(YUVPixel(), self->y, self->cb, self->cr);
}

/**************************************************************************/
/*							MÉTACLASSE PIXELCLASS						  */
/**************************************************************************/

/* Constructeur */
static void * PixelClass_ctor (void * _self, va_list * app) {
    // on appelle le constructeur du parent (appel en chaîne jusqu'à objet)
    struct PixelClass * self = super_ctor(PixelClass(), _self, app);
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
/*				   	   INITIALISATION PIXEL,PIXELCLASS					  */
/**************************************************************************/
static const void *_RGBPixel, *_YUVPixel, *_PixelClass; // références internes

// référence externe dans le projet
const void *const PixelClass(void) {
    return _PixelClass ?
           _PixelClass : (_PixelClass = new(Class(), "PixelClass",
                                            Class(), sizeof(struct PixelClass),
                                            ctor, PixelClass_ctor,	// constructeur de classe
                                            (void *) 0));
}

// référence externe dans le projet
const void *const RGBPixel(void) {
    return _RGBPixel ?
           _RGBPixel : (_RGBPixel = new(PixelClass(), "RGBPixel",
                                  Object(), sizeof(struct RGBPixel),
                                  ctor, RGBPixel_ctor,		// contructeur de classe
                                  dtor, RGBPixel_dtor,
                                  puto, RGBPixel_puto,
                                  clone, RGBPixel_clone,
                                  (void *) 0));
}

// référence externe dans le projet
const void *const YUVPixel(void) {
    return _YUVPixel ?
           _YUVPixel : (_YUVPixel = new(PixelClass(), "YUVPixel",
                                        Object(), sizeof(struct RGBPixel),
                                        ctor, YUVPixel_ctor,		// contructeur de classe
                                        dtor, YUVPixel_dtor,
                                        puto, YUVPixel_puto,
                                        clone, YUVPixel_clone,
                                        (void *) 0));
}