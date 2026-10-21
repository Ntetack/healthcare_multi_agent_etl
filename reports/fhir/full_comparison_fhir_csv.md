# Full Comparison Report

## Executive Summary

| Table | Rows (ours) | Rows (reference) | Matched | Coverage of the reference | Semantic agreement | Provenance (not scored) | Note |
|---|---|---|---|---|---|---|---|
| person | 114 | 114 | 114 | 114/114 (100.0%) | 114/114 (100.0%) | 54.5% |  |
| visit_occurrence | 6705 | 6703 | 46 | 46/6703 (0.7%) | 29/46 (63.0%) | 0.0% | non-unique key (1979/246 dupes, paired by signature); 1 events found with another date; 4680 ours-only / 6411 reference-only keys |
| condition_occurrence | 1985 | 1985 | 1684 | 1684/1985 (84.8%) | 1596/1684 (94.8%) | 100.0% | 250 events found with another date; 301 ours-only / 301 reference-only keys |
| drug_exposure | 7624 | 7616 | 3937 | 3937/7616 (51.7%) | 3930/3937 (99.8%) | 69.9% | non-unique key (59/47 dupes, paired by signature); 422 events found with another date; 3675 ours-only / 3679 reference-only keys |
| procedure_occurrence | 11974 | 11977 | 10279 | 10279/11977 (85.8%) | 10277/10279 (100.0%) | 100.0% | non-unique key (129/22 dupes, paired by signature); 1588 ours-only / 1698 reference-only keys |
| measurement | 57585 | 55920 | 55841 | 55841/55920 (99.9%) | 51127/55841 (91.6%) | 71.1% | non-unique key (1691/1688 dupes, paired by signature); 1741 ours-only / 79 reference-only keys |
| observation | 40979 | 39850 | 34373 | 34373/39850 (86.3%) | 1140/34373 (3.3%) | 94.0% | non-unique key (363/208 dupes, paired by signature); 131 events found with another date; 6272 ours-only / 5298 reference-only keys |
| death | 14 | 14 | 12 | 12/14 (85.7%) | 12/12 (100.0%) | n/a | 2 events found with another date; 2 ours-only / 2 reference-only keys |
| observation_period | 3893 | 6414 | 33 | 33/6414 (0.5%) | 30/33 (90.9%) | n/a | 1 events found with another date; 3860 ours-only / 6381 reference-only keys |

**Coverage of the reference (rows found here / rows of the reference): 106319/130593 (81.4%)**

**Semantic agreement (matched rows whose meaning agrees, weighted by rows): 68255/106319 (64.2%)**

**Reference rows reproduced with the same meaning (found AND agreeing): 68255/130593 (52.3%)**

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

## race_concept_id : 113/113 lignes concordent (100.0%)  [concept]

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

## gender_source_concept_id : 114/114 lignes concordent (100.0%)  [concept]

## race_source_concept_id : 98/113 lignes concordent (86.7%)  [concept]
    ex: nous=np.int64(8516) vs référence=np.int64(38003598)
    ex: nous=np.int64(8516) vs référence=np.int64(38003598)
    ex: nous=np.int64(8516) vs référence=np.int64(38003598)

# Écarts de portée (champs exclus du score)

  ethnicity_source_concept_id : renseigné seulement chez nous

