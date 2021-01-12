#include "huffman.h"
#include "data_types/list.h"
#include "data_types/dictionary.h"
#include "utils.h"
#include <stdio.h>

/*
 * Function: Node_create
 * ---------------------
 * Creates a new node with a value and frequency and allocated memory for
 * that object. Returns a pointer to that object.
 *
 *  value: the value of the node
 *  frequency: the frequency of apparition of the node
 *
 *  returns: a pointer to the created node
 */
Node *Node_create(void *value, int frequency) {
    Node *n = (Node *) malloc(sizeof(Node));
    n->right = NULL;
    n->left = NULL;
    n->frequency = frequency;
    n->value = value;

    return n;
}

/*
 * Function: Node_free
 * -------------------
 * Free the memory used for a specific node.
 *
 *  node: the node to free
 */
void Node_free(Node *node) {
    // fist set all properties to null
    node->right = NULL;
    node->left = NULL;
    node->value = NULL;
    // then free the node to avoid GC problems
    free(node);
}

/*
 * Function Node_mergeTwoNodes
 * ---------------------------
 * Takes two nodes and merges them by adding their frequency and
 * fusionning their value. Returns the merged node.
 *
 *  nodeA: the first node to merge
 *  nodeB: the second node to merge
 *
 *  returns: a new node created from nodeA and nodeB
 */
Node *Node_mergeTwoNodes(Node *nodeA, Node *nodeB)
{
    // creating the new value from the value of the two nodes
    char *newValue = malloc(sizeof(char) * 255);
    sprintf(newValue, "[%s, %s]", nodeA->value, nodeB->value);

    // creating the new frequency from the two nodes
    int newFrequency = nodeA->frequency + nodeB->frequency;

    // creating the merged node and setting its children
    Node *newNode = Node_create(newValue, newFrequency);
    newNode->left = nodeA;
    newNode->right = nodeB;

    // returning the newly created node
    return newNode;
}

/*
 * Function: Node_print
 * --------------------
 * Prints the representation of a node. That means pretty printing its value and
 * frequency.
 *
 *  node: the node to represent
 */
void Node_print(Node *node) {
    printf("Node : {Value: %s, Frequency: %d}\n", node->value, node->frequency);
}

/*
 * Function: Huffman_splitPhraseInNodes
 * ------------------------------------
 * Takes a phrase (serie of symbols) and creates a new node for each
 * symbol present in the phrase. It updates a symbols dictionary
 * containing all those symbols with their frequency. Then it creates a new
 * list of nodes from the symbols dictionary.
 *
 *  phrase: the phrase to split in nodes
 *  symbols: the dictionary containing symbols and their frequency
 *
 *  returns: a list of nodes from the symbols in the phrase with their frequency
 */
List **Huffman_splitPhraseInNodes(char *phrase, Dictionary **symbols) {
    List **listeNoeuds = List_create();

    // Calculating the frequencies
    int *freq;
    char key[2];
    key[1] = '\0';
    // for each symbol in the phrase
    for (int i = 0; phrase[i] != '\0'; i++) {
        // getting the key
        key[0] = phrase[i];
        // and its frequency
        freq = Dico_get(symbols, key);
        if (freq == NULL) {
            // first time seeing that key
            int *freq_init = calloc(sizeof(int), 1);
            *freq_init = 1;
            freq = freq_init;
        }
        else {
            // key already registered
            (*freq)++;
        }
        // updating the entry in the dictionary
        Dico_set(symbols, key, freq);
    }

    // Adding the nodes to the list
    List **dicoKeys = Dico_keys(symbols);
    List *ptr;
    // for each symbol in the dictionary
    for (ptr = *dicoKeys; ptr != NULL; ptr = ptr->next) {
        // creating a new node and adding it to the list
        Node *n = Node_create(ptr->element, *((int *) Dico_get(symbols, ptr->element)));
        List_append(listeNoeuds, n);
    }

    // returning the list of nodes at the end
    return listeNoeuds;
}

/*
 * Function: Huffman_getLowestFrequencySymbol
 * ------------------------------------------
 * Returns the node in a list with the lowest frequency. It
 * can be a single symbol or a merged node.
 *
 *  nodesList: the list of nodes to test
 *
 *  returns: the node with the lowest frequency
 */
