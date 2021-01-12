#include <stdlib.h>

#include "../types/Object.h"
#include "../types/Dictionary.h"

#include "../lib/huffman.h"

int main() {
    printf("\n/* -------- TEST Huffman -------- */\n");

    char *phrase = "phrase à tester ...";

    struct Dictionary *symbols = new(Dictionary());

    struct List *listeNoeuds = splitPhraseInNodes(phrase, symbols);
    printf("Nb éléments dans liste : %d\n", count(listeNoeuds));
    return 0;
}