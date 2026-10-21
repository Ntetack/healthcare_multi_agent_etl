# Full Comparison Report

## Executive Summary

| Table | Rows (ours) | Rows (reference) | Matched | Fully Identical | Warning |
|---|---|---|---|---|---|
| person | 108 | 108 | 108 | 0/108 (0.0%) |  |
| visit_occurrence | 0 | 0 | 0 | n/a |  |
| condition_occurrence | 1728 | 1717 | 1717 | 1717/1717 (100.0%) | 11 ours-only / 0 reference-only |
| drug_exposure | 5446 | 5207 | 5206 | 1356/5206 (26.0%) | ⚠️ non-unique key (32/32 dupes) |
| procedure_occurrence | 10272 | 8560 | 8560 | 8560/8560 (100.0%) | ⚠️ non-unique key (15/15 dupes) |
| measurement | 46728 | 46612 | 46612 | 42603/46612 (91.4%) | ⚠️ non-unique key (1693/1687 dupes) |
| observation | 31885 | 24882 | 24789 | 18753/24789 (75.7%) | ⚠️ non-unique key (103/14 dupes) |
| death | 9 | 8 | 1 | 1/1 (100.0%) | 8 ours-only / 7 reference-only |
| observation_period | 108 | 108 | 107 | 89/107 (83.2%) | 1 ours-only / 1 reference-only |

**Overall row-level concordance across scored tables: 73079/87100 (83.9%) (1 table(s) excluded - undefined due to a non-unique key)**

## Per-Table Detail

# Comparaison ligne à ligne — person

Clé naturelle : person + ['person_source_value']

## Volumes bruts (avant tout filtrage)
  Chez nous : 108 lignes
  Chez la référence : 108 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 108

## Volumes après restriction aux patients communs
  Chez nous : 108 lignes (0 exclues - patient non apparié)
  Chez la référence : 108 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 108
  Clés UNIQUEMENT chez nous : 0
  Clés UNIQUEMENT chez la référence : 0

Lignes appariées (même personne + même clé naturelle) : 108

## gender_concept_id : 108/108 lignes concordent (100.0%)

## year_of_birth : 108/108 lignes concordent (100.0%)

## month_of_birth : 108/108 lignes concordent (100.0%)

## day_of_birth : 108/108 lignes concordent (100.0%)

## race_concept_id : 94/108 lignes concordent (87.0%)
    ex: nous=38003598 vs référence=8516
    ex: nous=38003598 vs référence=8516
    ex: nous=38003598 vs référence=8516

## ethnicity_concept_id : 0/108 lignes concordent (0.0%)
    ex: nous=0 vs référence=38003564
    ex: nous=0 vs référence=38003564
    ex: nous=0 vs référence=38003564

## gender_source_value : 108/108 lignes concordent (100.0%)

## race_source_value : 108/108 lignes concordent (100.0%)

## ethnicity_source_value : 108/108 lignes concordent (100.0%)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 0/108 (0.0%)

---

# Comparaison ligne à ligne — visit_occurrence

