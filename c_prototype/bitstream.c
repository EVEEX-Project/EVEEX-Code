//
// Created by alexandre on 11/11/2020.
//

#include <stdlib.h>
#include <stdio.h>
#include "dictionary.h"
#include "bitstream.h"

Bitstream *Bitstream_create() {
    Bitstream *stream = (Bitstream *) malloc(sizeof(Bitstream));

    Dictionary **symbols = Dico_create();
    stream->symbols = symbols;
    stream->data = malloc(sizeof(char));

    return stream;
}

void Bitstream_free(Bitstream *bitstream) {
    free(bitstream->data);
    Dico_free(bitstream->symbols);
    free(bitstream);
}

char *Bitstream_encodeData(Bitstream *bitstream, char *plaintext) {
    char *cipher_data = malloc(sizeof(char));
    cipher_data[0] = '\0'; // closing the string

    // going through the whole plaintext data
    for (int i = 0; i < strlen(plaintext); i++)
    {
        char key[2];
        key[0] = plaintext[i];
        key[1] = '\0';

        char *value = Dico_get(bitstream->symbols, key);
        // if the encoding key is found
        if (value != NULL)
        {
            unsigned long cipher_size = strlen(cipher_data);
            unsigned long buf_size = strlen(value);
            unsigned long data_size = cipher_size + buf_size;

            cipher_data = (char *) realloc(cipher_data, data_size + 1);
            for (unsigned long j = 0; j < buf_size; j++) {
                cipher_data[j + cipher_size] = value[j];
            }
            cipher_data[data_size] = '\0';
            //printf("Bitstream : %s Cipher_data_size : %d Data_size : %d\n", cipher_data, cipher_size, data_size);
        }
    }

    return cipher_data;
}

char *Bitstream_decodeData(Bitstream *bitstream, char *cipherData) {
    Dictionary **reversedSymbols = Dico_create();
    Dico_getReversedDico(bitstream->symbols, reversedSymbols);

    char *buffer = malloc(sizeof(char));
    buffer[0] = '\0';
    char *plaintext_data = malloc(sizeof(char));
    plaintext_data[0] = '\0'; // closing the string

    // going through the whole cipher data
    for (int i = 0; i < strlen(cipherData) - 1; i++) {
        unsigned long buf_size = strlen(buffer);
        buffer = (char *) realloc(buffer, buf_size + 2);
        buffer[buf_size] = cipherData[i];
        buffer[buf_size + 1] = '\0';

        char *value = Dico_get(reversedSymbols, buffer);
        // if the encoding key is found
        if (value != NULL) {
            unsigned long plain_size = strlen(plaintext_data);
            buf_size = strlen(value);
            unsigned long data_size = plain_size + buf_size;

            plaintext_data = (char *) realloc(plaintext_data, data_size + 1);
            for (unsigned long j = 0; j < buf_size; j++) {
                plaintext_data[j + plain_size] = value[j];
            }
            plaintext_data[data_size] = '\0';
            //printf("PlainText : %s Plain_data_size : %d Data_size : %d\n", plaintext_data, plain_size, data_size);

            free(buffer);
            buffer = (char *) malloc(sizeof(char));
            buffer[0] = '\0';
        }
    }

    return plaintext_data;
}