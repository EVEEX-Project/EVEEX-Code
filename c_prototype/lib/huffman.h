#ifndef HUFFMAN_H
#define HUFFMAN_H

#include "../types/Node.r"
#include "../types/Dictionary.r"

#include "../types/Object.h"
#include "../types/List.h"

struct Node *mergeTwoNodes(struct Node *a, struct Node *b);
struct List *splitPhraseInNodes(const char *phrase, void *_symbols);
struct Node *getLowestFrequencySymbol(struct List *nodeList);
struct Node *generateTreeFromList(struct List *nodeList);
void printHuffmanTree(struct Node *root);
void generateEncodingDict(struct Dictionary *encoding, struct Node *root, char *prefix);

#endif