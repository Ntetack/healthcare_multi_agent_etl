# Full Comparison Report

## Executive Summary

| Table | Rows (ours) | Rows (reference) | Matched | Fully Identical | Warning |
|---|---|---|---|---|---|
| person | 114 | 114 | 114 | 0/114 (0.0%) |  |
| visit_occurrence | 6705 | 6703 | 44 | 0/44 (0.0%) | ⚠️ non-unique key (1844/242 dupes) |
| condition_occurrence | 1985 | 1985 | 1269 | 956/1269 (75.3%) | 716 ours-only / 716 reference-only |
| drug_exposure | 7624 | 7616 | 0 | n/a | ⚠️ non-unique key (58/59 dupes) |
| procedure_occurrence | 11974 | 11977 | 5724 | 5724/5724 (100.0%) | ⚠️ non-unique key (131/22 dupes) |
| measurement | 57621 | 55920 | 14880 | 9158/14880 (61.5%) | ⚠️ non-unique key (1102/1111 dupes) |
| observation | 40979 | 39850 | 19269 | 4541/19269 (23.6%) | ⚠️ non-unique key (351/207 dupes) |
| death | 14 | 14 | 7 | 0/7 (0.0%) | 7 ours-only / 7 reference-only |
| observation_period | 2330 | 6414 | 13 | n/a | 2317 ours-only / 6401 reference-only |

**Overall row-level concordance across scored tables: 20379/41307 (49.3%) (2 table(s) excluded - undefined due to a non-unique key)**

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

## gender_source_value : 0/114 lignes concordent (0.0%)
    ex: nous='female' vs référence='F'
    ex: nous='male' vs référence='M'
    ex: nous='male' vs référence='M'

## race_source_value : 0/114 lignes concordent (0.0%)
    ex: nous='White' vs référence='white'
    ex: nous='Black or African American' vs référence='black'
    ex: nous='Black or African American' vs référence='black'

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 0/114 (0.0%)

---

# Comparaison ligne à ligne — visit_occurrence

Clé naturelle : person + ['visit_start_date', 'visit_end_date', 'visit_concept_id']

