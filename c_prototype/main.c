
#include <stdlib.h>
#include "types/Object.h"
#include "types/Point.h"

int main() {
    printf("/* -------- TEST POINT -------- */\n");
    void *pA = new(Point(), 0, 0);

    puto(pA, stdout);
    draw(pA);
    move(pA, 5, 2);
    draw(pA);
    puto(pA, stdout);

    delete(pA);

    exit(EXIT_SUCCESS);
}