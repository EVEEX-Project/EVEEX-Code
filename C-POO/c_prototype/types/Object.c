#include <stdarg.h>
#include <stddef.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>

#include "Object.r"
#include "Object.h"

/*
 * OBJECT
 */

static void * Object_ctor (void * _self, va_list * app) {			/* Constructeur */
    return _self;
}

static void * Object_dtor (void * _self) {							/* Destructeur */
    return _self;
}

static int Object_differ (const void * _self, const void * b) {		/* Comparateur */
    return _self != b;
}

static int Object_puto (const void * _self, FILE * fp) {			/* Afficheur ? */
    const struct Class * class = classOf(_self);
    return fprintf(fp, "%s at %p\n", class->name, _self);
}

const void * classOf (const void * _self) {							/* Retourne la classe de l'objet */
    const struct Object * self = _self;
    assert(self && self->class);
    return self->class;
}

size_t sizeOf (const void * _self) {								/* Retourne la taille de l'objet */
    const struct Class * class = classOf(_self);
    return class->size;
}

/*
 * CLASS
 */

static void *Class_ctor (void *_self, va_list *app) {			/* Constructeur */
    struct Class *self = _self;
    const size_t offset = offsetof(struct Class, ctor);

    self->name = va_arg(*app, char *);							/* on récupère les arguments de la liste */
    self->super = va_arg(*app, struct Class *);
    self->size = va_arg(*app, size_t);

    assert(self->super);

    memcpy((char *) self + offset, (char *) self->super
                                   + offset, sizeOf(self->super) - offset);
    {
        typedef void (* voidf) ();	/* generic function pointer */
        voidf selector;
#ifdef va_copy
        va_list ap; va_copy(ap, * app);
#else
        va_list ap = * app;
#endif

        while ((selector = va_arg(ap, voidf)))
        {	voidf method = va_arg(ap, voidf);

            if (selector == (voidf) ctor)
                * (voidf *) & self -> ctor = method;
            else if (selector == (voidf) dtor)
                * (voidf *) & self -> dtor = method;
            else if (selector == (voidf) differ)
                * (voidf *) & self -> differ = method;
            else if (selector == (voidf) puto)
                * (voidf *) & self -> puto = method;
        }
#ifdef va_copy
        va_end(ap);
#endif

        return self;
    }}

static void *Class_dtor (void *_self)								/* Destructeur */
{	struct Class * self = _self;

    fprintf(stderr, "%s: cannot destroy class\n", self->name);
    return 0;
}

const void *super (const void *_self)								/* Récupérer la super classe */
{	const struct Class *self = _self;

    assert(self && self->super);
    return self->super;
}

/*
 * INITIALISATION
 */

static const struct Class _Object;
static const struct Class _Class;

/*static const struct Class objects[] = {
        { { objects + 1 },
                "Object", objects, sizeof(struct Object),
                Object_ctor, Object_dtor, Object_differ, Object_puto
        },
        { { objects + 1 },
                "Class", objects, sizeof(struct Class),
                Class_ctor, Class_dtor, Object_differ, Object_puto
        }
};*/

static const struct Class _Object = {
        { &_Class },
        "Object", &_Object, sizeof(struct Object),
        Object_ctor, Object_dtor,Object_differ, Object_puto
};

static const struct Class _Class = {
        { &_Class },
        "Class", &_Object, sizeof(struct Class),
        Class_ctor, Class_dtor, Object_differ, Object_puto
};

const void * const Object(void) {
    return &_Object;
}

const void * const Class(void) {
    return &_Class;
}

/*
 * SELECTORS AND OBJECT MANAGEMENT
 */

void *new (const void *_class, ...)	{							/* Nouvelle instance de classe */
    const struct Class *class = _class;
    struct Object *object;
    va_list ap;

    assert(class && class->size);
    object = calloc(1, class->size);	// allocation de l'espace mémoire nécessaire
    assert(object);
    object->class = class; // on attribue la classe
    va_start(ap, _class);
    object = ctor(object, &ap); // on appelle le constructeur de l'objet
    va_end(ap);
    return object; // on retourne l'instance
}

void delete (void * _self) {
    if (_self)
        free(dtor(_self)), _self = NULL;	// on appelle le destructeur puis on libère la référence
}

void *ctor (void *_self, va_list * app) {
    const struct Class *class = classOf(_self); // on récupère la classe de l'objet

    assert(class->ctor);	// on vérifie que l'objet possède un constructeur
    return class->ctor(_self, app); // on appelle son constructeur
}

void *super_ctor (const void *_class,
                  void *_self, va_list *app) {
    const struct Class * superclass = super(_class);	// on récupère la super classe

    assert(_self && superclass->ctor);
    return superclass->ctor(_self, app); // on appelle le constructeur de la super classe
}

void *dtor (void *_self) {
    const struct Class * class = classOf(_self); // on récupère la classe de l'objet

    assert(class->dtor);
    return class->dtor(_self); // on appelle son destructeur
}

void *super_dtor (const void *_class, void *_self) {
    const struct Class * superclass = super(_class); // on récupère la superclasse

    assert(_self && superclass->dtor);
    return superclass->dtor(_self); // on appelle le destructeur de la superclasse
}

int differ (const void *_self, const void *b) {	/* Comparaison */
    int result;
    const struct Class * class = classOf(_self);

    assert(class->differ);
    cast(Object(), b);

    result = class->differ(_self, b);
    return result;
}

int super_differ (const void *_class, const void *_self, const void *b)
{
    const struct Class *superclass = super(_class);
    cast(Object(), b);
    assert(superclass->differ);

    return superclass->differ(_self, b);
}

int puto (const void *_self, FILE *fp) {
    const struct Class *class = classOf(_self); // on récupère la classe de l'objet

    assert(class->puto);
    return class->puto(_self, fp); // on affiche le contenu dans fp
}

int super_puto (const void * _class, const void * _self, FILE * fp) {
    const struct Class * superclass = super(_class); // on récupère la superclasse de l'objet

    assert(_self && superclass->puto);
    return superclass->puto(_self, fp); // on affiche le contenu a l'aide de la superclasse
}

/*
 * UTILS
 */

int isA(const void *_self, const struct Class *class) {
    return _self && classOf(_self) == class;
}

int isOf(const void *_self, const struct Class *class) {
    if (_self) {
        const struct Class *myClass = classOf(_self);
        if (class != Object()) {
            while (myClass != class) {
                if (myClass != Object()) {
                    myClass = super(myClass);
                } else
                    return 0;
            }
        }
        return 1;
    }
    return 0;
}

void *cast(const struct Class *class, const void *_self) {
    assert(isOf(_self, class));
    return (void *) _self;
}