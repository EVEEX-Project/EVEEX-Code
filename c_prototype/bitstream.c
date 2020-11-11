//
// Created by alexandre on 11/11/2020.
//

#include <stdlib.h>
#include "bitstream.h"

Bitstream *Bitstream_create() {
    return (Bitstream *) malloc(sizeof(Bitstream));
}

void Bitstream_free(Bitstream *bitstream) {
    free(bitstream->data);
    free(bitstream);
}