Node *Huffman_getLowestFrequencySymbol(List **nodesList)
{
    List *ptr;
    Node *mini;
    // iteration over all the elements of the list
    for (ptr = *nodesList, mini = ptr->element; ptr != NULL; ptr = ptr->next) {
        Node *current = ptr->element;
        // we found a better candidate
        if (current->frequency < mini->frequency)
            mini = current;
    }

    // returning the element with the lowest frequency
    return mini;
}

/*
 * Function: Huffman_generateTreeFromList
 * --------------------------------------
 * Generates a tree (linked list of nodes) from a list of nodes by
 * merging the lowest frequencies together and so on until there
 * is only one nodes which becomes the root of the tree.
 *
 *  nodesList: list of nodes from which generating a tree
 *
 *  returns: the root of the tree
 */
Node *Huffman_generateTreeFromList(List **nodesList)
{
    printf("GENERATING TREE\n");
    // two lowest frequency nodes and the merged one
    Node *n1, *n2, *n12;
    bool find_result;
    // while there is still a node to merge
    while (List_size(nodesList) > 1) {
        // we get the two lowest scores to merge them
        n1 = Huffman_getLowestFrequencySymbol(nodesList);
        find_result = List_remove(nodesList, n1);
        ON_ERROR_EXIT(find_result == false, "Node(1) not found in list");
        n2 = Huffman_getLowestFrequencySymbol(nodesList);
        find_result = List_remove(nodesList, n2);
        ON_ERROR_EXIT(find_result == false, "Node(2) not found in list");

        // merging them
        n12 = Node_mergeTwoNodes(n1, n2);
        // adding the node back into the list
        List_append(nodesList, n12);
    }

    // the last one is then the root of the tree
    List *racine = *nodesList;
    // returning the node associated with the list element
    return racine->element;
}

/*
 * Helper function: _print_t
 * -------------------------
 * Helper function adapted from the following stack overflow post :
 * https://stackoverflow.com/questions/801740/c-how-to-draw-a-binary-tree-to-the-console
 * Helping the printing of a Huffman tree using a recursive function
 *
 *  node: the current node to print
 *  is_left: is the current node the left children of its parent?
 *  is_right: is the current node the right children of its parent?
 *  offset: the offset of the position from the left of the screen
 *  depth: depth in the roots of the tree
 *  s: the string representing the tree
 */
int _print_t(Node *node, int is_left, int offset, int depth, char s[20][255])
{
    char b[20];
    int width = 3;

    // si the node is null there is nothing to show
    if (!node) return 0;

    // if the node has no parent
    if (!node->left && !node->right) {
        // storing the nodes value in a buffer
        sprintf(b, "(%s)", node->value);
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

/*
 * Function: Huffman_printTree
 * ---------------------------
 * Prints the representation of a huffman encoding tree with
 * the help of the function _print_t.
 *
 *  root: the root of the tree to print
 */
void Huffman_printTree(Node *root) {
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

/*
 * Function: Huffman_generateEncodingDict
 * --------------------------------------
 * Generate a new dictionary to encode a phrase using the Huffman algorithm
 * principle. Returns such a dictionary from a tree. When going left in the
 * tree we append a "0" to the prefix and "1" if going right.
 * Each symbol is then encoded with an non ambiguous binary number.
 *
 *  encoding: the final encoding dictionary
 *  root: the root of the huffman tree
 *  prefix: the current prefix for the encoding
 */
void Huffman_generateEncodingDict(Dictionary **encoding, Node *root, char *prefix)
{
    // if there is no children we add the symbol to the dictionary
    if (root->left == NULL && root->right == NULL) {
        // getting the current prefix
        char *newPrefixe = strdup(prefix);
        // updating its entry in the dictionary
        Dico_set(encoding, root->value, newPrefixe);
        return;
    }

    // updating the size for the prefix
    char newPrefixe[strlen(prefix) + 2];
    strcpy(newPrefixe, prefix);
    newPrefixe[strlen(prefix) + 1] = '\0';

    // if there is a child on the left
    if (root->left != NULL) {
        // updating the prefix with a "0"
        newPrefixe[strlen(prefix)] = '0';
        // continue with the creation of the encoding dictionary
        Huffman_generateEncodingDict(encoding, root->left, newPrefixe);
    }
    // if there is a child on the right
    if (root->right != NULL) {
        // updating the prefix with a "1"
        newPrefixe[strlen(prefix)] = '1';
        // continue with the creation of the encoding dictionary
        Huffman_generateEncodingDict(encoding, root->right, newPrefixe);
    }
}