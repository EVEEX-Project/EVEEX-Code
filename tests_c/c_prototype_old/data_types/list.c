//
// Created by alexandre on 10/11/2020.
//

#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include "list.h"

/*
 * Function: List_create
 * ---------------------
 * Allocates the memory for a new list object and returns the pointer to
 * that space in the memory.
 *
 *  returns: pointer to the allocated space for the list
 */
List **List_create() {
    return calloc(sizeof(List), 1);
}

/*
 * Function: List_free
 * -------------------
 * Frees the space used by a list. That means iterating over each element
 * of the list and free the element and then free the list at the end.
 *
 *  list: the list to free
 */
void List_free(List **list) {
    // element over which iterating
    List *ptr = *list;
    // helper element to free the data
    List *toFree;
    while (ptr != NULL) {
        // saving the element to free
        toFree = ptr;
        // switching to the next element
        ptr = ptr->next;
        free(toFree);
    }
    // at the end don't forget to free the list
    free(list);
}

/*
 * Function: List_add
 * ------------------
 * Adds an element at the start of the list and updates the links to the
 * list and the next element.
 *
 *  list: list to modify
 *  elementToAdd: the element to add to the list
 */
void List_add(List **list, void *elementToAdd) {
    // creating a new element in the list
    List *l = malloc(sizeof(List));
    l->element = elementToAdd;
    l->next = *list; // don't forget to link the next element

    // updating the link to the list
    *list = l;
}

/*
 * Function: List_append
 * ---------------------
 * Adds an element at the end of the list and update the
 * link to the latest element of the list.
 *
 *  list: list to modify
 *  elementToAdd: the element to add to the list
 */
void List_append(List **list, void *elementToAdd) {
    // creating a new element in the list
    List *l = malloc(sizeof(List));
    l->element = elementToAdd;
    l->next = NULL;

    // pointer to iterate over the list's elements
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

/*
 * Function: List_remove
 * ---------------------
 * Removes and element from the list and updates the
 * missing link in the list
 *
 *  list: the list to modify
 *  elementToRemove: the element to remove
 *
 *  returns: the status of the operation
 */
bool List_remove(List **list, void *elementToRemove) {
    // pointers to the current and previous elements
    List *ptr;
    List *precedent;
    // iteration over the elements to find the one to remove
    for (ptr = *list; ptr != NULL; ptr = ptr->next) {
        // if we found it
        if (ptr->element == elementToRemove) {
            // if it's the first element
            if (ptr == *list)
                *list = ptr->next;
                // else the element to remove is not the first
            else
                precedent->next = ptr->next;

            // operation sucessful
            return true;
        }
        // if the element is not found we update the precedent
        precedent = ptr;
    }
    // operation failed
    return false;
}

/*
 * Function: List_size
 * -------------------
 * Returns the number of elements in the list as the
 * list does not have a fixed size.
 *
 *  list: the list to calculate size
 *
 *  returns: the number of elements in the list
 */
int List_size(List **list) {
    // starting the count
    int counter = 0;
    // pointer to the element over which iterative
    List *ptr = *list;
    while (ptr != NULL) {
        // going to the next element
        counter++;
        ptr = ptr->next;
    }
    // we have counted each one of the elements it's time to return that count
    return counter;
}

/*
 * Function: List_print
 * --------------------
 * Display the content of the list.
 *
 *  list: the list to represent
 */
void List_print(List **list) {
    // pointer over which we are iterating
    List *ptr;
    // showing the content of the list
    printf("List : {");
    for (ptr = *list; ptr != NULL; ptr = ptr->next) {
        // printing the element
        printf("%s", ptr->element);
        // if it's not the last one
        if (ptr->next != NULL)
            printf(", ");
    }
    printf("}\n");
}