#if defined(WIN32)
    #include <winsock2.h>
    typedef int socklen_t;
    #define SHUT_RDWR 2
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


#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#include "client.h"


void initialize_client(CLIENT* client, int port, char* ip_address, int bufsize) {
    /*
     * Permet d'initialiser la structure du client en question. Le programme se terminera
     * s'il y a une erreur lors de l'appel à la fonction "socket".
     *
     * Arguments
     * ---------
     * client     : Structure associée au client que l'on veut initialiser
     * port       : Port auquel le client va se rattacher
     * ip_address : Adresse IP (IPv4) associée au socket client
     * bufsize    : Taille maximale des paquets (utiles) envoyés par le client (/reçus par le serveur)
     *
     * Returns
     * -------
     * void
     */

    client->port = port;
    strcpy(client->ip_address, ip_address);
    client->bufsize = bufsize;

    client->client_sin_size = (socklen_t) sizeof(client->client_sin);
    client->client_socket = socket(AF_INET, SOCK_STREAM, 0);

    if (client->client_socket == INVALID_SOCKET) {
        printf("\n[CLIENT] Erreur lors de l'appel à la fonction socket()\n");
        exit(EXIT_FAILURE);
    }

    // Configuration du contexte d'adressage du client
    (client->client_sin).sin_addr.s_addr = inet_addr(ip_address);
    (client->client_sin).sin_family = AF_INET; // considération des adresses IPv4
    (client->client_sin).sin_port = htons(port);
}


void connect_to_server(CLIENT* client) {
    /*
     * Permet de connecter le client au serveur. Le programme se terminera s'il y a une
     * erreur lors de l'appel à la fonction "connect".
     *
     * Arguments
     * ---------
     * client : Structure associée au client en question
     *
     * Returns
     * -------
     * void
     */

    // Création de la connexion entre le serveur et le client
    int code_retour_connect = connect(client->client_socket, (SOCKADDR *) &(client->client_sin), client->client_sin_size);
    if (code_retour_connect == SOCKET_ERROR) {
        printf("\n[CLIENT] Impossible de se connecter au serveur");
        exit(EXIT_FAILURE);
    }

    printf("\n[CLIENT] Connexion a l'adresse IP \"%s\" sur le port %d", inet_ntoa((client->client_sin).sin_addr), htons((client->client_sin).sin_port));
}


void send_data_to_server(CLIENT* client, char* buffer_msg_to_send, int msg_number, bool est_un_bitstream) {
    /*
     * Permet d'envoyer un message du client au serveur. Le programme se terminera s'il
     * y a une erreur lors de l'appel à la fonction "send".
     *
     * Arguments
     * ---------
     * client             : Structure associée au client en question
     * buffer_msg_to_send : Message à envoyer au serveur
     * msg_number         : Numéro du message à envoyer, qui est normalement entre 1 et
     *                      client->nb_total_paquets. Si msg_number = -1, c'est que l'on
     *                      a affaire au message préliminaire à envoyer au serveur (mais on
     *                      le saura déjà car on aura alors est_un_bitstream = false)
     * est_un_bitstream   : Booléen indiquant si le message à envoyer est un paquet "officiel"/utile,
     *                      ce qui est ici équivalent à indiquer si le message à envoyer est un
     *                      bitstream (ou non)
     *
     * Returns
     * -------
     * void
     */

    int nb_sent_characters = send(client->client_socket, buffer_msg_to_send, client->bufsize, 0);

    if (nb_sent_characters > 0) {
        if (est_un_bitstream)
            printf("\n[CLIENT] Message numero %d/%d envoye (de taille <= %d) : \"%s\"", msg_number, client->nb_total_paquets, client->bufsize - 1, buffer_msg_to_send);
        else
            printf("\n[CLIENT] Message preliminaire envoye au serveur : msg_size = %d", atoi(buffer_msg_to_send));
    }

    else {
        if (est_un_bitstream)
            printf("\n[CLIENT] Erreur de transmission (message numero %d/%d)\n", msg_number, client->nb_total_paquets);
        else
            printf("\n[CLIENT] Erreur de transmission (message preliminaire)\n");
        exit(EXIT_FAILURE);
    }
}


