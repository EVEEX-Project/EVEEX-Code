//
// Created by alexandre on 10/11/2020.
//

#ifndef C_PROTOTYPE_HUFFMAN_H
#define C_PROTOTYPE_HUFFMAN_H

#include "data_types/list.h"
#include "data_types/dictionary.h"

/*
 * Structure: Image
 * ---------------------
 * Structure that describes a node in a tree with its value
 * and frequency and it's link to children nodes on the left and
 * right branches.
 */
typedef struct Node_struct {
    int frequency;
    void *value;
    struct Node_struct *right;
    struct Node_struct *left;
} Node;

/* Creation and deletion functions */
Node *Node_create(void *value, int frequency);
void Node_free(Node *node);

/* Nodes operations */
Node *Node_mergeTwoNodes(Node *nodeA, Node *nodeB);
void Node_print(Node *node);

/* Huffman misc functions */
void Huffman_printTree(Node *root);
List **Huffman_splitPhraseInNodes(char *phrase, Dictionary **symbols);
Node *Huffman_getLowestFrequencySymbol(List **nodesList);

/* Huffman generation functions */
Node *Huffman_generateTreeFromList(List **nodesList);
void Huffman_generateEncodingDict(Dictionary **encoding, Node *root, char *prefix);



#endif //C_PROTOTYPE_HUFFMAN_H
