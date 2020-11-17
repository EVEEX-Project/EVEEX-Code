//
// Created by alexandre on 10/11/2020.
//

#ifndef C_PROTOTYPE_DICTIONARY_H
#define C_PROTOTYPE_DICTIONARY_H

#include <string.h>
#include <stdlib.h>
#include "list.h"

typedef struct Dictionary_struct { /* table entry: */
    char *key; /* defined name */
    void *value; /* replacement text */
    struct Dictionary_struct *next; /* next entry in chain */
} Dictionary;

int Dico_size(Dictionary **hashtab);
void *Dico_get(Dictionary **hashtab, char *key);
void *Dico_set(Dictionary **hashtab, char *key, void *value);
Dictionary **Dico_create();
void Dico_free(Dictionary **hashtab);
void Dico_del(Dictionary **hashtab, char *key);
void Dico_printInt(Dictionary **hashtab);
void Dico_printString(Dictionary **hashtab);
List **Dico_keys(Dictionary **hashtab);
int Dico_keyInDico(Dictionary **hashtab, char *keyToTest);
void Dico_getReversedDico(Dictionary **original, Dictionary **reversed);

#endif //C_PROTOTYPE_DICTIONARY_H
