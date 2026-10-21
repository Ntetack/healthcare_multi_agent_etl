# Full Comparison Report

## Executive Summary

| Table | Rows (ours) | Rows (reference) | Matched | Fully Identical | Warning |
|---|---|---|---|---|---|
| person | 108 | 108 | 108 | 94/108 (87.0%) |  |
| visit_occurrence | 4089 | 0 | 0 | n/a | ⚠️ non-unique key (107/0 dupes) |
| condition_occurrence | 1728 | 1717 | 1717 | 1717/1717 (100.0%) | 11 ours-only / 0 reference-only |
| drug_exposure | 5446 | 5207 | 5270 | 5270/5270 (100.0%) | ⚠️ non-unique key (32/32 dupes) |
| procedure_occurrence | 10272 | 8560 | 8590 | 8590/8590 (100.0%) | ⚠️ non-unique key (15/15 dupes) |
| measurement | 46728 | 46612 | 50010 | 44931/50010 (89.8%) | ⚠️ non-unique key (1693/1687 dupes) |
| observation | 31885 | 24882 | 24857 | 0/24857 (0.0%) | ⚠️ non-unique key (103/14 dupes) |
| death | 9 | 8 | 1 | 1/1 (100.0%) | 8 ours-only / 7 reference-only |
| observation_period | 108 | 108 | 107 | 91/107 (85.0%) | 1 ours-only / 1 reference-only |

**Overall row-level concordance across scored tables: 60694/90660 (66.9%) (1 table(s) excluded - undefined due to a non-unique key)**

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

## ethnicity_concept_id : 108/108 lignes concordent (100.0%)

## gender_source_value : 108/108 lignes concordent (100.0%)

## race_source_value : 108/108 lignes concordent (100.0%)

## ethnicity_source_value : 108/108 lignes concordent (100.0%)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 94/108 (87.0%)

---

# Comparaison ligne à ligne — visit_occurrence

Clé naturelle : person + ['visit_concept_id', 'visit_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 4089 lignes
  Chez la référence : 0 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 108

## Volumes après restriction aux patients communs
  Chez nous : 4089 lignes (0 exclues - patient non apparié)
  Chez la référence : 0 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 107 doublon(s) chez nous, 0 chez la référence, sur (person + ['visit_concept_id', 'visit_start_date']). Les comparaisons ci-dessous compareront des COMBINAISONS pour ces lignes, pas des lignes individuelles fiables - ajoutez un champ à la clé naturelle (ex: une date ou une heure) pour qu'elle identifie vraiment une seule ligne.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 0
  Clés UNIQUEMENT chez nous : 3982
  Clés UNIQUEMENT chez la référence : 0
    ex: [(74, 581479, datetime.date(2009, 10, 2)), (53, 581479, datetime.date(1997, 11, 29)), (44, 581479, datetime.date(2017, 6, 13))]

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
    ex: [(100, 4272248, datetime.date(2016, 9, 12)), (80, 0, datetime.date(2024, 1, 28)), (70, 4272248, datetime.date(2024, 1, 20))]

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
    ex: [(28, 37003436, datetime.date(2021, 5, 4), datetime.date(2021, 5, 4)), (3, 37003436, datetime.date(2021, 3, 2), datetime.date(2021, 3, 2)), (93, 37003518, datetime.date(2021, 4, 28), datetime.date(2021, 4, 28))]
    ex: [(31, 19021481, datetime.date(1982, 10, 1), datetime.date(1983, 9, 26))]

Lignes appariées (même personne + même clé naturelle) : 5270

## drug_source_value : 5270/5270 lignes concordent (100.0%)

## drug_source_concept_id : 5270/5270 lignes concordent (100.0%)

## quantity : ignoré (toujours vide chez nous sur les lignes appariées)
## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 5270/5270 (100.0%)

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
    ex: [(54, 4155973, datetime.date(2026, 4, 3)), (28, 4263508, datetime.date(2016, 12, 9)), (44, 4036803, datetime.date(2017, 5, 9))]

Lignes appariées (même personne + même clé naturelle) : 8590

## procedure_source_value : 8590/8590 lignes concordent (100.0%)

## procedure_source_concept_id : 8590/8590 lignes concordent (100.0%)

## quantity : ignoré (toujours vide chez nous sur les lignes appariées)
## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 8590/8590 (100.0%)

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
    ex: [(46, 3033727, datetime.date(2011, 2, 24)), (46, 3032240, datetime.date(2013, 12, 10)), (39, 3032240, datetime.date(2023, 5, 26))]

Lignes appariées (même personne + même clé naturelle) : 50010

## value_as_number : 36657/38084 lignes concordent (96.3%)
    ex: nous=3.9 vs référence=5.7
    ex: nous=5.1 vs référence=4.9
    ex: nous=11.5 vs référence=14.5

## unit_concept_id : 45672/50010 lignes concordent (91.3%)
    ex: nous=44777566 vs référence=0
    ex: nous=44777566 vs référence=0
    ex: nous=44777566 vs référence=0

## measurement_source_value : 50010/50010 lignes concordent (100.0%)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 44931/50010 (89.8%)

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
    ex: [(22, 4313474, datetime.date(2021, 1, 12)), (60, 4085798, datetime.date(2024, 11, 2)), (52, 4054945, datetime.date(2019, 12, 3))]
    ex: [(57, 42538933, datetime.date(2001, 1, 3)), (52, 4122068, datetime.date(2005, 11, 11)), (67, 4117479, datetime.date(2006, 4, 9))]

Lignes appariées (même personne + même clé naturelle) : 24857

## value_as_number : 0/4276 lignes concordent (0.0%)
    ex: nous=42283.0 vs référence=None
    ex: nous=6.0 vs référence=None
    ex: nous=5.0 vs référence=None

## value_as_string : 0/24857 lignes concordent (0.0%)
    ex: nous='Received higher education (finding)' vs référence=None
    ex: nous='Full-time employment (finding)' vs référence=None
    ex: nous='Medication review due (situation)' vs référence=None

## observation_source_value : 24857/24857 lignes concordent (100.0%)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 0/24857 (0.0%)

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
    ex: [(53, datetime.date(1998, 10, 8)), (74, datetime.date(2018, 9, 23)), (46, datetime.date(2016, 6, 3))]
    ex: [(92, datetime.date(1961, 8, 25)), (53, datetime.date(1998, 10, 17)), (46, datetime.date(2016, 6, 13))]

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

## observation_period_end_date : 91/107 lignes concordent (85.0%)
    ex: nous=datetime.date(2026, 5, 23) vs référence=datetime.date(2026, 5, 10)
    ex: nous=datetime.date(2026, 3, 7) vs référence=datetime.date(2026, 2, 18)
    ex: nous=datetime.date(2026, 6, 7) vs référence=datetime.date(2026, 6, 5)

## Résumé : lignes ENTIÈREMENT identiques (tous les champs vérifiés à la fois) : 91/107 (85.0%)

---
