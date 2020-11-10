//
// Created by alexandre on 10/11/2020.
//

#ifndef C_PROTOTYPE_LISTE_H
#define C_PROTOTYPE_LISTE_H

typedef struct List_struct {
    struct List_struct *next;
    void *element;
} List;

List **List_create();
void List_add(List **list, void *elementToAdd);
void List_append(List **list, void *elementToAdd);
void List_remove(List **list, void *elementToRemove);
int List_size(List **list);
void List_free(List **list);
void List_print(List **list);

#endif //C_PROTOTYPE_LISTE_H
