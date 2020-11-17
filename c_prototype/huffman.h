//
// Created by alexandre on 10/11/2020.
//

#ifndef C_PROTOTYPE_HUFFMAN_H
#define C_PROTOTYPE_HUFFMAN_H

#include "data_types/list.h"
#include "data_types/dictionary.h"

typedef struct Noeud_struct {
    int frequence;
    void *valeur;
    struct Noeud_struct *droite;
    struct Noeud_struct *gauche;
} Noeud;

Noeud *Noeud_createNoeud(void *valeur, int frequence);
Noeud *Noeud_mergeTwoNodes(Noeud *noeud_a, Noeud *noeud_b);
void Noeud_printNode(Noeud *noeud);

List **Huffman_splitPhraseInNodes(char *phrase, Dictionary **symbols);
Noeud *Huffman_getLowestFrequencySymbol(List **listeNoeud);
Noeud *Huffman_generateTreeFromList(List **listeNoeud);
void Huffman_printTree(Noeud *racine);
void Huffman_generateEncodingDict(Dictionary **encoding, Noeud *racine, char *prefixe);

#endif //C_PROTOTYPE_HUFFMAN_H
