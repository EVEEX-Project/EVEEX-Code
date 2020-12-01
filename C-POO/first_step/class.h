//
// Created by alexandre on 24/11/2020.
//

#ifndef C_POO_CLASS_H
#define C_POO_CLASS_H

#include <stdlib.h>
#include <stdarg.h>

struct Class {
    size_t size;
    void * (* ctor) (void *self, va_list *app); 		/* Constructeur */
    void * (* dtor) (void *self); 						/* Destructeur */
    void * (* clone) (const void *self); 				/* Clonage */
    int (* differ) (const void *self, const void *b); 	/* Comparaison */
};

#endif //C_POO_CLASS_H
