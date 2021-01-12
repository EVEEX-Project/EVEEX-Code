#include <stdlib.h>
#include <string.h>

#include "../types/Object.h"
#include "../types/Bitstream.r"
#include "../types/Bitstream.h"

int main() {
    int frameid = 5;
    enum MessageTypes type = HEADER_MSG;
    char msg[] = "Hello world !!!!";
    unsigned long size = strlen(msg);

    void *stream = new(Bitstream(), frameid, type, size, msg);

    puto(stream, stdout);

    delete(stream);

    exit(EXIT_SUCCESS);
}