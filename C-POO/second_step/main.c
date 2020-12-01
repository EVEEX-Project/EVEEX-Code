//
// Created by alexandre on 01/12/2020.
//

#include "Object.h"
#include "Point.h"
#include "List.h"

int main() {
    printf("/* -------- TEST POINT -------- */\n");
    initPoint();
    void *pA = new(Point, 0, 0);

    puto(pA, stdout);
    draw(pA);
    move(pA, 5, 2);
    draw(pA);
    puto(pA, stdout);

    delete(pA);

    printf("\n/* -------- TEST LIST -------- */\n");
    initList();
    void *list = new(List);

    void *pB = new(Point, 1, 1);
    void *pC = new(Point, 2, 9);

    addLast(list, pB);
    addLast(list, pC);

    printf("Nb éléments dans liste : %d\n", count(list));

    printf("Affichage du premier élément : ");
    puto(lookAt(list, 0), stdout);

    delete(pB);
    delete(pC);
    delete(list);
    return 0;
}