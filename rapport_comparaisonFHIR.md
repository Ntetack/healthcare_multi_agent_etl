# Full Comparison Report

## Executive Summary

| Table | Rows (ours) | Rows (reference) | Matched | Coverage of the reference | Semantic agreement | Provenance (not scored) | Note |
|---|---|---|---|---|---|---|---|
| person | 114 | 114 | 114 | 114/114 (100.0%) | 109/114 (95.6%) | 28.7% |  |
| visit_occurrence | 6705 | 6110 | 46 | 46/6110 (0.8%) | 46/46 (100.0%) | 0.0% | non-unique key (1979/7 dupes, paired by signature); 4680 ours-only / 6057 reference-only keys |
| condition_occurrence | 1985 | 1973 | 1673 | 1673/1973 (84.8%) | 1585/1673 (94.7%) | 100.0% | 249 events found with another date; 312 ours-only / 300 reference-only keys |
| drug_exposure | 7624 | 7382 | 3707 | 3707/7382 (50.2%) | 3707/3707 (100.0%) | 100.0% | non-unique key (59/47 dupes, paired by signature); 422 events found with another date; 3905 ours-only / 3675 reference-only keys |
| procedure_occurrence | 11974 | 10154 | 10154 | 10154/10154 (100.0%) | 10154/10154 (100.0%) | 100.0% | non-unique key (129/22 dupes, paired by signature); 1713 ours-only / 0 reference-only keys |
| measurement | 57621 | 55833 | 55833 | 55833/55833 (100.0%) | 20438/55833 (36.6%) | 72.5% | non-unique key (1691/1682 dupes, paired by signature); 1779 ours-only / 0 reference-only keys |
| observation | 40979 | 30324 | 29979 | 29979/30324 (98.9%) | 29979/29979 (100.0%) | 100.0% | non-unique key (363/26 dupes, paired by signature); 132 events found with another date; 10663 ours-only / 345 reference-only keys |
| death | 14 | 14 | 0 | 0/14 (0.0%) | n/a | n/a | 14 events found with another date; 14 ours-only / 14 reference-only keys |
| observation_period | 3893 | 6110 | 33 | 33/6110 (0.5%) | 30/33 (90.9%) | n/a | non-unique key (0/18 dupes, paired by signature); 1 events found with another date; 3860 ours-only / 6059 reference-only keys |

**Coverage of the reference (rows found here / rows of the reference): 101539/118014 (86.0%)**

**Semantic agreement (matched rows whose meaning agrees, weighted by rows): 66048/101539 (65.0%)**

**Reference rows reproduced with the same meaning (found AND agreeing): 66048/118000 (56.0%)**

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
    ex: nous=np.int64(8657) vs référence=np.int64(0)

## ethnicity_concept_id : 114/114 lignes concordent (100.0%)  [concept]

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## gender_source_value : 0/114 lignes concordent (0.0%)  [text]
    ex: nous='female' vs référence='F'
    ex: nous='male' vs référence='M'
    ex: nous='male' vs référence='M'

## race_source_value : 98/114 lignes concordent (86.0%)  [text]
    ex: nous='Black or African American' vs référence='black'
    ex: nous='Black or African American' vs référence='black'
    ex: nous='Black or African American' vs référence='black'

## ethnicity_source_value : 0/114 lignes concordent (0.0%)  [text]
    ex: nous='Not Hispanic or Latino' vs référence='nonhispanic'
    ex: nous='Hispanic or Latino' vs référence='hispanic'
    ex: nous='Not Hispanic or Latino' vs référence='nonhispanic'

# Écarts de portée (champs exclus du score)

  gender_source_concept_id : renseigné seulement chez nous
  race_source_concept_id : renseigné seulement chez nous
  ethnicity_source_concept_id : renseigné seulement chez nous

## Résumé
  Couverture de la référence : 100.0%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 109/114 (95.6%)
  Accord sémantique par champ (toutes les valeurs comparées) : 99.4%
  Accord de provenance (hors score) : 28.7%

---

# Comparaison ligne à ligne — visit_occurrence

