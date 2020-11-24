#include <stdio.h>

#include "data_types/bitstream.h"
#include "data_types/image.h"
#include "data_types/dictionary.h"
#include "data_types/list.h"
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

    printf("La value du dico avec la clé %s est %d\n", "foo", *((int *) Dico_get(hashtab, "foo")));

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
        Node *n = ptr->element;
        printf("(%s: %d) ", n->value, n->frequency);
    }
    printf("\n");

    Node *noeud_a = Node_create("a", 5);
    Node *noeud_b = Node_create("b", 3);
    Node_print(noeud_a);
    Node_print(noeud_b);
    Node *noeud_c = Node_mergeTwoNodes(noeud_a, noeud_b);
    Node_print(noeud_c);
    Node_print(Node_mergeTwoNodes(noeud_c, noeud_a));

    Node *lowestFrequency = Huffman_getLowestFrequencySymbol(liste_noeuds);
    printf("The symbol with the lowest frequency is: '%s' with a frequency of: %d\n", lowestFrequency->value, lowestFrequency->frequency);
    printf("# element before removing : %d\n", List_size(liste_noeuds));
    List_remove(liste_noeuds, lowestFrequency);
    printf("# element after removing : %d\n", List_size(liste_noeuds));
    List_append(liste_noeuds, lowestFrequency);

    Node *racine = Huffman_generateTreeFromList(liste_noeuds);
    printf("Racine : ");
    Node_print(racine);
    printf("Sentence length : %lu\n", strlen(phrase));

    printf("\n\n");
}

void bitstream_test() {
    printf("===============BITSTREAM TEST===============\n");

    Bitstream *bitstream = Bitstream_create();

    // setting the symbols dictionnary with sample data
    Dico_set(bitstream->symbols, "a", "100");
    Dico_set(bitstream->symbols, "b", "1011");
    Dico_set(bitstream->symbols, "c", "11100");
    printf("Bitstream dictionary : ");
    Dico_printString(bitstream->symbols);

    char *plain_text = "aabbcc";
    printf("Initial plaintext : %s\n", plain_text);
    bitstream->data = Bitstream_encodeData(bitstream, plain_text);
    printf("Encoded data : %s\n", bitstream->data);
    plain_text = Bitstream_decodeData(bitstream, bitstream->data);
    printf("Decoded back data : %s\n", plain_text);

    // freeing the stream at the end
    Bitstream_free(bitstream);
    printf("\n\n");
}

void huffman_test() {
    printf("===============HUFFMAN TEST===============\n");

    char *phrase = "le chic de l'ensta bretagne sur la compression video";
    Dictionary **symbols = Dico_create();
    List **liste_noeuds = Huffman_splitPhraseInNodes(phrase, symbols);
    Node *racine = Huffman_generateTreeFromList(liste_noeuds);
    Node_print(racine);

    printf("Printing the tree : \n");
    Huffman_printTree(racine);

    Dictionary **encoding = Dico_create();
    Huffman_generateEncodingDict(encoding, racine, "");
    Dico_printString(encoding);

    // Bitstream
    Bitstream *bitstream = Bitstream_create();
    Dico_free(bitstream->symbols);
    bitstream->symbols = encoding;
    char *cipher_text = Bitstream_encodeData(bitstream, phrase);
    printf("Encoded string : %s\n", cipher_text);
    char *plain_text = Bitstream_decodeData(bitstream, cipher_text);
    printf("String decoded back : %s\n", plain_text);

    printf("\n\n");
}

int main() {
    dictionary_test();
    img_test();
    list_test();
    nodes_test();
    huffman_test();
    bitstream_test();

    return 0;
}
