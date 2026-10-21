# Full Comparison Report

## Executive Summary

| Table | Rows (ours) | Rows (reference) | Matched | Coverage of the reference | Semantic agreement | Provenance (not scored) | Note |
|---|---|---|---|---|---|---|---|
| person | 114 | 114 | 114 | 114/114 (100.0%) | 114/114 (100.0%) | 54.7% |  |
| visit_occurrence | 6705 | 6703 | 44 | 44/6703 (0.7%) | 0/44 (0.0%) | 0.0% | non-unique key (1970/246 dupes, paired by signature); 2 events found with another date; 4691 ours-only / 6413 reference-only keys |
| condition_occurrence | 1985 | 1985 | 1270 | 1270/1985 (64.0%) | 956/1270 (75.3%) | 100.0% | 613 events found with another date; 715 ours-only / 715 reference-only keys |
| drug_exposure | 7624 | 7616 | 2165 | 2165/7616 (28.4%) | 0/2165 (0.0%) | 50.0% | non-unique key (58/47 dupes, paired by signature); 965 events found with another date; 5434 ours-only / 5437 reference-only keys |
| procedure_occurrence | 11974 | 11977 | 5724 | 5724/11977 (47.8%) | 0/5724 (0.0%) | 100.0% | non-unique key (131/22 dupes, paired by signature); 1467 events found with another date; 6130 ours-only / 6242 reference-only keys |
| measurement | 57621 | 55920 | 30807 | 30807/55920 (55.1%) | 0/30807 (0.0%) | 72.7% | non-unique key (1713/1688 dupes, paired by signature); 4076 events found with another date; 26066 ours-only / 24390 reference-only keys |
| observation | 40979 | 39850 | 19269 | 19269/39850 (48.4%) | 1384/19269 (7.2%) | 100.0% | non-unique key (351/208 dupes, paired by signature); 3624 events found with another date; 21380 ours-only / 20394 reference-only keys |
| death | 14 | 14 | 7 | 7/14 (50.0%) | 7/7 (100.0%) | n/a | 7 events found with another date; 7 ours-only / 7 reference-only keys |
| observation_period | 2330 | 6414 | 13 | 13/6414 (0.2%) | 13/13 (100.0%) | n/a | non-unique key (4/0 dupes, paired by signature); 1 events found with another date; 2313 ours-only / 6401 reference-only keys |

**Coverage of the reference (rows found here / rows of the reference): 59413/130593 (45.5%)**

**Semantic agreement (matched rows whose meaning agrees, weighted by rows): 2474/59413 (4.2%)**

**Reference rows reproduced with the same meaning (found AND agreeing): 2474/130593 (1.9%)**

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

## race_concept_id : 113/113 lignes concordent (100.0%)  [concept]

## ethnicity_concept_id : 114/114 lignes concordent (100.0%)  [concept]

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## gender_source_value : 0/114 lignes concordent (0.0%)  [text]
    ex: nous='female' vs référence='F'
    ex: nous='male' vs référence='M'
    ex: nous='male' vs référence='M'

## race_source_value : 99/114 lignes concordent (86.8%)  [text]
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
  Accord de provenance (hors score) : 54.7%

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