Clé naturelle : person + ['visit_concept_id', 'visit_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 6705 lignes
  Chez la référence : 6110 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 6705 lignes (0 exclues - patient non apparié)
  Chez la référence : 6110 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 1979 doublon(s) chez nous, 7 chez la référence, sur (person + ['visit_concept_id', 'visit_start_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 46
  Clés UNIQUEMENT chez nous : 4680
  Clés UNIQUEMENT chez la référence : 6057
    ex: [(114, 9202, datetime.date(2021, 4, 6)), (114, 9202, datetime.date(2020, 2, 7)), (114, 9202, datetime.date(2023, 11, 2))]
    ex: [(113, 9202, datetime.date(2015, 5, 1)), (46, 9202, datetime.date(2016, 10, 10)), (67, 9202, datetime.date(2024, 1, 20))]

Lignes appariées (même personne + même clé naturelle) : 46
  Couverture de la référence : 46/6110 (0.8%) - part des lignes de la référence retrouvées chez nous
  Précision : 46/6705 (0.7%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## visit_start_datetime : 46/46 lignes concordent (100.0%)  [datetime]

## visit_end_date : 46/46 lignes concordent (100.0%)  [date]

## visit_end_datetime : 46/46 lignes concordent (100.0%)  [datetime]

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## visit_source_value : 0/46 lignes concordent (0.0%)  [text]
    ex: nous='Encounter for problem (procedure)' vs référence='d6bc18bd-99c9-6622-cdc4-24a3c0060763'
    ex: nous='Encounter for problem (procedure)' vs référence='d6bc18bd-99c9-6622-a9c9-37c0c9d78d84'
    ex: nous='General examination of patient (procedure)' vs référence='d6bc18bd-99c9-6622-5078-d1087d99d5f2'

# Écarts de portée (champs exclus du score)

  visit_source_concept_id : vide des deux côtés

## Résumé
  Couverture de la référence : 0.8%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 46/46 (100.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 100.0%
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
  Clés présentes des deux côtés : 1673
  Clés UNIQUEMENT chez nous : 312
  Clés UNIQUEMENT chez la référence : 300
    ex: [(67, 4281516, datetime.date(2023, 1, 15)), (35, 37018196, datetime.date(2022, 3, 27)), (32, 4090111, datetime.date(2024, 7, 27))]
    ex: [(112, 40481087, datetime.date(2021, 9, 2)), (73, 40481087, datetime.date(2021, 9, 12)), (73, 45769905, datetime.date(1993, 9, 5))]
  Parmi elles, 249 combinaison(s) (personne + ['condition_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 1673
  Couverture de la référence : 1673/1973 (84.8%) - part des lignes de la référence retrouvées chez nous
  Précision : 1673/1985 (84.3%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## condition_start_datetime : 1673/1673 lignes concordent (100.0%)  [datetime]

## condition_end_date : 1062/1150 lignes concordent (92.3%)  [date]
    ex: nous=datetime.date(2020, 4, 26) vs référence=datetime.date(2020, 4, 25)
    ex: nous=datetime.date(2020, 12, 20) vs référence=datetime.date(2020, 12, 19)
    ex: nous=datetime.date(2023, 1, 1) vs référence=datetime.date(2022, 12, 31)

## condition_end_datetime : 1062/1150 lignes concordent (92.3%)  [datetime]
    ex: nous=Timestamp('2020-04-26 00:06:02') vs référence=Timestamp('2020-04-25 00:00:00')
    ex: nous=Timestamp('2020-12-20 03:04:19') vs référence=Timestamp('2020-12-19 00:00:00')
    ex: nous=Timestamp('2023-01-01 00:01:59') vs référence=Timestamp('2022-12-31 00:00:00')

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## condition_source_value : 1673/1673 lignes concordent (100.0%)  [text]

## condition_source_concept_id : 1673/1673 lignes concordent (100.0%)  [concept]

## Résumé
  Couverture de la référence : 84.8%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 1585/1673 (94.7%)
  Accord sémantique par champ (toutes les valeurs comparées) : 95.6%
  Accord de provenance (hors score) : 100.0%

---

# Comparaison ligne à ligne — drug_exposure

Clé naturelle : person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 7624 lignes
  Chez la référence : 7382 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 7624 lignes (0 exclues - patient non apparié)
  Chez la référence : 7382 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 59 doublon(s) chez nous, 47 chez la référence, sur (person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 3660
  Clés UNIQUEMENT chez nous : 3905
  Clés UNIQUEMENT chez la référence : 3675
    ex: [(74, 19033893, datetime.date(2017, 7, 4), datetime.date(2017, 7, 4)), (4, 40162606, datetime.date(2017, 3, 6), datetime.date(2017, 3, 6)), (75, 19073094, datetime.date(1984, 8, 2), datetime.date(1984, 8, 2))]
    ex: [(32, 19080128, datetime.date(2026, 1, 2), datetime.date(2026, 3, 6)), (92, 19080128, datetime.date(2014, 1, 1), datetime.date(2014, 1, 8)), (62, 19009384, datetime.date(2020, 10, 27), datetime.date(2020, 11, 10))]
  Parmi elles, 422 combinaison(s) (personne + ['drug_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 3707
  Couverture de la référence : 3707/7382 (50.2%) - part des lignes de la référence retrouvées chez nous
  Précision : 3707/7624 (48.6%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## drug_exposure_start_datetime : 3707/3707 lignes concordent (100.0%)  [datetime]

## drug_exposure_end_datetime : 3707/3707 lignes concordent (100.0%)  [datetime]

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## drug_source_value : 3707/3707 lignes concordent (100.0%)  [text]

## drug_source_concept_id : 3707/3707 lignes concordent (100.0%)  [concept]

# Écarts de portée (champs exclus du score)

  quantity : jamais renseigné chez nous
  days_supply : jamais renseigné chez nous

## Résumé
  Couverture de la référence : 50.2%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 3707/3707 (100.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 100.0%
  Accord de provenance (hors score) : 100.0%

---

# Comparaison ligne à ligne — procedure_occurrence

Clé naturelle : person + ['procedure_concept_id', 'procedure_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 11974 lignes
  Chez la référence : 10154 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 11974 lignes (0 exclues - patient non apparié)
  Chez la référence : 10154 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 129 doublon(s) chez nous, 22 chez la référence, sur (person + ['procedure_concept_id', 'procedure_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 10132
  Clés UNIQUEMENT chez nous : 1713
  Clés UNIQUEMENT chez la référence : 0
    ex: [(114, 4036803, datetime.date(2010, 12, 24)), (114, 4263508, datetime.date(2018, 10, 14)), (114, 4036803, datetime.date(2025, 11, 10))]

Lignes appariées (même personne + même clé naturelle) : 10154
  Couverture de la référence : 10154/10154 (100.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 10154/11974 (84.8%) - part de nos lignes qui existent aussi chez la référence

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
  Chez nous : 57621 lignes
  Chez la référence : 55833 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 57621 lignes (0 exclues - patient non apparié)
  Chez la référence : 55833 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 1691 doublon(s) chez nous, 1682 chez la référence, sur (person + ['measurement_concept_id', 'measurement_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 54151
  Clés UNIQUEMENT chez nous : 1779
  Clés UNIQUEMENT chez la référence : 0
    ex: [(57, 4135663, datetime.date(2019, 9, 9)), (57, 36203185, datetime.date(2025, 4, 26)), (22, 36203185, datetime.date(2017, 11, 14))]

Lignes appariées (même personne + même clé naturelle) : 55833
  Couverture de la référence : 55833/55833 (100.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 55833/57621 (96.9%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## measurement_datetime : 55833/55833 lignes concordent (100.0%)  [datetime]

## value_as_number : 43595/44087 lignes concordent (98.9%)  [number]
    ex: nous=np.float64(-10.95) vs référence=np.float64(nan)
    ex: nous=np.float64(-0.4863) vs référence=np.float64(nan)
    ex: nous=np.float64(6.9768) vs référence=np.float64(6.0)

## unit_concept_id : 3380/38684 lignes concordent (8.7%)  [concept]
    ex: nous=np.int64(0) vs référence=np.int64(8848)
    ex: nous=np.int64(0) vs référence=np.int64(8713)
    ex: nous=np.int64(0) vs référence=np.int64(8583)

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## measurement_source_value : 55833/55833 lignes concordent (100.0%)  [text]

## measurement_source_concept_id : 55833/55833 lignes concordent (100.0%)  [concept]

## unit_source_value : 44087/51454 lignes concordent (85.7%)  [text]
    ex: nous='' vs référence='{nominal}'
    ex: nous='' vs référence='{nominal}'
    ex: nous='' vs référence='{nominal}'

## value_source_value : 0/51606 lignes concordent (0.0%)  [text]
    ex: nous='' vs référence='1.0'
    ex: nous='' vs référence='Urine leukocyte test one plus (finding)'
    ex: nous='' vs référence='6.7'

# Écarts de portée (champs exclus du score)

  value_as_concept_id : vide des deux côtés

## Résumé
  Couverture de la référence : 100.0%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 20438/55833 (36.6%)
  Accord sémantique par champ (toutes les valeurs comparées) : 74.2%
  Accord de provenance (hors score) : 72.5%

---

# Comparaison ligne à ligne — observation

Clé naturelle : person + ['observation_concept_id', 'observation_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 40979 lignes
  Chez la référence : 30324 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 40979 lignes (0 exclues - patient non apparié)
  Chez la référence : 30324 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 363 doublon(s) chez nous, 26 chez la référence, sur (person + ['observation_concept_id', 'observation_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 29953
  Clés UNIQUEMENT chez nous : 10663
  Clés UNIQUEMENT chez la référence : 345
    ex: [(114, 4054945, datetime.date(2020, 5, 6)), (103, 37021305, datetime.date(2017, 12, 1)), (90, 44784270, datetime.date(2017, 1, 6))]
    ex: [(51, 4251306, datetime.date(2021, 1, 9)), (93, 4199788, datetime.date(2024, 12, 11)), (104, 4199788, datetime.date(1980, 7, 20))]
  Parmi elles, 132 combinaison(s) (personne + ['observation_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 29979
  Couverture de la référence : 29979/30324 (98.9%) - part des lignes de la référence retrouvées chez nous
  Précision : 29979/40979 (73.2%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## observation_datetime : 29979/29979 lignes concordent (100.0%)  [datetime]

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## observation_source_value : 29979/29979 lignes concordent (100.0%)  [text]

## observation_source_concept_id : 29979/29979 lignes concordent (100.0%)  [concept]

# Écarts de portée (champs exclus du score)

  value_as_number : renseigné seulement chez nous
  value_as_string : renseigné seulement chez nous
  value_as_concept_id : vide des deux côtés
  unit_concept_id : renseigné seulement chez nous
  unit_source_value : renseigné seulement chez nous

## Résumé
  Couverture de la référence : 98.9%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 29979/29979 (100.0%)
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
    ex: [(28, datetime.date(2021, 1, 13)), (70, datetime.date(2025, 12, 13)), (63, datetime.date(2020, 7, 3))]
    ex: [(92, datetime.date(2015, 3, 11)), (106, datetime.date(2008, 4, 5)), (75, datetime.date(1992, 11, 26))]
  Parmi elles, 14 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 0
  Couverture de la référence : 0/14 (0.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 0/14 (0.0%) - part de nos lignes qui existent aussi chez la référence

Aucune ligne appariée : le contenu ne peut pas être comparé.

---

# Comparaison ligne à ligne — observation_period

Clé naturelle : person + ['observation_period_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 3893 lignes
  Chez la référence : 6110 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 3893 lignes (0 exclues - patient non apparié)
  Chez la référence : 6110 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 0 doublon(s) chez nous, 18 chez la référence, sur (person + ['observation_period_start_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 33
  Clés UNIQUEMENT chez nous : 3860
  Clés UNIQUEMENT chez la référence : 6059
    ex: [(114, datetime.date(1976, 9, 20)), (114, datetime.date(2010, 6, 2)), (114, datetime.date(2010, 11, 24))]
    ex: [(70, datetime.date(2025, 4, 25)), (52, datetime.date(2021, 8, 7)), (70, datetime.date(2025, 2, 2))]
  Parmi elles, 1 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 33
  Couverture de la référence : 33/6110 (0.5%) - part des lignes de la référence retrouvées chez nous
  Précision : 33/3893 (0.8%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## observation_period_end_date : 30/33 lignes concordent (90.9%)  [date]
    ex: nous=datetime.date(2018, 4, 26) vs référence=datetime.date(2018, 4, 25)
    ex: nous=datetime.date(2023, 4, 28) vs référence=datetime.date(2023, 4, 27)
    ex: nous=datetime.date(2026, 7, 30) vs référence=datetime.date(2026, 7, 29)

## Résumé
  Couverture de la référence : 0.5%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 30/33 (90.9%)
  Accord sémantique par champ (toutes les valeurs comparées) : 90.9%

---
