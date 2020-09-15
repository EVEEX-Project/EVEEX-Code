# Compte rendu premier rdv 
membres : tous  
date : le 15/09/20 de 8h30 à 12h30 

## Objectifs 

1. elaborer les taches qui seront réalisé au premier sprint 
2. installation des softwares 
3. mise en place d'un début d'env. de developpement. 
4. topo rapide sur le mode agile 

## Réalisation 

### 1. la comprehension de l'algo 

*toutes les taches seront évalués selont leur difficulté envisagé (de 0 à 10/10 pour le plus dur)*  

les points à surveiller sont les suivants : 

- fonctionement du découpage en macrobloc 8x8 
- transformation en cosinus durect (DCT)
- zig zag scanning (parcoure de l'image selon la diagonale)
- run lenght level encoding (RLL) 
- codage de huffman. 

#### découpage en macrobloc : 

pour une résolution en 720p, avec blocs de 16x16, il y a 45x80 blocs
ça suppose une transformation flux-video ==> bitestream 
bibliothèque pour capture video : open-cv 
*pip install opencv-python*  
0915 : on a un début de code qui permet de prendre des screenshots (dossier webcam capture)

**1ere étape du sprint 1 : transformer un screenshot en bitstream, connexion socket entre 2 clients. décodage du bitstream pour afficher une image** 

norme MPEG-1: bloc de 16x16, encodage PAL 25i/s, 352x288px => 22x18blocs. 
#### blocs  

 **blocs I : intracodé (indépendant)**  
 blocs P : prédictif (décrite par différence avec images précédentes)  
 blocs B : prédicitif + images suivantes  
 blocs DC : moyennes par bloc. 

MPEG1 : sépration partie video et partie audio. 
on utilisera une bibliotèque pour conversion flux audio en MP3. 





### 2. installation des softwares 

client git : gitkraken 
repository sur git-hub : https://github.com/EVEEX-Project/
IDE python : pycharm avec python 3.8  
*il y aura un fichier requirements pour l'installation des bibliothèques*  
webcam : modèle 720p intégré a nos ordis portables. 



### 3. mise en place de l'environement de dev 

structure du programme (prototype python pour commencer)



### 4. topo mode agile 

