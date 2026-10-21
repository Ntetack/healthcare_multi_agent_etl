# Full Comparison Report

## Executive Summary

| Table | Rows (ours) | Rows (reference) | Matched | Coverage of the reference | Semantic agreement | Provenance (not scored) | Note |
|---|---|---|---|---|---|---|---|
| person | 114 | 114 | 114 | 114/114 (100.0%) | 109/114 (95.6%) | 28.7% |  |
| visit_occurrence | 6705 | 6110 | 46 | 46/6110 (0.8%) | 46/46 (100.0%) | 0.0% | non-unique key (1979/7 dupes, paired by signature); 4680 ours-only / 6057 reference-only keys |
| condition_occurrence | 1985 | 1973 | 1673 | 1673/1973 (84.8%) | 1585/1673 (94.7%) | 100.0% | 249 events found with another date; 312 ours-only / 300 reference-only keys |
| drug_exposure | 7624 | 7382 | 0 | 0/7382 (0.0%) | n/a | n/a | non-unique key (12/47 dupes, paired by signature); 1174 events found with another date; 7612 ours-only / 7335 reference-only keys |
| procedure_occurrence | 11974 | 10154 | 0 | 0/10154 (0.0%) | n/a | n/a | non-unique key (28/22 dupes, paired by signature); 2063 events found with another date; 11946 ours-only / 10132 reference-only keys |
| measurement | 57621 | 55833 | 55833 | 55833/55833 (100.0%) | 20438/55833 (36.6%) | 72.5% | non-unique key (1691/1682 dupes, paired by signature); 1779 ours-only / 0 reference-only keys |
| observation | 40979 | 30324 | 21 | 21/30324 (0.1%) | n/a | 100.0% | non-unique key (28/26 dupes, paired by signature); 3724 events found with another date; 40930 ours-only / 30277 reference-only keys |
| death | 14 | 14 | 0 | 0/14 (0.0%) | n/a | n/a | 14 events found with another date; 14 ours-only / 14 reference-only keys |
| observation_period | 3893 | 6110 | 33 | 33/6110 (0.5%) | 30/33 (90.9%) | n/a | non-unique key (0/18 dupes, paired by signature); 1 events found with another date; 3860 ours-only / 6059 reference-only keys |

**Coverage of the reference (rows found here / rows of the reference): 57720/118014 (48.9%)**

**Semantic agreement (matched rows whose meaning agrees, weighted by rows): 22208/57699 (38.5%)**

**Reference rows reproduced with the same meaning (found AND agreeing): 22208/70140 (31.7%)**

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
    ex: [(114, 9202, datetime.date(2022, 5, 7)), (114, 9202, datetime.date(2026, 9, 29)), (114, 9202, datetime.date(2024, 3, 24))]
    ex: [(62, 9202, datetime.date(2023, 3, 21)), (73, 9202, datetime.date(2024, 8, 26)), (52, 9202, datetime.date(2026, 6, 13))]

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
    ex: [(33, 443614, datetime.date(1971, 3, 6)), (25, 4112343, datetime.date(2019, 6, 4)), (23, 4079749, datetime.date(1961, 5, 17))]
    ex: [(113, 260139, datetime.date(2019, 8, 27)), (73, 434073, datetime.date(2007, 7, 8)), (77, 4112343, datetime.date(2020, 10, 31))]
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

