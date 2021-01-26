int main(int argc, char const *argv[])
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
}