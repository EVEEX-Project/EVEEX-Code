#include<stdlib.h>

#include "../types/Node.r"

#include "../types/Object.h"
#include "../types/Node.h"
#include "../types/Point.h"

int main() {
    void *pt = new(Point(), 2, 5);
    struct Node *noeud = new(Node(), 5, pt);
    struct Node *sousnoeud = new(Node(), 15, pt);

    puto(noeud, stdout);

    noeud->right = sousnoeud;
    puto(sousnoeud, stdout);

    delete(noeud);
    delete(sousnoeud);
    delete(pt);

    exit(EXIT_SUCCESS);
}