#ifndef C_PROTOTYPE_DICTIONARY_H
#define C_PROTOTYPE_DICTIONARY_H

#include <string.h>
#include <stdlib.h>
#include "list.h"

/*
 * Structure: Dictionary
 * ---------------------
 * Structure that describes a typical dictionary (in Python) or a hashtable (Java)
 * Each element contains a key (string) and a value (int/string)
 * A full dictionary is a linked list of those elements
 */
typedef struct Dictionary_struct { /* table entry: */
    char *key; /* defined name */
    void *value; /* replacement text */
    struct Dictionary_struct *next; /* next entry in chain */
} Dictionary;

/* Creation and deletion functions */
Dictionary **Dico_create();
void Dico_free(Dictionary **hashtab);

/* Setting, getting, deleting element functions */
void *Dico_get(Dictionary **hashtab, char *key);
void *Dico_set(Dictionary **hashtab, char *key, void *value);
void Dico_del(Dictionary **hashtab, char *key);

/* Dictionary representation functions */
void Dico_printInt(Dictionary **hashtab);
void Dico_printString(Dictionary **hashtab);

/* Misc. functions */
int Dico_size(Dictionary **hashtab);
List **Dico_keys(Dictionary **hashtab);
int Dico_keyInDico(Dictionary **hashtab, char *keyToTest);
void Dico_getReversedDico(Dictionary **original, Dictionary **reversed);

#endif //C_PROTOTYPE_DICTIONARY_H
