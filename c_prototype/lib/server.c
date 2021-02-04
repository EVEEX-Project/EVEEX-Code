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


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#include "server.h"


void initialize_server(SERVER* server, int port, char* ip_address, int bufsize) {
    /*
     * Permet d'initialiser la struture du serveur en question. Le programme se terminera
     * s'il y a une erreur lors de l'appel aux fonctions "socket" ou "bind".
     *
     * Arguments
     * ---------
     * server     : Structure associée au serveur que l'on veut initialiser
     * port       : Port auquel le serveur va se rattacher
     * ip_address : Adresse IP (IPv4) associée au socket serveur
     * bufsize    : Taille maximale des paquets (utiles) reçus par le serveur (/envoyés par le client)
     *
     * Returns
     * -------
     * void
     */

    int code_retour_bind;

    server->port = port;
    strcpy(server->ip_address, ip_address);
    server->bufsize = bufsize;

    server->server_sin_size = (socklen_t) sizeof(server->server_sin);
    server->client_sin_size = (socklen_t) sizeof(server->client_sin);

    // Création d'une socket (pour le serveur)
    // AF_INET --> considération des adresses IPv4
    // SOCK_STREAM --> protocole TCP/IP
    // 0 --> protocole par défaut (ie le protocole le plus adapté vis-à-vis des 2 paramètres précédents)
    server->server_socket = socket(AF_INET, SOCK_STREAM, 0);

    if (server->server_socket != INVALID_SOCKET) {
        printf("\n[SERVER] Le socket %d est maintenant ouvert en mode TCP/IP", (int) server->server_socket);

        // Configuration du contexte d'adressage du serveur
        (server->server_sin).sin_addr.s_addr = inet_addr(server->ip_address);
        (server->server_sin).sin_family = AF_INET;
        (server->server_sin).sin_port = htons(server->port);

        // On lie ici la socket du serveur avec sa structure SOCKADDR
        code_retour_bind = bind(server->server_socket, (SOCKADDR *) &(server->server_sin), server->server_sin_size);

        if (code_retour_bind == SOCKET_ERROR) {
            printf("\n[SERVER] Erreur lors de l'appel à la fonction bind()\n");
            exit(EXIT_FAILURE);
        }
    }

    else {
        printf("\n[SERVER] Erreur lors de l'appel à la fonction socket()\n");
        exit(EXIT_FAILURE);
    }
}


void listen_for_packets(SERVER* server) {
    /*
     * Permet au serveur de se mettre en mode écoute. Le programme se terminera s'il
     * y a une erreur lors de l'appel à la fonction "listen".
     *
     * Arguments
     * ---------
     * server : Structure associée au serveur en question
     *
     * Returns
     * -------
     * void
     */

    // Démarrage du listage
    int code_retour_listen = listen(server->server_socket, 5);
    if (code_retour_listen == SOCKET_ERROR) {
        printf("\n[SERVER] Erreur lors de l'appel à la fonction listen()\n");
        exit(EXIT_FAILURE);
    }

    printf("\n[SERVER] Listage du port %d ...", server->port);
}


void accept_client(SERVER* server) {
    /*
     * Permet au serveur de démarrer la communication avec un client. Le programme
     * se terminera s'il y a une erreur lors de l'appel à la fonction "accept".
     *
     * Arguments
     * ---------
     * server : Structure associée au serveur en question
     *
     * Returns
     * -------
     * void
     */

    // On attend que le client se connecte
    printf("\n[SERVER] Patientez pendant que le client se connecte sur le port %d ...", server->port);
    server->client_socket = accept(server->server_socket, (SOCKADDR *) &(server->client_sin), &(server->client_sin_size));

    if (server->client_socket == INVALID_SOCKET) {
        printf("\n[SERVER] Erreur lors de l'appel à la fonction accept()\n");
        exit(EXIT_FAILURE);
    }

    printf("\n[SERVER] Un client vient de se connecter avec la socket %d de l'adresse IP \"%s\"\n", server->client_socket, inet_ntoa(server->client_sin.sin_addr));
}


