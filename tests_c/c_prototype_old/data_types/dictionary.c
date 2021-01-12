#include <stdio.h>
#include "dictionary.h"

/*
 * Function: Dico_create
 * ---------------------
 * Allocate the memory for a new dictionary and returns a pointer to that space in the memory.
 *
 *  returns: pointer to the dictionary
 */
Dictionary **Dico_create() {
    return (Dictionary **) calloc(sizeof(Dictionary), 1);
}

/*
 * Function: Dico_free
 * -------------------
 * Free the memory used by an instance of a dictionary.
 *
 *  hashtab: the dictionary to free
 */
void Dico_free(Dictionary **hashtab) {
    // new pointer that will iterate over the dictionary
    Dictionary *ptr = *hashtab;
    // temporary pointer helping freeing the data
    Dictionary *toFree;
    // while the whole dictionary is not free
    while (ptr != NULL) {
        toFree = ptr;
        ptr = ptr->next;
        // freeing what needs to be set free
        free(toFree->key);
        free(toFree);
    }
    free(hashtab);
}

/*
 * Function: Dico_get
 * ------------------
 * Lookup for an element in the dictionary. Returns NULL if no element with the provided key
 * was found.
 *
 *  hashtab: dictionary in which lookup into
 *  key: the element's key
 *
 *  returns: NULL if no element found, the value of the element else
 */
void *Dico_get(Dictionary **hashtab, char *key)
{
    // new pointer that will iterate over the dictionary
    Dictionary *ptr;
    // for each entry in the dictionary
    for (ptr = *hashtab; ptr != NULL; ptr = ptr->next) {
        // if we have found the correct key
        if (strcmp(ptr->key, key) == 0) {
            return ptr->value;
        }
    }

    // there was no element with that key
    return NULL;
}

/*
 * Function: Dico_set
 * ------------------
 * Set an entry into the dictionary with key and value.
 *
 *  hashtab: dictionary in which setting an element
 *  key: the key of the element
 *  value: the value of the element
 */
void *Dico_set(Dictionary **hashtab, char *key, void *value)
{
    // If we already have a item with this key, delete it
    Dico_del(hashtab, key);
    // allocating size for that element
    Dictionary *d = malloc(sizeof(Dictionary));
    // setting the key into the element
    d->key = malloc(strlen(key) + 1);
    strcpy(d->key, key);
    // setting the value
    d->value = value;
    // adding it to the dictionary
    d->next = *hashtab;
    *hashtab = d;
}

/*
 * Function Dico_del
 * -----------------
 * Removes an element of the dictionary and updates the dictionary.
 *
 *  hashtab: the dictionary to update
 *  key: the key of the element to remove
 */
void Dico_del(Dictionary **hashtab, char *key) {
    // pointers needed for the operation
    Dictionary *ptr, *prev;
    // iteration over the elements of the dictionary
    for (ptr = *hashtab, prev = NULL; ptr != NULL; prev = ptr, ptr = ptr->next) {
        // if we have found the element to remove
        if (strcmp(ptr->key, key) == 0) {
            // if the element is not the tail of the dictionary
            if (ptr->next != NULL) {
                // if it was the head of the dictionary
                if (prev == NULL) {
                    // update the reference to the dictonary
                    *hashtab = ptr->next;
                } else {
                    // link the previous element with the next
                    prev->next = ptr->next;
                }
            }
            // else if the element is the tail but there is an element before
            else if (prev != NULL) {
                prev->next = NULL;
            }
            // else the dictionary is empty
            else {
                *hashtab = NULL;
            }

            // now we can free the element in the dictionary
            free(ptr->key);
            free(ptr);

            // the job is done, we can exit the function
            return;
        }
    }
}

/*
 * Function: Dico_printString
 * --------------------------
 * Print the representation of the dictionary in the case in which the values are all strings.
 *
 *  hashtab: the dictionary to print
 */
void Dico_printString(Dictionary **hashtab) {
    printf("Dictionnary : {");
    // iteration over all of the element of the dictionary
    for (Dictionary *ptr = *hashtab; ptr != NULL; ptr = ptr->next) {
        printf("'%s': '%s'", ptr->key, ptr->value);
        // pretty print if not the tail of the dictionary
        if (ptr->next != NULL)
            printf(", ");
    }
    printf("}\n");
}

/*
 * Function: Dico_printInt
 * -----------------------
 * Print the representation of the dictionary in the case in which the values are all ints.
 *
 *  hashtab: the dictionary to print
 */
void Dico_printInt(Dictionary **hashtab) {
    printf("Dictionnary : {");
    // iteration over all of the element of the dictionary
    for (Dictionary *ptr = *hashtab; ptr != NULL; ptr = ptr->next) {
        printf("'%s': '%d'", ptr->key, *((int *) ptr->value));
        // pretty print if not the tail of the dictionary
        if (ptr->next != NULL)
            printf(", ");
    }
    printf("}\n");
}

/*
 * Function: Dico_size
 * -------------------
 * Returns the number of elements in a dictionary
 *
 *  hashtab: the dictionary to count
 *
 *  returns: the number of elements in the dictionary
 */
int Dico_size(Dictionary **hashtab) {
    int counter = 0;
    // iteration over the elements of the dictionary
    for (Dictionary *ptr = *hashtab; ptr != NULL; ptr = ptr->next) counter++;
    return counter;
}

/*
 * Function: Dico_keys
 * -------------------
 * Returns a list of all the keys in a dictionary
 *
 *  hashtab: dictionary from which to pull keys
 *
 *  returns: a list of the dictionary's keys
 */
List **Dico_keys(Dictionary **hashtab) {
    // instanciation of the list
    List **keysList = List_create();

    // for each element in the dictionary
    for (Dictionary *ptr = *hashtab; ptr != NULL; ptr = ptr->next) {
        // appeding it's key
        List_append(keysList, ptr->key);
    }
    return keysList;
}

/*
 * Function: Dico_keyInDico
 * ------------------------
 * Checks if a specific key is present in the dictionary.
 *
 *  hashtab: dictionary to test
 *  keyToTest: key to check
 */
int Dico_keyInDico(Dictionary **hashtab, char *keyToTest) {
    // for each element in the dictionary
    for (Dictionary *ptr = *hashtab; ptr != NULL; ptr = ptr->next) {
        // if we found the key
        if (strcmp(ptr->key, keyToTest) == 0)
            return 1;
    }
    // if we have'nt found the key
    return 0;
}

/*
 * Function: Dico_getReversedDico
 * ------------------------------
 * Update a new dictionary from an old one by swapping all the values and all the keys
 *
 *  original: original dictionary to swap
 *  reversed: dictionary which will end with the swapped entries
 */
void Dico_getReversedDico(Dictionary **original, Dictionary **reversed)
{
    // for each element in the dictionary
    for (Dictionary *ptr = *original; ptr != NULL; ptr = ptr->next) {
        // adding a new entry swapping the key and value
        Dico_set(reversed, ptr->value, ptr->key);
    }
}