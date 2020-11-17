//
// Created by alexandre on 10/11/2020.
//

#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include "list.h"

List **List_create() {
    return calloc(sizeof(List), 1);
}

void List_add(List **list, void *elementToAdd) {
    List *l = malloc(sizeof(List));
    l->element = elementToAdd;
    l->next = *list;
    *list = l;
}

void List_append(List **list, void *elementToAdd) {
    List *l = malloc(sizeof(List));
    l->element = elementToAdd;
    l->next = NULL;

    List *ptr = *list;
    // if the list is empty
    if (ptr == NULL) {
        *list = l;
    } else {
        // going through the list
        while (ptr->next != NULL) ptr = ptr->next;
        // appending the new item
        ptr->next = l;
    }
}

int List_size(List **list) {
    int counter = 0;
    List *ptr = *list;
    while (ptr != NULL) {
        counter++;
        ptr = ptr->next;
    }
    return counter;
}

void List_print(List **list) {
    List *ptr;
    printf("List : {");
    for (ptr = *list; ptr != NULL; ptr = ptr->next) {
        printf("%s", ptr->element);
        if (ptr->next != NULL)
            printf(", ");
    }
    printf("}\n");
}

bool List_remove(List **list, void *elementToRemove) {
    List *ptr;
    List *precedent;
    for (ptr = *list; ptr != NULL; ptr = ptr->next) {
        if (ptr->element == elementToRemove) {
            // if it's the first element
            if (ptr == *list)
                *list = ptr->next;
            // else the element to remove is not the first
            else
                precedent->next = ptr->next;

            return true;
        }
        // if the element is not found we update the precedent
        precedent = ptr;
    }
    return false;
}

void List_free(List **list) {
    List *ptr = *list;
    List *toFree;
    while (ptr != NULL) {
        toFree = ptr;
        ptr = ptr->next;
        free(toFree);
    }
    free(list);
}