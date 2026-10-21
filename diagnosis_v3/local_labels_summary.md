# Diagnostic du mapping local

## CHARTEVENTS.itemid

Jointure : D_ITEMS.label · vocabulaires : LOINC, SNOMED · **cherché par le pipeline : oui**
Identifiants distincts : 1679 ; sans libellé (absent du dictionnaire ou libellé vide) : 0 (0 lignes).

| Catégorie | Identifiants | % | Lignes | % |
|---|---|---|---|---|
| 1_resolu_et_route | 112 | 6.7 | 100800 | 13.3 |
| 2_resolu_domaine_hors_5_tables | 36 | 2.1 | 16313 | 2.2 |
| 3_nom_trouve_sans_Maps_to_standard | 38 | 2.3 | 16445 | 2.2 |
| 4_recuperable_casse_ponctuation | 3 | 0.2 | 4986 | 0.7 |
| 5_recuperable_sans_crochets_a_verifier | 20 | 1.2 | 8245 | 1.1 |
| 6_recuperable_par_synonyme | 15 | 0.9 | 8368 | 1.1 |
| 7_nom_exact_dans_un_autre_vocabulaire | 6 | 0.4 | 991 | 0.1 |
| 8_aucun_candidat | 1449 | 86.3 | 602207 | 79.4 |

## DATETIMEEVENTS.itemid

Jointure : D_ITEMS.label · vocabulaires : LOINC, SNOMED · **cherché par le pipeline : oui**
Identifiants distincts : 80 ; sans libellé (absent du dictionnaire ou libellé vide) : 0 (0 lignes).

| Catégorie | Identifiants | % | Lignes | % |
|---|---|---|---|---|
| 1_resolu_et_route | 1 | 1.2 | 71 | 0.5 |
| 8_aucun_candidat | 79 | 98.8 | 15480 | 99.5 |

## INPUTEVENTS_CV.itemid

Jointure : D_ITEMS.label · vocabulaires : RxNorm, LOINC, SNOMED · **cherché par le pipeline : oui**
Identifiants distincts : 79 ; sans libellé (absent du dictionnaire ou libellé vide) : 1 (891 lignes).

| Catégorie | Identifiants | % | Lignes | % |
|---|---|---|---|---|
| 1_resolu_et_route | 17 | 21.8 | 8621 | 25.4 |
| 2_resolu_domaine_hors_5_tables | 7 | 9.0 | 3963 | 11.7 |
| 3_nom_trouve_sans_Maps_to_standard | 8 | 10.3 | 1589 | 4.7 |
| 6_recuperable_par_synonyme | 1 | 1.3 | 441 | 1.3 |
| 8_aucun_candidat | 45 | 57.7 | 19294 | 56.9 |

## INPUTEVENTS_MV.itemid

Jointure : D_ITEMS.label · vocabulaires : RxNorm, LOINC · **cherché par le pipeline : oui**
Identifiants distincts : 135 ; sans libellé (absent du dictionnaire ou libellé vide) : 0 (0 lignes).

| Catégorie | Identifiants | % | Lignes | % |
|---|---|---|---|---|
| 1_resolu_et_route | 51 | 37.8 | 3601 | 27.2 |
| 2_resolu_domaine_hors_5_tables | 7 | 5.2 | 277 | 2.1 |
| 3_nom_trouve_sans_Maps_to_standard | 4 | 3.0 | 701 | 5.3 |
| 4_recuperable_casse_ponctuation | 1 | 0.7 | 16 | 0.1 |
| 7_nom_exact_dans_un_autre_vocabulaire | 1 | 0.7 | 78 | 0.6 |
| 8_aucun_candidat | 71 | 52.6 | 8551 | 64.7 |

## LABEVENTS.itemid
Jointure de type `code` (code réel) : hors périmètre de ce diagnostic.

## MICROBIOLOGYEVENTS.ab_itemid

Jointure : D_ITEMS.label · vocabulaires : RxNorm, SNOMED · **cherché par le pipeline : oui**
Identifiants distincts : 28 ; sans libellé (absent du dictionnaire ou libellé vide) : 0 (0 lignes).

| Catégorie | Identifiants | % | Lignes | % |
|---|---|---|---|---|
| 1_resolu_et_route | 24 | 85.7 | 800 | 82.4 |
| 3_nom_trouve_sans_Maps_to_standard | 1 | 3.6 | 21 | 2.2 |
| 8_aucun_candidat | 3 | 10.7 | 150 | 15.4 |

### Sondage MICROBIOLOGYEVENTS : '<libellé> [Susceptibility]' dans LOINC

| Statut | Libellés |
|---|---|
| absent | 3 |
| trouve_standard | 25 |


Accord avec la référence : non=25, non_trouve=3

## OUTPUTEVENTS.itemid

Jointure : D_ITEMS.label · vocabulaires : LOINC, SNOMED · **cherché par le pipeline : oui**
Identifiants distincts : 62 ; sans libellé (absent du dictionnaire ou libellé vide) : 0 (0 lignes).

| Catégorie | Identifiants | % | Lignes | % |
|---|---|---|---|---|
| 2_resolu_domaine_hors_5_tables | 6 | 9.7 | 185 | 1.6 |
| 6_recuperable_par_synonyme | 4 | 6.5 | 22 | 0.2 |
| 7_nom_exact_dans_un_autre_vocabulaire | 1 | 1.6 | 4138 | 36.6 |
| 8_aucun_candidat | 51 | 82.3 | 6975 | 61.6 |

## PROCEDUREEVENTS_MV.itemid

Jointure : D_ITEMS.label · vocabulaires : SNOMED, CPT · **cherché par le pipeline : oui**
Identifiants distincts : 64 ; sans libellé (absent du dictionnaire ou libellé vide) : 0 (0 lignes).

| Catégorie | Identifiants | % | Lignes | % |
|---|---|---|---|---|
| 1_resolu_et_route | 23 | 35.9 | 219 | 29.1 |
| 2_resolu_domaine_hors_5_tables | 3 | 4.7 | 33 | 4.4 |
| 3_nom_trouve_sans_Maps_to_standard | 2 | 3.1 | 33 | 4.4 |
| 6_recuperable_par_synonyme | 5 | 7.8 | 39 | 5.2 |
| 7_nom_exact_dans_un_autre_vocabulaire | 2 | 3.1 | 38 | 5.0 |
| 8_aucun_candidat | 29 | 45.3 | 391 | 51.9 |
