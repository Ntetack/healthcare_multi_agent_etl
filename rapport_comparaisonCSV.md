# Full Comparison Report

## Executive Summary

| Table | Rows (ours) | Rows (reference) | Matched | Coverage of the reference | Semantic agreement | Provenance (not scored) | Note |
|---|---|---|---|---|---|---|---|
| person | 114 | 114 | 114 | 114/114 (100.0%) | 109/114 (95.6%) | 100.0% |  |
| visit_occurrence | 6703 | 6110 | 6110 | 6110/6110 (100.0%) | 6098/6110 (99.8%) | 0.0% | non-unique key (246/7 dupes, paired by signature); 354 ours-only / 0 reference-only keys |
| condition_occurrence | 1985 | 1973 | 1973 | 1973/1973 (100.0%) | 1973/1973 (100.0%) | 100.0% | 12 ours-only / 0 reference-only keys |
| drug_exposure | 7616 | 7382 | 7382 | 7382/7382 (100.0%) | 0/7382 (0.0%) | 100.0% | non-unique key (47/47 dupes, paired by signature); 234 ours-only / 0 reference-only keys |
| procedure_occurrence | 11977 | 10154 | 10154 | 10154/10154 (100.0%) | 10154/10154 (100.0%) | 100.0% | non-unique key (22/22 dupes, paired by signature); 1823 ours-only / 0 reference-only keys |
| measurement | 55920 | 55833 | 55833 | 55833/55833 (100.0%) | 50742/55833 (90.9%) | 99.8% | non-unique key (1688/1682 dupes, paired by signature); 81 ours-only / 0 reference-only keys |
| observation | 39850 | 30324 | 30242 | 30242/30324 (99.7%) | 30242/30242 (100.0%) | 100.0% | non-unique key (208/26 dupes, paired by signature); 9426 ours-only / 82 reference-only keys |
| death | 14 | 14 | 0 | 0/14 (0.0%) | n/a | n/a | 14 events found with another date; 14 ours-only / 14 reference-only keys |
| observation_period | 6414 | 6110 | 6080 | 6080/6110 (99.5%) | 6069/6080 (99.8%) | n/a | non-unique key (0/18 dupes, paired by signature); 5 events found with another date; 334 ours-only / 12 reference-only keys |

**Coverage of the reference (rows found here / rows of the reference): 117888/118014 (99.9%)**

**Semantic agreement (matched rows whose meaning agrees, weighted by rows): 105387/117888 (89.4%)**

**Reference rows reproduced with the same meaning (found AND agreeing): 105387/118000 (89.3%)**

