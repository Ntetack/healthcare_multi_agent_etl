# Full Comparison Report

## Executive Summary

| Table | Rows (ours) | Rows (reference) | Matched | Coverage of the reference | Semantic agreement | Provenance (not scored) | Note |
|---|---|---|---|---|---|---|---|
| person | 114 | 114 | 114 | 114/114 (100.0%) | 109/114 (95.6%) | 28.7% |  |
| visit_occurrence | 6705 | 6110 | 6110 | 6110/6110 (100.0%) | 6098/6110 (99.8%) | 0.0% | non-unique key (246/7 dupes, paired by signature); 356 ours-only / 0 reference-only keys |
| condition_occurrence | 1985 | 1973 | 1673 | 1673/1973 (84.8%) | 1585/1673 (94.7%) | 100.0% | 249 events found with another date; 312 ours-only / 300 reference-only keys |
| drug_exposure | 7624 | 7382 | 7382 | 7382/7382 (100.0%) | 3707/7382 (50.2%) | 100.0% | non-unique key (59/59 dupes, paired by signature); 242 ours-only / 0 reference-only keys |
| procedure_occurrence | 11974 | 10154 | 10154 | 10154/10154 (100.0%) | 10154/10154 (100.0%) | 100.0% | non-unique key (22/22 dupes, paired by signature); 1820 ours-only / 0 reference-only keys |
| measurement | 57585 | 55833 | 55833 | 55833/55833 (100.0%) | 55340/55833 (99.1%) | 72.5% | non-unique key (1691/1682 dupes, paired by signature); 1743 ours-only / 0 reference-only keys |
| observation | 40979 | 30324 | 29979 | 29979/30324 (98.9%) | 29979/29979 (100.0%) | 100.0% | non-unique key (208/26 dupes, paired by signature); 132 events found with another date; 10818 ours-only / 345 reference-only keys |
| death | 14 | 14 | 0 | 0/14 (0.0%) | n/a | n/a | 14 events found with another date; 14 ours-only / 14 reference-only keys |
| observation_period | 6392 | 6110 | 6080 | 6080/6110 (99.5%) | 6046/6080 (99.4%) | n/a | non-unique key (0/18 dupes, paired by signature); 5 events found with another date; 312 ours-only / 12 reference-only keys |

**Coverage of the reference (rows found here / rows of the reference): 117325/118014 (99.4%)**

**Semantic agreement (matched rows whose meaning agrees, weighted by rows): 113018/117325 (96.3%)**

**Reference rows reproduced with the same meaning (found AND agreeing): 113018/118000 (95.8%)**

Provenance fields (`*_source_value`, `*_source_concept_id`) are listed per table but are not part of any figure above: they record how the source wrote a value, which two faithful exports may do differently.

## Diagnostics of the run

- Patient bridge: person_source_value identical on both sides
- Patients: 114 ours, 114 reference, 114 bridged

Key granularity: date

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

