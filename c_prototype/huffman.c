#include "huffman.h"
#include "list.h"
#include "dictionary.h"
#include "utils.h"

Noeud *Noeud_createNoeud(void *valeur, int frequence) {
    Noeud *n = (Noeud *) malloc(sizeof(Noeud));
    n->droite = NULL;
    n->gauche = NULL;
    n->frequence = frequence;
    n->valeur = valeur;

    return n;
}

List **Huffman_splitPhraseInNodes(char *phrase, Dictionary **symbols) {
    List **listeNoeuds = List_create();

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

    return listeNoeuds;
}
