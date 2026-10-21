# Full Comparison Report

## Executive Summary

| Table | Rows (ours) | Rows (reference) | Matched | Fully Identical | Warning |
|---|---|---|---|---|---|
| person | 100 | 100 | 100 | 0/100 (0.0%) |  |
| visit_occurrence | 129 | 129 | 119 | 119/119 (100.0%) | 10 ours-only / 10 reference-only |
| condition_occurrence | 1736 | 1903 | 133 | 0/133 (0.0%) | ⚠️ non-unique key (114/1565 dupes) |
| drug_exposure | 27318 | 56715 | 9458 | 0/9458 (0.0%) | ⚠️ non-unique key (16330/44864 dupes) |
| procedure_occurrence | 1273 | 2815 | 11 | 0/11 (0.0%) | ⚠️ non-unique key (228/963 dupes) |
| measurement | 112806 | 823220 | 86063 | 0/86063 (0.0%) | ⚠️ non-unique key (54078/746654 dupes) |
| observation | 95415 | 22529 | 6469 | 0/6469 (0.0%) | ⚠️ non-unique key (74853/20847 dupes) |
| death | 100 | 92 | 90 | 0/90 (0.0%) | 10 ours-only / 2 reference-only |
| observation_period | 129 | 129 | 119 | 119/119 (100.0%) | 10 ours-only / 10 reference-only |

**Overall row-level concordance across scored tables: 238/102562 (0.2%)**

## Per-Table Detail

# Comparaison ligne à ligne — person

Clé naturelle : person + ['person_source_value']

## Volumes bruts (avant tout filtrage)
  Chez nous : 100 lignes
  Chez la référence : 100 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 100 lignes (0 exclues - patient non apparié)
  Chez la référence : 100 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 100
  Clés UNIQUEMENT chez nous : 0
  Clés UNIQUEMENT chez la référence : 0

Lignes appariées (même personne + même clé naturelle) : 100

## gender_concept_id : 100/100 lignes concordent (100.0%)

## year_of_birth : 100/100 lignes concordent (100.0%)

## month_of_birth : 100/100 lignes concordent (100.0%)

## day_of_birth : 100/100 lignes concordent (100.0%)

## race_concept_id : 100/100 lignes concordent (100.0%)

## ethnicity_concept_id : 0/100 lignes concordent (0.0%)
    ex: nous=38003564 vs référence=0
    ex: nous=38003564 vs référence=0
    ex: nous=38003564 vs référence=0

## gender_source_value : 100/100 lignes concordent (100.0%)

## race_source_value : 99/100 lignes concordent (99.0%)
    ex: nous='AMERICAN INDIAN/ALASKA NATIVE FEDERALLY RECOGNIZED' vs référence='AMERICAN INDIAN/ALASKA NATIVE FEDERALLY RECOGNIZED TRIBE'

## ethnicity_source_value : 0/100 lignes concordent (0.0%)
    ex: nous='BLACK/AFRICAN AMERICAN' vs référence=None
    ex: nous='UNKNOWN/NOT SPECIFIED' vs référence=None
    ex: nous='UNKNOWN/NOT SPECIFIED' vs référence=None

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 0/100 (0.0%)

---

# Comparaison ligne à ligne — visit_occurrence

