# -*- coding: utf-8 -*-

"""
N = image_height = image_width (image carrée / macrobloc carré), N >= 2
N est typiquement de la taille d'un macrobloc, donc idéalement il faudrait 
éviter d'avoir N > 16. 
De plus, le temps de génération de l'opérateur de la DTT pour N > 20 est assez 
élevé. Avec la nouvelle amélioration de l'algorithme, on n'est plus limité
par la précision du calcul de S, mais plutôt par le temps de calcul de A !
(cf. articles)

DTT = Discrete Tchebychev Transform
iDTT = integer DTT
SERM = Single-row Elementary Reversible Matrix

Sources :
1) sciencedirect.com/science/article/abs/pii/S0925231216306907
2) researchgate.net/publication/3318095_Matrix_factorizations_for_reversible_integer_mapping

En gros : 
Article 1 (pages 2/7 et 3/7) : Implémentation de la DTT et de la iDTT (+ leur inverse)
Article 2 (pages 5/12 et 6/12) : Décomposition de l'opérateur A (pour la DTT) en SERMs

Tout au long du code, on a essayé de se rapprocher du plus possible des notations
de ces 2 articles.
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


# N >= 2, 0 <= n < N
def a1(n, N):
    return((2 / n) * np.sqrt((4 * n**2 - 1) / (N**2 - n**2)))


# N >= 2, 0 <= n < N
def a2(n, N):
    return(((1 - N) / n) * np.sqrt((4 * n**2 - 1) / (N**2 - n**2)))


# N >= 2, 0 <= n < N
def a3(n, N):
    return(((1 - n) / n) * np.sqrt((2 * n + 1) / (2 * n - 3)) * np.sqrt((N**2 - (n - 1)**2) / (N**2 - n**2)))


# N >= 2, 0 <= n < N, x : entier >= 0
# algo récursif
def t_tilde(n, x, N):
    if n == 0:
        return(1 / np.sqrt(N))
    
    if n == 1:
        return((2 * x + 1 - N) * np.sqrt(3 / (N * (N**2 - 1))))
    
    return((a1(n, N) * x + a2(n, N)) * t_tilde(n-1, x, N) + a3(n, N) * t_tilde(n-2, x, N))


# Génère l'opérateur de la DTT
# Pour N = 8, on retrouve bien la matrice A de l'article n°1
# L'opérateur A est orthogonal, ie np.linalg.inv(A) = A.T
def DTT_operator(N):
    A = np.zeros((N, N))
    
    for i in range(N):
        for j in range(N):
            A[i, j] = t_tilde(i, j, N)
    
    return(A)


#----------------------------------------------------------------------------#


# DTT

# A : opérateur orthogonal de la DTT, A.shape = (N, N)
# yuv_data.shape = (N, N) ou (N, N, 3)
# On aurait pu générer A directement dans la fonction, mais comme A est
# amenée à être réutilisée, autant la mettre en argument
def apply_DTT(A, yuv_data):
    if len(yuv_data.shape) == 2:
        # ici yuv_data.shape = (N, N)
        return(A @ yuv_data @ A.T)
    
    # si on est arrivé jusque là, on a yuv_data.shape = (N, N, 3)
    dtt_data = np.zeros(yuv_data.shape)
    
    for k in range(3):
        dtt_data[:, :, k] = apply_DTT(A, yuv_data[:, :, k])
    
    return(dtt_data)


#----------------------------------------------------------------------------#


# DTT inverse

# A : opérateur orthogonal de la DTT, A.shape = (N, N)
# dtt_data.shape = (N, N) ou (N, N, 3)
def decode_DTT(A, dtt_data):
    if len(dtt_data.shape) == 2:
        # ici dtt_data.shape = (N, N)
        return(A.T @ dtt_data @ A)
    
    # si on est arrivé jusque là, on a dtt_data.shape = (N, N, 3)
    yuv_data = np.zeros(dtt_data.shape)
    
    for k in range(3):
        yuv_data[:, :, k] = decode_DTT(A, dtt_data[:, :, k])
    
    return(yuv_data)


#----------------------------------------------------------------------------#


# vérifie si les fonctions "apply_DTT" et "decode_DTT" sont précises
def check_DTT_functions(A):
    N = A.shape[0]
    
    # ici on vérifie si on a bien DTT(DTT_inverse(tab)) = tab
    dtt_data = np.random.uniform(0, 255, size=(N, N, 3))
    test1 = apply_DTT(A, decode_DTT(A, dtt_data))
    epsilon1 = np.linalg.norm(test1 - dtt_data)
    
    # ici on vérifie si on a bien DTT_inverse(DTT(tab)) = tab
    yuv_data = np.random.uniform(0, 255, size=(N, N, 3))
    test2 = decode_DTT(A, apply_DTT(A, yuv_data))
    epsilon2 = np.linalg.norm(test2 - yuv_data)
    
    print(f"\nTest de précision (DTT & DTT inverse) : {epsilon1:.2e}, {epsilon2:.2e}")


##############################################################################
############################  iDTT & iDTT inverse ############################
##############################################################################


# fonctions auxiliaires pour pouvoir décomposer A en SERMs


"""
Il y a de nouveau une erreur qui pourrait prêter à confusion dans l'article n°1,
page 3/7, si jamais on venait à vérifier les calculs.