Clé naturelle : person + ['drug_concept_id', 'drug_exposure_start_datetime', 'drug_exposure_end_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 7624 lignes
  Chez la référence : 7382 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 7624 lignes (0 exclues - patient non apparié)
  Chez la référence : 7382 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 12 doublon(s) chez nous, 47 chez la référence, sur (person + ['drug_concept_id', 'drug_exposure_start_datetime', 'drug_exposure_end_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 0
  Clés UNIQUEMENT chez nous : 7612
  Clés UNIQUEMENT chez la référence : 7335
    ex: [(92, 19030765, Timestamp('2010-08-18 03:31:44'), datetime.date(2010, 8, 18)), (92, 40163554, Timestamp('2015-03-04 16:55:44'), datetime.date(2015, 3, 4)), (92, 19009384, Timestamp('2014-01-01 16:55:44'), datetime.date(2014, 1, 1))]
    ex: [(59, 40213154, Timestamp('2019-08-22 00:00:00'), datetime.date(2019, 8, 22)), (92, 19078106, Timestamp('2014-07-16 00:00:00'), datetime.date(2014, 8, 13)), (56, 1378388, Timestamp('2026-08-13 00:00:00'), datetime.date(2026, 8, 13))]
  Parmi elles, 1174 combinaison(s) (personne + ['drug_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 0
  Couverture de la référence : 0/7382 (0.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 0/7624 (0.0%) - part de nos lignes qui existent aussi chez la référence

Aucune ligne appariée : le contenu ne peut pas être comparé.

---

# Comparaison ligne à ligne — procedure_occurrence

Clé naturelle : person + ['procedure_concept_id', 'procedure_datetime']

## Volumes bruts (avant tout filtrage)
  Chez nous : 11974 lignes
  Chez la référence : 10154 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 11974 lignes (0 exclues - patient non apparié)
  Chez la référence : 10154 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 28 doublon(s) chez nous, 22 chez la référence, sur (person + ['procedure_concept_id', 'procedure_datetime']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 0
  Clés UNIQUEMENT chez nous : 11946
  Clés UNIQUEMENT chez la référence : 10132
    ex: [(38, 4168236, Timestamp('2017-05-06 22:11:51')), (114, 4036803, Timestamp('2026-06-29 01:16:42')), (14, 762506, Timestamp('1987-05-09 04:15:16'))]
    ex: [(90, 46272472, Timestamp('2022-01-24 00:00:00')), (92, 4146536, Timestamp('2010-10-20 00:00:00')), (92, 4146536, Timestamp('2014-11-29 00:00:00'))]
  Parmi elles, 2063 combinaison(s) (personne + ['procedure_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 0
  Couverture de la référence : 0/10154 (0.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 0/11974 (0.0%) - part de nos lignes qui existent aussi chez la référence

Aucune ligne appariée : le contenu ne peut pas être comparé.

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
    ex: [(70, 36203185, datetime.date(2024, 5, 3)), (55, 36203185, datetime.date(2019, 3, 19)), (105, 36203185, datetime.date(1988, 9, 22))]

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

Clé naturelle : person + ['observation_concept_id', 'observation_datetime']

## Volumes bruts (avant tout filtrage)
  Chez nous : 40979 lignes
  Chez la référence : 30324 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 40979 lignes (0 exclues - patient non apparié)
  Chez la référence : 30324 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 28 doublon(s) chez nous, 26 chez la référence, sur (person + ['observation_concept_id', 'observation_datetime']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 21
  Clés UNIQUEMENT chez nous : 40930
  Clés UNIQUEMENT chez la référence : 30277
    ex: [(73, 37020116, Timestamp('2019-05-13 03:52:27')), (44, 37020108, Timestamp('2017-08-30 17:55:17')), (13, 42868746, Timestamp('2016-10-19 18:12:50'))]
    ex: [(39, 40766239, Timestamp('2023-03-26 00:00:00')), (57, 42529243, Timestamp('2024-08-24 00:00:00')), (65, 43054909, Timestamp('2016-11-12 00:00:00'))]
  Parmi elles, 3724 combinaison(s) (personne + ['observation_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 21
  Couverture de la référence : 21/30324 (0.1%) - part des lignes de la référence retrouvées chez nous
  Précision : 21/40979 (0.1%) - part de nos lignes qui existent aussi chez la référence

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## observation_source_value : 21/21 lignes concordent (100.0%)  [text]

## observation_source_concept_id : 21/21 lignes concordent (100.0%)  [concept]

# Écarts de portée (champs exclus du score)

  value_as_number : renseigné seulement chez nous
  value_as_string : renseigné seulement chez nous
  value_as_concept_id : vide des deux côtés
  unit_concept_id : renseigné seulement chez nous
  unit_source_value : renseigné seulement chez nous

## Résumé
  Couverture de la référence : 0.1%
  Accord sémantique : aucun champ sémantique comparable.
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
    ex: [(104, datetime.date(1987, 8, 22)), (63, datetime.date(2020, 7, 3)), (106, datetime.date(2008, 3, 31))]
    ex: [(63, datetime.date(2020, 7, 16)), (64, datetime.date(1973, 9, 15)), (70, datetime.date(2025, 12, 21))]
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
    ex: [(114, datetime.date(2011, 8, 11)), (114, datetime.date(1992, 5, 4)), (114, datetime.date(2021, 3, 19))]
    ex: [(7, datetime.date(2025, 7, 22)), (73, datetime.date(2021, 6, 28)), (62, datetime.date(2021, 10, 12))]
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
