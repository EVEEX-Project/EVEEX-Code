# -*- coding: utf-8 -*-

"""
N = image_height = image_width (image carrée / macrobloc carré), N >= 2
N est typiquement de la taille d'un macrobloc, donc idéalement il faudrait 
éviter d'avoir N > 10 (par exemple)

DTT = Discrete Tchebychev Transform
iDTT = integer DTT
SERM = Single-row Elementary Reversible Matrix

Sources :
1) sciencedirect.com/science/article/abs/pii/S0925231216306907
2) researchgate.net/publication/3318095_Matrix_factorizations_for_reversible_integer_mapping

En gros : 
Article 1 (pages 2/7 et 3/7) : Implémentation de la DTT et de la iDTT (+ leur inverse)
Article 2 (pages 5/12 et 6/12) : Décomposition de l'opérateur A (pour la DTT) en SERMs
"""

import numpy as np

##############################################################################
#############################  DTT & DTT inverse #############################
##############################################################################


# fonctions auxiliaires


"""
ATTENTION AUX FORMULES DONNÉES DANS L'ARTICLE 1 (page 2/7)

Il y a (au moins) 2 erreurs d'étourderie :

1) Dans l'expression de t_tilde(n, x) en fonction de t_tilde(n-1, x) et de 
   t_tilde(n-2, x), il n'y a PAS de 'n' au dénominateur. La bonne expression
   est :
   t_tilde(n, x) = (a1 * x + a2) * t_tilde(n-1, x) + a3 * t_tilde(n-2, x)

2) Dans l'expression de t_tilde(1, x), il n'y a PAS de 'N' au dénominateur. La 
   bonne expression est :
   t_tilde(1, x) = (2 * x + 1 - N) * sqrt(3 / (N * (N**2 - 1)))
"""


# n : entier >= 0, N : entier >= 2 et > n
def a1(n, N):
    return((2 / n) * np.sqrt((4 * n**2 - 1) / (N**2 - n**2)))


# n : entier >= 0, N : entier >= 2 et > n
def a2(n, N):
    return(((1 - N) / n) * np.sqrt((4 * n**2 - 1) / (N**2 - n**2)))


# n : entier >= 0, N : entier >= 2 et > n
def a3(n, N):
    return(((1 - n) / n) * np.sqrt((2 * n + 1) / (2 * n - 3)) * np.sqrt((N**2 - (n - 1)**2) / (N**2 - n**2)))


# n : entier >= 0, x : entier >= 0, N : entier >= 2 et > n
# algo récursif
def t_tilde(n, x, N):
    if n == 0:
        return(1 / np.sqrt(N))
    
    if n == 1:
        return((2 * x + 1 - N) * np.sqrt(3 / (N * (N**2 - 1))))
    
    return((a1(n, N) * x + a2(n, N)) * t_tilde(n-1, x, N) + a3(n, N) * t_tilde(n-2, x, N))


# génère l'opérateur de la DTT (ie la matrice A de l'article n°1)
# la matrice A est orthogonale, ie np.linalg.inv(A) = A.T
def DTT_operator(N):
    A = np.zeros((N, N))
    
    for i in range(N):
        for j in range(N):
            A[i, j] = t_tilde(i, j, N)
    
    return(A)


#----------------------------------------------------------------------------#


# DTT

# yuv_data.shape = (N, N, 3)
# A : opérateur orthogonal de la DTT
# on aurait pu générer A directement dans la fonction, mais comme A est
# amenée à être réutilisée, autant la mettre en argument
def apply_DTT(A, yuv_data):
    dtt_data = np.zeros(yuv_data.shape)
    
    for k in range(3):
        dtt_data[:, :, k] = A @ yuv_data[:, :, k] @ A.T
    
    return(dtt_data)


#----------------------------------------------------------------------------#


# DTT inverse

# dtt_data.shape = (N, N, 3)
# A : opérateur orthogonal de la DTT
def decode_DTT(A, dtt_data):
    yuv_data = np.zeros(dtt_data.shape)
    
    for k in range(3):
        yuv_data[:, :, k] = A.T @ dtt_data[:, :, k] @ A
    
    return(yuv_data)


#----------------------------------------------------------------------------#


