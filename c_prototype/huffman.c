#include "huffman.h"
#include "utils.h"

Noeud **Noeud_createList() {
    return calloc(sizeof(Noeud), 1);
}

Noeud **Huffman_splitPhraseInNodes(char *phrase, Dictionary **symbols) {
    Noeud **listeNoeuds = Noeud_createList();

    for (char *symbol = phrase; *symbol != '\0'; symbol++) {
        printf("%c", *symbol);
    }

    free(listeNoeuds);
}
