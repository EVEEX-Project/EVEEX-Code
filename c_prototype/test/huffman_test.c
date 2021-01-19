#include <stdlib.h>
#include <string.h>

#include "../types/Object.h"
#include "../types/Dictionary.h"

#include "../lib/huffman.h"
#include "../types/Native.h"
#include "../types/Node.h"
#include "../types/Native.r"

int main() {
    printf("\n/* -------- TEST Huffman -------- */\n");

    char *phrase = "phrase a tester ...";
    printf("Sentence to test : '%s' with a length of : %lu\n", phrase, strlen(phrase));

    struct List *listeNoeuds = splitPhraseInNodes(phrase);
    printf("Nb éléments dans liste : %d\n", count(listeNoeuds));

    for (unsigned i = 0; i < count(listeNoeuds); i++) {
        struct Node *noeud = cast(Node(), lookAt(listeNoeuds, i));
        struct List *valList = cast(List(), noeud->value);
        struct Native *val = cast(Native(), lookAt(valList, 0));
        char *sym = (char *) val->value;
        unsigned long freq = noeud->frequency;
        printf("-- Fréquence : %lu, Value : %s\n", freq, sym);
    }

    struct Node *mini = cast(Node(), getLowestFrequencySymbol(listeNoeuds));
    char *symMin = (char *) ((struct Native *) lookAt(mini->value, 0))->value;
    printf("Lowest node : %s with freq : %lu\n", symMin, mini->frequency);

    struct Node *racine = generateTreeFromList(listeNoeuds);
    char *symRacine = (char *) ((struct Native *) lookAt(racine->value, 0))->value;
    printf("Root node : %s with freq : %lu\n", symRacine, racine->frequency);

    if (racine->frequency != strlen(phrase)) {
        perror("Bad frequency addition");
        exit(EXIT_FAILURE);
    }

    printf("Printing huffman tree : \n");
    printHuffmanTree(racine);

    printf("Encoding dictionary : \n");
    struct Dictionary *encodingDict = new(Dictionary());
    generateEncodingDict(encodingDict, racine, "");

    struct List *encodingKeys = getKeys(encodingDict);
    for (unsigned i = 0; i < count(encodingKeys); i++) {
        const char *key = ((struct Native *) cast(Native(), lookAt(encodingKeys, i)))->value;
        struct Native *val = cast(Native(), lookAt(cast(List(), get(encodingDict, key)), 0));
        printf("%s --> %s\n", key, (char *) val->value);
    }

    freeNodeTree(racine);
    delete(encodingKeys);
    delete(encodingDict);
    delete(listeNoeuds);

    return 0;
}