Provenance fields (`*_source_value`, `*_source_concept_id`) are listed per table but are not part of any figure above: they record how the source wrote a value, which two faithful exports may do differently.

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
  Couverture de la référence : 114/114 (100.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 114/114 (100.0%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## gender_concept_id : 114/114 lignes concordent (100.0%)  [concept]

## year_of_birth : 114/114 lignes concordent (100.0%)  [exact]

## month_of_birth : 114/114 lignes concordent (100.0%)  [exact]

## day_of_birth : 114/114 lignes concordent (100.0%)  [exact]

## birth_datetime : 114/114 lignes concordent (100.0%)  [datetime]

## race_concept_id : 108/113 lignes concordent (95.6%)  [concept]
    ex: nous=np.int64(8657) vs référence=np.int64(0)
    ex: nous=np.int64(8657) vs référence=np.int64(0)
    ex: nous=np.int64(8557) vs référence=np.int64(0)

## ethnicity_concept_id : 114/114 lignes concordent (100.0%)  [concept]

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## gender_source_value : 114/114 lignes concordent (100.0%)  [text]

## race_source_value : 114/114 lignes concordent (100.0%)  [text]

## ethnicity_source_value : 114/114 lignes concordent (100.0%)  [text]

# Écarts de portée (champs exclus du score)

  gender_source_concept_id : renseigné seulement chez nous
  race_source_concept_id : renseigné seulement chez nous
  ethnicity_source_concept_id : vide des deux côtés

## Résumé
  Couverture de la référence : 100.0%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 109/114 (95.6%)
  Accord sémantique par champ (toutes les valeurs comparées) : 99.4%
  Accord de provenance (hors score) : 100.0%

---

# Comparaison ligne à ligne — visit_occurrence

Clé naturelle : person + ['visit_concept_id', 'visit_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 6703 lignes
  Chez la référence : 6110 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 6703 lignes (0 exclues - patient non apparié)
  Chez la référence : 6110 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 246 doublon(s) chez nous, 7 chez la référence, sur (person + ['visit_concept_id', 'visit_start_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 6103
  Clés UNIQUEMENT chez nous : 354
  Clés UNIQUEMENT chez la référence : 0
    ex: [(57, 9203, datetime.date(2000, 1, 4)), (110, 9203, datetime.date(2006, 10, 11)), (47, 9203, datetime.date(2025, 3, 24))]

Lignes appariées (même personne + même clé naturelle) : 6110
  Couverture de la référence : 6110/6110 (100.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 6110/6703 (91.2%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## visit_start_datetime : 6110/6110 lignes concordent (100.0%)  [datetime]

## visit_end_date : 6098/6110 lignes concordent (99.8%)  [date]
    ex: nous=datetime.date(2022, 10, 26) vs référence=datetime.date(2022, 10, 27)
    ex: nous=datetime.date(2020, 4, 19) vs référence=datetime.date(2020, 4, 22)
    ex: nous=datetime.date(2020, 4, 21) vs référence=datetime.date(2020, 4, 22)

## visit_end_datetime : 6098/6110 lignes concordent (99.8%)  [datetime]
    ex: nous=Timestamp('2022-10-26 22:03:09') vs référence=Timestamp('2022-10-27 00:00:00')
    ex: nous=Timestamp('2020-04-19 16:23:42') vs référence=Timestamp('2020-04-22 00:00:00')
    ex: nous=Timestamp('2020-04-21 02:36:52') vs référence=Timestamp('2020-04-22 00:00:00')

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## visit_source_value : 0/6110 lignes concordent (0.0%)  [text]
    ex: nous='wellness' vs référence='534f299e-c6a6-e37b-7900-1509a59f232a'
    ex: nous='wellness' vs référence='534f299e-c6a6-e37b-f9fe-c19c365276cf'
    ex: nous='outpatient' vs référence='534f299e-c6a6-e37b-11ff-06138c31ba7f'

# Écarts de portée (champs exclus du score)

  visit_source_concept_id : vide des deux côtés

## Résumé
  Couverture de la référence : 100.0%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 6098/6110 (99.8%)
  Accord sémantique par champ (toutes les valeurs comparées) : 99.9%
  Accord de provenance (hors score) : 0.0%

---

# Comparaison ligne à ligne — condition_occurrence

Clé naturelle : person + ['condition_concept_id', 'condition_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 1985 lignes
  Chez la référence : 1973 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 1985 lignes (0 exclues - patient non apparié)
  Chez la référence : 1973 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 1973
  Clés UNIQUEMENT chez nous : 12
  Clés UNIQUEMENT chez la référence : 0
    ex: [(94, 0, datetime.date(2026, 4, 24)), (57, 0, datetime.date(1998, 6, 4)), (20, 0, datetime.date(2017, 10, 1))]

Lignes appariées (même personne + même clé naturelle) : 1973
  Couverture de la référence : 1973/1973 (100.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 1973/1985 (99.4%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## condition_start_datetime : 1973/1973 lignes concordent (100.0%)  [datetime]

## condition_end_date : 1353/1353 lignes concordent (100.0%)  [date]

## condition_end_datetime : 1353/1353 lignes concordent (100.0%)  [datetime]

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## condition_source_value : 1973/1973 lignes concordent (100.0%)  [text]

## condition_source_concept_id : 1973/1973 lignes concordent (100.0%)  [concept]

## Résumé
  Couverture de la référence : 100.0%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 1973/1973 (100.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 100.0%
  Accord de provenance (hors score) : 100.0%

---

# Comparaison ligne à ligne — drug_exposure

Clé naturelle : person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 7616 lignes
  Chez la référence : 7382 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 7616 lignes (0 exclues - patient non apparié)
  Chez la référence : 7382 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 47 doublon(s) chez nous, 47 chez la référence, sur (person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 7335
  Clés UNIQUEMENT chez nous : 234
  Clés UNIQUEMENT chez la référence : 0
    ex: [(95, 37003518, datetime.date(2021, 4, 22), datetime.date(2021, 4, 22)), (74, 40213291, datetime.date(2019, 9, 21), datetime.date(2019, 9, 21)), (74, 40213291, datetime.date(2020, 10, 24), datetime.date(2020, 10, 24))]

Lignes appariées (même personne + même clé naturelle) : 7382
  Couverture de la référence : 7382/7382 (100.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 7382/7616 (96.9%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## drug_exposure_start_datetime : 7382/7382 lignes concordent (100.0%)  [datetime]

## drug_exposure_end_datetime : 7382/7382 lignes concordent (100.0%)  [datetime]

## quantity : 0/7382 lignes concordent (0.0%)  [number]
    ex: nous=np.float64(1.0) vs référence=np.float64(0.0)
    ex: nous=np.float64(nan) vs référence=np.float64(0.0)
    ex: nous=np.float64(nan) vs référence=np.float64(0.0)

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## drug_source_value : 7382/7382 lignes concordent (100.0%)  [text]

## drug_source_concept_id : 7382/7382 lignes concordent (100.0%)  [concept]

# Écarts de portée (champs exclus du score)

  days_supply : jamais renseigné chez nous

## Résumé
  Couverture de la référence : 100.0%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 0/7382 (0.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 66.7%
  Accord de provenance (hors score) : 100.0%

---

# Comparaison ligne à ligne — procedure_occurrence

Clé naturelle : person + ['procedure_concept_id', 'procedure_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 11977 lignes
  Chez la référence : 10154 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 11977 lignes (0 exclues - patient non apparié)
  Chez la référence : 10154 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 22 doublon(s) chez nous, 22 chez la référence, sur (person + ['procedure_concept_id', 'procedure_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 10132
  Clés UNIQUEMENT chez nous : 1823
  Clés UNIQUEMENT chez la référence : 0
    ex: [(91, 4036803, datetime.date(2025, 3, 7)), (23, 0, datetime.date(2017, 3, 17)), (23, 4036803, datetime.date(2015, 2, 19))]

Lignes appariées (même personne + même clé naturelle) : 10154
  Couverture de la référence : 10154/10154 (100.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 10154/11977 (84.8%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## procedure_datetime : 10154/10154 lignes concordent (100.0%)  [datetime]

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## procedure_source_value : 10154/10154 lignes concordent (100.0%)  [text]

## procedure_source_concept_id : 10154/10154 lignes concordent (100.0%)  [concept]

# Écarts de portée (champs exclus du score)

  quantity : vide des deux côtés

## Résumé
  Couverture de la référence : 100.0%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 10154/10154 (100.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 100.0%
  Accord de provenance (hors score) : 100.0%

---

# Comparaison ligne à ligne — measurement

Clé naturelle : person + ['measurement_concept_id', 'measurement_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 55920 lignes
  Chez la référence : 55833 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 55920 lignes (0 exclues - patient non apparié)
  Chez la référence : 55833 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 1688 doublon(s) chez nous, 1682 chez la référence, sur (person + ['measurement_concept_id', 'measurement_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 54151
  Clés UNIQUEMENT chez nous : 81
  Clés UNIQUEMENT chez la référence : 0
    ex: [(39, 3001714, datetime.date(2020, 3, 18)), (42, 3001714, datetime.date(2020, 12, 21)), (109, 3033727, datetime.date(2026, 6, 18))]

Lignes appariées (même personne + même clé naturelle) : 55833
  Couverture de la référence : 55833/55833 (100.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 55833/55920 (99.8%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## measurement_datetime : 55833/55833 lignes concordent (100.0%)  [datetime]

## value_as_number : 43594/44087 lignes concordent (98.9%)  [number]
    ex: nous=np.float64(16.0) vs référence=np.float64(13.1)
    ex: nous=np.float64(13.1) vs référence=np.float64(16.0)
    ex: nous=np.float64(40.0) vs référence=np.float64(32.4)

## unit_concept_id : 38585/43298 lignes concordent (89.1%)  [concept]
    ex: nous=np.int64(44777566) vs référence=np.int64(0)
    ex: nous=np.int64(44777566) vs référence=np.int64(0)
    ex: nous=np.int64(44777566) vs référence=np.int64(0)

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## measurement_source_value : 55833/55833 lignes concordent (100.0%)  [text]

## measurement_source_concept_id : 55833/55833 lignes concordent (100.0%)  [concept]

## unit_source_value : 51454/51454 lignes concordent (100.0%)  [text]

## value_source_value : 51121/51606 lignes concordent (99.1%)  [text]
    ex: nous='16.0' vs référence='13.1'
    ex: nous='13.1' vs référence='16.0'
    ex: nous='40.0' vs référence='32.4'

# Écarts de portée (champs exclus du score)

  value_as_concept_id : vide des deux côtés

## Résumé
  Couverture de la référence : 100.0%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 50742/55833 (90.9%)
  Accord sémantique par champ (toutes les valeurs comparées) : 96.4%
  Accord de provenance (hors score) : 99.8%

---

# Comparaison ligne à ligne — observation

Clé naturelle : person + ['observation_concept_id', 'observation_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 39850 lignes
  Chez la référence : 30324 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 39850 lignes (0 exclues - patient non apparié)
  Chez la référence : 30324 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 208 doublon(s) chez nous, 26 chez la référence, sur (person + ['observation_concept_id', 'observation_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 30216
  Clés UNIQUEMENT chez nous : 9426
  Clés UNIQUEMENT chez la référence : 82
    ex: [(85, 4301458, datetime.date(2021, 10, 13)), (53, 4054945, datetime.date(2022, 12, 1)), (108, 4085798, datetime.date(1985, 6, 20))]
    ex: [(103, 4117479, datetime.date(2008, 12, 12)), (21, 43530807, datetime.date(2012, 2, 19)), (73, 36684363, datetime.date(1957, 8, 10))]

Lignes appariées (même personne + même clé naturelle) : 30242
  Couverture de la référence : 30242/30324 (99.7%) - part des lignes de la référence retrouvées chez nous
  Précision : 30242/39850 (75.9%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## observation_datetime : 30242/30242 lignes concordent (100.0%)  [datetime]

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## observation_source_value : 30242/30242 lignes concordent (100.0%)  [text]

## observation_source_concept_id : 30242/30242 lignes concordent (100.0%)  [concept]

# Écarts de portée (champs exclus du score)

  value_as_number : renseigné seulement chez nous
  value_as_string : renseigné seulement chez nous
  value_as_concept_id : vide des deux côtés
  unit_concept_id : renseigné seulement chez nous
  unit_source_value : renseigné seulement chez nous

## Résumé
  Couverture de la référence : 99.7%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 30242/30242 (100.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 100.0%
  Accord de provenance (hors score) : 100.0%

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
  Clés présentes des deux côtés : 0
  Clés UNIQUEMENT chez nous : 14
  Clés UNIQUEMENT chez la référence : 14
    ex: [(68, datetime.date(2020, 7, 3)), (110, datetime.date(2015, 3, 6)), (108, datetime.date(1994, 7, 10))]
    ex: [(42, datetime.date(2021, 1, 25)), (15, datetime.date(1988, 12, 3)), (46, datetime.date(1983, 7, 2))]
  Parmi elles, 14 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 0
  Couverture de la référence : 0/14 (0.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 0/14 (0.0%) - part de nos lignes qui existent aussi chez la référence

Aucune ligne appariée : le contenu ne peut pas être comparé.

---

# Comparaison ligne à ligne — observation_period

Clé naturelle : person + ['observation_period_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 6414 lignes
  Chez la référence : 6110 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 6414 lignes (0 exclues - patient non apparié)
  Chez la référence : 6110 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 0 doublon(s) chez nous, 18 chez la référence, sur (person + ['observation_period_start_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 6080
  Clés UNIQUEMENT chez nous : 334
  Clés UNIQUEMENT chez la référence : 12
    ex: [(108, datetime.date(1986, 10, 23)), (110, datetime.date(2013, 6, 19)), (110, datetime.date(2012, 11, 14))]
    ex: [(36, datetime.date(2023, 8, 30)), (108, datetime.date(1988, 11, 20)), (32, datetime.date(2020, 4, 19))]
  Parmi elles, 5 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 6080
  Couverture de la référence : 6080/6110 (99.5%) - part des lignes de la référence retrouvées chez nous
  Précision : 6080/6414 (94.8%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## observation_period_end_date : 6069/6080 lignes concordent (99.8%)  [date]
    ex: nous=datetime.date(1988, 2, 18) vs référence=datetime.date(1988, 2, 11)
    ex: nous=datetime.date(1973, 9, 5) vs référence=datetime.date(1973, 8, 31)
    ex: nous=datetime.date(2016, 1, 7) vs référence=datetime.date(2016, 1, 6)

## Résumé
  Couverture de la référence : 99.5%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 6069/6080 (99.8%)
  Accord sémantique par champ (toutes les valeurs comparées) : 99.8%

---