Il s'agit de la ligne située juste après l'équation (13).

Les vraies équations sont : 

inv(S_0) = I - e_8 @ s_0.T
inv(S_m) = I - e_m @ s_m.T (m = 1, ..., 7)
inv(S_8) = S_8 = I + e_8 @ s_8.T

Le fait que S_8 soit de la forme "I + e_8 @ s_8.T" et qu'il soit son propre 
inverse explique notamment pourquoi s_8 se finit par -2.

En fait, contrairement à ce que dit l'article dans cette ligne, S_0 ne sera 
**jamais** égal à son propre inverse. Le seul SERM (ie le seul S_m, avec 
0 <= m <= N) qui pourra potentiellement être égal à son propre inverse est S_N,
et cela arrive **ssi** s_N se termine par -2.

Les 2 premières équations se généralisent bien :

inv(S_0) = I - e_N @ s_0.T
inv(S_m) = I - e_m @ s_m.T (m = 1, ..., N-1)

Cependant, la dernière équation ne se généralise pas très bien.

En effet, si on considère les entiers N de 1 (inclus) à 30 (inclus), on a que
le dernier terme de s_N vaudra toujours 0, sauf pour N = 6, 8, 13, 16, 20, 24, 
25, 26 et 27, où celui-ci vaudra -2.
Si ce coeff vaut -2, alors S_N est son propre inverse, et on a bien la propriété
suivante : inv(S_N) = S_N = I + e_N @ s_N.T
Cependant, s'il vaut 0, alors on a : inv(S_N) = I - e_N @ s_N.T (comme pour 
les autres S_m, avec 1 <= m <= N-1).
"""


# L : matrice triangulaire inférieure avec que des '1' sur la diagonale
# U : matrice triangulaire supérieure avec que des '1' sur la diagonale
# len(liste_S_m) = N + 1, liste_S_m : [S_0, S_1, ..., S_N]
# pour tout m dans [0, N], S_m.shape = (N, N)
def generer_liste_S_m(S_0, L, U):
    N = S_0.shape[0]
    liste_S_m = [np.copy(S_0)]
    
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
# Cette fonction ne sert que pour la fonction generer_matrice_S
def extract_s_m(S_m, m):
    N = S_m.shape[0]
    
    if m == 0:
        return(extract_s_m(S_m, N))
    
    else:
        s_m = np.copy(S_m[m-1, :])
        s_m[m-1] -= 1
        return(s_m)


# len(liste_S_m) = N + 1
# liste_S_m = [S_0, S_1, ..., _S_N]
# pour tout m dans [0, N], S_m.shape = (N, N)
def generer_matrice_S(liste_S_m):
    N = len(liste_S_m) - 1
    S = np.zeros((N+1, N))
    
    for m in range(0, N+1):
        S_m = liste_S_m[m]
        s_m = extract_s_m(S_m, m)
        S[m, :] = s_m
    
    return(S)


# Détermine le numéro de la ligne à échanger avec la ligne n°k_ref, de telle 
# sorte à ce que la quantité abs((a_k_kref - 1) / a_k_N) (ie abs(s_k)) soit 
# minimisée
# Cette fonction ne sert que pour la fonction genere_P_k
# Attention : dans cette fonction, les s_k dont on parle ne sont pas les vecteurs
# qui composent la matrice S, mais les coefficients qui se situent à la dernière 
# ligne de la matrice S_0
# k_ref : entier, 1 <= k_ref <= N-1
def determine_ligne_a_echanger(k_ref, A_modifie):
    N = A_modifie.shape[0]
    
    indice_du_min = -1
    signe_ref = 0
    valeur_ref = -1
    initialisation_valeur_ref = False
    
    # on commence à partir de k_ref, car, à ce stade, les parties sous la 
    # diagonale des colonnes n°k_i ont déjà été mises à 0, avec k_i dans 
    # [1, k_ref - 1] (et si k_ref = 1 rien n'a encore été fait)
    for k in range(k_ref, N+1):
        a_k_N = A_modifie[k-1, N-1]
        
        if a_k_N != 0:
            a_k_kref = A_modifie[k-1, k_ref-1]
            
            s_k = (a_k_kref - 1) / a_k_N
            if s_k >= 0:
                signe_s_k = 1
            else:
                signe_s_k = -1
            
            # calcul de la valeur absolue de s_k
            abs_s_k = abs(s_k)
            
            if not(initialisation_valeur_ref):
                # Ici, valeur_ref = -1, donc on la met à jour quoiqu'il arrive
                # On passera forcément au moins une fois dans cette boucle, sans
                # quoi A_modifie serait non-inversible (--> absurde)
                indice_du_min = k
                signe_ref = signe_s_k
                valeur_ref = abs_s_k
                initialisation_valeur_ref = True
            
            else:
                if abs_s_k < valeur_ref:
                    signe_ref = signe_s_k
                    valeur_ref = abs_s_k
                    indice_du_min = k
    
    s_k_min = signe_ref * valeur_ref
    
    return(indice_du_min, s_k_min)


# Attention : dans cette fonction, les s_k dont on parle ne sont pas les vecteurs 
# qui composent la matrice S, mais les coefficients qui se situent à la dernière 
# ligne de la matrice S_0
# Détermine l'indice de la ligne de A_modifie pour laquelle le coeff s_k est
# minimal en valeur absolue (disons k_echange), puis génère une matrice de 
# permutation, qui, une fois multipliée à A_modifie par la **gauche**, échange 
# les lignes k_ref et k_echange
# k_ref : entier, 1 <= k_ref <= N-1, A_modifie.shape = (N, N)
def genere_P_k(k_ref, A_modifie):
    N = A_modifie.shape[0]
    P_k = np.eye(N)
    
    res_intermediaire = determine_ligne_a_echanger(k_ref, A_modifie)
    
    k_echange = res_intermediaire[0]
    s_k_min = res_intermediaire[1]
    
    if k_echange != k_ref:
        P_k[k_ref-1, k_ref-1] = 0
        P_k[k_echange-1, k_echange-1] = 0
        
        P_k[k_ref-1, k_echange-1] = 1
        P_k[k_echange-1, k_ref-1] = 1
    
    return(P_k, s_k_min)


# permet de générer une matrice de Gauss, qui, une fois multipliée à A_modifie
# par la **gauche**, met à 0 tous les coefficients sous la diagonale, dans la
# colonne k de A_modifie
# k : entier, 1 <= k <= N-1, A_modifie.shape = (N, N)
def genere_L_k(k, A_modifie):
    N = A_modifie.shape[0]
    L_k = np.eye(N)
    
    for i in range(k+1, N+1):
        L_k[i-1, k-1] = -A_modifie[i-1, k-1]
    
    return(L_k)


# permet d'arrondir chacune des composantes de M à l'entier le plus proche
# M est une matrice **réelle** de taille quelconque
def round_matrix(M):
    return(np.round(M, 0).astype(dtype=int))


#----------------------------------------------------------------------------#


# A : matrice à décomposer en P * S_N * ... * S_1 * S_0
# A.shape = (N, N), P.shape = (N, N), S.shape = (N+1, N)
# génération d'une décomposition de A en SERMs
def generer_decomp(A):
    """
    ATTENTION : Il n'y a pas qu'une seule décomposition en SERMs possible !
    
    En effet, selon la manière dont on choisit l'indice 'indice_du_min' dans la 
    fonction determine_ligne_a_echanger, on aura des S_m (et donc des s_m, et
    donc une matrice S) vraisemblablement différents.
    
    On a ici fait en sorte de coder determine_ligne_a_echanger de manière à
    optimiser les performances de la iDTT, ie minimiser (en valeur absolue) le 
    maximum de S.
    
    Par ailleurs, pour N = 8, on retrouve bien la matrice S de l'article n°1.
    """
    N = A.shape[0]
    
    P = np.eye(N, dtype=int)
    M = np.eye(N)
    S_0 = np.eye(N)
    
    
    A_modifie = np.copy(A)
    
    # ici, on met à jour itérativement P, M, et S_0 (et A_modifie)
    for k in range(1, N):
        #--------------------------------------------------------------------#
        
        # Étape 1 : détermination de P_k et mise à jour de P (et de A_modifie)
        
        res = genere_P_k(k, A_modifie)
        
        P_k = res[0]
        A_modifie = P_k @ A_modifie
        
        P = P @ round_matrix(P_k).T
        
        #--------------------------------------------------------------------#
        
        # Étape 2 : détermination de S_0_k et mise à jour de S_0 (et de A_modifie)
        
        # Attention : dans cette fonction, les s_k dont on parle ne sont pas 
        # les vecteurs qui composent la matrice S, mais les coefficients
        # qui se situent à la dernière ligne de la matrice S_0
        s_k = res[1]
        
        # si s_k = 0, S_0_k = np.eye(N), et donc il ne se passe rien, ie S_0
        # et A_modifie sont inchangés
        if s_k != 0:
            S_0_k = np.eye(N)
            S_0_k[N-1, k-1] = -s_k
            A_modifie = A_modifie @ S_0_k
            
            S_0 = np.linalg.inv(S_0_k) @ S_0
        
        #--------------------------------------------------------------------#
        
        # Étape 3 : détermination de L_k et mise à jour de M (et de A_modifie)
        
        L_k = genere_L_k(k, A_modifie)
        A_modifie = L_k @ A_modifie
        
        M = (L_k @ P_k) @ M
        
        #--------------------------------------------------------------------#
    
    
    L = P.T @ np.linalg.inv(M)
    
    # En réalité, il s'agit ici de la matrice D_R @ U, où D_R = diag(1, ..., 1, epsilon),
    # où epsilon = det(A) * produit(k=1, k=N-1, det(P_k)) 
    # Si det(A) = +/- 1 (ce qui est le cas ici), epsilon vaut +/- 1, car les 
    # P_k ont tous un det de +/- 1
    # Faire la décomposition de L @ (D_R @ U) au lieu de celle de L @ U n'est
    # ici pas très gênant, car en fin de compte ce qui importe c'est que les
    # coefficients de la matrice S finale soient faibles en valeur absolue
    # Or, ce changement n'est pas dramatique, car la seule chose qui est modifiée 
    # c'est (en gros) le dernier terme de s_N, qui vaut -2 au lieu de 0, mais en
    # contrepartie sans ce changement on doit considérer une 2ème matrice de 
    # permutation dans la décomposition de A (cf. article n°2) !
    U = np.copy(A_modifie)
    
    liste_S_m = generer_liste_S_m(S_0, L, U)
    S = generer_matrice_S(liste_S_m)
    
    return(P, S)


#----------------------------------------------------------------------------#


# S.shape = (N+1, N)
def extract_S_m(S, m):
    N = S.shape[1]
    S_m = np.eye(N)
    
    s_m = S[m, :]
    
    if m == 0:
        S_m[N-1, :] += s_m
    
    else:
        S_m[m-1, :] += s_m
    
    return(S_m)


# P.shape = (N, N), S.shape = (N+1, N), A_ref.shape = (N, N) = A_check.shape
# on veut vérifier que A = P * S_N * ... * S_0
def check_decomp(A, P, S):
    N = P.shape[0]
    A_check = np.copy(P).astype(dtype=float)
    
    # on va de m = N (inclus) à m = 0 (inclus), dans l'ordre décroissant
    for m in range(N, -1, -1):
        S_m = extract_S_m(S, m)
        A_check = A_check @ S_m
    
    precision_decomp = np.linalg.norm(A - A_check)
    
    return(precision_decomp)


#----------------------------------------------------------------------------#


# iDTT forward "intermédiaire"

# int_yuv_data.shape = (N, 1), (N,) ou (N, N)
def apply_forward_iDTT(P, S, int_yuv_data):
    N = P.shape[0]
    
    # initialisation
    S_0 = extract_S_m(S, 0)
    int_dtt_data = round_matrix(S_0 @ int_yuv_data)
    
    for m in range(1, N+1):
        S_m = extract_S_m(S, m)
        int_dtt_data = round_matrix(S_m @ int_dtt_data)
    
    int_dtt_data = P @ int_dtt_data
    
    return(int_dtt_data)


#----------------------------------------------------------------------------#


# iDTT inverse "intermédiaire"

# int_dtt_data.shape = (N, 1), (N,) ou (N, N)
# Ici, int_dtt_data.shape est plus voué à être (N, N)
def decode_forward_iDTT(P, S, int_dtt_data):
    N = P.shape[0]
    
    # initialisation
    S_N = extract_S_m(S, N)
    int_yuv_data = round_matrix(np.linalg.inv(S_N) @ P.T @ int_dtt_data)
    
    for m in range(N-1, -1, -1):
        S_m = extract_S_m(S, m)
        int_yuv_data = round_matrix(np.linalg.inv(S_m) @ int_yuv_data)
    
    return(int_yuv_data)


#----------------------------------------------------------------------------#


"""
Remarque concernant la définition de la iDTT (et de son inverse) pour 
une matrice en 2D, telle qu'elle a été énoncée dans l'article n°1

