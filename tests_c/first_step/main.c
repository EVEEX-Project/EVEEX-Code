#include <stdio.h>
#include "new.h"
#include "String.h"
#include "Point.h"

int main() {
    void *a = new(String, "a"),
    *aa = clone(a);
    void *b = new(String, "b"); // création de 2 strings + 1 clone

    printf("sizeOf(a) == %zu\n", sizeOf(a));
    if (differ(a, b)) // 2 textes différents donnent 2 strings différentes
        puts("ok");
    if (differ(a, aa)) // on vérifie qu'une copie est égale mais pas identique
        puts("differ?");
    if (a == aa)
        puts("clone?");

    // résultat : sizeOf(a) == 8 \n ok

    delete(a), delete(aa), delete(b);

    // POINT
    void *pa = new(Point, 1, 5), *ppa = clone(pa);
    void *pb = new(Point, 2, 4);
    void *pc = new(Point, 1, 5);

    if (!differ(pa, ppa))
        puts("clone identique");
    if (!differ(pa, pc))
        puts("pa et pc identiques");

    delete(pa), delete(pb), delete(pc);
    return 0;
}