⚠️  CLÉ NON UNIQUE : 246 doublon(s) chez nous, 7 chez la référence, sur (person + ['visit_concept_id', 'visit_start_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 6103
  Clés UNIQUEMENT chez nous : 356
  Clés UNIQUEMENT chez la référence : 0
    ex: [(92, 9202, datetime.date(2007, 7, 11)), (92, 9202, datetime.date(2006, 9, 20)), (99, 9202, datetime.date(2022, 5, 18))]

Lignes appariées (même personne + même clé naturelle) : 6110
  Couverture de la référence : 6110/6110 (100.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 6110/6705 (91.1%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## visit_start_datetime : 6110/6110 lignes concordent (100.0%)  [datetime]

## visit_end_date : 6098/6110 lignes concordent (99.8%)  [date]
    ex: nous=datetime.date(2020, 4, 19) vs référence=datetime.date(2020, 4, 22)
    ex: nous=datetime.date(2020, 4, 21) vs référence=datetime.date(2020, 4, 22)
    ex: nous=datetime.date(2023, 9, 2) vs référence=datetime.date(2023, 9, 3)

## visit_end_datetime : 6098/6110 lignes concordent (99.8%)  [datetime]
    ex: nous=Timestamp('2020-04-19 16:23:42') vs référence=Timestamp('2020-04-22 00:00:00')
    ex: nous=Timestamp('2020-04-21 02:36:52') vs référence=Timestamp('2020-04-22 00:00:00')
    ex: nous=Timestamp('2023-09-02 23:45:55') vs référence=Timestamp('2023-09-03 00:00:00')

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## visit_source_value : 0/6110 lignes concordent (0.0%)  [text]
    ex: nous='Well child visit (procedure)' vs référence='6db51dcc-9a9b-39a8-c25d-712d64f3aa49'
    ex: nous='Well child visit (procedure)' vs référence='6db51dcc-9a9b-39a8-9cf5-acc2af55fcb9'
    ex: nous='Consultation for treatment (procedure)' vs référence='6db51dcc-9a9b-39a8-f643-151c5613bfce'

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
  Clés présentes des deux côtés : 1673
  Clés UNIQUEMENT chez nous : 312
  Clés UNIQUEMENT chez la référence : 300
    ex: [(73, 192279, datetime.date(1989, 8, 14)), (35, 4309238, datetime.date(2026, 8, 30)), (110, 4281516, datetime.date(1984, 4, 21))]
    ex: [(51, 4281516, datetime.date(2025, 2, 1)), (45, 28060, datetime.date(2018, 10, 31)), (112, 40481087, datetime.date(2021, 9, 2))]
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

Clé naturelle : person + ['drug_concept_id', 'drug_exposure_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 7624 lignes
  Chez la référence : 7382 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 7624 lignes (0 exclues - patient non apparié)
  Chez la référence : 7382 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 59 doublon(s) chez nous, 59 chez la référence, sur (person + ['drug_concept_id', 'drug_exposure_start_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 7323
  Clés UNIQUEMENT chez nous : 242
  Clés UNIQUEMENT chez la référence : 0
    ex: [(82, 37003518, datetime.date(2021, 5, 13)), (17, 37003436, datetime.date(2021, 6, 7)), (71, 40213304, datetime.date(2017, 1, 12))]

Lignes appariées (même personne + même clé naturelle) : 7382
  Couverture de la référence : 7382/7382 (100.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 7382/7624 (96.8%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## drug_exposure_start_datetime : 7382/7382 lignes concordent (100.0%)  [datetime]

## drug_exposure_end_datetime : 3707/7382 lignes concordent (50.2%)  [datetime]
    ex: nous=Timestamp('2019-04-11 09:28:01') vs référence=Timestamp('2019-04-29 00:00:00')
    ex: nous=Timestamp('2020-04-01 13:12:35') vs référence=Timestamp('2020-04-13 00:00:00')
    ex: nous=Timestamp('2023-09-27 21:08:35') vs référence=Timestamp('2024-09-21 00:00:00')

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## drug_source_value : 7382/7382 lignes concordent (100.0%)  [text]

## drug_source_concept_id : 7382/7382 lignes concordent (100.0%)  [concept]

# Écarts de portée (champs exclus du score)

  quantity : jamais renseigné chez nous
  days_supply : jamais renseigné chez nous

## Résumé
  Couverture de la référence : 100.0%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 3707/7382 (50.2%)
  Accord sémantique par champ (toutes les valeurs comparées) : 75.1%
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

⚠️  CLÉ NON UNIQUE : 22 doublon(s) chez nous, 22 chez la référence, sur (person + ['procedure_concept_id', 'procedure_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 10132
  Clés UNIQUEMENT chez nous : 1820
  Clés UNIQUEMENT chez la référence : 0
    ex: [(87, 4144375, datetime.date(2021, 7, 23)), (94, 4144375, datetime.date(2021, 4, 2)), (34, 4036803, datetime.date(2026, 7, 16))]

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
  Chez nous : 57585 lignes
  Chez la référence : 55833 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 57585 lignes (0 exclues - patient non apparié)
  Chez la référence : 55833 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 1691 doublon(s) chez nous, 1682 chez la référence, sur (person + ['measurement_concept_id', 'measurement_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 54151
  Clés UNIQUEMENT chez nous : 1743
  Clés UNIQUEMENT chez la référence : 0
    ex: [(61, 36203185, datetime.date(2019, 7, 10)), (70, 36203185, datetime.date(2025, 4, 1)), (92, 36203185, datetime.date(2010, 2, 10))]

Lignes appariées (même personne + même clé naturelle) : 55833
  Couverture de la référence : 55833/55833 (100.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 55833/57585 (97.0%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## measurement_datetime : 55833/55833 lignes concordent (100.0%)  [datetime]

## value_as_number : 43595/44087 lignes concordent (98.9%)  [number]
    ex: nous=np.float64(-10.95) vs référence=np.float64(nan)
    ex: nous=np.float64(-0.4863) vs référence=np.float64(nan)
    ex: nous=np.float64(6.9768) vs référence=np.float64(6.0)

## unit_concept_id : 38683/38684 lignes concordent (100.0%)  [concept]
    ex: nous=np.int64(0) vs référence=np.int64(8848)

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
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 55340/55833 (99.1%)
  Accord sémantique par champ (toutes les valeurs comparées) : 99.6%
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

⚠️  CLÉ NON UNIQUE : 208 doublon(s) chez nous, 26 chez la référence, sur (person + ['observation_concept_id', 'observation_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 29953
  Clés UNIQUEMENT chez nous : 10818
  Clés UNIQUEMENT chez la référence : 345
    ex: [(105, 4085798, datetime.date(1988, 6, 10)), (56, 37021305, datetime.date(2018, 3, 24)), (82, 4055248, datetime.date(2025, 11, 13))]
    ex: [(73, 4251306, datetime.date(2023, 5, 21)), (25, 4251171, datetime.date(2026, 5, 10)), (51, 4251306, datetime.date(2021, 1, 9))]
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
  unit_concept_id : vide des deux côtés
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
    ex: [(75, datetime.date(1992, 11, 16)), (85, datetime.date(1987, 9, 2)), (33, datetime.date(1983, 7, 1))]
    ex: [(75, datetime.date(1992, 11, 26)), (63, datetime.date(2020, 7, 16)), (105, datetime.date(1994, 7, 14))]
  Parmi elles, 14 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 0
  Couverture de la référence : 0/14 (0.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 0/14 (0.0%) - part de nos lignes qui existent aussi chez la référence

Aucune ligne appariée : le contenu ne peut pas être comparé.

---

# Comparaison ligne à ligne — observation_period

Clé naturelle : person + ['observation_period_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 6392 lignes
  Chez la référence : 6110 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 6392 lignes (0 exclues - patient non apparié)
  Chez la référence : 6110 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 0 doublon(s) chez nous, 18 chez la référence, sur (person + ['observation_period_start_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 6080
  Clés UNIQUEMENT chez nous : 312
  Clés UNIQUEMENT chez la référence : 12
    ex: [(92, datetime.date(2006, 10, 18)), (32, datetime.date(2023, 9, 15)), (92, datetime.date(2012, 11, 14))]
    ex: [(46, datetime.date(2016, 1, 6)), (92, datetime.date(2013, 12, 25)), (105, datetime.date(1986, 7, 22))]
  Parmi elles, 5 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 6080
  Couverture de la référence : 6080/6110 (99.5%) - part des lignes de la référence retrouvées chez nous
  Précision : 6080/6392 (95.1%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## observation_period_end_date : 6046/6080 lignes concordent (99.4%)  [date]
    ex: nous=datetime.date(2023, 2, 14) vs référence=datetime.date(2023, 1, 11)
    ex: nous=datetime.date(2010, 3, 11) vs référence=datetime.date(2010, 3, 7)
    ex: nous=datetime.date(2016, 5, 17) vs référence=datetime.date(2016, 5, 12)

## Résumé
  Couverture de la référence : 99.5%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 6046/6080 (99.4%)
  Accord sémantique par champ (toutes les valeurs comparées) : 99.4%

---
