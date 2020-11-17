//
// Created by alexandre on 10/11/2020.
//

#include <stdio.h>
#include "dictionary.h"

int Dico_size(Dictionary **hashtab) {
    Dictionary *ptr;
    int counter = 0;
    for (ptr = *hashtab; ptr != NULL; ptr = ptr->next) {
        counter++;
    }
    return counter;
}

/* lookup: look for s in hashtab */
void *Dico_get(Dictionary **hashtab, char *key)
{
    Dictionary *ptr;
    for (ptr = *hashtab; ptr != NULL; ptr = ptr->next) {
        // printf("Testing : %c & %s with res : %d\n", key, ptr->key, strcmp(ptr->key, key));
        if (strcmp(ptr->key, key) == 0) {
            return ptr->value;
        }
    }

    return NULL;
}

/* install: put (name, defn) in hashtab */
void *Dico_set(Dictionary **hashtab, char *key, void *value)
{
    Dico_del(hashtab, key); /* If we already have a item with this key, delete it. */
    Dictionary *d = malloc(sizeof(Dictionary));
    d->key = malloc(strlen(key) + 1);
    strcpy(d->key, key);
    d->value = value;
    d->next = *hashtab;
    *hashtab = d;
}

void Dico_del(Dictionary **hashtab, char *key) {
    Dictionary *ptr, *prev;
    for (ptr = *hashtab, prev = NULL; ptr != NULL; prev = ptr, ptr = ptr->next) {
        if (strcmp(ptr->key, key) == 0) {
            if (ptr->next != NULL) {
                if (prev == NULL) {
                    *hashtab = ptr->next;
                } else {
                    prev->next = ptr->next;
                }
            } else if (prev != NULL) {
                prev->next = NULL;
            } else {
                *hashtab = NULL;
            }

            free(ptr->key);
            free(ptr);

            return;
        }
    }
}

Dictionary **Dico_create() {
    return (Dictionary **) calloc(sizeof(Dictionary), 1);
}

void Dico_free(Dictionary **hashtab) {
    Dictionary *ptr = *hashtab;
    Dictionary *toFree;
    while (ptr != NULL) {
        toFree = ptr;
        ptr = ptr->next;
        free(toFree->key);
        free(toFree);
    }
    free(hashtab);
}

void Dico_printString(Dictionary **hashtab) {
    Dictionary *ptr;
    printf("Dictionnary : {");
    for (ptr = *hashtab; ptr != NULL; ptr = ptr->next) {
        printf("'%s': '%s'", ptr->key, ptr->value);
        if (ptr->next != NULL)
            printf(", ");
    }
    printf("}\n");
}

void Dico_printInt(Dictionary **hashtab) {
    Dictionary *ptr;
    printf("Dictionnary : {");
    for (ptr = *hashtab; ptr != NULL; ptr = ptr->next) {
        printf("'%s': '%d'", ptr->key, *((int *) ptr->value));
        if (ptr->next != NULL)
            printf(", ");
    }
    printf("}\n");
}

List **Dico_keys(Dictionary **hashtab) {
    List **keysList = List_create();
    Dictionary *ptr;

    for (ptr = *hashtab; ptr != NULL; ptr = ptr->next) {
        List_append(keysList, ptr->key);
    }
    return keysList;
}

int Dico_keyInDico(Dictionary **hashtab, char *keyToTest) {
    Dictionary  *ptr;

    for (ptr = *hashtab; ptr != NULL; ptr = ptr->next) {
        // if we found the key
        if (strcmp(ptr->key, keyToTest) == 0)
            return 1;
    }
    // if we have'nt found the key
    return 0;
}

void Dico_getReversedDico(Dictionary **original, Dictionary **reversed)
{
    Dictionary *ptr;
    for (ptr = *original; ptr != NULL; ptr = ptr->next) {
        Dico_set(reversed, ptr->value, ptr->key);
    }
}