# vérifie si les fonctions "apply_DTT" et "decode_DTT" sont précises
def check_DTT_functions(N):
    A = DTT_operator(N)
    
    # ici on vérifie si on a bien DTT(DTT_inverse(tab)) = tab
    dtt_data = np.random.uniform(0, 255, size=(N, N, 3))
    test1 = apply_DTT(A, decode_DTT(A, dtt_data))
    epsilon1 = np.linalg.norm(test1 - dtt_data)
    
    # ici on vérifie si on a bien DTT_inverse(DTT(tab)) = tab
    yuv_data = np.random.uniform(0, 255, size=(N, N, 3))
    test2 = decode_DTT(A, apply_DTT(A, yuv_data))
    epsilon2 = np.linalg.norm(test2 - yuv_data)
    
    print(f"\nTest de précision (DTT & DTT inverse) : {epsilon1}, {epsilon2}")


##############################################################################
############################  iDTT & iDTT inverse ############################
##############################################################################


# fonctions auxiliaires


# L : matrice triangulaire inférieure avec que des '1' sur la diagonale
# U : matrice triangulaire supérieure avec que des '1' sur la diagonale
# len(liste_S_m) = N + 1, liste_S_m : [S_0, S_1, ..., S_N]
# pour tout m dans [0, N], S_m.shape = (N, N)
def generer_liste_S_m(S_0, L, U):
    N = L.shape[0]
    liste_S_m = [S_0]
    
    M_ref = L @ U
    for m in range(1, N):
        S_m = np.eye(N)
        S_m[m-1, :] = M_ref[m-1, :]
        
        liste_S_m.append(S_m)
        M_ref = M_ref @ np.linalg.inv(S_m)
    
    # on rajoute le dernier terme
    S_N = np.copy(M_ref)
    liste_S_m.append(S_N)
    
    return(liste_S_m)


# S_m.shape = (N, N), m : entier, 0 <= m <= N
# on sait que S_m est de la forme I + e_m @ s_m.T, et l'objectif est de retrouver
# s_m à partir de S_m
def extraire_s_m(S_m, m):
    N = S_m.shape[0]
    I = np.eye(N)
    
    if m == 0:
        e_m = I[N-1, :]
    else:
        e_m = I[m-1, :]
    
    s_m = (S_m.T - I) @ e_m
    
    return(s_m)


# len(liste_S_m) = N + 1
# liste_S_m = [S_0, S_1, ..., _S_N]
# pour tout m dans [0, N], S_m.shape = (N, N)
def generer_matrice_S(liste_S_m):
    N = len(liste_S_m) - 1
    S = np.zeros((N+1, N))
    
    for m in range(0, N+1):
        S_m = liste_S_m[m]
        s_m = extraire_s_m(S_m, m)
        S[m, :] = s_m
    
    return(S)


# détermine l'indice de ligne d'un coeff non-nul de la colonne N de A_modifie 
# (disons i_ref), et renvoie une matrice de permutation qui échange les lignes
# k et i_ref
# on suppose ici que A_modifie[k-1, N-1] = 0, donc on sait que i_ref != k
# k : entier, 1 <= k <= N, A_modifie.shape = (N, N)
def genere_P_k(k, A_modifie):
    N = A_modifie.shape[0]
    P_k = np.eye(N)
    
    i_ref = -1
    for i in range(1, N+1):
        if (i != k) and (A_modifie[i-1, N-1] != 0):
            i_ref = i
            break
    
    P_k[k-1, k-1] = 0
    P_k[i_ref-1, i_ref-1] = 0
    
    P_k[k-1, i_ref-1] = 1
    P_k[i_ref-1, k-1] = 1
    
    return(P_k)


# permet de générer une matrice de Gauss, qui, une fois multipliée à A_modifie
# par la **gauche**, met à 0 tous les coefficients sous la diagonale, dans la
# colonne k de A_modifie
# k : entier, 1 <= k <= N, A_modifie.shape = (N, N)
def genere_L_k(k, A_modifie):
    N = A_modifie.shape[0]
    L_k = np.eye(N)
    
    for i in range(k+1, N+1):
        L_k[i-1, k-1] = -A_modifie[i-1, k-1]
    
    return(L_k)


#----------------------------------------------------------------------------#


