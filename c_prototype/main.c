#include <stdio.h>
#include "image.h"
#include "dictionary.h"
#include "list.h"
#include "huffman.h"
#include "utils.h"


void img_test() {
    printf("===============IMAGE TEST===============\n");

    Image img, gray, sepia;

    Image_load(&img, "assets/image_res.jpg");
    ON_ERROR_EXIT( img.data == NULL, "Error while loading the image");
    printf("Image loaded with a width of %dpx and height of %dpx with %d channels\n", img.width, img.height, img.channels);

    Image_to_gray(&img, &gray);
    Image_to_sepia(&img, &sepia);
    Image_save(&gray, "assets/gray_res.jpg");
    printf("Saving gray img to disk\n");
    Image_save(&sepia, "assets/sepia_res.jpg");
    printf("Saving sepia img to disk\n");

    Image_free(&img);
    Image_free(&gray);
    Image_free(&sepia);

    printf("\n\n");
}

void dictionary_test() {
    printf("===============DICO TEST===============\n");

    Dictionary **hashtab = Dico_create();
    ON_ERROR_EXIT(hashtab == NULL, "Error while allocating dico memory");

    int a = 5, b = 2, c = 10;

    // on ajoute des éléments
    Dico_set(hashtab, "foo", &a);
    Dico_set(hashtab, "bar", &b);
    Dico_printInt(hashtab);

    printf("La valeur du dico avec la clé %s est %d\n", "foo", *((int *) Dico_get(hashtab, "foo")));

    Dico_del(hashtab, "foo");
    Dico_del(hashtab, "bar");
    Dico_printInt(hashtab);

    Dico_set(hashtab, "foo", &a);
    Dico_set(hashtab, "bar", &b);
    Dico_set(hashtab, "bar", &c);
    Dico_printInt(hashtab);

    Dico_free(hashtab);

    printf("\n\n");
}

void list_test() {
    printf("===============LIST TEST===============\n");

    List **maListe = List_create();

    List_append(maListe, "hello");
    List_append(maListe, "world");
    List_add(maListe, "I'm saying : ");
    List_append(maListe, "!");

    List_print(maListe);
    printf("This list contains : %d elements\n", List_size(maListe));
    List_free(maListe);

    printf("\n\n");
}

void nodes_test() {
    printf("===============NODES TEST===============\n");

    Dictionary **symbols = Dico_create();
    char *phrase = "hello world";
    List **liste_noeuds = Huffman_splitPhraseInNodes(phrase, symbols);
    printf("Testing sentence : '%s'\n", phrase);

    printf("Symbol keys : ");
    List_print(Dico_keys(symbols));

    char *letter = "e";
    printf("Symbol apparition frequency for '%s' : %d\n", letter, *((int *) Dico_get(symbols, letter)));

    printf("Letters apparition frequency : ");
    Dico_printInt(symbols);

    printf("Nodes list (%d elements) (value: frequency): ", List_size(liste_noeuds));
    List *ptr;
    for (ptr = *liste_noeuds; ptr != NULL; ptr = ptr->next) {
        Noeud *n = ptr->element;
        printf("(%s: %d) ", n->valeur, n->frequence);
    }
    printf("\n");

    Noeud *noeud_a = Noeud_createNoeud("a", 5);
    Noeud *noeud_b = Noeud_createNoeud("b", 3);
    Noeud_printNode(noeud_a);
    Noeud_printNode(noeud_b);
    Noeud *noeud_c = Noeud_mergeTwoNodes(noeud_a, noeud_b);
    Noeud_printNode(noeud_c);
    Noeud_printNode(Noeud_mergeTwoNodes(noeud_c, noeud_a));

    Noeud *lowestFrequency = Huffman_getLowestFrequencySymbol(liste_noeuds);
    printf("The symbol with the lowest frequency is: '%s' with a frequency of: %d\n", lowestFrequency->valeur, lowestFrequency->frequence);
    printf("# element before removing : %d\n", List_size(liste_noeuds));
    List_remove(liste_noeuds, lowestFrequency);
    printf("# element after removing : %d\n", List_size(liste_noeuds));
    List_append(liste_noeuds, lowestFrequency);

    Noeud *racine = Huffman_generateTreeFromList(liste_noeuds);
    printf("Racine : ");
    Noeud_printNode(racine);
    printf("Sentence length : %lu\n", strlen(phrase));

    printf("\n\n");
}

void huffman_test() {
    printf("===============HUFFMAN TEST===============\n");

    char *phrase = "le chic de l'ensta bretagne sur la compression video";
    Dictionary **symbols = Dico_create();
    List **liste_noeuds = Huffman_splitPhraseInNodes(phrase, symbols);
    Noeud *racine = Huffman_generateTreeFromList(liste_noeuds);
    Noeud_printNode(racine);

    printf("Printing the tree : \n");
    Huffman_printTree(racine);

    Dictionary **encoding = Dico_create();
    Huffman_generateEncodingDict(encoding, racine, "");
    Dico_printString(encoding);

    printf("\n\n");
}

int main() {
    dictionary_test();
    img_test();
    list_test();
    nodes_test();
    huffman_test();

    return 0;
}
