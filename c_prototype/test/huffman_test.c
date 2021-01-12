#include <stdlib.h>

#include "../types/Object.h"
#include "../types/Dictionary.h"

#include "../lib/huffman.h"
#include "../types/Native.h"
#include "../types/Node.r"
#include "../types/Native.r"

int main() {
    printf("\n/* -------- TEST Huffman -------- */\n");

    char *phrase = "phrase a tester ...";

    struct Dictionary *symbols = new(Dictionary());

    struct List *listeNoeuds = splitPhraseInNodes(phrase, symbols);
    printf("Nb éléments dans liste : %d\n", count(listeNoeuds));

    for (unsigned i = 0; i < count(listeNoeuds); i++) {
        struct Node *item = cast(Node(), lookAt(listeNoeuds, i));
        struct List *valList = cast(List(), item->value);
        struct Native *val = cast(Native(), lookAt(valList, 0));
        char *sym = (char *) val->value;
        unsigned long freq = item->frequency;
        printf("-- Fréquence : %lu, Value : %s\n", freq, sym);
    }

    struct Node *mini = cast(Node(), getLowestFrequencySymbol(listeNoeuds));
    char *symMin = (char *) ((struct Native *) lookAt(mini->value, 0))->value;
    printf("Lowest node : %s with freq : %lu\n", symMin, mini->frequency);

    return 0;
}