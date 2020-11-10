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

    // on ajoute des éléments
    Dico_set(hashtab, "foo", "bar");
    Dico_set(hashtab, "bar", "foo");
    Dico_print(hashtab);

    printf("La valeur du dico avec la clé %s est %s\n", "foo", Dico_get(hashtab, "foo"));

    Dico_del(hashtab, "foo");
    Dico_del(hashtab, "bar");
    Dico_print(hashtab);

    Dico_set(hashtab, "foo", "bar");
    Dico_set(hashtab, "bar", "foo");
    Dico_set(hashtab, "bar", "pan");
    Dico_print(hashtab);

    Dico_free(hashtab);

    printf("\n\n");
}

void list_test() {
    printf("===============DICO TEST===============\n");

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

void huffman_test() {
    Dictionary **symbols = Dico_create();
    Noeud **liste_noeuds = Huffman_splitPhraseInNodes("jaime les citrons", symbols);
}

int main() {
    /*dictionary_test();
    img_test();
    huffman_test();*/
    list_test();

    return 0;
}