⚠️  CLÉ NON UNIQUE : 1970 doublon(s) chez nous, 246 chez la référence, sur (person + ['visit_concept_id', 'visit_start_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 44
  Clés UNIQUEMENT chez nous : 4691
  Clés UNIQUEMENT chez la référence : 6413
    ex: [(114, 9202, datetime.date(2025, 8, 3)), (114, 9202, datetime.date(2023, 10, 26)), (114, 9202, datetime.date(2021, 1, 26))]
    ex: [(105, 9202, datetime.date(1988, 3, 20)), (30, 9202, datetime.date(2016, 5, 28)), (34, 9202, datetime.date(2020, 5, 5))]
  Parmi elles, 2 combinaison(s) (personne + ['visit_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 44
  Couverture de la référence : 44/6703 (0.7%) - part des lignes de la référence retrouvées chez nous
  Précision : 44/6705 (0.7%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## visit_start_datetime : 0/44 lignes concordent (0.0%)  [datetime]
    ex: nous=Timestamp('1976-05-11 22:14:31') vs référence=Timestamp('1976-05-11 13:07:08')
    ex: nous=Timestamp('1976-06-02 22:14:31') vs référence=Timestamp('1976-06-02 17:07:08')
    ex: nous=Timestamp('1993-05-12 14:05:03') vs référence=Timestamp('1993-05-12 17:07:08')

## visit_end_date : 44/44 lignes concordent (100.0%)  [date]

## visit_end_datetime : 0/44 lignes concordent (0.0%)  [datetime]
    ex: nous=Timestamp('1976-05-11 23:06:37') vs référence=Timestamp('1976-05-11 13:22:08')
    ex: nous=Timestamp('1976-06-02 22:29:31') vs référence=Timestamp('1976-06-02 17:33:35')
    ex: nous=Timestamp('1993-05-12 14:55:31') vs référence=Timestamp('1993-05-12 18:06:12')

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## visit_source_value : 0/44 lignes concordent (0.0%)  [text]
    ex: nous='Encounter for check up (procedure)' vs référence='ambulatory'
    ex: nous='Encounter for symptom (procedure)' vs référence='ambulatory'
    ex: nous='Outpatient procedure (procedure)' vs référence='wellness'

# Écarts de portée (champs exclus du score)

  visit_source_concept_id : vide des deux côtés

## Résumé
  Couverture de la référence : 0.7%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 0/44 (0.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 33.3%
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
  Clés présentes des deux côtés : 1270
  Clés UNIQUEMENT chez nous : 715
  Clés UNIQUEMENT chez la référence : 715
    ex: [(109, 4281516, datetime.date(2021, 3, 2)), (50, 4281516, datetime.date(2022, 2, 4)), (53, 4281516, datetime.date(2021, 1, 2))]
    ex: [(82, 317510, datetime.date(2025, 4, 2)), (92, 4322737, datetime.date(2010, 6, 9)), (73, 443601, datetime.date(1993, 9, 5))]
  Parmi elles, 613 combinaison(s) (personne + ['condition_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 1270
  Couverture de la référence : 1270/1985 (64.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 1270/1985 (64.0%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## condition_start_datetime : 1269/1270 lignes concordent (99.9%)  [datetime]
    ex: nous=Timestamp('2014-07-15 09:55:05') vs référence=Timestamp('2014-07-15 13:55:05')

## condition_end_date : 561/875 lignes concordent (64.1%)  [date]
    ex: nous=datetime.date(2021, 7, 4) vs référence=datetime.date(2021, 4, 7)
    ex: nous=datetime.date(2024, 4, 10) vs référence=datetime.date(2024, 10, 4)
    ex: nous=datetime.date(2025, 3, 2) vs référence=datetime.date(2025, 2, 3)

## condition_end_datetime : 561/875 lignes concordent (64.1%)  [datetime]
    ex: nous=Timestamp('2021-07-04 14:57:19') vs référence=Timestamp('2021-04-07 00:00:00')
    ex: nous=Timestamp('2024-04-10 12:07:42') vs référence=Timestamp('2024-10-04 00:00:00')
    ex: nous=Timestamp('2025-03-02 14:19:00') vs référence=Timestamp('2025-02-03 00:00:00')

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## condition_source_value : 1269/1270 lignes concordent (99.9%)  [text]
    ex: nous='' vs référence='365853002'

## condition_source_concept_id : 1270/1270 lignes concordent (100.0%)  [concept]

## Résumé
  Couverture de la référence : 64.0%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 956/1270 (75.3%)
  Accord sémantique par champ (toutes les valeurs comparées) : 79.2%
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

⚠️  CLÉ NON UNIQUE : 58 doublon(s) chez nous, 47 chez la référence, sur (person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 2132
  Clés UNIQUEMENT chez nous : 5434
  Clés UNIQUEMENT chez la référence : 5437
    ex: [(92, 19009384, datetime.date(2010, 6, 30), datetime.date(2010, 6, 30)), (62, 19009384, datetime.date(2016, 1, 11), datetime.date(2016, 1, 11)), (92, 40163554, datetime.date(2008, 9, 7), datetime.date(2008, 9, 7))]
    ex: [(92, 40163554, datetime.date(2010, 11, 24), datetime.date(2010, 12, 22)), (102, 1115171, datetime.date(2020, 10, 17), datetime.date(2020, 12, 30)), (92, 40213154, datetime.date(2006, 8, 9), datetime.date(2006, 8, 9))]
  Parmi elles, 965 combinaison(s) (personne + ['drug_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 2165
  Couverture de la référence : 2165/7616 (28.4%) - part des lignes de la référence retrouvées chez nous
  Précision : 2165/7624 (28.4%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## drug_exposure_start_datetime : 0/2165 lignes concordent (0.0%)  [datetime]
    ex: nous=Timestamp('2024-09-29 18:19:33') vs référence=Timestamp('2024-09-29 22:19:33')
    ex: nous=Timestamp('2021-04-24 17:08:35') vs référence=Timestamp('2021-04-24 21:08:35')
    ex: nous=Timestamp('2021-05-15 17:08:35') vs référence=Timestamp('2021-05-15 21:08:35')

## drug_exposure_end_datetime : 0/2165 lignes concordent (0.0%)  [datetime]
    ex: nous=Timestamp('2024-09-29 18:19:33') vs référence=Timestamp('2024-09-29 23:19:33')
    ex: nous=Timestamp('2021-04-24 17:08:35') vs référence=Timestamp('2021-04-24 21:08:35')
    ex: nous=Timestamp('2021-05-15 17:08:35') vs référence=Timestamp('2021-05-15 21:08:35')

## quantity : 21/1339 lignes concordent (1.6%)  [number]
    ex: nous=np.float64(nan) vs référence=np.float64(1.0)
    ex: nous=np.float64(nan) vs référence=np.float64(1.0)
    ex: nous=np.float64(nan) vs référence=np.float64(354.0)

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## drug_source_value : 0/2165 lignes concordent (0.0%)  [text]
    ex: nous='amoxicillin 500 MG / clavulanate 125 MG Oral Table' vs référence='617296'
    ex: nous='COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose' vs référence='208'
    ex: nous='COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose' vs référence='208'

## drug_source_concept_id : 2165/2165 lignes concordent (100.0%)  [concept]

# Écarts de portée (champs exclus du score)

  days_supply : vide des deux côtés

## Résumé
  Couverture de la référence : 28.4%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 0/2165 (0.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 0.4%
  Accord de provenance (hors score) : 50.0%

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

⚠️  CLÉ NON UNIQUE : 131 doublon(s) chez nous, 22 chez la référence, sur (person + ['procedure_concept_id', 'procedure_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 5713
  Clés UNIQUEMENT chez nous : 6130
  Clés UNIQUEMENT chez la référence : 6242
    ex: [(114, 4036803, datetime.date(2020, 4, 17)), (76, 4060626, datetime.date(2023, 12, 11)), (78, 4298386, datetime.date(2017, 11, 4))]
    ex: [(33, 37166720, datetime.date(1974, 12, 28)), (40, 4238738, datetime.date(2018, 1, 9)), (73, 37166720, datetime.date(2017, 1, 30))]
  Parmi elles, 1467 combinaison(s) (personne + ['procedure_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 5724
  Couverture de la référence : 5724/11977 (47.8%) - part des lignes de la référence retrouvées chez nous
  Précision : 5724/11974 (47.8%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## procedure_datetime : 0/5724 lignes concordent (0.0%)  [datetime]
    ex: nous=Timestamp('2017-11-18 16:50:15') vs référence=Timestamp('2017-11-18 21:50:15')
    ex: nous=Timestamp('2018-11-24 16:48:22') vs référence=Timestamp('2018-11-24 21:48:22')
    ex: nous=Timestamp('2019-04-20 17:23:58') vs référence=Timestamp('2019-04-20 21:23:58')

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## procedure_source_value : 5724/5724 lignes concordent (100.0%)  [text]

## procedure_source_concept_id : 5724/5724 lignes concordent (100.0%)  [concept]

# Écarts de portée (champs exclus du score)

  quantity : vide des deux côtés

## Résumé
  Couverture de la référence : 47.8%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 0/5724 (0.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 0.0%
  Accord de provenance (hors score) : 100.0%

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

⚠️  CLÉ NON UNIQUE : 1713 doublon(s) chez nous, 1688 chez la référence, sur (person + ['measurement_concept_id', 'measurement_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 29842
  Clés UNIQUEMENT chez nous : 26066
  Clés UNIQUEMENT chez la référence : 24390
    ex: [(73, 3006906, datetime.date(2022, 2, 13)), (28, 3018834, datetime.date(2017, 6, 3)), (33, 3004501, datetime.date(1978, 12, 5))]
    ex: [(92, 3020630, datetime.date(2010, 5, 12)), (73, 3012888, datetime.date(2017, 6, 19)), (71, 3027018, datetime.date(2017, 11, 16))]
  Parmi elles, 4076 combinaison(s) (personne + ['measurement_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 30807
  Couverture de la référence : 30807/55920 (55.1%) - part des lignes de la référence retrouvées chez nous
  Précision : 30807/57621 (53.5%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## measurement_datetime : 0/30807 lignes concordent (0.0%)  [datetime]
    ex: nous=Timestamp('2024-09-29 18:09:33') vs référence=Timestamp('2024-09-29 22:09:33')
    ex: nous=Timestamp('2024-09-29 18:09:33') vs référence=Timestamp('2024-09-29 22:09:33')
    ex: nous=Timestamp('2024-09-29 18:09:33') vs référence=Timestamp('2024-09-29 22:09:33')

## value_as_number : 23817/24496 lignes concordent (97.2%)  [number]
    ex: nous=np.float64(47.254) vs référence=np.float64(31.0)
    ex: nous=np.float64(47.242) vs référence=np.float64(47.3)
    ex: nous=np.float64(24.615) vs référence=np.float64(47.2)

## unit_concept_id : 1908/24080 lignes concordent (7.9%)  [concept]
    ex: nous=np.int64(0) vs référence=np.int64(8840)
    ex: nous=np.int64(0) vs référence=np.int64(8786)
    ex: nous=np.int64(0) vs référence=np.int64(8482)

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## measurement_source_value : 30807/30807 lignes concordent (100.0%)  [text]

## measurement_source_concept_id : 30807/30807 lignes concordent (100.0%)  [concept]

## unit_source_value : 24496/28401 lignes concordent (86.3%)  [text]
    ex: nous='' vs référence='{nominal}'
    ex: nous='' vs référence='{nominal}'
    ex: nous='' vs référence='{nominal}'

## value_source_value : 6/28486 lignes concordent (0.0%)  [text]
    ex: nous='' vs référence='1.0'
    ex: nous='' vs référence='Urine leukocyte test one plus (finding)'
    ex: nous='' vs référence='Urine microscopy: no casts (finding)'

# Écarts de portée (champs exclus du score)

  value_as_concept_id : vide des deux côtés

## Résumé
  Couverture de la référence : 55.1%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 0/30807 (0.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 32.4%
  Accord de provenance (hors score) : 72.7%

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

⚠️  CLÉ NON UNIQUE : 351 doublon(s) chez nous, 208 chez la référence, sur (person + ['observation_concept_id', 'observation_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 19248
  Clés UNIQUEMENT chez nous : 21380
  Clés UNIQUEMENT chez la référence : 20394
    ex: [(92, 46235654, datetime.date(2008, 10, 9)), (99, 46235654, datetime.date(2024, 10, 1)), (114, 4085799, datetime.date(2020, 8, 3))]
    ex: [(92, 0, datetime.date(2014, 3, 19)), (16, 43054909, datetime.date(2020, 9, 4)), (52, 42868746, datetime.date(2020, 5, 9))]
  Parmi elles, 3624 combinaison(s) (personne + ['observation_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 19269
  Couverture de la référence : 19269/39850 (48.4%) - part des lignes de la référence retrouvées chez nous
  Précision : 19269/40979 (47.0%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## observation_datetime : 1384/19269 lignes concordent (7.2%)  [datetime]
    ex: nous=Timestamp('2023-12-23 18:05:27') vs référence=Timestamp('2023-12-23 23:05:27')
    ex: nous=Timestamp('2022-12-17 17:01:10') vs référence=Timestamp('2022-12-17 22:01:10')
    ex: nous=Timestamp('2023-12-23 16:57:25') vs référence=Timestamp('2023-12-23 21:57:25')

## value_as_number : 2655/5353 lignes concordent (49.6%)  [number]
    ex: nous=np.float64(nan) vs référence=np.float64(431.4)
    ex: nous=np.float64(nan) vs référence=np.float64(431.4)
    ex: nous=np.float64(nan) vs référence=np.float64(431.4)

## value_as_string : 2013/19269 lignes concordent (10.4%)  [text]
    ex: nous='' vs référence='20.0'
    ex: nous='' vs référence='White'
    ex: nous='' vs référence='White'

## unit_concept_id : 630/2110 lignes concordent (29.9%)  [concept]
    ex: nous=np.int64(0) vs référence=np.int64(44777566)
    ex: nous=np.int64(0) vs référence=np.int64(44777566)
    ex: nous=np.int64(0) vs référence=np.int64(44777566)

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## observation_source_value : 19269/19269 lignes concordent (100.0%)  [text]

## observation_source_concept_id : 19269/19269 lignes concordent (100.0%)  [concept]

## unit_source_value : 2849/2869 lignes concordent (99.3%)  [text]
    ex: nous='' vs référence='{#}'
    ex: nous='' vs référence='{#}'
    ex: nous='' vs référence='{#}'

# Écarts de portée (champs exclus du score)

  value_as_concept_id : vide des deux côtés

## Résumé
  Couverture de la référence : 48.4%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 1384/19269 (7.2%)
  Accord sémantique par champ (toutes les valeurs comparées) : 14.5%
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
  Clés présentes des deux côtés : 7
  Clés UNIQUEMENT chez nous : 7
  Clés UNIQUEMENT chez la référence : 7
    ex: [(105, datetime.date(1994, 10, 7)), (63, datetime.date(2020, 3, 7)), (92, datetime.date(2015, 6, 3))]
    ex: [(63, datetime.date(2020, 7, 3)), (27, datetime.date(2016, 6, 7)), (33, datetime.date(1983, 7, 1))]
  Parmi elles, 7 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 7
  Couverture de la référence : 7/14 (50.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 7/14 (50.0%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## death_datetime : 7/7 lignes concordent (100.0%)  [datetime]

# Écarts de portée (champs exclus du score)

  cause_concept_id : vide des deux côtés
  cause_source_value : vide des deux côtés
  cause_source_concept_id : vide des deux côtés

## Résumé
  Couverture de la référence : 50.0%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 7/7 (100.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 100.0%

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

⚠️  CLÉ NON UNIQUE : 4 doublon(s) chez nous, 0 chez la référence, sur (person + ['observation_period_start_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 13
  Clés UNIQUEMENT chez nous : 2313
  Clés UNIQUEMENT chez la référence : 6401
    ex: [(114, datetime.date(2016, 7, 12)), (114, datetime.date(1999, 4, 24)), (114, datetime.date(2023, 10, 31))]
    ex: [(28, datetime.date(2014, 12, 15)), (112, datetime.date(2017, 8, 18)), (46, datetime.date(2018, 4, 13))]
  Parmi elles, 1 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 13
  Couverture de la référence : 13/6414 (0.2%) - part des lignes de la référence retrouvées chez nous
  Précision : 13/2330 (0.6%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## observation_period_end_date : 13/13 lignes concordent (100.0%)  [date]

## Résumé
  Couverture de la référence : 0.2%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 13/13 (100.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 100.0%

---