void wait_for_response(CLIENT* client, char* buffer_received_msg, char* ok_msg_to_receive, int msg_number, bool est_un_bitstream) {
    /*
     * Permet de recevoir l'accusé de réception du serveur relatif au paquet qui vient
     * d'être envoyé. Le programme se terminera s'il y a une erreur lors de l'appel à la
     * fonction "recv".
     *
     * Arguments
     * ---------
     * client              : Structure associée au client en question
     * buffer_received_msg : Tampon qui contiendra le message reçu par le serveur (ie l'accusé
     *                       de réception)
     * ok_msg_to_receive   : Message qui est censé être reçu par le client (= le message "ok")
     * msg_number          : Numéro du message reçu, qui est normalement entre 1 et
     *                       client->nb_total_paquets. Si msg_number = -1, c'est que l'on
     *                       a affaire à l'accusé de réception du message préliminaire envoyé au
     *                       serveur (mais on le saura déjà car on aura alors est_un_bitstream = false)
     * est_un_bitstream    : Booléen indiquant si l'accusé de réception est associé à un paquet
     *                       "officiel"/utile, ce qui est ici équivalent à indiquer si l'accusé de
     *                       réception est associé à un bitstream (ou non)
     *
     * Returns
     * -------
     * void
     */

    int nb_received_characters = recv(client->client_socket, buffer_received_msg, 3, 0);

    if ((nb_received_characters > 0) && (strcmp(ok_msg_to_receive, buffer_received_msg) == 0))
        if (est_un_bitstream)
            printf("\n[CLIENT] Accuse de reception du message numero %d/%d recu correctement\n", msg_number, client->nb_total_paquets);
        else
            printf("\n[CLIENT] Accuse de reception du message preliminaire recu correctement\n");

    else {
        if (est_un_bitstream)
            printf("\n[CLIENT] L'accuse de reception du message numero %d/%d n'a pas été recu correctement\n", msg_number, client->nb_total_paquets);
        else
            printf("\n[CLIENT] L'accuse de reception du message preliminaire n'a pas été recu correctement\n");
        exit(EXIT_FAILURE);
    }
}


void shutdown_client(CLIENT* client) {
    /*
     * Permet d'empêcher la communication entre le client et le serveur, sans pour
     * autant détruire de sockets (la destruction de sockets sera faite via la
     * fonction "close_client"). Le programme se terminera s'il y a une erreur lors
     * de l'appel à la fonction "shutdown".
     *
     * Arguments
     * ---------
     * client : Structure associée au client en question
     *
     * Returns
     * -------
     * void
     */

    // NB : La fonction "shutdown" ne fonctionne qu'avec des sockets actives (= sockets clients)
    int code_retour_shutdown = shutdown(client->client_socket, SHUT_RDWR);
    if (code_retour_shutdown != 0) {
        printf("\n[CLIENT] Erreur lors du shutdown de la socket client\n");
        exit(EXIT_FAILURE);
    }

    printf("\n[CLIENT] Blocage de toute nouvelle communication avec le serveur");
}


void close_client(CLIENT* client) {
    /*
     * Permet de supprimer le socket du client (côté client).
     *
     * Arguments
     * ---------
     * client : Structure associée au client en question
     *
     * Returns
     * -------
     * void
     */

    int code_retour_closesocket = closesocket(client->client_socket);
    if (code_retour_closesocket != 0) {
        printf("\n[CLIENT] Erreur lors de la fermeture du socket client\n");
        exit(EXIT_FAILURE);
    }

    printf("\n\n--> Fermeture du socket client (*cote client*)\n");
}
