#ifndef HUFFMAN_H
#define HUFFMAN_H

#include "../types/Object.h"
#include "../types/Node.h"
#include "../types/List.h"

struct Node *mergeTwoNodes(struct Node *a, struct Node *b);
struct List *splitPhraseInNodes(const char *phrase, void *_symbols);
struct Node *getLowestFrequencySymbol(struct List *nodeList);

#endif