#include <stdlib.h>

#include "../types/Object.h"
#include "../types/Point.h"
#include "../types/Dictionary.h"

int main() {
    printf("\n/* -------- TEST DICO -------- */\n");

    void *dict = new(Dictionary());

    void *pD = new(Point(), 1, 5);
    void *pE = new(Point(), 5, 2);

    set(dict, "D", pD);
    set(dict, "E", pE);
    set(dict, "D2", pD);

    void *pD2 = get(dict, "D");
    if (!differ(pD, pD2)) {
        puts("pD == pD2");
    }
    printf("Nb éléments dans le dico : %d\n", size(dict));

    if (size(dict) != 3) {
        perror("Wrong dictionnary size!");
        exit(EXIT_FAILURE);
    }

    delete(pD);
    delete(pE);
    delete(dict);

    return 0;
}