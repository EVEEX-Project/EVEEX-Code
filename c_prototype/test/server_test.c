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
#include <stdbool.h>
#include <string.h>

#include "../lib/server.h"


#define PORT 3456
#define IP_ADDRESS "127.0.0.1"
#define BUFFER_SIZE 10


int main(void) {
    /*
     * Application serveur. On supposera que le serveur créé n'a qu'un seul client.
     * Pour modifier le port, l'adresse IP et/ou le bufsize de référence du serveur, il
     * suffit de modifier les "#define" ci-desssus.
     * Ce code source a été fait en conjonction avec "client_test.c".
     */

    int i, code_retour_au_lancement, msg_size, code_retour_strcmp, nb_received_characters;
    const int taille_utile_paquet = BUFFER_SIZE - 1; // on laisse une place pour le '\0' final
    char buffer_received_msg[BUFFER_SIZE], ok_msg_to_send[3] = "ok", filler_str[1] = "";
    char *buffer_total_msg_received, *buffer_bitstream_total_reel;

    SERVER server;

    /* ------------------------------------------------------------------------------ */

    #if defined(WIN32)
        WSACleanup(); // au cas où il y ait eu des erreurs lors de la précédente exécution

        WSADATA WSAData;
        code_retour_au_lancement = WSAStartup(MAKEWORD(2, 2), &WSAData);

        if (code_retour_au_lancement != 0) {
            printf("\n[SERVER] Erreur au lancement (sur Windows)\n");
            exit(EXIT_FAILURE);
        }
    #endif

    /* ------------------------------------------------------------------------------ */

    printf("\n# ------------ TEST - APPLICATION SERVEUR ------------ #\n");

    initialize_server(&server, PORT, IP_ADDRESS, BUFFER_SIZE);
    listen_for_packets(&server);
    accept_client(&server); // attente de la connexion d'un client

    // Récupération de msg_size
    receive_msg_from_client(&server, filler_str, buffer_received_msg, -1, false);
    send_response_to_client(&server, ok_msg_to_send, -1, false);
    msg_size = atoi(buffer_received_msg); // atoi = "string/ASCII to int"

    // Détermination de nb_total_paquets (rappel : taille_utile_paquet = BUFFER_SIZE - 1)
    if (msg_size % taille_utile_paquet == 0)
        server.nb_total_paquets = msg_size / taille_utile_paquet;
    else
        server.nb_total_paquets = msg_size / taille_utile_paquet + 1;

    // Initialisation du message total à recevoir
    buffer_total_msg_received = (char *) malloc((msg_size + 1) * sizeof(char));
    buffer_total_msg_received[0] = '\0'; // pour que le strcat initial ne fasse pas n'importe quoi

    // Communication client-serveur "officielle"/utile (transfert de bitstreams)
    for (i = 1; i <= server.nb_total_paquets; i++) {
        receive_msg_from_client(&server, buffer_total_msg_received, buffer_received_msg, i, true);
        send_response_to_client(&server, ok_msg_to_send, i, true);
    }

    // Récupération du bitstream total réel (pour tester la validité de "buffer_total_msg_received")
    buffer_bitstream_total_reel = (char *) malloc((msg_size + 1) * sizeof(char));
    nb_received_characters = recv(server.client_socket, buffer_bitstream_total_reel, msg_size+1, 0);
    if (nb_received_characters <= 0) {
        printf("\n[SERVER] Erreur lors du recv() final\n");
        exit(EXIT_FAILURE);
    }

    shutdown_server(&server);
    close_server(&server);

    printf("\n--> Bitstream total recu par le serveur : \"%s\"\n", buffer_total_msg_received);

    // Comparaison finale (test de cohérence)
    printf("--> Le bitstream total recu est-il coherent ? ");
    code_retour_strcmp = strcmp(buffer_total_msg_received, buffer_bitstream_total_reel);
    if (code_retour_strcmp == 0)
        printf("TRUE\n");
    else
        printf("FALSE\n");

    // Pour éviter qu'il y ait des fuites de mémoire
    free(buffer_total_msg_received);
    free(buffer_bitstream_total_reel);

    /* ------------------------------------------------------------------------------ */

    #if defined(WIN32)
        WSACleanup();
    #endif

    return EXIT_SUCCESS;
}
