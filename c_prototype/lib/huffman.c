#include <malloc.h>
#include <string.h>
#include <assert.h>

#include "huffman.h"

#include "../types/Dictionary.h"
#include "../types/DictionaryItem.h"
#include "../types/Native.h"
#include "../types/Node.h"

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

struct Node *generateTreeFromList(struct List *nodeList) {
    struct Node *n1, *n2, *n12;
    struct Object *removed;
    while (count(nodeList) > 1) {
        n1 = getLowestFrequencySymbol(nodeList);
        removed = removeItem(nodeList, (const struct Object *) n1);
        assert(removed);
        n2 = getLowestFrequencySymbol(nodeList);
        removed = removeItem(nodeList, (const struct Object *) n2);
        assert(removed);

        // merging the two nodes
        n12 = mergeTwoNodes(n1, n2);
        addLast(nodeList, (const struct Object *) n12);
    }

    struct Node *racine = cast(Node(), lookAt(nodeList, 0));
    return racine;
}

static int _print_t(struct Node *node, int is_left, int offset, int depth, char s[20][255])
{
    char b[20];
    int width = 3;

    // si the node is null there is nothing to show
    if (!node) return 0;

    // if the node has no parent
    if (!node->left && !node->right) {
        struct Native *val = cast(Native(), lookAt(node->value, 0));
        // storing the nodes value in a buffer
        sprintf(b, "(%s)", (char *) val->value);
    }
        // the node has a parent we show the branch
    else
        sprintf(b, " | ");

    // calculating left and right offset to display the branches
    int left  = _print_t(node->left, 1, offset, depth + 1, s);
    int right = _print_t(node->right, 0, offset + left + width, depth + 1, s);

    //printf("Node : %s, Depth : %d, Left : %d, right : %d, offset : %d\n", node->value, depth, left, right, offset);
    // showing the nodes value
    for (int i = 0; i < width; i++) {
        // if we haven't reached the end of the buffer
        if (b[i] != '\0')
            s[2 * depth][offset + left + i] = b[i];
        else
            break;
    }

    // if this is not the first layer and the child is left one from parent
    if (depth && is_left) {
        // printing the horizontal branch
        for (int i = 0; i < width + right; i++)
            s[2 * depth - 1][offset + left + width/2 + i] = '-';

        // printing the end of the branch
        s[2 * depth - 1][offset + left + width/2] = '+';
        s[2 * depth - 1][offset + left + width + right + width/2] = '+';

    }
        // if this is not the first layer and the child is right one from parent
    else if (depth && !is_left) {
        // printing the horizontal branch
        for (int i = 0; i < left + width; i++)
            s[2 * depth - 1][offset - width/2 + i] = '-';

        // printing the end of the branch
        s[2 * depth - 1][offset + left + width/2] = '+';
        s[2 * depth - 1][offset - width/2 - 1] = '+';
    }

    // returning the space used by this side of the branch
    return left + width + right;
}

void printHuffmanTree(struct Node *root) {
    // preparing the string that will contain the representation
    char s[20][255];
    for (int i = 0; i < 20; i++)
        for (int j = 0; j < 255; j++)
            s[i][j] = ' ';

    // getting the tree in the string
    _print_t(root, 0, 0, 0, s);

    // printing the string to the screen
    for (int i = 0; i < 20; i++) {
        int empty = 1;
        int c = 0;
        // checking if a row is empty
        while (s[i][c] != '\0' && c < 255) {
            if (s[i][c] != ' ') {
                empty = 0;
                break;
            }
            c++;
        }

        // if the row is not empty then print it on the screen
        if (!empty) {
            for (int j = 0; j < 255; j++) {
                printf("%c", s[i][j]);
            }
            printf("\n");
        }
    }
}

void generateEncodingDict(struct Dictionary *encoding, struct Node *root, char *prefix) {
    // if there is no children we add the symbol to the dictionary
    if (root->left == NULL && root->right == NULL) {
        // getting the current prefix
        char *newPrefix = strdup(prefix);
        // updating its entry in the dictionary
        set(encoding, newPrefix, root->value);
        return;
    }

    // updating the size for the prefix
    char newPrefix[strlen(prefix) + 2];
    strcpy(newPrefix, prefix);
    newPrefix[strlen(prefix) + 1] = '\0';

    // if there is a child on the left
    if (root->left != NULL) {
        // updating the prefix with a "0"
        newPrefix[strlen(prefix)] = '0';
        // continue with the creation of the encoding dictionary
        generateEncodingDict(encoding, root->left, newPrefix);
    }
    // if there is a child on the right
    if (root->right != NULL) {
        // updating the prefix with a "1"
        newPrefix[strlen(prefix)] = '1';
        // continue with the creation of the encoding dictionary
        generateEncodingDict(encoding, root->right, newPrefix);
    }
}