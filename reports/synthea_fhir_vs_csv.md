# Full Comparison Report

## Executive Summary

| Table | Rows (ours) | Rows (reference) | Matched | Fully Identical | Warning |
|---|---|---|---|---|---|
| person | 114 | 114 | 114 | 0/114 (0.0%) |  |
| visit_occurrence | 6705 | 6703 | 44 | 0/44 (0.0%) | ⚠️ non-unique key (1970/246 dupes) |
| condition_occurrence | 1985 | 1985 | 1270 | 956/1270 (75.3%) | 715 ours-only / 715 reference-only |
| drug_exposure | 7624 | 7616 | 2165 | 0/2165 (0.0%) | ⚠️ non-unique key (58/47 dupes) |
| procedure_occurrence | 11974 | 11977 | 5724 | 5724/5724 (100.0%) | ⚠️ non-unique key (131/22 dupes) |
| measurement | 57621 | 55920 | 30807 | 8186/30807 (26.6%) | ⚠️ non-unique key (1713/1688 dupes) |
| observation | 40979 | 39850 | 19269 | 4541/19269 (23.6%) | ⚠️ non-unique key (351/208 dupes) |
| death | 14 | 14 | 7 | 0/7 (0.0%) | 7 ours-only / 7 reference-only |
| observation_period | 2330 | 6414 | 13 | 13/13 (100.0%) | ⚠️ non-unique key (4/0 dupes) |

**Overall row-level concordance across scored tables: 19420/59413 (32.7%)**

## Per-Table Detail

# Comparaison ligne à ligne — person

Clé naturelle : person + ['person_source_value']

## Volumes bruts (avant tout filtrage)
  Chez nous : 114 lignes
  Chez la référence : 114 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 114 lignes (0 exclues - patient non apparié)
  Chez la référence : 114 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 114
  Clés UNIQUEMENT chez nous : 0
  Clés UNIQUEMENT chez la référence : 0

Lignes appariées (même personne + même clé naturelle) : 114

## gender_concept_id : 114/114 lignes concordent (100.0%)

## year_of_birth : 114/114 lignes concordent (100.0%)

## month_of_birth : 114/114 lignes concordent (100.0%)

## day_of_birth : 114/114 lignes concordent (100.0%)

## race_concept_id : 114/114 lignes concordent (100.0%)

## ethnicity_concept_id : 114/114 lignes concordent (100.0%)

## gender_source_value : 0/114 lignes concordent (0.0%)
    ex: nous='female' vs référence='F'
    ex: nous='male' vs référence='M'
    ex: nous='male' vs référence='M'

## race_source_value : 0/114 lignes concordent (0.0%)
    ex: nous='White' vs référence='white'
    ex: nous='Black or African American' vs référence='black'
    ex: nous='Black or African American' vs référence='black'

## ethnicity_source_value : 0/114 lignes concordent (0.0%)
    ex: nous='Not Hispanic or Latino' vs référence='nonhispanic'
    ex: nous='Hispanic or Latino' vs référence='hispanic'
    ex: nous='Not Hispanic or Latino' vs référence='nonhispanic'

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 0/114 (0.0%)

---

# Comparaison ligne à ligne — visit_occurrence

