#include <stdlib.h>

#include "../types/Object.h"
#include "../types/Point.h"
#include "../types/Dictionary.h"

int main() {
    printf("\n/* -------- TEST DICO -------- */\n");

    void *dict = new(Dictionary());

    struct Point *pD = new(Point(), 1, 5);
    struct Point *pE = new(Point(), 5, 2);

    set(dict, "D", (void *) pD);
    set(dict, "E", (void *) pE);
    set(dict, "D2", (void *) pD);

    struct Point *pD2 = (struct Point *) get(dict, "D");
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