#include <malloc.h>
#include <string.h>

#include "huffman.h"

#include "../types/Dictionary.h"
#include "../types/DictionaryItem.h"
#include "../types/Native.h"

#include "../types/Node.r"
#include "../types/List.r"
#include "../types/DictionaryItem.r"
#include "../types/Native.r"

struct Node *mergeTwoNodes(struct Node *a, struct Node *b) {
    // Creation of the new value
    struct List *newValue = new(List());
    struct List *listA = cast(List(), a->value);
    struct List *listB = cast(List(), b->value);

    // Adding every element to the new value
    for (int i = 0; i < listA->count; i++)
        addLast(newValue, lookAt(listA, i));
    for (int i = 0; i < listB->count; i++)
        addLast(newValue, lookAt(listB, i));

    // Calculation of the new frequency
    unsigned long newFreq = a->frequency + b->frequency;

    
    struct Node *newNode = new(Node(), newFreq, newValue);
    newNode->left = a;
    newNode->right = b;

    return newNode;
}

struct List *splitPhraseInNodes(const char *phrase, void *_symbols) {
    struct Dictionary *symbols = _symbols;
    struct List *listeNoeuds = new(List());

    // Calculation of the frequencies
    struct DictionaryItem *item;
    char key[2];
    key[1] = '\0';
    // for each symbol in the phrase
    for (int i = 0; phrase[i] != '\0'; i++) {
        // getting the key
        key[0] = phrase[i];
        // and its frequency
        item = (struct DictionaryItem *) get(symbols, key);
        // the first time seeing that key
        if (item == NULL) {
            unsigned long *freq_init = calloc(sizeof(unsigned long), 1);
            *freq_init = 1;
            struct Native *freq = new(Native(), freq_init);
            item = new(DictionaryItem(), key, freq);
        }
        // key already registered
        else {
            struct Native *freq = cast(Native(), item->value);
            unsigned long* val = (unsigned long *) freq->value;
            (*val)++;
        }
        set(symbols, key, (const struct Object *) item);
    }

    // Adding the nodes to the list
    struct List *dicoKeys = getKeys(symbols);
    // for each symbol in the dictionary
    for (unsigned i = 0; i < count(dicoKeys); i++) {
        const struct Native *dicKey = cast(Native(), lookAt(dicoKeys, i));
        const struct DictionaryItem *dicItem = cast(DictionaryItem(), get(symbols, (char *) dicKey->value));
        const struct Native *dicFreq = cast(Native(), dicItem->value);
        struct List *newValue = new(List());
        addLast(newValue, (const struct Object *) dicKey);

        struct Node *n = new(Node(), *((unsigned long *) dicFreq->value), newValue);
        addLast(listeNoeuds, (const struct Object *) n);
    }

    return listeNoeuds;
}

struct Node *getLowestFrequencySymbol(struct List *nodeList) {
    struct Node *min = cast(Node(), lookAt(nodeList, 0));
    for (unsigned i = 1; i < count(nodeList); i++) {
        struct Node *current = cast(Node(), lookAt(nodeList, i));
        if (current->frequency < min->frequency)
            min = current;
    }
    return min;
}