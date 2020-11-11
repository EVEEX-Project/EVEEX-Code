#include "huffman.h"
#include "list.h"
#include "dictionary.h"
#include "utils.h"
#include <stdio.h>

Noeud *Noeud_createNoeud(void *valeur, int frequence) {
    Noeud *n = (Noeud *) malloc(sizeof(Noeud));
    n->droite = NULL;
    n->gauche = NULL;
    n->frequence = frequence;
    n->valeur = valeur;

    return n;
}

Noeud *Noeud_mergeTwoNodes(Noeud *noeud_a, Noeud *noeud_b)
{
    char *newValeur = malloc(sizeof(char) * 255);
    sprintf(newValeur, "[%s, %s]", noeud_a->valeur, noeud_b->valeur);
    Noeud *newNode = Noeud_createNoeud(newValeur, noeud_a->frequence + noeud_b->frequence);
    newNode->gauche = noeud_a;
    newNode->droite = noeud_b;

    return newNode;
}

void Noeud_printNode(Noeud *noeud) {
    printf("Noeud : {Value: %s, Frequency: %d}\n", noeud->valeur, noeud->frequence);
}

/* ------------------- HUFFMAN ------------------ */

List **Huffman_splitPhraseInNodes(char *phrase, Dictionary **symbols) {
    List **listeNoeuds = List_create();

    // Calculating the frequencies
    int *freq;
    char key[2];
    key[1] = '\0';
    for (int i = 0; phrase[i] != '\0'; i++) {
        key[0] = phrase[i];
        freq = Dico_get(symbols, key);
        if (freq == NULL) {
            //printf("1st time seeing : %s\n", key);
            int *freq_init = calloc(sizeof(int), 1);
            *freq_init = 1;
            freq = freq_init;
        }
        else {
            //printf("I know %s with frequence %d\n", key, *freq);
            (*freq)++;
        }
        Dico_set(symbols, key, freq);
    }

    // Adding the nodes to the list
    List **dicoKeys = Dico_keys(symbols);
    List *ptr;
    for (ptr = *dicoKeys; ptr != NULL; ptr = ptr->next) {
        Noeud *n = Noeud_createNoeud(ptr->element, *Dico_get(symbols, ptr->element));
        List_append(listeNoeuds, n);
    }

    return listeNoeuds;
}

Noeud *Huffman_getLowestFrequencySymbol(List **listeNoeud)
{
    List *ptr;
    Noeud *mini;
    for (ptr = *listeNoeud, mini = ptr->element; ptr != NULL; ptr = ptr->next) {
        Noeud *current = ptr->element;
        if (current->frequence < mini->frequence)
            mini = current;
    }

    return mini;
}

Noeud *Huffman_generateTreeFromList(List **listeNoeud)
{
    printf("GENERATING TREE\n");
    Noeud *n1, *n2, *n12;
    bool find_result;
    while (List_size(listeNoeud) > 1) {
        //printf("List size : %d\n", List_size(listeNoeud));
        // we get the two lowest scores to merge them
        n1 = Huffman_getLowestFrequencySymbol(listeNoeud);
        find_result = List_remove(listeNoeud, n1);
        ON_ERROR_EXIT(find_result == false, "Node(1) not found in list");
        n2 = Huffman_getLowestFrequencySymbol(listeNoeud);
        find_result = List_remove(listeNoeud, n2);
        ON_ERROR_EXIT(find_result == false, "Node(2) not found in list");

        // merging them
        n12 = Noeud_mergeTwoNodes(n1, n2);
        // adding the node back into the list
        List_append(listeNoeud, n12);

        printf("Merging : (%s: %d) + (%s: %d) => (%s: %d)\n", n1->valeur, n1->frequence, n2->valeur, n2->frequence, n12->valeur, n12->frequence);
    }

    List *racine = *listeNoeud;
    return racine->element;
}

// from : https://stackoverflow.com/questions/801740/c-how-to-draw-a-binary-tree-to-the-console
int _print_t(Noeud *noeud, int is_left, int offset, int depth, char s[20][255])
{
    char b[20];
    int width = 3;

    if (!noeud) return 0;

    if (!noeud->gauche && !noeud->droite) {
        sprintf(b, "(%s)", noeud->valeur);
    }
    else
        sprintf(b, " | ");

    int left  = _print_t(noeud->gauche,  1, offset,                depth + 1, s);
    int right = _print_t(noeud->droite, 0, offset + left + width, depth + 1, s);

    printf("Noeud : %s, Depth : %d, Left : %d, right : %d, offset : %d\n", noeud->valeur, depth, left, right, offset);
    for (int i = 0; i < width; i++) {
        if (b[i] != '\0')
            s[2 * depth][offset + left + i] = b[i];
        else
            break;
    }

    if (depth && is_left) {

        for (int i = 0; i < width + right; i++)
            s[2 * depth - 1][offset + left + width/2 + i] = '-';

        s[2 * depth - 1][offset + left + width/2] = '+';
        s[2 * depth - 1][offset + left + width + right + width/2] = '+';

    } else if (depth && !is_left) {

        for (int i = 0; i < left + width; i++)
            s[2 * depth - 1][offset - width/2 + i] = '-';

        s[2 * depth - 1][offset + left + width/2] = '+';
        s[2 * depth - 1][offset - width/2 - 1] = '+';
    }

    return left + width + right;
}

void Huffman_printTree(Noeud *racine) {
    char s[20][255];
    for (int i = 0; i < 20; i++)
        for (int j = 0; j < 255; j++)
            s[i][j] = ' ';

    _print_t(racine, 0, 0, 0, s);

    for (int i = 0; i < 20; i++)
        printf("%s\n", s[i]);
}