//
// Created by alexandre on 12/01/2021.
//

#include <math.h>

#include "../lib/decoder.h"

void IDCT(float Coeff_DCT[N][N], int reconstructed_matrix[N][N])
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
                    f[y][x]+=Coeff_DCT[v][u]*au*av*cos(((x+0.5)*M_PI*u)/N)*cos(((y+0.5)*M_PI*v)/N);
                }
            }
            f[y][x]*=0.25;
            //conversion of real integers
            reconstructed_matrix[y][x]=floor(f[y][x]+0.5);
        }
    }
}