Cette remarque traite essentiellement du lien entre les équations (12) à (15) 
(page 3/7) et l'équation (9) (page 2/7)

D'après (12) et (10), on peut considérer que iDTT_forward(X) n'est autre qu'une 
sorte "d'approximation entière" (ou "AE") de A @ X. (A priori, on ne peut pas
supposer que "AE" et "round" sont exactement les mêmes fonctions.) De même, 
d'après (13) et (10), on peut dire que iDTT_inverse(Y) est une AE de inv(A) @ Y,
ie une AE de A.T @ Y (car A est orthogonale).

Ainsi : 
(14) fournit que Y est une AE de A @ (A @ X).T = A @ X.T @ A.T = (A @ X @ A.T).T
(15) fournit que X est une AE de A.T @ (A.T @ Y).T = A.T @ Y.T @ A = (A.T @ Y @ A).T

On obtient donc que (cf. equation (9)) : 
1) Y est une AE de DTT_2D(X).T
2) X est une AE de DTT_2D_inverse(Y).T

Or, on s'attendrait logiquement à obtenir, dans les équations (14) et (15), que :
1) Y est une AE DTT_2D(X) (et non de sa transposée)
2) X est une AE de DTT_2D_inverse(Y) (et non de sa transposée)

En conséquence, pour rester fidèle à la DTT de base (et à l'appellation "integer
DTT" !), dans la fonction apply_2D_iDTT, nous allons transposer la formule de 
l'encodage de l'article 1 (ie (14)) pour stocker (et afficher) la vraie 
repésentation des données issues de la DTT. Et donc, dans la fonction 
decode_2D_iDTT, comme on sait que la matrice iDTT traitée (2D) est la 
transposée de ce qui a été encodé, on transpose directement l'entrée avant de 
passer au décodage avec la formule de l'article 1 (ie (15)).

En toute rigueur, les modifications précédentes ne sont pas nécessaires, car
les fonctions matricielles X --> (A @ X @ A.T).T et X --> (A.T @ X @ A).T sont
inverses l'une de l'autre (car A est orthogonale), et donc on peut considérer
que des AE de ces 2 fonctions le sont aussi. En d'autres termes, on peut 
considérer que (14) et (15) sont inverses l'une de l'autre, ce qui est le 
cas en pratique (ouf).
"""


#----------------------------------------------------------------------------#


# iDTT bidimensionnelle

# int_yuv_2D_data.shape = (N, N)
def apply_2D_iDTT(P, S, int_yuv_2D_data):
    res_intermediaire = apply_forward_iDTT(P, S, int_yuv_2D_data)
    int_dtt_2D_data = apply_forward_iDTT(P, S, res_intermediaire.T).T
    
    return(int_dtt_2D_data)


#----------------------------------------------------------------------------#


# iDTT inverse bidimensionnelle

# int_dtt_2D_data.shape = (N, N)
def decode_2D_iDTT(P, S, int_dtt_2D_data):
    res_intermediaire = decode_forward_iDTT(P, S, int_dtt_2D_data.T)
    int_yuv_2D_data = decode_forward_iDTT(P, S, res_intermediaire.T)
    
    return(int_yuv_2D_data)


#----------------------------------------------------------------------------#


# iDTT (complète)

# int_yuv_data.shape = (N, N, 3)
def apply_iDTT(P, S, int_yuv_data):
    int_dtt_data = np.zeros(int_yuv_data.shape, dtype=int)
    
    for k in range(3):
        int_dtt_data[:, :, k] = apply_2D_iDTT(P, S, int_yuv_data[:, :, k])
    
    return(int_dtt_data)


#----------------------------------------------------------------------------#


# iDTT inverse (complète)

# int_dtt_data.shape = (N, N, 3)
def decode_iDTT(P, S, int_dtt_data):
    int_yuv_data = np.zeros(int_dtt_data.shape, dtype=int)
    
    for k in range(3):
        int_yuv_data[:, :, k] = decode_2D_iDTT(P, S, int_dtt_data[:, :, k])
    
    return(int_yuv_data)


#----------------------------------------------------------------------------#


# vérifie si les fonctions "apply_iDTT" et "decode_iDTT" sont précises
def check_iDTT_functions(A, P, S):
    N = A.shape[0]
    
    # ici on vérifie que la décomposition de A est bien cohérente
    epsilon_decomp = check_decomp(A, P, S)
    print(f"\nPrécision de la décomposition de A : {epsilon_decomp:.2e}")
    
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
    """
    N = image_height = image_width (image carrée / macrobloc carré), N >= 2
    N est typiquement de la taille d'un macrobloc, donc idéalement il faudrait 
    éviter d'avoir N > 16. 
    De plus, le temps de génération de l'opérateur de la DTT pour N > 20 est assez 
    élevé.
    """
    N = 8
    print(f"\n\nN = {N}")
    
    #------------------------------------------------------------------------#
    
    # Génération de l'opérateur de la DTT et de sa décomposition en SERMs
    
    # Comme la fonction DTT_operator est assez lourde en termes de calculs, on 
    # fait en sorte de n'y faire appel qu'une seule fois dans tout le code
    # Pour optimiser le code, on fait de même avec la fonction generer_decomp
    # (même si celle-ci s'exécute assez rapidement une fois que l'opérateur
    # A est généré)
    A = DTT_operator(N)
    (P, S) = generer_decomp(A)
    
    #------------------------------------------------------------------------#
    
    # DTT & DTT inverse
    
    check_DTT_functions(A)
    # --> OK
    
    #------------------------------------------------------------------------#
    
    # iDTT & iDTT inverse
    
    check_iDTT_functions(A, P, S)
    # --> OK

