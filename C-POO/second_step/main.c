//
// Created by alexandre on 01/12/2020.
//

#include "Object.h"
#include "Point.h"
#include "List.h"
#include "Dictionary.h"

int main() {
    printf("/* -------- TEST POINT -------- */\n");
    void *pA = new(Point(), 0, 0);

    puto(pA, stdout);
    draw(pA);
    move(pA, 5, 2);
    draw(pA);
    puto(pA, stdout);

    delete(pA);

    printf("\n/* -------- TEST LIST -------- */\n");
    void *list = new(List());

    void *pB = new(Point(), 1, 1);
    void *pC = new(Point(), 2, 9);

    addLast(list, pB);
    addLast(list, pC);

    printf("Nb éléments dans liste : %d\n", count(list));

    printf("Affichage du premier élément : ");
    puto(lookAt(list, 0), stdout);

    delete(pB);
    delete(pC);
    delete(list);

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

    delete(pD);
    delete(pE);
    delete(dict);

    return 0;
}