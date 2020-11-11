//
// Created by alexandre on 11/11/2020.
//

#ifndef C_PROTOTYPE_BITSTREAM_H
#define C_PROTOTYPE_BITSTREAM_H

#include "dictionary.h"

typedef struct Bitstream_struct {
  int size;
  void *data;
} Bitstream;

Bitstream *Bitstream_create();
void Bitstream_free(Bitstream *bitstream);
void Bitstream_encodeData(Dictionary **encodingDict, char *plaintext);
void Bitstream_decodeData(Dictionary **decodingDict, char *cipherData);

#endif //C_PROTOTYPE_BITSTREAM_H