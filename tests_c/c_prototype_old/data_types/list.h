//
// Created by alexandre on 10/11/2020.
//

#ifndef C_PROTOTYPE_LISTE_H
#define C_PROTOTYPE_LISTE_H

#include <stdbool.h>

/*
 * Structure: List
 * ---------------
 * Structure that describes a typical list (in Python) or a linked list (C).
 * That means this is a list with no fixed size for a python-like behaviour.
 */
typedef struct List_struct {
    struct List_struct *next;
    void *element;
} List;

/* Creation and deletion functions */
List **List_create();
void List_free(List **list);

/* List modification functions */
void List_add(List **list, void *elementToAdd);
void List_append(List **list, void *elementToAdd);
bool List_remove(List **list, void *elementToRemove);

/* Misc functions */
int List_size(List **list);
void List_print(List **list);

#endif //C_PROTOTYPE_LISTE_H
