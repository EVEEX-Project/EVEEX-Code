#include <stdlib.h>
#include <stdio.h>
#include "dictionary.h"
#include "bitstream.h"

/*
 * Function : Bitstream_create
 * ---------------------------
 * Creates an instance of a Bitstream and returns the pointer to that instance.
 *
 *  returns: new instance of Bitstream
 */
Bitstream *Bitstream_create() {
    // Allocating the required space for the bitsteam
    Bitstream *stream = (Bitstream *) malloc(sizeof(Bitstream));

    // creating the encoding dictionary
    Dictionary **symbols = Dico_create();
    stream->symbols = symbols;
    // allocation of the space for the data
    stream->data = malloc(sizeof(char));

    return stream;
}

/*
 * Function : Bitstream_free
 * -------------------------
 * Free the memory allocated to a specific instance of a Bitstream.
 * Having such a function allow the program to not forget specific attributes to free.
 *
 *  bitstream: the Bitstream to free
 */
void Bitstream_free(Bitstream *bitstream) {
    // we have to think about each memory allocation
    Dico_free(bitstream->symbols);
    free(bitstream->data);
    free(bitstream);
}

/*
 * Function : Bitstream_encodeData
 * -------------------------------
 * Encodes a plaintext using the encoding dictionary inside the Bitstream and returns the encoded data.
 *
 *  bitstream: the bitstream helping to encode
 *  plaintext: the plain text to encode
 *
 *  returns: the encoded data corresponding to the plain text
 */
char *Bitstream_encodeData(Bitstream *bitstream, char *plaintext) {
    // creating a dynamic size string to store the data
    char *cipher_data = malloc(sizeof(char));
    cipher_data[0] = '\0'; // closing the string

    // going through the whole plaintext data
    for (int i = 0; i < strlen(plaintext); i++)
    {
        // building a string key from a char
        char key[2];
        key[0] = plaintext[i];
        key[1] = '\0';

        // getting back the value from the dictionary
        char *value = Dico_get(bitstream->symbols, key);
        // if the encoding key is found
        if (value != NULL)
        {
            // getting sizes for later usage
            unsigned long cipher_size = strlen(cipher_data),
                            buf_size = strlen(value),
                            data_size = cipher_size + buf_size;

            // changing the size of the data
            cipher_data = (char *) realloc(cipher_data, data_size + 1);
            // pasting the new value onto the data
            for (unsigned long j = 0; j < buf_size; j++) {
                cipher_data[j + cipher_size] = value[j];
            }
            // closing the data string
            cipher_data[data_size] = '\0';
        }
    }

    return cipher_data;
}

/*
 * Function: Bitstream_decodeData
 * ------------------------------
 * Decodes an encoded string using the encoding dictionary inside the Bitstream and returns the plain text data.
 *
 *  bitstream: the bitstream helping to decode
 *  cipherData: the encoded text to decode
 *
 *  returns: the decoded data corresponding to the ciphered text
 */
char *Bitstream_decodeData(Bitstream *bitstream, char *cipherData) {
    // first step is to get the reverse encoding dictionary
    Dictionary **reversedSymbols = Dico_create();
    Dico_getReversedDico(bitstream->symbols, reversedSymbols);

    // dynamic sized strings for the plaintext data and the buffer for the encoded data
    char *buffer = malloc(sizeof(char));
    buffer[0] = '\0';
    char *plaintext_data = malloc(sizeof(char));
    plaintext_data[0] = '\0'; // closing the string

    // going through the whole cipher data
    for (int i = 0; i < strlen(cipherData) - 1; i++) {
        // adding the next char to the buffer
        unsigned long buf_size = strlen(buffer);
        buffer = (char *) realloc(buffer, buf_size + 2);
        buffer[buf_size] = cipherData[i];
        buffer[buf_size + 1] = '\0';

        // getting back the value from the dictionary
        char *value = Dico_get(reversedSymbols, buffer);
        // if the encoding key is found
        if (value != NULL) {
            // getting different sizes for later usage
            unsigned long plain_size = strlen(plaintext_data);
            buf_size = strlen(value);
            unsigned long data_size = plain_size + buf_size;

            // changing the size of the plaintext data string
            plaintext_data = (char *) realloc(plaintext_data, data_size + 1);
            // pasting the new value
            for (unsigned long j = 0; j < buf_size; j++) {
                plaintext_data[j + plain_size] = value[j];
            }
            // closing the data string
            plaintext_data[data_size] = '\0';

            // we have to make a new buffer as the old one become useless
            free(buffer);
            buffer = (char *) malloc(sizeof(char));
            buffer[0] = '\0';
        }
    }
    // freeing the temporary variables
    Dico_free(reversedSymbols);
    free(buffer);

    return plaintext_data;
}