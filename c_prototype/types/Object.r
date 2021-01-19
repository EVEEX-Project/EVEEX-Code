#ifndef OBJECT_R
#define OBJECT_R

#include <stdio.h>

struct Object {
    const struct Class * class;					/* Description d'objet */
};

struct Class {
    const struct Object _;						/* Description de la classe */
    const char * name;							/* Nom de la classe */
    const struct Class * super;					/* Super classe de la classe */
    size_t size;								/* Taille d'objet de la classe */
    void * (* ctor) (void * self, va_list * app);
    void * (* dtor) (void * self);
    int (* differ) (const void * self, const void * b);
    int (* puto) (const void * self, FILE * fp);
    void * (* clone) (const void * self);
};

void * super_ctor (const void * class, void * self, va_list * app);
void * super_dtor (const void * class, void * self);
int super_differ (const void * class, const void * self, const void * b);
int super_puto (const void * class, const void * self, FILE * fp);

#endif