Clé naturelle : person + ['visit_concept_id', 'visit_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 6705 lignes
  Chez la référence : 6703 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 6705 lignes (0 exclues - patient non apparié)
  Chez la référence : 6703 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 1970 doublon(s) chez nous, 246 chez la référence, sur (person + ['visit_concept_id', 'visit_start_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 44
  Clés UNIQUEMENT chez nous : 4691
  Clés UNIQUEMENT chez la référence : 6413
    ex: [(114, 9202, datetime.date(1985, 10, 26)), (114, 9202, datetime.date(2020, 7, 16)), (114, 9202, datetime.date(2009, 8, 23))]
    ex: [(14, 9202, datetime.date(1993, 7, 3)), (92, 9202, datetime.date(2014, 1, 29)), (30, 9202, datetime.date(2018, 12, 8))]

Lignes appariées (même personne + même clé naturelle) : 44

## visit_end_date : 43/44 lignes concordent (97.7%)
    ex: nous=datetime.date(2023, 6, 10) vs référence=datetime.date(2023, 5, 10)

## visit_source_value : 0/44 lignes concordent (0.0%)
    ex: nous='General examination of patient (procedure)' vs référence='outpatient'
    ex: nous='Encounter for check up (procedure)' vs référence='ambulatory'
    ex: nous='Encounter for check up (procedure)' vs référence='wellness'

## visit_source_concept_id : ignoré (toujours vide chez nous sur les lignes appariées)
## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 0/44 (0.0%)

---

# Comparaison ligne à ligne — condition_occurrence

Clé naturelle : person + ['condition_concept_id', 'condition_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 1985 lignes
  Chez la référence : 1985 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 1985 lignes (0 exclues - patient non apparié)
  Chez la référence : 1985 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 1270
  Clés UNIQUEMENT chez nous : 715
  Clés UNIQUEMENT chez la référence : 715
    ex: [(95, 4112343, datetime.date(2019, 4, 2)), (66, 4112343, datetime.date(2017, 1, 4)), (95, 4309238, datetime.date(2014, 3, 2))]
    ex: [(47, 4112343, datetime.date(2024, 4, 10)), (109, 443614, datetime.date(2016, 6, 1)), (25, 4112343, datetime.date(2019, 6, 3))]

Lignes appariées (même personne + même clé naturelle) : 1270

## condition_source_value : 1269/1270 lignes concordent (99.9%)
    ex: nous='' vs référence='365853002'

## condition_source_concept_id : 1270/1270 lignes concordent (100.0%)

## condition_end_date : 561/874 lignes concordent (64.2%)
    ex: nous=datetime.date(2021, 7, 4) vs référence=datetime.date(2021, 4, 7)
    ex: nous=datetime.date(2024, 4, 10) vs référence=datetime.date(2024, 10, 4)
    ex: nous=datetime.date(2017, 6, 3) vs référence=datetime.date(2017, 3, 6)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 956/1270 (75.3%)

---

# Comparaison ligne à ligne — drug_exposure

Clé naturelle : person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 7624 lignes
  Chez la référence : 7616 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 7624 lignes (0 exclues - patient non apparié)
  Chez la référence : 7616 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 58 doublon(s) chez nous, 47 chez la référence, sur (person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 2132
  Clés UNIQUEMENT chez nous : 5434
  Clés UNIQUEMENT chez la référence : 5437
    ex: [(105, 19030765, datetime.date(1987, 12, 3), datetime.date(1987, 12, 3)), (92, 19073094, datetime.date(2006, 12, 27), datetime.date(2006, 12, 27)), (102, 1115171, datetime.date(2020, 10, 17), datetime.date(2020, 10, 17))]
    ex: [(105, 19030765, datetime.date(1984, 10, 7), datetime.date(1984, 10, 7)), (92, 19080128, datetime.date(2014, 4, 30), datetime.date(2014, 5, 7)), (92, 40163554, datetime.date(2006, 3, 1), datetime.date(2006, 3, 8))]

Lignes appariées (même personne + même clé naturelle) : 2165

## drug_source_value : 0/2165 lignes concordent (0.0%)
    ex: nous='Administration of vaccine product containing only ' vs référence='399014008'
    ex: nous='Administration of vaccine product containing only ' vs référence='399014008'
    ex: nous='Administration of vaccine product containing only ' vs référence='399014008'

## drug_source_concept_id : 2165/2165 lignes concordent (100.0%)

## quantity : 21/70 lignes concordent (30.0%)
    ex: nous=1.0 vs référence=3.0
    ex: nous=1.0 vs référence=3.0
    ex: nous=1.0 vs référence=3.0

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 0/2165 (0.0%)

---

# Comparaison ligne à ligne — procedure_occurrence

Clé naturelle : person + ['procedure_concept_id', 'procedure_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 11974 lignes
  Chez la référence : 11977 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 11974 lignes (0 exclues - patient non apparié)
  Chez la référence : 11977 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 131 doublon(s) chez nous, 22 chez la référence, sur (person + ['procedure_concept_id', 'procedure_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 5713
  Clés UNIQUEMENT chez nous : 6130
  Clés UNIQUEMENT chez la référence : 6242
    ex: [(74, 4180248, datetime.date(2019, 2, 20)), (68, 762506, datetime.date(2018, 6, 4)), (73, 46272459, datetime.date(2024, 9, 15))]
    ex: [(86, 4180248, datetime.date(2026, 4, 2)), (63, 4305852, datetime.date(2013, 3, 12)), (34, 46272459, datetime.date(2017, 7, 6))]

Lignes appariées (même personne + même clé naturelle) : 5724

## procedure_source_value : 5724/5724 lignes concordent (100.0%)

## procedure_source_concept_id : 5724/5724 lignes concordent (100.0%)

## quantity : ignoré (toujours vide chez nous sur les lignes appariées)
## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 5724/5724 (100.0%)

---

# Comparaison ligne à ligne — measurement

Clé naturelle : person + ['measurement_concept_id', 'measurement_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 57621 lignes
  Chez la référence : 55920 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 57621 lignes (0 exclues - patient non apparié)
  Chez la référence : 55920 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 1713 doublon(s) chez nous, 1688 chez la référence, sur (person + ['measurement_concept_id', 'measurement_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 29842
  Clés UNIQUEMENT chez nous : 26066
  Clés UNIQUEMENT chez la référence : 24390
    ex: [(59, 3012888, datetime.date(2022, 6, 10)), (105, 3005897, datetime.date(1986, 11, 12)), (91, 36203185, datetime.date(2019, 9, 22))]
    ex: [(82, 3027801, datetime.date(2025, 11, 12)), (12, 3025315, datetime.date(2018, 9, 3)), (109, 3000285, datetime.date(2020, 7, 8))]

Lignes appariées (même personne + même clé naturelle) : 30807

## value_as_number : 7551/24496 lignes concordent (30.8%)
    ex: nous=19.38 vs référence=19.4
    ex: nous=58.563 vs référence=58.6
    ex: nous=19.91 vs référence=19.9

## unit_concept_id : 8635/30807 lignes concordent (28.0%)
    ex: nous=0 vs référence=8582
    ex: nous=0 vs référence=44777566
    ex: nous=0 vs référence=9529

## measurement_source_value : 30807/30807 lignes concordent (100.0%)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 8186/30807 (26.6%)

---

# Comparaison ligne à ligne — observation

Clé naturelle : person + ['observation_concept_id', 'observation_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 40979 lignes
  Chez la référence : 39850 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 40979 lignes (0 exclues - patient non apparié)
  Chez la référence : 39850 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 351 doublon(s) chez nous, 208 chez la référence, sur (person + ['observation_concept_id', 'observation_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 19248
  Clés UNIQUEMENT chez nous : 21380
  Clés UNIQUEMENT chez la référence : 20394
    ex: [(60, 37020172, datetime.date(2017, 5, 7)), (10, 42868746, datetime.date(2021, 2, 18)), (114, 0, datetime.date(2006, 9, 20))]
    ex: [(51, 37020032, datetime.date(2023, 1, 22)), (33, 46235654, datetime.date(1979, 4, 21)), (38, 40766311, datetime.date(2023, 4, 8))]

Lignes appariées (même personne + même clé naturelle) : 19269

## value_as_number : 2611/2849 lignes concordent (91.6%)
    ex: nous=1.1441 vs référence=1.1
    ex: nous=1.413 vs référence=1.4
    ex: nous=4.9424 vs référence=4.9

## value_as_string : 2013/16741 lignes concordent (12.0%)
    ex: nous='' vs référence='Never smoked tobacco (finding)'
    ex: nous='' vs référence='1.0'
    ex: nous='' vs référence='Never smoked tobacco (finding)'

## observation_source_value : 19269/19269 lignes concordent (100.0%)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 4541/19269 (23.6%)

---

# Comparaison ligne à ligne — death

Clé naturelle : person + ['death_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 14 lignes
  Chez la référence : 14 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 14 lignes (0 exclues - patient non apparié)
  Chez la référence : 14 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 7
  Clés UNIQUEMENT chez nous : 7
  Clés UNIQUEMENT chez la référence : 7
    ex: [(63, datetime.date(2020, 3, 7)), (27, datetime.date(2016, 7, 6)), (64, datetime.date(1973, 5, 9))]
    ex: [(27, datetime.date(2016, 6, 7)), (85, datetime.date(1987, 9, 2)), (63, datetime.date(2020, 7, 3))]

Lignes appariées (même personne + même clé naturelle) : 7

## death_datetime : 0/7 lignes concordent (0.0%)
    ex: nous=Timestamp('1993-12-28 00:10:35') vs référence=Timestamp('1993-12-28 00:00:00')
    ex: nous=Timestamp('2021-01-13 09:53:22') vs référence=Timestamp('2021-01-13 00:00:00')
    ex: nous=Timestamp('2025-12-13 08:07:49') vs référence=Timestamp('2025-12-13 00:00:00')

## cause_concept_id : ignoré (toujours vide chez nous sur les lignes appariées)
## cause_source_value : ignoré (toujours vide chez nous sur les lignes appariées)
## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 0/7 (0.0%)

---

# Comparaison ligne à ligne — observation_period

Clé naturelle : person + ['observation_period_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 2330 lignes
  Chez la référence : 6414 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 2330 lignes (0 exclues - patient non apparié)
  Chez la référence : 6414 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 4 doublon(s) chez nous, 0 chez la référence, sur (person + ['observation_period_start_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 13
  Clés UNIQUEMENT chez nous : 2313
  Clés UNIQUEMENT chez la référence : 6401
    ex: [(114, datetime.date(1985, 7, 14)), (114, datetime.date(1993, 4, 11)), (114, datetime.date(1978, 12, 5))]
    ex: [(86, datetime.date(2024, 10, 9)), (92, datetime.date(2014, 3, 12)), (62, datetime.date(2018, 3, 13))]

Lignes appariées (même personne + même clé naturelle) : 13

## observation_period_end_date : 13/13 lignes concordent (100.0%)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 13/13 (100.0%)

---
