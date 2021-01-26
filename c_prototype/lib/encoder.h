//
// Created by alexandre on 12/01/2021.
//

#ifndef C_PROTOTYPE_ENCODER_H
#define C_PROTOTYPE_ENCODER_H

#define PI 3.141592653589793
#define N 16

void DCT_N(int pixel[N][N], float Coeff_DCT[N][N])
{
    int u=0, v=0;
    int x=0, y=0;
    float au=0, av=0;

    for(v=0;v<=N-1;v++)
    {
        for(u=0;u<=N-1;u++)
        {
            //Calculate the double sum
            for(y=0;y<=N-1;y++)
            {
                for(x=0;x<=N-1;x++)
                {
                    Coeff_DCT[v][u]+=pixel[y][x]*(cos((PI*(x+0.5)*u)/N)*cos((PI*(y+0.5)*v)/N));
                }
            }

            //Calculate the orthogonality factors
            if(u==0){
                au=(1/sqrt(2));
            }
            else {
                au=1;
            }

            if(v==0){
                av=(1/sqrt(2));
            }
            else{
                av=1;
            }

            //Calculate the complete coefficients
            Coeff_DCT[v][u]=Coeff_DCT[v][u]*0.25*au*av;
        }
    }

}

void IDCT_N(float Coeff_DCT[N][N], int reconstructed_matrix[N][N])
{
    int u=0, v=0;
    int x=0, y=0;
    float au=0, av=0;
    //Intermediate matrix to work with real numbers
    float f[N][N]={0};

    for(y=0;y<=N-1;y++)
    {
        for(x=0;x<=N-1;x++)
        {
            for(v=0;v<=N-1;v++)
            {
                for(u=0;u<=N-1;u++)
                {
                    if(u==0){
                        au=1/sqrt(2);
                    }
                    else {
                        au=1;
                    }

                    if(v==0){
                        av=1/sqrt(2);
                    }
                    else{
                        av=1;
                    }
                    f[y][x]+=Coeff_DCT[v][u]*au*av*cos(((x+0.5)*PI*u)/N)*cos(((y+0.5)*PI*v)/N);
                }
            }
            f[y][x]*=0.25;
            //conversion of real integers
            reconstructed_matrix[y][x]=floor(f[y][x]+0.5);
        }
    }
}

const struct Image *toYUVImage(const void *self);
const struct List *splitInMacroblocs(const void *self, int size);

#endif //C_PROTOTYPE_ENCODER_H
