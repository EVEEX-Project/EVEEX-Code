#ifndef CLIENT_H
#define CLIENT_H

#if defined(WIN32)
    #include <winsock2.h>
    typedef int socklen_t;
#elif defined(__linux__)
    #include <sys/types.h>
    #include <sys/socket.h>

    typedef int SOCKET;
    typedef struct sockaddr_in SOCKADDR_IN;
#else
    #error not defined for this platform
#endif

#include <stdbool.h>

/* Structure qui va contenir toutes les informations utiles au client créé */
typedef struct {
    int port;
    char ip_address[30];
    int bufsize;
    int nb_total_paquets;

    // Socket et contexte d'adressage du client (*côté client*)
    SOCKET client_socket;
    SOCKADDR_IN client_sin;
    socklen_t client_sin_size;
} CLIENT;

extern void initialize_client(CLIENT* client, int port, char* ip_address, int bufsize);
extern void connect_to_server(CLIENT* client);
extern void send_data_to_server(CLIENT* client, char* buffer_msg_to_send, int msg_number, bool est_un_bitstream);
extern void wait_for_response(CLIENT* client, char* buffer_received_msg, char* ok_msg_to_receive, int msg_number, bool est_un_bitstream);
extern void shutdown_client(CLIENT* client);
extern void close_client(CLIENT* client);

#endif /* CLIENT_H */