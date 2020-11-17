/*
 * Data-type: BITSTREAM
 * --------------------
 * Lybrary that describes a Bitstream by its encoding dictionnary called
 * here "symbols" and its data
 */

#ifndef C_PROTOTYPE_BITSTREAM_H
#define C_PROTOTYPE_BITSTREAM_H

#include "dictionary.h"

typedef struct Bitstream_struct {
  Dictionary **symbols;
  void *data;
} Bitstream;

Bitstream *Bitstream_create();
void Bitstream_free(Bitstream *bitstream);
char *Bitstream_encodeData(Bitstream *bitstream, char *plaintext);
char *Bitstream_decodeData(Bitstream *bitstream, char *cipherData);

#endif //C_PROTOTYPE_BITSTREAM_H