# A : matrice à décomposer en P * S_N * ... * S_1 * S_0
# A.shape = (N, N), P.shape = (N, N), S.shape = (N+1, N)
# génération d'une décomposition de A en SERMs
def generer_decomp(A):
    """
    ATTENTION : Il n'y a pas qu'une seule décomposition en SERMs possible !
    
    En effet, selon la manière dont on choisit l'indice i_ref dans la fonction
    genere_P_k, on aura des S_m (et donc des s_m) différents.
    
    Ici il est donc normal de trouver une décomposition différente de l'article
    n°1 pour N = 8. Cependant, la décomposition obtenue est correcte (utiliser
    la fonction check_decomp pour s'en convaincre).
    """
    
    # matrice à décomposer
    N = A.shape[0]
    
    P = np.eye(N).astype(dtype=int)
    M = np.eye(N)
    S_0 = np.eye(N)
    
    
    A_modifie = np.copy(A)
    
    # ici, on met à jour itérativement P, M, et S_0 (et A_modifie)
    for k in range(1, N):
        # étape 1 : détermination de P_k et mise à jour de P (et de A_modifie)
        
        p_k_N = A_modifie[k-1, N-1]
        
        # si p_k_N != 0, il n'y a rien à faire dans cette étape, car P_k = np.eye(N),
        # donc P et A_modifie sont inchangés
        if p_k_N == 0:
            P_k_is_identity = False
            
            P_k = genere_P_k(k, A_modifie)
            A_modifie = P_k @ A_modifie
            p_k_N = A_modifie[k-1, N-1]
            
            int_P_k = P_k.astype(dtype=int)
            P = P @ int_P_k.T
        else:
            P_k_is_identity = True
        
        # étape 2 : détermination de S_0_k et mise à jour de S_0 (et de A_modifie)
        
        s_k = (A_modifie[k-1, k-1] - 1) / p_k_N
        
        # si s_k = 0, S_0_k = np.eye(N), et donc il ne se passe rien, ie S_0
        # et A_modifie sont inchangés
        if s_k != 0:
            S_0_k = np.eye(N)
            S_0_k[N-1, k-1] = -s_k
            A_modifie = A_modifie @ S_0_k
            
            S_0 = np.linalg.inv(S_0_k) @ S_0
        
        # étape 3 : détermination de L_k et mise à jour de M (et de A_modifie)
        
        L_k = genere_L_k(k, A_modifie)
        A_modifie = L_k @ A_modifie
        
        if P_k_is_identity:
            # dans ce cas précis, P_k = np.eye(N)
            M = L_k @ M
        else:
            M = (L_k @ P_k) @ M
    
    
    L = P.T @ np.linalg.inv(M)
    U = np.copy(A_modifie)
    
    liste_S_m = generer_liste_S_m(S_0, L, U)
    S = generer_matrice_S(liste_S_m)
    
    return(P, S)


#----------------------------------------------------------------------------#


# S.shape = (N+1, N), I = np.eye(N)
def extract_S_m(S, m, I):
    N = S.shape[1]
    s_m = S[m, :].reshape((N, 1))
    
    if m == 0:
        e_m = I[N-1, :].reshape((N, 1))
    else:
        e_m = I[m-1, :].reshape((N, 1))
    
    S_m = I + e_m @ s_m.T
    
    return(S_m)


# P.shape = (N, N), S.shape = (N+1, N), A_ref.shape = (N, N) = A_check.shape
# on veut vérifier que A = P * S_N * ... * S_0
# /!\ S : matrice des s_i (et NON des S_i) /!\
def check_decomp(A, P, S):
    N = P.shape[0]
    A_check = np.copy(P).astype(dtype=float)
    I = np.eye(N)
    
    # on va de m = N (inclus) à m = 0 (inclus), dans l'ordre **décroissant**
    for m in range(N, -1, -1):
        S_m = extract_S_m(S, m, I)
        A_check = A_check @ S_m
    
    precision_decomp = np.linalg.norm(A - A_check)
    
    return(precision_decomp)


# permet d'arrondir chacune des composantes de M à l'entier le plus proche
# M est une matrice **réelle** de taille quelconque
def round_matrix(M):
    return(np.round(M, 0).astype(dtype=int))


#----------------------------------------------------------------------------#


# iDTT forward "intermédiaire"

# int_yuv_data.shape = (N, 1), (N,) ou (N, N)
def apply_forward_iDTT(P, S, int_yuv_data):
    N = P.shape[0]
    I = np.eye(N)
    
    # initialisation
    S_0 = extract_S_m(S, 0, I)
    int_dtt_data = round_matrix(S_0 @ int_yuv_data)
    
    for m in range(1, N+1):
        S_m = extract_S_m(S, m, I)
        int_dtt_data = round_matrix(S_m @ int_dtt_data)
    
    int_dtt_data = P @ int_dtt_data
    
    return(int_dtt_data)


#----------------------------------------------------------------------------#


# iDTT inverse "intermédiaire"