## Résumé
  Couverture de la référence : 100.0%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 114/114 (100.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 100.0%
  Accord de provenance (hors score) : 54.5%

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

⚠️  CLÉ NON UNIQUE : 1979 doublon(s) chez nous, 246 chez la référence, sur (person + ['visit_concept_id', 'visit_start_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 46
  Clés UNIQUEMENT chez nous : 4680
  Clés UNIQUEMENT chez la référence : 6411
    ex: [(114, 9202, datetime.date(2020, 4, 18)), (114, 9202, datetime.date(2016, 10, 13)), (114, 9202, datetime.date(2007, 3, 14))]
    ex: [(97, 9202, datetime.date(2026, 2, 16)), (4, 9202, datetime.date(2022, 8, 13)), (56, 581476, datetime.date(2022, 7, 15))]
  Parmi elles, 1 combinaison(s) (personne + ['visit_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 46
  Couverture de la référence : 46/6703 (0.7%) - part des lignes de la référence retrouvées chez nous
  Précision : 46/6705 (0.7%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## visit_start_datetime : 29/46 lignes concordent (63.0%)  [datetime]
    ex: nous=Timestamp('2006-05-31 16:55:44') vs référence=Timestamp('2006-05-31 17:07:08')
    ex: nous=Timestamp('2012-06-06 06:39:18') vs référence=Timestamp('2012-06-06 17:07:08')
    ex: nous=Timestamp('2020-01-01 12:32:25') vs référence=Timestamp('2020-01-01 17:07:08')

## visit_end_date : 46/46 lignes concordent (100.0%)  [date]

## visit_end_datetime : 29/46 lignes concordent (63.0%)  [datetime]
    ex: nous=Timestamp('2006-05-31 20:20:09') vs référence=Timestamp('2006-05-31 17:59:55')
    ex: nous=Timestamp('2012-06-06 07:34:15') vs référence=Timestamp('2012-06-06 17:53:25')
    ex: nous=Timestamp('2020-01-01 15:20:27') vs référence=Timestamp('2020-01-01 17:53:22')

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## visit_source_value : 0/46 lignes concordent (0.0%)  [text]
    ex: nous='Encounter for problem (procedure)' vs référence='185347001'
    ex: nous='Encounter for problem (procedure)' vs référence='185347001'
    ex: nous='General examination of patient (procedure)' vs référence='162673000'

# Écarts de portée (champs exclus du score)

  visit_source_concept_id : vide des deux côtés

## Résumé
  Couverture de la référence : 0.7%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 29/46 (63.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 75.4%
  Accord de provenance (hors score) : 0.0%

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
  Clés présentes des deux côtés : 1684
  Clés UNIQUEMENT chez nous : 301
  Clés UNIQUEMENT chez la référence : 301
    ex: [(33, 4172829, datetime.date(1976, 11, 6)), (25, 4309238, datetime.date(2026, 5, 11)), (73, 132797, datetime.date(1983, 5, 23))]
    ex: [(15, 4281516, datetime.date(2021, 3, 25)), (70, 4283893, datetime.date(2022, 1, 24)), (33, 436940, datetime.date(1972, 7, 28))]
  Parmi elles, 250 combinaison(s) (personne + ['condition_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 1684
  Couverture de la référence : 1684/1985 (84.8%) - part des lignes de la référence retrouvées chez nous
  Précision : 1684/1985 (84.8%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## condition_start_datetime : 1684/1684 lignes concordent (100.0%)  [datetime]

## condition_end_date : 1070/1158 lignes concordent (92.4%)  [date]
    ex: nous=datetime.date(2020, 4, 26) vs référence=datetime.date(2020, 4, 25)
    ex: nous=datetime.date(2020, 12, 20) vs référence=datetime.date(2020, 12, 19)
    ex: nous=datetime.date(2023, 1, 1) vs référence=datetime.date(2022, 12, 31)

## condition_end_datetime : 1070/1158 lignes concordent (92.4%)  [datetime]
    ex: nous=Timestamp('2020-04-26 00:06:02') vs référence=Timestamp('2020-04-25 00:00:00')
    ex: nous=Timestamp('2020-12-20 03:04:19') vs référence=Timestamp('2020-12-19 00:00:00')
    ex: nous=Timestamp('2023-01-01 00:01:59') vs référence=Timestamp('2022-12-31 00:00:00')

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## condition_source_value : 1684/1684 lignes concordent (100.0%)  [text]

## condition_source_concept_id : 1684/1684 lignes concordent (100.0%)  [concept]

## Résumé
  Couverture de la référence : 84.8%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 1596/1684 (94.8%)
  Accord sémantique par champ (toutes les valeurs comparées) : 95.6%
  Accord de provenance (hors score) : 100.0%

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

⚠️  CLÉ NON UNIQUE : 59 doublon(s) chez nous, 47 chez la référence, sur (person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 3890
  Clés UNIQUEMENT chez nous : 3675
  Clés UNIQUEMENT chez la référence : 3679
    ex: [(73, 19080128, datetime.date(2022, 5, 30), datetime.date(2022, 5, 30)), (73, 19073094, datetime.date(2019, 1, 28), datetime.date(2019, 1, 28)), (103, 1539463, datetime.date(2018, 12, 16), datetime.date(2018, 12, 16))]
    ex: [(92, 19078106, datetime.date(2014, 12, 31), datetime.date(2015, 1, 7)), (92, 19078106, datetime.date(2007, 12, 12), datetime.date(2008, 1, 2)), (92, 19009384, datetime.date(2013, 10, 9), datetime.date(2013, 11, 6))]
  Parmi elles, 422 combinaison(s) (personne + ['drug_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 3937
  Couverture de la référence : 3937/7616 (51.7%) - part des lignes de la référence retrouvées chez nous
  Précision : 3937/7624 (51.6%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## drug_exposure_start_datetime : 3937/3937 lignes concordent (100.0%)  [datetime]

## drug_exposure_end_datetime : 3930/3937 lignes concordent (99.8%)  [datetime]
    ex: nous=Timestamp('2024-09-29 22:19:33') vs référence=Timestamp('2024-09-29 23:19:33')
    ex: nous=Timestamp('2023-02-28 01:51:03') vs référence=Timestamp('2023-02-28 21:33:39')
    ex: nous=Timestamp('2021-01-19 09:57:00') vs référence=Timestamp('2021-01-19 10:27:00')

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## drug_source_value : 1567/3937 lignes concordent (39.8%)  [text]
    ex: nous='617296' vs référence='amoxicillin 500 MG / clavulanate 125 MG Oral Table'
    ex: nous='Administration of vaccine product containing only ' vs référence='399014008'
    ex: nous='1000126' vs référence='1 ML medroxyPROGESTERone acetate 150 MG/ML Injecti'

## drug_source_concept_id : 3937/3937 lignes concordent (100.0%)  [concept]

# Écarts de portée (champs exclus du score)

  quantity : jamais renseigné chez nous
  days_supply : jamais renseigné chez nous

## Résumé
  Couverture de la référence : 51.7%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 3930/3937 (99.8%)
  Accord sémantique par champ (toutes les valeurs comparées) : 99.9%
  Accord de provenance (hors score) : 69.9%

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

⚠️  CLÉ NON UNIQUE : 129 doublon(s) chez nous, 22 chez la référence, sur (person + ['procedure_concept_id', 'procedure_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 10257
  Clés UNIQUEMENT chez nous : 1588
  Clés UNIQUEMENT chez la référence : 1698
    ex: [(114, 4036803, datetime.date(2022, 12, 17)), (114, 4036803, datetime.date(2025, 12, 13)), (114, 4036803, datetime.date(2001, 6, 10))]
    ex: [(105, 4155973, datetime.date(1992, 1, 25)), (19, 4036803, datetime.date(2016, 1, 24)), (55, 4036803, datetime.date(2024, 4, 16))]

Lignes appariées (même personne + même clé naturelle) : 10279
  Couverture de la référence : 10279/11977 (85.8%) - part des lignes de la référence retrouvées chez nous
  Précision : 10279/11974 (85.8%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## procedure_datetime : 10277/10279 lignes concordent (100.0%)  [datetime]
    ex: nous=Timestamp('2012-06-06 06:39:18') vs référence=Timestamp('2012-06-06 17:07:08')
    ex: nous=Timestamp('2021-04-14 06:39:18') vs référence=Timestamp('2021-04-14 17:07:08')

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## procedure_source_value : 10279/10279 lignes concordent (100.0%)  [text]

## procedure_source_concept_id : 10279/10279 lignes concordent (100.0%)  [concept]

# Écarts de portée (champs exclus du score)

  quantity : vide des deux côtés

## Résumé
  Couverture de la référence : 85.8%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 10277/10279 (100.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 100.0%
  Accord de provenance (hors score) : 100.0%

---

# Comparaison ligne à ligne — measurement

Clé naturelle : person + ['measurement_concept_id', 'measurement_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 57585 lignes
  Chez la référence : 55920 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 57585 lignes (0 exclues - patient non apparié)
  Chez la référence : 55920 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 1691 doublon(s) chez nous, 1688 chez la référence, sur (person + ['measurement_concept_id', 'measurement_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 54153
  Clés UNIQUEMENT chez nous : 1741
  Clés UNIQUEMENT chez la référence : 79
    ex: [(92, 36203185, datetime.date(2005, 6, 29)), (55, 36203185, datetime.date(2017, 3, 7)), (70, 36203185, datetime.date(2024, 5, 8))]
    ex: [(62, 3033727, datetime.date(2025, 7, 23)), (62, 3033727, datetime.date(2023, 8, 10)), (63, 3024209, datetime.date(2013, 1, 3))]

Lignes appariées (même personne + même clé naturelle) : 55841
  Couverture de la référence : 55841/55920 (99.9%) - part des lignes de la référence retrouvées chez nous
  Précision : 55841/57585 (97.0%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## measurement_datetime : 55841/55841 lignes concordent (100.0%)  [datetime]

## value_as_number : 44087/44087 lignes concordent (100.0%)  [number]

## unit_concept_id : 38585/43299 lignes concordent (89.1%)  [concept]
    ex: nous=np.int64(0) vs référence=np.int64(44777566)
    ex: nous=np.int64(0) vs référence=np.int64(44777566)
    ex: nous=np.int64(0) vs référence=np.int64(44777566)

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## measurement_source_value : 55837/55841 lignes concordent (100.0%)  [text]
    ex: nous='85318-4' vs référence='85319-2'
    ex: nous='85319-2' vs référence='85337-4'
    ex: nous='85337-4' vs référence='85339-0'

## measurement_source_concept_id : 55837/55841 lignes concordent (100.0%)  [concept]
    ex: nous=np.int64(36203113) vs référence=np.int64(36203114)
    ex: nous=np.int64(36203114) vs référence=np.int64(36203168)
    ex: nous=np.int64(36203168) vs référence=np.int64(36203170)

## unit_source_value : 44087/51455 lignes concordent (85.7%)  [text]
    ex: nous='' vs référence='{nominal}'
    ex: nous='' vs référence='{nominal}'
    ex: nous='' vs référence='{nominal}'

## value_source_value : 0/55841 lignes concordent (0.0%)  [text]
    ex: nous='' vs référence='1.0'
    ex: nous='' vs référence='Urine leukocyte test one plus (finding)'
    ex: nous='' vs référence='6.7'

# Écarts de portée (champs exclus du score)

  value_as_concept_id : vide des deux côtés

## Résumé
  Couverture de la référence : 99.9%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 51127/55841 (91.6%)
  Accord sémantique par champ (toutes les valeurs comparées) : 96.7%
  Accord de provenance (hors score) : 71.1%

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

⚠️  CLÉ NON UNIQUE : 363 doublon(s) chez nous, 208 chez la référence, sur (person + ['observation_concept_id', 'observation_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 34344
  Clés UNIQUEMENT chez nous : 6272
  Clés UNIQUEMENT chez la référence : 5298
    ex: [(114, 4085798, datetime.date(1984, 11, 16)), (33, 4199788, datetime.date(1981, 5, 9)), (114, 4176269, datetime.date(2014, 12, 3))]
    ex: [(46, 4085798, datetime.date(2018, 8, 25)), (105, 4085798, datetime.date(1985, 6, 4)), (62, 4085798, datetime.date(2022, 10, 7))]
  Parmi elles, 131 combinaison(s) (personne + ['observation_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 34373
  Couverture de la référence : 34373/39850 (86.3%) - part des lignes de la référence retrouvées chez nous
  Précision : 34373/40979 (83.9%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## observation_datetime : 34370/34373 lignes concordent (100.0%)  [datetime]
    ex: nous=Timestamp('2020-01-01 12:32:25') vs référence=Timestamp('2020-01-01 17:07:08')
    ex: nous=Timestamp('2022-01-19 04:16:04') vs référence=Timestamp('2022-01-19 17:07:08')
    ex: nous=Timestamp('2022-05-25 12:32:25') vs référence=Timestamp('2022-05-25 17:07:08')

## value_as_number : 4804/5180 lignes concordent (92.7%)  [number]
    ex: nous=np.float64(164370.0) vs référence=np.float64(164369.0)
    ex: nous=np.float64(164370.0) vs référence=np.float64(164369.0)
    ex: nous=np.float64(164370.0) vs référence=np.float64(164369.0)

## value_as_string : 1140/34373 lignes concordent (3.3%)  [text]
    ex: nous=nan vs référence='Postoperative care for dental procedure (regime/therapy)'
    ex: nous=nan vs référence='Postoperative care for dental procedure (regime/therapy)'
    ex: nous=nan vs référence='Postoperative care for dental procedure (regime/therapy)'

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## observation_source_value : 29976/34373 lignes concordent (87.2%)  [text]
    ex: nous='Postoperative care for dental procedure (regime/th' vs référence='456191000124101'
    ex: nous='Postoperative care for dental procedure (regime/th' vs référence='456191000124101'
    ex: nous='Postoperative care for dental procedure (regime/th' vs référence='456191000124101'

## observation_source_concept_id : 34373/34373 lignes concordent (100.0%)  [concept]

## unit_source_value : 5180/5204 lignes concordent (99.5%)  [text]
    ex: nous='' vs référence='{#}'
    ex: nous='' vs référence='{#}'
    ex: nous='' vs référence='{#}'

# Écarts de portée (champs exclus du score)

  value_as_concept_id : vide des deux côtés
  unit_concept_id : jamais renseigné chez nous

## Résumé
  Couverture de la référence : 86.3%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 1140/34373 (3.3%)
  Accord sémantique par champ (toutes les valeurs comparées) : 54.5%
  Accord de provenance (hors score) : 94.0%

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
  Clés présentes des deux côtés : 12
  Clés UNIQUEMENT chez nous : 2
  Clés UNIQUEMENT chez la référence : 2
    ex: [(64, datetime.date(1973, 9, 6)), (104, datetime.date(1987, 8, 22))]
    ex: [(104, datetime.date(1987, 8, 21)), (64, datetime.date(1973, 9, 5))]
  Parmi elles, 2 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 12
  Couverture de la référence : 12/14 (85.7%) - part des lignes de la référence retrouvées chez nous
  Précision : 12/14 (85.7%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## death_datetime : 12/12 lignes concordent (100.0%)  [datetime]

# Écarts de portée (champs exclus du score)

  cause_concept_id : vide des deux côtés
  cause_source_value : vide des deux côtés
  cause_source_concept_id : vide des deux côtés

## Résumé
  Couverture de la référence : 85.7%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 12/12 (100.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 100.0%

---

# Comparaison ligne à ligne — observation_period

Clé naturelle : person + ['observation_period_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 3893 lignes
  Chez la référence : 6414 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 114

## Volumes après restriction aux patients communs
  Chez nous : 3893 lignes (0 exclues - patient non apparié)
  Chez la référence : 6414 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 33
  Clés UNIQUEMENT chez nous : 3860
  Clés UNIQUEMENT chez la référence : 6381
    ex: [(114, datetime.date(2022, 5, 27)), (114, datetime.date(2024, 7, 5)), (114, datetime.date(1991, 9, 26))]
    ex: [(105, datetime.date(1990, 11, 29)), (70, datetime.date(2025, 12, 11)), (100, datetime.date(2019, 12, 22))]
  Parmi elles, 1 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 33
  Couverture de la référence : 33/6414 (0.5%) - part des lignes de la référence retrouvées chez nous
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
