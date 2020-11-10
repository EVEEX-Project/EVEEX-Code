#include "huffman.h"
#include "list.h"
#include "dictionary.h"
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
    for (ptr = *listeNoeud; ptr != NULL; ptr = ptr->next) {
        Noeud *current = ptr->element;
        if (current->frequence < mini->frequence)
            mini = current;
    }

    return mini;
}