//
// Created by alexandre on 12/01/2021.
//

#include <stdlib.h>
#include <assert.h>
#include <stdio.h>
#include <math.h>
#include "encoder.h"
#include "huffman.h"
#include "../types/Image.h"
#include "../types/Image.r"




#define N 16
#define PI 3.141592653589793





const struct Image *toYUVImage(const void *_self) {
    const struct Image *self = cast(Image(), _self);

    struct Image *yuv = new(Image(), self->width, self->height, self->channels, 1);

    for (uint8_t *p = self->data, *yp = yuv->data; p != self->data + self->size; p += self->channels, yp += yuv->channels) {
        uint8_t red = *p, green = *(p+1), blue = *(p+2);
        uint8_t y = 0.299 * red + 0.587 * green + 0.114 * blue;
        uint8_t u = -0.147 * red + -0.289 * green + 0.436 * blue;
        uint8_t v = 0.615 * red + -0.515 * green + -0.100 * blue;

        *yp = y, *(yp+1) = u, *(yp+2) = v;

        // if there is transparency
        if (self->channels == 4) {
            *(yp+3) = *(p+3);
        }
    }

    return yuv;
}

const struct List *splitInMacroblocs(const void *_self, int size) {
    const struct Image *self = cast(Image(), _self);

    // check for a valid image
    if(self->allocationType == NO_ALLOCATION || self->channels < 3) {
        perror("The input image must have at least 3 channels.");
        exit(EXIT_FAILURE);
    }

    // Checking if picture size if compatible
    assert(self->width % size == 0);
    assert(self->height % size == 0);

    // number of blocks
    long widthMB = self->width / size;
    long heightMB = self->height / size;

    // Populating the macroblocs list
    struct List* macroblocs = new(List(), widthMB * heightMB);
    for (int k = 0; k < widthMB * heightMB ; k++) {
        struct Image *block = new(Image(), size, size, self->channels, 1);
        addLast(macroblocs, (void *) block);
        //puto(block, stdout);
    }
    printf("Created %u blocks\n", count(macroblocs));

    // Iterating over the pixels
    struct Image *mBlock;
    for (uint8_t *p = self->data; p != self->data + self->size; p += self->channels) {
        unsigned idx = (p - self->data) / self->channels;
        unsigned line = idx / self->width;
        unsigned col = idx - (line * self->width);
        unsigned blockId = col / size + (line / size) * widthMB;

        // switching to the correct macroblock
        if (col % size == 0) {
            mBlock = cast(Image(), lookAt(macroblocs, blockId));
        }


        // getting coordinates on the macrobloc
        unsigned mbLine = line - (blockId / widthMB) * size;
        unsigned mbCol = col - (blockId % widthMB) * size;
        unsigned mbIdx = mbLine * size + mbCol;

        uint8_t *c_p = mBlock->data + (mbIdx * self->channels);
        *(c_p) = *p;
        *(c_p + 1) = *(p+1);
        *(c_p + 2) = *(p+2);
        // if there was transparency
        if(self->channels == 4) {
            // update the transparency pixel
            *(c_p + 3) = *(p+3);
        }
    }

    return macroblocs;
}







void DCT_N(int pixel[N][N], float Coeff_DCT[N][N]);
void IDCT_N(float C[N][N], int reconstructed_matrix[N][N]);

/*int main(int argc, char const *argv[])
{
    int i=0,j=0,k=0;

    float coeff_DCT[N][N]={0};//matrix to put the coefficients of DCT
    int reconstructed_matrix[N][N]={0}; //Matrix to put the reconstructed matix
    //Matrix representing the signal
    int matrix[N][N]={{244,243,118,154,126,246,137,184,244,243,118,154,126,246,137,184},
                      {178,127,196,155,184,184,147,245,244,243,118,154,126,246,137,184},
                      {114,116,134,231,145,166,214,112,244,243,118,154,126,246,137,184},
                      {178,127,196,155,184,184,247,245,244,243,118,154,126,246,137,184},
                      {200,224,133,145,105,167,237,118,244,243,118,154,126,246,137,184},
                      {137,263,118,154,126,246,137,89,244,243,118,154,126,246,137,184},
                      {178,127,196,255,184,184,147,245,244,243,118,154,126,246,137,184},
                      {114,116,134,231,145,166,247,198,244,243,118,154,126,246,137,184},
                      {244,243,118,154,126,246,137,184,244,243,118,154,126,246,137,184},
                      {178,127,196,155,184,184,147,245,244,243,118,154,126,246,137,184},
                      {114,116,134,231,145,166,214,112,244,243,118,154,126,246,137,184},
                      {178,127,196,155,184,184,247,245,244,243,118,154,126,246,137,184},
                      {200,224,133,145,105,167,237,118,244,243,118,154,126,246,137,184},
                      {137,263,118,154,126,246,137,89,244,243,118,154,126,246,137,184},
                      {178,127,196,255,184,184,147,245,244,243,118,154,126,246,137,184},
                      {114,116,134,231,145,166,247,198,244,243,118,154,126,246,137,184}};

    //Calculate the origin matrix of DCT
    //Put the coefficients in coeff_DCT
    DCT_N(matrix, coeff_DCT);

    //Calculate the IDCT using the Coefficients matrix
    //Put the regenerated signal in the reconstructed matrix
    IDCT_N(coeff_DCT, reconstructed_matrix);


    //printing the different steps
    for(k=0;k<4;k++)
    {
        if(k==0)puts("\nOrigin Matrix :");
        if(k==1)puts("\nCoefficients Matrix :");
        if(k==2)puts("\nReconstructed Matrix :");
        if(k==3)puts("\nDifference Origin/Reconstructed:");

        for(i=0;i<N;i++)
        {
            for(j=0;j<N;j++)
            {
                if(k==0)printf("%d ",matrix[i][j]);
                if(k==1)printf("%5.1f ",coeff_DCT[i][j]);
                if(k==2)printf("%d ",reconstructed_matrix[i][j]);
                if(k==3)printf("%d ",matrix[i][j]-reconstructed_matrix[i][j]);
            }
            printf("\n");
        }
    }
    return 0;
}*/