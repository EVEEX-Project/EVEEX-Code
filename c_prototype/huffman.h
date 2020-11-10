//
// Created by alexandre on 10/11/2020.
//

#ifndef C_PROTOTYPE_HUFFMAN_H
#define C_PROTOTYPE_HUFFMAN_H

#include "list.h"
#include "dictionary.h"

typedef struct {
    int frequence;
    void *valeur;
    struct Noeud *droite;
    struct Noeud *gauche;
} Noeud;

Noeud *Noeud_createNoeud(void *valeur, int frequence);
Noeud *Noeud_mergeTwoNodes(Noeud noeud_a, Noeud noeud_b);

List **Huffman_splitPhraseInNodes(char *phrase, Dictionary **symbols);
Noeud *Huffman_getTwoLowestSymbols(Noeud **listeNoeud);
Noeud *Huffman_sortNodes(Noeud **listeNoeud);


#endif //C_PROTOTYPE_HUFFMAN_H