## Volumes bruts (avant tout filtrage)
  Chez nous : 6705 lignes
  Chez la référence : 6703 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 6705 lignes (0 exclues - patient non apparié)
  Chez la référence : 6703 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 1844 doublon(s) chez nous, 242 chez la référence, sur (person + ['visit_start_date', 'visit_end_date', 'visit_concept_id']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 44
  Clés UNIQUEMENT chez nous : 4817
  Clés UNIQUEMENT chez la référence : 6417
    ex: [(114, datetime.date(2022, 4, 4), datetime.date(2022, 4, 4), 9202), (114, datetime.date(2020, 11, 11), datetime.date(2020, 11, 11), 9202), (114, datetime.date(2010, 1, 13), datetime.date(2010, 1, 13), 9202)]
    ex: [(34, datetime.date(2011, 3, 13), datetime.date(2011, 3, 22), 9203), (105, datetime.date(1986, 6, 8), datetime.date(1986, 6, 8), 9202), (34, datetime.date(2022, 6, 23), datetime.date(2022, 6, 23), 9202)]

Lignes appariées (même personne + même clé naturelle) : 44

## visit_source_value : 0/44 lignes concordent (0.0%)
    ex: nous='General examination of patient (procedure)' vs référence='outpatient'
    ex: nous='Encounter for check up (procedure)' vs référence='ambulatory'
    ex: nous='Outpatient procedure (procedure)' vs référence='wellness'

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 0/44 (0.0%)

---

# Comparaison ligne à ligne — condition_occurrence

Clé naturelle : person + ['condition_source_value', 'condition_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 1985 lignes
  Chez la référence : 1985 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 1985 lignes (0 exclues - patient non apparié)
  Chez la référence : 1985 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 1269
  Clés UNIQUEMENT chez nous : 716
  Clés UNIQUEMENT chez la référence : 716
    ex: [(33, '274531002', datetime.date(1978, 4, 2)), (109, '127013003', datetime.date(1997, 3, 9)), (67, '195662009', datetime.date(2025, 4, 10))]
    ex: [(71, '444814009', datetime.date(2020, 7, 9)), (30, '271737000', datetime.date(2018, 12, 8)), (70, '18718003', datetime.date(2024, 10, 6))]

Lignes appariées (même personne + même clé naturelle) : 1269

## condition_concept_id : 1269/1269 lignes concordent (100.0%)

## condition_source_concept_id : 1269/1269 lignes concordent (100.0%)

## condition_end_date : 561/874 lignes concordent (64.2%)
    ex: nous=datetime.date(2021, 7, 4) vs référence=datetime.date(2021, 4, 7)
    ex: nous=datetime.date(2024, 4, 10) vs référence=datetime.date(2024, 10, 4)
    ex: nous=datetime.date(2017, 6, 3) vs référence=datetime.date(2017, 3, 6)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 956/1269 (75.3%)

---

# Comparaison ligne à ligne — drug_exposure

Clé naturelle : person + ['drug_source_value', 'drug_exposure_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 7624 lignes
  Chez la référence : 7616 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 7624 lignes (0 exclues - patient non apparié)
  Chez la référence : 7616 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 58 doublon(s) chez nous, 59 chez la référence, sur (person + ['drug_source_value', 'drug_exposure_start_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 0
  Clés UNIQUEMENT chez nous : 7566
  Clés UNIQUEMENT chez la référence : 7557
    ex: [(31, 'COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose', datetime.date(2021, 4, 30)), (62, '1 ML Epoetin Alfa 4000 UNT/ML Injection [Epogen]', datetime.date(2023, 10, 16)), (62, '1 ML Epoetin Alfa 4000 UNT/ML Injection [Epogen]', datetime.date(2023, 12, 8))]
    ex: [(92, '314076', datetime.date(2008, 7, 30)), (92, '205923', datetime.date(2010, 6, 20)), (92, '855332', datetime.date(2014, 7, 2))]

Lignes appariées (même personne + même clé naturelle) : 0

## drug_concept_id : ignoré (toujours vide chez nous sur les lignes appariées)
## drug_source_concept_id : ignoré (toujours vide chez nous sur les lignes appariées)
## drug_exposure_end_date : ignoré (toujours vide chez nous sur les lignes appariées)
---

# Comparaison ligne à ligne — procedure_occurrence

Clé naturelle : person + ['procedure_source_value', 'procedure_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 11974 lignes
  Chez la référence : 11977 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 11974 lignes (0 exclues - patient non apparié)
  Chez la référence : 11977 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 131 doublon(s) chez nous, 22 chez la référence, sur (person + ['procedure_source_value', 'procedure_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 5713
  Clés UNIQUEMENT chez nous : 6130
  Clés UNIQUEMENT chez la référence : 6242
    ex: [(104, '710824005', datetime.date(1979, 7, 15)), (63, '65677008', datetime.date(2013, 12, 3)), (114, '371883000', datetime.date(2023, 2, 21))]
    ex: [(52, '428211000124100', datetime.date(2019, 3, 9)), (13, '162673000', datetime.date(2015, 10, 14)), (102, '162673000', datetime.date(2020, 3, 11))]

Lignes appariées (même personne + même clé naturelle) : 5724

## procedure_concept_id : 5724/5724 lignes concordent (100.0%)

## procedure_source_concept_id : 5724/5724 lignes concordent (100.0%)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 5724/5724 (100.0%)

---

# Comparaison ligne à ligne — measurement

Clé naturelle : person + ['measurement_source_value', 'measurement_date', 'value_as_number']

## Volumes bruts (avant tout filtrage)
  Chez nous : 57621 lignes
  Chez la référence : 55920 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 57621 lignes (0 exclues - patient non apparié)
  Chez la référence : 55920 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 1102 doublon(s) chez nous, 1111 chez la référence, sur (person + ['measurement_source_value', 'measurement_date', 'value_as_number']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 7563
  Clés UNIQUEMENT chez nous : 49835
  Clés UNIQUEMENT chez la référence : 48132
    ex: [(110, '2075-0', datetime.date(1988, 2, 14), 103.63), (13, '171207006', datetime.date(2016, 10, 19), nan), (109, '5802-4', datetime.date(2020, 8, 7), nan)]
    ex: [(92, '33914-3', datetime.date(2007, 8, 8), 36.4), (92, '33914-3', datetime.date(2007, 12, 5), 42.5), (69, '77606-2', datetime.date(2024, 5, 1), 69.6)]

Lignes appariées (même personne + même clé naturelle) : 14880

## measurement_concept_id : 14836/14880 lignes concordent (99.7%)
    ex: nous=4131378 vs référence=3032240
    ex: nous=4135663 vs référence=3033727
    ex: nous=4131378 vs référence=3032240

## unit_concept_id : 9202/14880 lignes concordent (61.8%)
    ex: nous=0 vs référence=8582
    ex: nous=0 vs référence=44777566
    ex: nous=0 vs référence=9529

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 9158/14880 (61.5%)

---

# Comparaison ligne à ligne — observation

Clé naturelle : person + ['observation_source_value', 'observation_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 40979 lignes
  Chez la référence : 39850 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 40979 lignes (0 exclues - patient non apparié)
  Chez la référence : 39850 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 351 doublon(s) chez nous, 207 chez la référence, sur (person + ['observation_source_value', 'observation_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 19248
  Clés UNIQUEMENT chez nous : 21380
  Clés UNIQUEMENT chez la référence : 20395
    ex: [(92, '93030-5', datetime.date(2013, 7, 8)), (103, '93028-9', datetime.date(2025, 10, 1)), (16, '72166-2', datetime.date(2023, 3, 16))]
    ex: [(20, '93029-7', datetime.date(2022, 9, 12)), (89, '185349003', datetime.date(2021, 6, 11)), (56, '93035-4', datetime.date(2026, 5, 9))]

Lignes appariées (même personne + même clé naturelle) : 19269

## observation_concept_id : 19269/19269 lignes concordent (100.0%)

## value_as_number : 2611/2849 lignes concordent (91.6%)
    ex: nous=1.1441 vs référence=1.1
    ex: nous=1.413 vs référence=1.4
    ex: nous=4.9424 vs référence=4.9

## value_as_string : 2013/16741 lignes concordent (12.0%)
    ex: nous='' vs référence='Never smoked tobacco (finding)'
    ex: nous='' vs référence='1.0'
    ex: nous='' vs référence='Never smoked tobacco (finding)'

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
    ex: [(85, datetime.date(1987, 2, 9)), (92, datetime.date(2015, 6, 3)), (105, datetime.date(1994, 10, 7))]
    ex: [(33, datetime.date(1983, 7, 1)), (85, datetime.date(1987, 9, 2)), (105, datetime.date(1994, 7, 10))]

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

Clé naturelle : person + ['observation_period_start_date', 'observation_period_end_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 2330 lignes
  Chez la référence : 6414 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 2330 lignes (0 exclues - patient non apparié)
  Chez la référence : 6414 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 13
  Clés UNIQUEMENT chez nous : 2317
  Clés UNIQUEMENT chez la référence : 6401
    ex: [(114, datetime.date(1992, 6, 19), datetime.date(1992, 6, 20)), (114, datetime.date(2013, 1, 5), datetime.date(2013, 1, 5)), (114, datetime.date(2023, 1, 16), datetime.date(2023, 1, 16))]
    ex: [(109, datetime.date(2018, 1, 17), datetime.date(2018, 1, 17)), (13, datetime.date(2020, 11, 11), datetime.date(2020, 11, 11)), (92, datetime.date(2009, 4, 15), datetime.date(2009, 4, 15))]

Lignes appariées (même personne + même clé naturelle) : 13

---