Clé naturelle : person + ['visit_concept_id', 'visit_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 129 lignes
  Chez la référence : 129 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 129 lignes (0 exclues - patient non apparié)
  Chez la référence : 129 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 119
  Clés UNIQUEMENT chez nous : 10
  Clés UNIQUEMENT chez la référence : 10
    ex: [(26, 262, datetime.date(2188, 2, 8)), (62, 262, datetime.date(2159, 11, 17)), (54, 262, datetime.date(2151, 8, 13))]
    ex: [(54, 262, datetime.date(2151, 8, 12)), (18, 262, datetime.date(2129, 11, 23)), (10, 262, datetime.date(2132, 12, 4))]

Lignes appariées (même personne + même clé naturelle) : 119

## visit_end_date : 119/119 lignes concordent (100.0%)

## visit_source_value : 119/119 lignes concordent (100.0%)

## visit_source_concept_id : ignoré (toujours vide chez nous sur les lignes appariées)
## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 119/119 (100.0%)

---

# Comparaison ligne à ligne — condition_occurrence

Clé naturelle : person + ['condition_concept_id', 'condition_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 1736 lignes
  Chez la référence : 1903 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 1736 lignes (0 exclues - patient non apparié)
  Chez la référence : 1903 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 114 doublon(s) chez nous, 1565 chez la référence, sur (person + ['condition_concept_id', 'condition_start_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 115
  Clés UNIQUEMENT chez nous : 1507
  Clés UNIQUEMENT chez la référence : 223
    ex: [(67, 197320, datetime.date(2200, 3, 17)), (47, 198683, datetime.date(2171, 7, 12)), (78, 201826, datetime.date(2160, 5, 4))]
    ex: [(98, 0, datetime.date(2123, 11, 24)), (37, 4306267, datetime.date(2105, 5, 29)), (34, 317002, datetime.date(2180, 2, 29))]

Lignes appariées (même personne + même clé naturelle) : 133

## condition_source_value : 76/133 lignes concordent (57.1%)
    ex: nous='99591' vs référence='SEPSIS'
    ex: nous='0389' vs référence='SEPSIS'
    ex: nous='1985' vs référence='81249'

## condition_source_concept_id : 0/133 lignes concordent (0.0%)
    ex: nous=44820254 vs référence=nan
    ex: nous=44821245 vs référence=44821245.0
    ex: nous=44823969 vs référence=nan

## condition_end_date : ignoré (toujours vide chez nous sur les lignes appariées)
## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 0/133 (0.0%)

---

# Comparaison ligne à ligne — drug_exposure

Clé naturelle : person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 27318 lignes
  Chez la référence : 56715 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 27318 lignes (0 exclues - patient non apparié)
  Chez la référence : 56715 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 16330 doublon(s) chez nous, 44864 chez la référence, sur (person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 8141
  Clés UNIQUEMENT chez nous : 2847
  Clés UNIQUEMENT chez la référence : 3710
    ex: [(57, 1707687, datetime.date(2144, 12, 25), datetime.date(2144, 12, 25)), (98, 19011034, datetime.date(2123, 12, 14), datetime.date(2123, 12, 15)), (15, 40231540, datetime.date(2147, 2, 11), datetime.date(2147, 2, 12))]
    ex: [(66, 3006552, datetime.date(2145, 12, 8), datetime.date(2145, 12, 9)), (98, 3037253, datetime.date(2123, 12, 16), datetime.date(2123, 12, 17)), (76, 3006552, datetime.date(2119, 11, 3), datetime.date(2119, 11, 3))]

Lignes appariées (même personne + même clé naturelle) : 9458

## drug_source_value : 0/9458 lignes concordent (0.0%)
    ex: nous='222168' vs référence='Propofol'
    ex: nous='222168' vs référence='Propofol'
    ex: nous='222168' vs référence='Propofol'

## drug_source_concept_id : 0/9458 lignes concordent (0.0%)
    ex: nous=753626 vs référence=2001028256.0
    ex: nous=753626 vs référence=2001028256.0
    ex: nous=753626 vs référence=2001028256.0

## quantity : 7836/8779 lignes concordent (89.3%)
    ex: nous=100.0 vs référence=20.0008871429
    ex: nous=100.0 vs référence=714.2859428571
    ex: nous=100.0 vs référence=20.0008885714

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 0/9458 (0.0%)

---

# Comparaison ligne à ligne — procedure_occurrence

Clé naturelle : person + ['procedure_concept_id', 'procedure_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 1273 lignes
  Chez la référence : 2815 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 1273 lignes (0 exclues - patient non apparié)
  Chez la référence : 2815 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 228 doublon(s) chez nous, 963 chez la référence, sur (person + ['procedure_concept_id', 'procedure_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 11
  Clés UNIQUEMENT chez nous : 1034
  Clés UNIQUEMENT chez la référence : 1841
    ex: [(30, 2008005, datetime.date(2107, 1, 29)), (51, 3526814, datetime.date(2130, 2, 5)), (76, 2002449, datetime.date(2119, 10, 17))]
    ex: [(52, 4304943, datetime.date(2169, 5, 7)), (28, 2008250, datetime.date(2107, 3, 30)), (67, 4027135, datetime.date(2200, 10, 29))]

Lignes appariées (même personne + même clé naturelle) : 11

## procedure_source_value : 3/11 lignes concordent (27.3%)
    ex: nous='3491' vs référence='Respiratory system'
    ex: nous='8181' vs référence='Musculoskeletal system'
    ex: nous='3995' vs référence='Dialysis'

## procedure_source_concept_id : 0/11 lignes concordent (0.0%)
    ex: nous=2001430 vs référence=42736235
    ex: nous=2005945 vs référence=2103758
    ex: nous=2008356 vs référence=2001017911

## quantity : ignoré (toujours vide chez nous sur les lignes appariées)
## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 0/11 (0.0%)

---

# Comparaison ligne à ligne — measurement

Clé naturelle : person + ['measurement_concept_id', 'measurement_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 112806 lignes
  Chez la référence : 823220 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 112806 lignes (0 exclues - patient non apparié)
  Chez la référence : 823220 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 54078 doublon(s) chez nous, 746654 chez la référence, sur (person + ['measurement_concept_id', 'measurement_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 54273
  Clés UNIQUEMENT chez nous : 4455
  Clés UNIQUEMENT chez la référence : 22293
    ex: [(28, 45876226, datetime.date(2107, 3, 29)), (87, 4265595, datetime.date(2179, 8, 14)), (60, 3022217, datetime.date(2144, 10, 24))]
    ex: [(72, 21490753, datetime.date(2127, 10, 12)), (50, 3034795, datetime.date(2123, 8, 26)), (57, 0, datetime.date(2144, 7, 27))]

Lignes appariées (même personne + même clé naturelle) : 86063

## value_as_number : 73646/79882 lignes concordent (92.2%)
    ex: nous=15.0 vs référence=nan
    ex: nous=15.0 vs référence=nan
    ex: nous=17.0 vs référence=15.0

## unit_concept_id : 0/86063 lignes concordent (0.0%)
    ex: nous=0 vs référence=nan
    ex: nous=0 vs référence=nan
    ex: nous=0 vs référence=8541.0

## measurement_source_value : 83773/86063 lignes concordent (97.3%)
    ex: nous='220210' vs référence='50827'
    ex: nous='220210' vs référence='50827'
    ex: nous='220210' vs référence='224689'

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 0/86063 (0.0%)

---

# Comparaison ligne à ligne — observation

Clé naturelle : person + ['observation_concept_id', 'observation_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 95415 lignes
  Chez la référence : 22529 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 95415 lignes (0 exclues - patient non apparié)
  Chez la référence : 22529 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 74853 doublon(s) chez nous, 20847 chez la référence, sur (person + ['observation_concept_id', 'observation_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 626
  Clés UNIQUEMENT chez nous : 19936
  Clés UNIQUEMENT chez la référence : 1056
    ex: [(73, 37023540, datetime.date(2117, 3, 23)), (65, 40789527, datetime.date(2145, 7, 8)), (2, 4232754, datetime.date(2126, 8, 18))]
    ex: [(76, 40758030, datetime.date(2119, 10, 17)), (94, 0, datetime.date(2073, 11, 22)), (41, 44803968, datetime.date(2148, 1, 13))]

Lignes appariées (même personne + même clé naturelle) : 6469

## value_as_number : ignoré (toujours vide chez nous sur les lignes appariées)
## value_as_string : 0/6469 lignes concordent (0.0%)
    ex: nous='2107-03-24 00:00:00' vs référence='INV#3 Dsg Change [MM]'
    ex: nous='2107-03-24 00:00:00' vs référence='INV#3 Dsg Change [MM]'
    ex: nous='2107-03-24 00:00:00' vs référence='INV#3 Dsg Change [MM]'

## observation_source_value : 0/6469 lignes concordent (0.0%)
    ex: nous='5684' vs référence=nan
    ex: nous='5684' vs référence=nan
    ex: nous='5684' vs référence=nan

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 0/6469 (0.0%)

---

# Comparaison ligne à ligne — death

Clé naturelle : person + ['death_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 100 lignes
  Chez la référence : 92 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 100 lignes (0 exclues - patient non apparié)
  Chez la référence : 92 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 90
  Clés UNIQUEMENT chez nous : 10
  Clés UNIQUEMENT chez la référence : 2
    ex: [(73, datetime.date(2117, 4, 4)), (75, datetime.date(2136, 3, 26)), (64, datetime.date(2155, 3, 12))]
    ex: [(64, datetime.date(2155, 3, 11)), (74, datetime.date(2103, 5, 18))]

Lignes appariées (même personne + même clé naturelle) : 90

## death_datetime : 32/32 lignes concordent (100.0%)

## cause_concept_id : ignoré (toujours vide chez nous sur les lignes appariées)
## cause_source_value : 0/90 lignes concordent (0.0%)
    ex: nous='SEPSIS' vs référence=None
    ex: nous='HEPATITIS B' vs référence=None
    ex: nous='SEPSIS' vs référence=None

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 0/90 (0.0%)

---

# Comparaison ligne à ligne — observation_period

Clé naturelle : person + ['observation_period_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 129 lignes
  Chez la référence : 129 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 129 lignes (0 exclues - patient non apparié)
  Chez la référence : 129 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 119
  Clés UNIQUEMENT chez nous : 10
  Clés UNIQUEMENT chez la référence : 10
    ex: [(65, datetime.date(2145, 9, 6)), (65, datetime.date(2145, 7, 7)), (26, datetime.date(2188, 2, 8))]
    ex: [(26, datetime.date(2188, 2, 7)), (65, datetime.date(2145, 9, 5)), (62, datetime.date(2159, 11, 16))]

Lignes appariées (même personne + même clé naturelle) : 119

## observation_period_end_date : 119/119 lignes concordent (100.0%)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 119/119 (100.0%)

---
