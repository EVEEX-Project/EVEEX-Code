#include <stdlib.h>

#include "../types/Object.h"
#include "../types/Point.h"
#include "../types/List.h"

int main() {
    printf("\n/* -------- TEST LIST -------- */\n");
    void *list = new(List());

    void *pB = new(Point(), 1, 1);
    void *pC = new(Point(), 2, 9);

    addLast(list, pB);
    addLast(list, pC);

    printf("Nb éléments dans liste : %d\n", count(list));

    // checking that the list has the right nuwber of éléments
    if (count(list) != 2) {
        perror("Wrong number of element in list!");
        exit(EXIT_FAILURE);
    }

    if (differ(lookAt(list, 0), pB)) {
        perror("First element is different!");
        exit(EXIT_FAILURE);
    }

    printf("Affichage du premier élément : ");
    puto(lookAt(list, 0), stdout);

    struct Point *removed = (struct Point *) removeItem(list, pB);
    if (removed == NULL) {
        perror("Can't remove element from list");
        exit(EXIT_FAILURE);
    }
    if (differ(removed, pB)) {
        perror("Removed wrong element");
        exit(EXIT_FAILURE);
    }

    printf("Nb éléments dans liste apres remove : %d\n", count(list));
    printf("Affichage de l'élément retiré : ");
    puto(removed, stdout);

    delete(pB);
    delete(pC);
    delete(list);

    exit(EXIT_SUCCESS);
}