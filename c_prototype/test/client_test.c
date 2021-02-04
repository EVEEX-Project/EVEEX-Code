#if defined(WIN32)
    #include <winsock2.h>
    typedef int socklen_t;
#elif defined(__linux__)
    #include <sys/types.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <netdb.h>

    #define INVALID_SOCKET -1
    #define SOCKET_ERROR -1
    #define closesocket(s) close(s)

    typedef int SOCKET;
    typedef struct sockaddr_in SOCKADDR_IN;
    typedef struct sockaddr SOCKADDR;
    typedef struct in_addr IN_ADDR;
#else
    // unsupported platform
#endif


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#include "../types/Object.h"
#include "../types/Dictionary.h"
#include "../lib/huffman.h"
#include "../types/Native.h"
#include "../types/Native.r"
#include "../types/Bitstream.r"
#include "../types/Bitstream.h"

#include "../lib/client.h"


#define PORT 3456
#define IP_ADDRESS "127.0.0.1"
#define BUFFER_SIZE 10


int main(void) {
    /*
     * Application client. On supposera que le client créé n'est associé qu'à un seul serveur.
     * Pour modifier le port, l'adresse IP et/ou le bufsize de référence du client, il
     * suffit de modifier les "#define" ci-desssus.
     * Ce code source a été fait en conjonction avec "server_test.c".
     */

    int i, code_retour_au_lancement, j, j_debut, j_fin, nb_sent_characters;
    const int taille_utile_paquet = BUFFER_SIZE - 1; // on laisse une place pour le '\0' final
    char buffer_msg_to_send[BUFFER_SIZE], buffer_received_msg[3], ok_msg[3] = "ok";

    CLIENT client;

    char * phrase_huffman = "ensta bretagne ftw";
    int nb_elems_phrase_huffman = (int) strlen(phrase_huffman);

    // Préparatifs pour l'encodage de Huffman de la phrase précédente
    struct List * liste_noeuds = splitPhraseInNodes(phrase_huffman);
    struct Node * racine = generateTreeFromList(liste_noeuds);
    struct Dictionary * dico_huffman = new(Dictionary());
    generateEncodingDict(dico_huffman, racine, "");

    char lettre[2]; lettre[1] = '\0';
    struct Native * lettre_encodee;

    char * phrase_encodee;
    int nb_elems_phrase_encodee;

    // Préparatifs pour le bitstream
    int frame_id = 0;
    enum MessageTypes msg_type = BODY_MSG;
    unsigned long msg_size;
    struct Bitstream * bitstream;

    /* ------------------------------------------------------------------------------ */

    #if defined(WIN32)
        WSACleanup(); // au cas où il y ait eu des erreurs lors de la précédente exécution

        WSADATA WSAData;
        code_retour_au_lancement = WSAStartup(MAKEWORD(2, 2), &WSAData);

        if (code_retour_au_lancement != 0) {
            printf("\n[CLIENT] Erreur au lancement (sur Windows)\n");
            exit(EXIT_FAILURE);
        }
    #endif

    /* ------------------------------------------------------------------------------ */

    printf("\n# ------------ TEST - APPLICATION CLIENT ------------ #\n");

    initialize_client(&client, PORT, IP_ADDRESS, BUFFER_SIZE);
    connect_to_server(&client);

    // Détermination du nombre d'élements dans la phrase encodée de Huffman
    nb_elems_phrase_encodee = 0;
    for (i = 0; i < nb_elems_phrase_huffman; i++) {
        lettre[0] = phrase_huffman[i];
        lettre_encodee = cast(Native(), get(dico_huffman, lettre));
        nb_elems_phrase_encodee += (int) strlen((char *) lettre_encodee->value);
    }

    // Initialisation de de la phrase encodée
    phrase_encodee = (char *) malloc((nb_elems_phrase_encodee + 1) * sizeof(char));
    phrase_encodee[0] = '\0'; // pour que le strcat initial ne fasse pas n'importe quoi

    // Encodage de Huffman
    for (i = 0; i < nb_elems_phrase_huffman; i++) {
        lettre[0] = phrase_huffman[i];
        lettre_encodee = cast(Native(), get(dico_huffman, lettre));
        strcat(phrase_encodee, (char *) lettre_encodee->value);
    }

    printf("\n\nPhrase de depart : \"%s\"", phrase_huffman);
    printf("\nPhrase encodee : \"%s\"", phrase_encodee);
    printf("\nstrlen(phrase_encodee) : %d\n", (int) strlen(phrase_encodee));

    // Génération de l'instance de la classe Bitstream associée au message encodé
    msg_size = (unsigned long) strlen(phrase_encodee); // = nb_elems_phrase_encodee
    bitstream = cast(Bitstream(), new(Bitstream(), frame_id, msg_type, msg_size, phrase_encodee));

    // Envoi de la valeur de "msg_size" au serveur
    sprintf(buffer_msg_to_send, "%d", msg_size);
    send_data_to_server(&client, buffer_msg_to_send, -1, false);
    wait_for_response(&client, buffer_received_msg, ok_msg, -1, false);

    // Détermination de nb_total_paquets (rappel : taille_utile_paquet = BUFFER_SIZE - 1)
    if (msg_size % taille_utile_paquet == 0)
        client.nb_total_paquets = msg_size / taille_utile_paquet;
    else
        client.nb_total_paquets = msg_size / taille_utile_paquet + 1;

    // Communication client-serveur "officielle"/utile
    for (i = 1; i <= client.nb_total_paquets; i++) {
        j_debut = (i - 1) * taille_utile_paquet;
        if (i != client.nb_total_paquets)
            j_fin = i * taille_utile_paquet - 1;
        else
            j_fin = msg_size - 1;

        // Détermination du paquet à envoyer au serveur (de 'taille utile' égale à bufsize-1)
        for (j = j_debut; j <= j_fin; j++) {
            buffer_msg_to_send[j - j_debut] = (bitstream->data)[j];
            // OU BIEN : buffer_msg_to_send[j - debut] = phrase_encodee[j];
        }
        buffer_msg_to_send[j_fin - j_debut + 1] = '\0';

        send_data_to_server(&client, buffer_msg_to_send, i, true);
        wait_for_response(&client, buffer_received_msg, ok_msg, i, true);
    }

    // Envoi du bitstream total au serveur, afin que le serveur puisse vérifier si
    // la concaténation des tous les messages (utiles) qu'il a reçus est bien égale
    // au bitstream de référence
    nb_sent_characters = send(client.client_socket, phrase_encodee, msg_size+1, 0);
    if (nb_sent_characters <= 0) {
        printf("\n[CLIENT] Erreur lors du send() final\n");
        exit(EXIT_FAILURE);
    }

    shutdown_client(&client);
    close_client(&client);

    // Pour éviter qu'il y ait des fuites de mémoire
    free(phrase_encodee);
    delete(racine);
    delete(dico_huffman);
    delete(liste_noeuds);
    delete(bitstream);

    /* ------------------------------------------------------------------------------ */

    #if defined(WIN32)
        WSACleanup();
    #endif

    return EXIT_SUCCESS;
}