Clé naturelle : person + ['visit_concept_id', 'visit_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 0 lignes
  Chez la référence : 0 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 108

## Volumes après restriction aux patients communs
  Chez nous : 0 lignes (0 exclues - patient non apparié)
  Chez la référence : 0 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 0
  Clés UNIQUEMENT chez nous : 0
  Clés UNIQUEMENT chez la référence : 0

Lignes appariées (même personne + même clé naturelle) : 0

## visit_end_date : ignoré (toujours vide chez nous sur les lignes appariées)
## visit_source_value : ignoré (toujours vide chez nous sur les lignes appariées)
## visit_source_concept_id : ignoré (toujours vide chez nous sur les lignes appariées)
---

# Comparaison ligne à ligne — condition_occurrence

Clé naturelle : person + ['condition_concept_id', 'condition_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 1728 lignes
  Chez la référence : 1717 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 108

## Volumes après restriction aux patients communs
  Chez nous : 1728 lignes (0 exclues - patient non apparié)
  Chez la référence : 1717 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 1717
  Clés UNIQUEMENT chez nous : 11
  Clés UNIQUEMENT chez la référence : 0
    ex: [(80, 0, datetime.date(2024, 1, 28)), (78, 0, datetime.date(2020, 5, 4)), (105, 4272248, datetime.date(2022, 5, 8))]

Lignes appariées (même personne + même clé naturelle) : 1717

## condition_source_value : 1717/1717 lignes concordent (100.0%)

## condition_source_concept_id : 1717/1717 lignes concordent (100.0%)

## condition_end_date : 1218/1218 lignes concordent (100.0%)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 1717/1717 (100.0%)

---

# Comparaison ligne à ligne — drug_exposure

Clé naturelle : person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 5446 lignes
  Chez la référence : 5207 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 108

## Volumes après restriction aux patients communs
  Chez nous : 5446 lignes (0 exclues - patient non apparié)
  Chez la référence : 5207 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 32 doublon(s) chez nous, 32 chez la référence, sur (person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 5174
  Clés UNIQUEMENT chez nous : 240
  Clés UNIQUEMENT chez la référence : 1
    ex: [(64, 40213304, datetime.date(2017, 3, 25), datetime.date(2017, 3, 25)), (57, 37003436, datetime.date(2021, 6, 20), datetime.date(2021, 6, 20)), (21, 37003436, datetime.date(2021, 4, 28), datetime.date(2021, 4, 28))]
    ex: [(31, 19021481, datetime.date(1982, 10, 1), datetime.date(1983, 9, 26))]

Lignes appariées (même personne + même clé naturelle) : 5206

## drug_source_value : 5206/5206 lignes concordent (100.0%)

## drug_source_concept_id : 5206/5206 lignes concordent (100.0%)

## quantity : 0/3850 lignes concordent (0.0%)
    ex: nous=1.0 vs référence=0.0
    ex: nous=1.0 vs référence=0.0
    ex: nous=1.0 vs référence=0.0

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 1356/5206 (26.0%)

---

# Comparaison ligne à ligne — procedure_occurrence

Clé naturelle : person + ['procedure_concept_id', 'procedure_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 10272 lignes
  Chez la référence : 8560 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 108

## Volumes après restriction aux patients communs
  Chez nous : 10272 lignes (0 exclues - patient non apparié)
  Chez la référence : 8560 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 15 doublon(s) chez nous, 15 chez la référence, sur (person + ['procedure_concept_id', 'procedure_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 8545
  Clés UNIQUEMENT chez nous : 1712
  Clés UNIQUEMENT chez la référence : 0
    ex: [(1, 4036803, datetime.date(2009, 3, 30)), (106, 0, datetime.date(2017, 5, 24)), (39, 4263508, datetime.date(2025, 3, 13))]

Lignes appariées (même personne + même clé naturelle) : 8560

## procedure_source_value : 8560/8560 lignes concordent (100.0%)

## procedure_source_concept_id : 8560/8560 lignes concordent (100.0%)

## quantity : ignoré (toujours vide chez nous sur les lignes appariées)
## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 8560/8560 (100.0%)

---

# Comparaison ligne à ligne — measurement

Clé naturelle : person + ['measurement_concept_id', 'measurement_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 46728 lignes
  Chez la référence : 46612 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 108

## Volumes après restriction aux patients communs
  Chez nous : 46728 lignes (0 exclues - patient non apparié)
  Chez la référence : 46612 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 1693 doublon(s) chez nous, 1687 chez la référence, sur (person + ['measurement_concept_id', 'measurement_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 44925
  Clés UNIQUEMENT chez nous : 110
  Clés UNIQUEMENT chez la référence : 0
    ex: [(46, 3033727, datetime.date(2013, 1, 14)), (48, 3024120, datetime.date(2016, 8, 27)), (106, 3033727, datetime.date(2022, 6, 21))]

Lignes appariées (même personne + même clé naturelle) : 46612

## value_as_number : 35445/36096 lignes concordent (98.2%)
    ex: nous=865.9 vs référence=355.2
    ex: nous=4.3 vs référence=5.6
    ex: nous=5.0 vs référence=4.9

## unit_concept_id : 42968/46612 lignes concordent (92.2%)
    ex: nous=44777566 vs référence=0
    ex: nous=44777566 vs référence=0
    ex: nous=44777566 vs référence=0

## measurement_source_value : 46612/46612 lignes concordent (100.0%)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 42603/46612 (91.4%)

---

# Comparaison ligne à ligne — observation

Clé naturelle : person + ['observation_concept_id', 'observation_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 31885 lignes
  Chez la référence : 24882 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 108

## Volumes après restriction aux patients communs
  Chez nous : 31885 lignes (0 exclues - patient non apparié)
  Chez la référence : 24882 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 103 doublon(s) chez nous, 14 chez la référence, sur (person + ['observation_concept_id', 'observation_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 24775
  Clés UNIQUEMENT chez nous : 7007
  Clés UNIQUEMENT chez la référence : 93
    ex: [(45, 4145111, datetime.date(2020, 1, 7)), (60, 4085799, datetime.date(2017, 6, 21)), (68, 4203130, datetime.date(2023, 6, 18))]
    ex: [(52, 4122068, datetime.date(2005, 11, 11)), (26, 4224654, datetime.date(2020, 4, 21)), (29, 43530807, datetime.date(1993, 5, 3))]

Lignes appariées (même personne + même clé naturelle) : 24789

## value_as_number : 0/4276 lignes concordent (0.0%)
    ex: nous=42283.0 vs référence=None
    ex: nous=6.0 vs référence=None
    ex: nous=5.0 vs référence=None

## value_as_string : 0/1760 lignes concordent (0.0%)
    ex: nous='Received higher education (finding)' vs référence=None
    ex: nous='Full-time employment (finding)' vs référence=None
    ex: nous='Medication review due (situation)' vs référence=None

## observation_source_value : 24789/24789 lignes concordent (100.0%)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 18753/24789 (75.7%)

---

# Comparaison ligne à ligne — death

Clé naturelle : person + ['death_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 9 lignes
  Chez la référence : 8 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 108

## Volumes après restriction aux patients communs
  Chez nous : 9 lignes (0 exclues - patient non apparié)
  Chez la référence : 8 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 1
  Clés UNIQUEMENT chez nous : 8
  Clés UNIQUEMENT chez la référence : 7
    ex: [(46, datetime.date(2016, 6, 3)), (14, datetime.date(2026, 5, 3)), (58, datetime.date(2015, 9, 24))]
    ex: [(92, datetime.date(1961, 8, 25)), (53, datetime.date(1998, 10, 17)), (31, datetime.date(1991, 6, 8))]

Lignes appariées (même personne + même clé naturelle) : 1

## death_datetime : 1/1 lignes concordent (100.0%)

## cause_concept_id : ignoré (toujours vide chez nous sur les lignes appariées)
## cause_source_value : ignoré (toujours vide chez nous sur les lignes appariées)
## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 1/1 (100.0%)

---

# Comparaison ligne à ligne — observation_period

Clé naturelle : person + ['observation_period_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 108 lignes
  Chez la référence : 108 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 108

## Volumes après restriction aux patients communs
  Chez nous : 108 lignes (0 exclues - patient non apparié)
  Chez la référence : 108 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 107
  Clés UNIQUEMENT chez nous : 1
  Clés UNIQUEMENT chez la référence : 1
    ex: [(108, datetime.date(1955, 12, 11))]
    ex: [(108, datetime.date(1991, 5, 19))]

Lignes appariées (même personne + même clé naturelle) : 107

## observation_period_end_date : 89/107 lignes concordent (83.2%)
    ex: nous=datetime.date(2026, 5, 23) vs référence=datetime.date(2026, 5, 10)
    ex: nous=datetime.date(2026, 3, 7) vs référence=datetime.date(2026, 2, 18)
    ex: nous=datetime.date(2026, 2, 9) vs référence=datetime.date(2026, 2, 10)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 89/107 (83.2%)

---