void receive_msg_from_client(SERVER* server, char* buffer_total_msg_received, char* buffer_received_msg, int msg_number, bool est_un_bitstream) {
    /*
     * Permet de recevoir les informations envoyées par le client (pour un seul paquet).
     * De plus, si la variable "est_un_bitstream" vaut "true", les données reçues seront
     * "append"/concaténées à "buffer_total_msg_received".
     * Le programme se terminera s'il y a une erreur lors de l'appel à la fonction "recv".
     *
     * Arguments
     * ---------
     * server                    : Structure associée au serveur en question
     * buffer_total_msg_received : Message total reçu par le serveur (au moment de l'appel à la
     *                             fonction "receive_msg_from_client")
     * buffer_received_msg       : Tampon qui contiendra le message reçu par le client
     * msg_number                : Numéro du message envoyé par le client, qui est normalement
     *                             entre 1 et server->nb_total_paquets. Si msg_number = -1, c'est
     *                             que l'on a affaire au message préliminaire du client (mais on le
     *                             saura déjà car on aura alors est_un_bitstream = false)
     * est_un_bitstream          : Booléen indiquant si le message reçu est un paquet "officiel"/utile,
     *                             ce qui est ici équivalent à indiquer si le message reçu est un
     *                             bitstream ou non
     *
     * Returns
     * -------
     * void
     */

    int nb_received_characters = recv(server->client_socket, buffer_received_msg, server->bufsize, 0);

    if (nb_received_characters > 0) {
        if (est_un_bitstream) {
            printf("\n[SERVER] Message numero %d/%d recu : \"%s\"", msg_number, server->nb_total_paquets, buffer_received_msg);
            strcat(buffer_total_msg_received, buffer_received_msg);
        }
        else
            printf("\n[SERVER] Message preliminaire recu de la part du client : msg_size = %d", atoi(buffer_received_msg));
    }

    else {
        if (est_un_bitstream)
            printf("\n[SERVER] Message numero %d/%d recu corrompu\n", msg_number, server->nb_total_paquets);
        else
            printf("\n[SERVER] Message preliminaire recu corrompu\n");
        exit(EXIT_FAILURE);
    }
}


void send_response_to_client(SERVER* server, char* ok_msg_to_send, int msg_number, bool est_un_bitstream) {
    /*
     * Permet d'envoyer l'accusé de réception (du paquet venant d'être reçu) au client. Le programme
     * se terminera s'il y a une erreur lors de l'appel à la fonction "send".
     *
     * Arguments
     * ---------
     * server           : Structure associée au serveur en question
     * ok_msg_to_send   : Message (/accusé de réception) envoyé au client (= le message "ok")
     * msg_number       : Numéro du message envoyé par le client (dont on fait l'accusé de réception),
     *                    qui est normalement entre 1 et server->nb_total_paquets. Si msg_number = -1,
     *                    c'est que l'on a affaire au message préliminaire du client (mais on le saura
     *                    déjà car on aura alors est_un_bitstream = false)
     * est_un_bitstream : Booléen indiquant si l'on renvoie l'accusé de réception associé à un paquet
     *                    "officiel"/utile, ce qui est ici équivalent à indiquer si le message
     *                    reçu (dont on fait l'accusé de réception) est un bitstream (ou non)
     *
     * Returns
     * -------
     * void
     */

    int nb_sent_characters = send(server->client_socket, ok_msg_to_send, 3, 0);

    if (nb_sent_characters > 0) {
        if (est_un_bitstream)
            printf("\n[SERVER] Envoi de l'accuse de reception du message numero %d/%d\n", msg_number, server->nb_total_paquets);
        else
            printf("\n[SERVER] Envoi de l'accuse de reception du message preliminaire\n");
    }

    else {
        if (est_un_bitstream)
            printf("\n[SERVER] Echec de l'envoi de l'accuse de reception du message numero %d/%d\n", msg_number, server->nb_total_paquets);
        else
            printf("\n[SERVER] Echec de l'envoi de l'accuse de reception du message preliminaire\n");
        exit(EXIT_FAILURE);
    }
}


void shutdown_server(SERVER* server) {
    /*
     * Permet d'empêcher la communication entre le serveur et le client, sans pour
     * autant détruire de sockets (la destruction de sockets sera faite via la
     * fonction "close_server"). Le programme se terminera s'il y a une erreur lors
     * de l'appel à la fonction "shutdown".
     *
     * Arguments
     * ---------
     * server : Structure associée au serveur en question
     *
     * Returns
     * -------
     * void
     */

    // NB : La fonction "shutdown" ne fonctionne qu'avec des sockets actives (= sockets clients)
    int code_retour_shutdown = shutdown(server->client_socket, SHUT_RDWR);
    if (code_retour_shutdown != 0) {
        printf("\n[SERVER] Erreur lors du shutdown de la socket client\n");
        exit(EXIT_FAILURE);
    }

    printf("\n[SERVER] Blocage de toute nouvelle communication avec le client");
}


void close_server(SERVER* server) {
    /*
     * Permet de supprimer les sockets du client (côté serveur) et du serveur.
     *
     * Arguments
     * ---------
     * server : Structure associée au serveur en question
     *
     * Returns
     * -------
     * void
     */

    int code_retour_closesocket_client = closesocket(server->client_socket);
    if (code_retour_closesocket_client != 0) {
        printf("\n[SERVER] Erreur lors de la fermeture du socket client\n");
        exit(EXIT_FAILURE);
    }
    printf("\n--> Fermeture du socket client (*cote serveur*)");

    int code_retour_closesocket_serveur = closesocket(server->server_socket);
    if (code_retour_closesocket_serveur != 0) {
        printf("\n[SERVER] Erreur lors de la fermeture du socket serveur\n");
        exit(EXIT_FAILURE);
    }
    printf("\n--> Fermeture du socket serveur");

    printf("\n--> Fermeture des sockets terminee\n");
}
