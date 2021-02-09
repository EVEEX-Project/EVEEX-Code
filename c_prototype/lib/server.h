#ifndef SERVER_H
#define SERVER_H

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

#include <stdbool.h>

/* Structure qui va contenir toutes les informations utiles au serveur créé */
typedef struct {
    int port;
    char ip_address[30];
    int bufsize;
    int nb_total_paquets;

    // Socket et contexte d'adressage du serveur
    SOCKET server_socket;
    SOCKADDR_IN server_sin;
    socklen_t server_sin_size;

    // Socket et contexte d'adressage du client (*côté serveur*)
    SOCKET client_socket;
    SOCKADDR_IN client_sin;
    socklen_t client_sin_size;
} SERVER;

extern void initialize_server(SERVER* server, int port, char* ip_address, int bufsize);
extern void listen_for_packets(SERVER* server);
extern void accept_client(SERVER* server);
extern void receive_msg_from_client(SERVER* server, char* buffer_total_msg_received, char* buffer_received_msg, int msg_number, bool est_un_bitstream);
extern void send_response_to_client(SERVER* server, char* ok_msg_to_send, int msg_number, bool est_un_bitstream);
extern void shutdown_server(SERVER* server);
extern void close_server(SERVER* server);

#endif /* SERVER_H */