//
// Created by alexandre on 10/11/2020.
//

#ifndef C_PROTOTYPE_DICTIONARY_H
#define C_PROTOTYPE_DICTIONARY_H

#include <string.h>
#include <stdlib.h>

typedef struct Dictionary_struct { /* table entry: */
    char *key; /* defined name */
    int *value; /* replacement text */
    struct Dictionary_struct *next; /* next entry in chain */
} Dictionary;

int Dico_size(Dictionary **hashtab);
int *Dico_get(Dictionary **hashtab, char *key);
void *Dico_set(Dictionary **hashtab, char *key, int *value);
Dictionary **Dico_create();
void Dico_free(Dictionary **hashtab);
void Dico_del(Dictionary **hashtab, char *key);
void Dico_print(Dictionary **hashtab);

#endif //C_PROTOTYPE_DICTIONARY_H
