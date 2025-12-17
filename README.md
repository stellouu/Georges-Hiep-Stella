# Georges-Hiep-Stella
Groupe de 1ère NSI CIV - Projet 2025-2026 

Idées de départ:
- Jeu en 2D
- Histoire
- Jeu d'horreur
- Escape Game
- Jeu de logique
- 1 personnage principal
- Des PNJ
- Dans notre monde
- Screamers
- Psychologique

**Personnage principal**:
 - Victor Blackwell
 - Patient dans un hôpital psychiatrique
 - Porte une blouse tachée (laisser vague pour que le joueur ne sache pas qui est le personnage encore), avec une étiquette trop ensanglantée pour déchiffrer le prénom, on voit que 'V...B...'
 - Se réveille, allongé sur le sol froid de l'hôpital de , dans une chambre d'hôpital. Il n'a aucun souvenir, il ne connaît pas son nom, pourquoi il est la. Il ne sait pas si il est un patient ou un docteur.
 - Il trouve un bout de verre cassé par terre, qu'il garde sur lui pour se défendre
 - Il doit s'échapper, en parlant à des PNJ (en dehors des docteurs/monstes(zombies)) qui lui donnent des indication pour trouver les clés pour sortir. A chaque fois qu'il quitte une personne, celle-ci lui donne un vers de poésie (chacun sa raison) qui forme un acrostiche révélant à Victor son nom, lui rendant tous ses souvenirs.
 - Les PNJ parlent sous forme d'énigme.
 - *Backstory* : Blackwell a tué, dans sa folie, tous les patients de l'hôpital + les soignants, puis a subi une overdose d'opioïde en essayant de mettre fin à ses jours. En se réveillant, il est totalement déboussolé. Les gens 'nnormaux' à qui il parle sont en réalité des créations de sa folie qui lui donnent des détails peu à peu sur l'origine de cette situation, toutes des personnes dont il se sent subconsciemment coupable d'avoir tué. Les esprits de l'hôpital s'éveillent la nuit pour se venger des meurtres de Victor, essayant de le tuer à leur tour suos la forme de créatures ~zombie.
 - 
![9434944_1](https://github.com/user-attachments/assets/4d66ba04-944d-466f-95f7-5d7db3f5bcd2)

**Nombre de joueurs** : 1 + des PNJ

Les personnages parleront comme ça:

![images](https://github.com/user-attachments/assets/9d6e3462-8303-4b32-a580-7cc776ffd9dd)


**Types/création de graphiques**: 

 - 2D graphics
 - Même esprit et configuration des personnage que les vieux jeux (ex Pokemon)
 - Annimations simples
 - La carte n'est pas entièrement visible
 - Carte avec défilement

![00-featured-pokemon-demo-game-inbrowser](https://github.com/user-attachments/assets/81b05fbc-cdb3-4712-bc71-e86f81bf77bd)

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/0c4ebdb0-d983-4011-a98f-f34c8d5eaa7e" />


**Bibliothèque utilisée**:

 - Pygame

**Types d'ennemis**:

 - Les docteurs de l'hôpital 50pv et -5pv
 - Les patients (sous forme de monstre) 75pv et -5pv
 - une "IA" très simple

<img width="640" height="240" alt="xoByzu" src="https://github.com/user-attachments/assets/be4d3b59-ac16-4d4b-85a1-79fa8e8cdd32" />


**Mouvements/attaques possibles**: 

 - Bout de verre (Attaque faibles) -15pv
 - Couteau (Attaque plus forte) -40pv
 - Révolver (Attaque puissante + à distance) -75pv
    - A trouver caché dans l'hôpital
      

**Système de score de vie**: 
 - Système basique, le joueur commence avec une barre de vie qui diminue avec la fatigue (-1 toutes les 3 secondes sur 200 HP, laissant 10min au joueur avant de devoir se soigner)
 - Pour reprendre de la force, Victor doit prendre ses médicaments, situés à côté du point de départ sur une table.
 - jusqu'à 5 sauvegardes différentes + 1 sauvegarde automatique

![360_F_1573978198_ty8a15RWmnpEk83Xa1wYZu5HClyDShLd](https://github.com/user-attachments/assets/e1b1a763-638e-4445-9f0c-d4bc0a2008e8)


**Contrôles souris/clavier**: 

 - Z pour le nord, D pour l'est, S pour le sud et Q pour l'Ouest
 - E pour les intéraction
 - F pour lampe torche
 - X pour l'inventaire
 - Clic de souris pour attaquer

**Idées de musiques**: 

 - https://www.youtube.com/watch?v=_Qr2T1az1Ck&list=PL0J7CU72FU1M6eExlRP8QikATJ38TD86Y
 - https://www.youtube.com/watch?v=AO5u-ylgaIY&list=PL0J7CU72FU1M6eExlRP8QikATJ38TD86Y&index=7
 - https://www.youtube.com/watch?v=-sOadAaGiq4

inspirations: 

 - Silent Hill
 - Resident Evil
 - https://www.pressplaygaming.net/articles/2024/12/04/ppg-game-of-the-year-2024-22-the-best-top-down-rpgs

                    
Y aura-t-il des animations ? La carte est-elle entièrement visible ? Y a-t-il un défilement ? Comment sont gérés le score, les sauvegardes (s'il y en a), les obstacles ? Comment se comportent les ennemis ?
Les réponses à ces questions (et d'autres) vont faire grandement varier la complexité de votre projet.
