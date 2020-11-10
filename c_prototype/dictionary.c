//
// Created by alexandre on 10/11/2020.
//

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
char *Dico_get(Dictionary **hashtab, char *key)
{
    Dictionary *ptr;
    for (ptr = *hashtab; ptr != NULL; ptr = ptr->next) {
        if (strcmp(ptr->key, key) == 0) {
            return ptr->value;
        }
    }

    return NULL;
}

/* install: put (name, defn) in hashtab */
Dictionary *Dico_set(Dictionary **hashtab, char *key, char *value)
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
    return calloc(sizeof(Dictionary), 1);
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

void Dico_print(Dictionary **hashtab) {
    Dictionary *ptr;
    printf("Dictionnary : {");
    for (ptr = *hashtab; ptr != NULL; ptr = ptr->next) {
        printf("'%s': '%s'", ptr->key, ptr->value);
        if (ptr->next != NULL)
            printf(", ");
    }
    printf("}\n");
}