# int_dtt_data.shape = (N, 1), (N,) ou (N, N)
def decode_forward_iDTT(P, S, int_dtt_data):
    N = P.shape[0]
    I = np.eye(N)
    
    # initialisation
    S_N = extract_S_m(S, N, I)
    int_yuv_data = round_matrix(np.linalg.inv(S_N) @ P.T @ int_dtt_data)
    
    for m in range(N-1, -1, -1):
        S_m = extract_S_m(S, m, I)
        int_yuv_data = round_matrix(np.linalg.inv(S_m) @ int_yuv_data)
    
    return(int_yuv_data)


#----------------------------------------------------------------------------#


# iDTT bidimensionnelle

# int_yuv_2D_data.shape = (N, N)
def apply_2D_iDTT(P, S, int_yuv_2D_data):
    res_intermediaire = apply_forward_iDTT(P, S, int_yuv_2D_data)
    int_dtt_2D_data = apply_forward_iDTT(P, S, res_intermediaire.T)
    
    return(int_dtt_2D_data)


#----------------------------------------------------------------------------#


# iDTT inverse bidimensionnelle

# int_dtt_2D_data.shape = (N, N)
def decode_2D_iDTT(P, S, int_dtt_2D_data):
    res_intermediaire = decode_forward_iDTT(P, S, int_dtt_2D_data)
    int_yuv_2D_data = decode_forward_iDTT(P, S, res_intermediaire.T)
    
    return(int_yuv_2D_data)


#----------------------------------------------------------------------------#


# iDTT (complète)

# int_yuv_data.shape = (N, N, 3)
def apply_iDTT(P, S, int_yuv_data):
    int_dtt_data = np.zeros(int_yuv_data.shape).astype(dtype=int)
    
    for k in range(3):
        int_dtt_data[:, :, k] = apply_2D_iDTT(P, S, int_yuv_data[:, :, k])
    
    return(int_dtt_data)


#----------------------------------------------------------------------------#


# iDTT inverse (complète)

# int_dtt_data.shape = (N, N, 3)
def decode_iDTT(P, S, int_dtt_data):
    int_yuv_data = np.zeros(int_dtt_data.shape).astype(dtype=int)
    
    for k in range(3):
        int_yuv_data[:, :, k] = decode_2D_iDTT(P, S, int_dtt_data[:, :, k])
    
    return(int_yuv_data)


#----------------------------------------------------------------------------#


# vérifie si les fonctions "apply_iDTT" et "decode_iDTT" sont précises
def check_iDTT_functions(N):
    A = DTT_operator(N)
    (P, S) = generer_decomp(A)
    
    # ici on vérifie que la décomposition de A est bien cohérente
    epsilon_decomp = check_decomp(A, P, S)
    print(f"\nPrécision de la décomposition de A : {epsilon_decomp}")
    
    # ici on vérifie si on a bien iDTT(iDTT_inverse(tab)) = tab
    int_dtt_data = np.random.randint(0, 256, size=(N, N, 3))
    test1 = apply_iDTT(P, S, decode_iDTT(P, S, int_dtt_data))
    epsilon1 = np.linalg.norm(test1 - int_dtt_data)
    
    # ici on vérifie si on a bien iDTT_inverse(iDTT(tab)) = tab
    int_yuv_data = np.random.randint(0, 256, size=(N, N, 3))
    test2 = decode_iDTT(P, S, apply_iDTT(P, S, int_yuv_data))
    epsilon2 = np.linalg.norm(test2 - int_yuv_data)
    
    print(f"Test de précision (iDTT & iDTT inverse) : {epsilon1}, {epsilon2}\n")


##############################################################################
################################  Débuggage  #################################
##############################################################################


if __name__ == "__main__":
    # N = image_height = image_width (image carrée / macrobloc carré), N >= 2
    # N est typiquement de la taille d'un macrobloc, donc idéalement il faudrait
    # éviter d'avoir N > 10 (par exemple)
    N = 8
    print(f"\n\nN = {N}")
    # On remarque que, pour N > 12, les erreurs lors de l'application de la iDTT
    # et la iDTT inverse sont monumentales, alors qu'elles sont (littéralement)
    # nulles pour N <= 12
    
    #------------------------------------------------------------------------#
    
    # DTT & DTT inverse
    
    check_DTT_functions(N)
    # --> OK
    
    #------------------------------------------------------------------------#
    
    # iDTT & iDTT inverse
    
    check_iDTT_functions(N)
    # --> OK

