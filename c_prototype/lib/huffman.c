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

struct List *splitPhraseInNodes(const char *phrase) {
    struct Dictionary *symbols = new(Dictionary());
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
            // printf("New key : %s\n", key);
            unsigned long *freq_init = calloc(sizeof(unsigned long), 1);
            *freq_init = 1;
            struct Native *freq = new(Native(), freq_init);
            item = new(DictionaryItem(), key, freq);
        }
        // key already registered
        else {
            // printf("Already known : %s\n", key);
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
        unsigned long dicFreq = *((unsigned long *) ((struct Native *) cast(Native(), dicItem->value))->value);
        struct List *newValue = new(List());

        char *copyKey = calloc(strlen(dicKey->value), 1);
        strcpy(copyKey, dicKey->value);
        addLast(newValue, new(Native(), copyKey));

        addLast(listeNoeuds, new(Node(), dicFreq, newValue));

        struct Node *last = cast(Node(), lookAt(listeNoeuds, count(listeNoeuds) - 1));
        struct Native *val = cast(Native(), lookAt(last->value, 0));
    }

    struct Node *last = cast(Node(), lookAt(listeNoeuds, count(listeNoeuds) - 1));
    struct Native *val = cast(Native(), lookAt(last->value, 0));

    delete(dicoKeys);
    delete(symbols);

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
    struct List *list = copyList(nodeList);
    while (count(list) > 1) {
        n1 = getLowestFrequencySymbol(list);
        removed = removeItem(list, (const struct Object *) n1);
        assert(removed);
        n2 = getLowestFrequencySymbol(list);
        removed = removeItem(list, (const struct Object *) n2);
        assert(removed);

        // merging the two nodes
        n12 = mergeTwoNodes(n1, n2);
        addLast(list, (const struct Object *) n12);
        addLast(nodeList, (const struct Object *) n12);
    }

    struct Node *racine = cast(Node(), lookAt(list, 0));
    delete(list);

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

    int empty, c;
    // printing the string to the screen
    for (int i = 0; i < 20; i++) {
        empty = 1;
        c = 0;
        // checking if a row is empty
        while (c < 255 && s[i][c] != '\0') {
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
        // updating its entry in the dictionary
        set(encoding, prefix, root->value);
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

void freeNodeTree(struct Node *root) {
    if (root->left)
        freeNodeTree(root->left);
    if (root->right)
        freeNodeTree(root->right);
    delete(root);
}