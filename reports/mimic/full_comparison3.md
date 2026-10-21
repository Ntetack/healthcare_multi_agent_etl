# Full Comparison Report

## Executive Summary

| Table | Rows (ours) | Rows (reference) | Matched | Coverage of the reference | Semantic agreement | Provenance (not scored) | Note |
|---|---|---|---|---|---|---|---|
| person | 100 | 100 | 0 | 0/100 (0.0%) | n/a | n/a | 100 ours-only / 100 reference-only keys |
| visit_occurrence | 129 | 129 | 119 | 119/129 (92.2%) | 37/119 (31.1%) | 100.0% | 9 events found with another date; 10 ours-only / 10 reference-only keys |
| condition_occurrence | 1743 | 1903 | 133 | 133/1903 (7.0%) | n/a | 59.4% | non-unique key (115/1565 dupes, paired by signature); 8 events found with another date; 1513 ours-only / 223 reference-only keys |
| drug_exposure | 27306 | 56715 | 9456 | 9456/56715 (16.7%) | 8955/9456 (94.7%) | 0.0% | non-unique key (16185/44864 dupes, paired by signature); 58 events found with another date; 2982 ours-only / 3712 reference-only keys |
| procedure_occurrence | 1337 | 2815 | 42 | 42/2815 (1.5%) | 33/42 (78.6%) | 3.6% | non-unique key (233/996 dupes, paired by signature); 206 events found with another date; 1063 ours-only / 1778 reference-only keys |
| measurement | 112850 | 823220 | 86063 | 86063/823220 (10.5%) | 78139/86063 (90.8%) | 71.9% | non-unique key (54078/746654 dupes, paired by signature); 4499 ours-only / 22293 reference-only keys |
| observation | 80092 | 22529 | 0 | 0/22529 (0.0%) | n/a | n/a | non-unique key (60721/20847 dupes, paired by signature); 19371 ours-only / 1682 reference-only keys |
| death | 100 | 92 | 90 | 90/92 (97.8%) | 32/90 (35.6%) | n/a | 2 events found with another date; 10 ours-only / 2 reference-only keys |
| observation_period | 129 | 129 | 119 | 119/129 (92.2%) | 119/119 (100.0%) | n/a | 9 events found with another date; 10 ours-only / 10 reference-only keys |

**Coverage of the reference (rows found here / rows of the reference): 96022/907632 (10.6%)**

**Semantic agreement (matched rows whose meaning agrees, weighted by rows): 87315/95889 (91.1%)**

**Reference rows reproduced with the same meaning (found AND agreeing): 87315/883100 (9.9%)**

Provenance fields (`*_source_value`, `*_source_concept_id`) are listed per table but are not part of any figure above: they record how the source wrote a value, which two faithful exports may do differently.

## Per-Table Detail

# Comparaison ligne à ligne — person

Clé naturelle : person + ['person_source_value']

## Volumes bruts (avant tout filtrage)
  Chez nous : 100 lignes
  Chez la référence : 100 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 100 lignes (0 exclues - patient non apparié)
  Chez la référence : 100 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 0
  Clés UNIQUEMENT chez nous : 100
  Clés UNIQUEMENT chez la référence : 100
    ex: [(28, '9533'), (34, '9550'), (24, '9523')]
    ex: [(47, '10126'), (28, '10076'), (84, '42458')]

Lignes appariées (même personne + même clé naturelle) : 0
  Couverture de la référence : 0/100 (0.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 0/100 (0.0%) - part de nos lignes qui existent aussi chez la référence

Aucune ligne appariée : le contenu ne peut pas être comparé.

---

# Comparaison ligne à ligne — visit_occurrence

Clé naturelle : person + ['visit_concept_id', 'visit_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 129 lignes
  Chez la référence : 129 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 129 lignes (0 exclues - patient non apparié)
  Chez la référence : 129 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 119
  Clés UNIQUEMENT chez nous : 10
  Clés UNIQUEMENT chez la référence : 10
    ex: [(29, 262, datetime.date(2192, 11, 20)), (65, 262, datetime.date(2145, 9, 6)), (16, 262, datetime.date(2185, 4, 14))]
    ex: [(54, 262, datetime.date(2151, 8, 12)), (18, 262, datetime.date(2129, 11, 23)), (26, 262, datetime.date(2188, 2, 7))]
  Parmi elles, 9 combinaison(s) (personne + ['visit_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 119
  Couverture de la référence : 119/129 (92.2%) - part des lignes de la référence retrouvées chez nous
  Précision : 119/129 (92.2%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## visit_start_datetime : 37/119 lignes concordent (31.1%)  [datetime]
    ex: nous=Timestamp('2164-10-23 21:09:00') vs référence=Timestamp('2164-10-23 16:43:00')
    ex: nous=Timestamp('2149-05-26 17:19:00') vs référence=Timestamp('2149-05-26 12:08:00')
    ex: nous=Timestamp('2195-05-17 07:39:00') vs référence=Timestamp('2195-05-17 01:49:00')

## visit_end_date : 119/119 lignes concordent (100.0%)  [date]

## visit_end_datetime : 119/119 lignes concordent (100.0%)  [datetime]

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## visit_source_value : 119/119 lignes concordent (100.0%)  [text]

# Écarts de portée (champs exclus du score)

  visit_source_concept_id : jamais renseigné chez nous

## Résumé
  Couverture de la référence : 92.2%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 37/119 (31.1%)
  Accord sémantique par champ (toutes les valeurs comparées) : 77.0%
  Accord de provenance (hors score) : 100.0%

---

# Comparaison ligne à ligne — condition_occurrence

Clé naturelle : person + ['condition_concept_id', 'condition_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 1743 lignes
  Chez la référence : 1903 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 1743 lignes (0 exclues - patient non apparié)
  Chez la référence : 1903 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 115 doublon(s) chez nous, 1565 chez la référence, sur (person + ['condition_concept_id', 'condition_start_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 115
  Clés UNIQUEMENT chez nous : 1513
  Clés UNIQUEMENT chez la référence : 223
    ex: [(99, 44784439, datetime.date(2180, 7, 19)), (12, 435508, datetime.date(2185, 3, 24)), (43, 440276, datetime.date(2138, 11, 9))]
    ex: [(10, 0, datetime.date(2132, 12, 4)), (25, 440897, datetime.date(2130, 10, 6)), (33, 0, datetime.date(2141, 1, 25))]
  Parmi elles, 8 combinaison(s) (personne + ['condition_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 133
  Couverture de la référence : 133/1903 (7.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 133/1743 (7.6%) - part de nos lignes qui existent aussi chez la référence

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## condition_source_value : 79/133 lignes concordent (59.4%)  [text]
    ex: nous='99591' vs référence='SEPSIS'
    ex: nous='0389' vs référence='SEPSIS'
    ex: nous='0389' vs référence='SEPSIS'

## condition_source_concept_id : 79/133 lignes concordent (59.4%)  [concept]
    ex: nous=np.int64(44820254) vs référence=np.float64(nan)
    ex: nous=np.int64(44823969) vs référence=np.float64(nan)
    ex: nous=np.int64(44823969) vs référence=np.float64(nan)

# Écarts de portée (champs exclus du score)

  condition_start_datetime : jamais renseigné chez nous
  condition_end_date : jamais renseigné chez nous
  condition_end_datetime : jamais renseigné chez nous

## Résumé
  Couverture de la référence : 7.0%
  Accord sémantique : aucun champ sémantique comparable.
  Accord de provenance (hors score) : 59.4%

---

# Comparaison ligne à ligne — drug_exposure

Clé naturelle : person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 27306 lignes
  Chez la référence : 56715 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 27306 lignes (0 exclues - patient non apparié)
  Chez la référence : 56715 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 16185 doublon(s) chez nous, 44864 chez la référence, sur (person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 8139
  Clés UNIQUEMENT chez nous : 2982
  Clés UNIQUEMENT chez la référence : 3712
    ex: [(81, 19111276, datetime.date(2147, 10, 3), datetime.date(2147, 10, 4)), (47, 4298217, datetime.date(2171, 7, 16), datetime.date(2171, 7, 16)), (6, 42799739, datetime.date(2195, 5, 17), datetime.date(2195, 5, 18))]
    ex: [(76, 3037253, datetime.date(2119, 11, 4), datetime.date(2119, 11, 4)), (100, 3037253, datetime.date(2170, 12, 19), datetime.date(2170, 12, 19)), (56, 0, datetime.date(2163, 11, 22), datetime.date(2163, 11, 22))]
  Parmi elles, 58 combinaison(s) (personne + ['drug_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 9456
  Couverture de la référence : 9456/56715 (16.7%) - part des lignes de la référence retrouvées chez nous
  Précision : 9456/27306 (34.6%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## drug_exposure_start_datetime : 9402/9456 lignes concordent (99.4%)  [datetime]
    ex: nous=Timestamp('2144-07-13 16:52:00') vs référence=Timestamp('2144-07-13 19:32:00')
    ex: nous=Timestamp('2144-07-17 00:41:00') vs référence=Timestamp('2144-07-17 02:47:00')
    ex: nous=Timestamp('2144-07-17 02:47:00') vs référence=Timestamp('2144-07-17 07:29:00')

## drug_exposure_end_datetime : 9396/9456 lignes concordent (99.4%)  [datetime]
    ex: nous=Timestamp('2144-07-13 19:32:00') vs référence=Timestamp('2144-07-13 22:12:00')
    ex: nous=Timestamp('2144-07-17 07:31:00') vs référence=Timestamp('2144-07-17 02:48:00')
    ex: nous=Timestamp('2144-07-17 02:48:00') vs référence=Timestamp('2144-07-17 10:56:00')

## quantity : 8426/8921 lignes concordent (94.5%)  [number]
    ex: nous=np.float64(nan) vs référence=np.float64(40000.0)
    ex: nous=np.float64(538.205958) vs référence=np.float64(40.0272168675)
    ex: nous=np.float64(0.0308333351) vs référence=np.float64(25.0000014)

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## drug_source_value : 0/9456 lignes concordent (0.0%)  [text]
    ex: nous='Acetaminophen' vs référence='00677178110'
    ex: nous='Atorvastatin' vs référence='00071015623'
    ex: nous='Metronidazole' vs référence='51079012620'

## drug_source_concept_id : 0/9456 lignes concordent (0.0%)  [concept]
    ex: nous=np.int64(44841251) vs référence=np.float64(nan)
    ex: nous=np.int64(44907135) vs référence=np.float64(nan)
    ex: nous=np.int64(45376246) vs référence=np.float64(nan)

# Écarts de portée (champs exclus du score)

  days_supply : vide des deux côtés

## Résumé
  Couverture de la référence : 16.7%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 8955/9456 (94.7%)
  Accord sémantique par champ (toutes les valeurs comparées) : 97.8%
  Accord de provenance (hors score) : 0.0%

---

# Comparaison ligne à ligne — procedure_occurrence

Clé naturelle : person + ['procedure_concept_id', 'procedure_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 1337 lignes
  Chez la référence : 2815 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 1337 lignes (0 exclues - patient non apparié)
  Chez la référence : 2815 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 233 doublon(s) chez nous, 996 chez la référence, sur (person + ['procedure_concept_id', 'procedure_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 41
  Clés UNIQUEMENT chez nous : 1063
  Clés UNIQUEMENT chez la référence : 1778
    ex: [(81, 3526814, datetime.date(2147, 10, 20)), (30, 4213288, datetime.date(2107, 1, 4)), (98, 3526814, datetime.date(2123, 12, 15))]
    ex: [(76, 4214577, datetime.date(2119, 11, 13)), (67, 4163951, datetime.date(2201, 9, 28)), (81, 4214577, datetime.date(2147, 10, 25))]
  Parmi elles, 206 combinaison(s) (personne + ['procedure_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 42
  Couverture de la référence : 42/2815 (1.5%) - part des lignes de la référence retrouvées chez nous
  Précision : 42/1337 (3.1%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## procedure_datetime : 33/42 lignes concordent (78.6%)  [datetime]
    ex: nous=NaT vs référence=Timestamp('2149-05-26 17:19:00')
    ex: nous=NaT vs référence=Timestamp('2130-10-06 02:29:00')
    ex: nous=NaT vs référence=Timestamp('2130-10-06 02:29:00')

## quantity : 33/35 lignes concordent (94.3%)  [number]
    ex: nous=np.float64(nan) vs référence=np.float64(3610.0)
    ex: nous=np.float64(nan) vs référence=np.float64(164.0)

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## procedure_source_value : 3/42 lignes concordent (7.1%)  [text]
    ex: nous='8181' vs référence='Musculoskeletal system'
    ex: nous='3491' vs référence='Respiratory system'
    ex: nous='225400' vs référence='Bronchoscopy'

## procedure_source_concept_id : 0/42 lignes concordent (0.0%)  [concept]
    ex: nous=np.int64(2005945) vs référence=np.int64(2103758)
    ex: nous=np.int64(2008008) vs référence=np.int64(2001018244)
    ex: nous=np.int64(2008356) vs référence=np.int64(2001017911)

## Résumé
  Couverture de la référence : 1.5%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 33/42 (78.6%)
  Accord sémantique par champ (toutes les valeurs comparées) : 85.7%
  Accord de provenance (hors score) : 3.6%

---

# Comparaison ligne à ligne — measurement

Clé naturelle : person + ['measurement_concept_id', 'measurement_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 112850 lignes
  Chez la référence : 823220 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 112850 lignes (0 exclues - patient non apparié)
  Chez la référence : 823220 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 54078 doublon(s) chez nous, 746654 chez la référence, sur (person + ['measurement_concept_id', 'measurement_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 54273
  Clés UNIQUEMENT chez nous : 4499
  Clés UNIQUEMENT chez la référence : 22293
    ex: [(71, 3000593, datetime.date(2166, 2, 17)), (71, 3022217, datetime.date(2166, 2, 25)), (22, 4208254, datetime.date(2107, 1, 21))]
    ex: [(100, 3034263, datetime.date(2170, 12, 17)), (31, 3012888, datetime.date(2132, 8, 6)), (44, 3020716, datetime.date(2117, 8, 9))]

Lignes appariées (même personne + même clé naturelle) : 86063
  Couverture de la référence : 86063/823220 (10.5%) - part des lignes de la référence retrouvées chez nous
  Précision : 86063/112850 (76.3%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## measurement_datetime : 78709/86063 lignes concordent (91.5%)  [datetime]
    ex: nous=Timestamp('2125-10-05 03:00:00') vs référence=Timestamp('2125-10-05 01:00:00')
    ex: nous=Timestamp('2125-10-05 04:00:00') vs référence=Timestamp('2125-10-05 01:00:00')
    ex: nous=Timestamp('2125-10-05 05:00:00') vs référence=Timestamp('2125-10-05 01:00:00')

## value_as_number : 73479/80126 lignes concordent (91.7%)  [number]
    ex: nous=np.float64(nan) vs référence=np.float64(2.0)
    ex: nous=np.float64(nan) vs référence=np.float64(50.0)
    ex: nous=np.float64(nan) vs référence=np.float64(1.0)

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## measurement_source_value : 83344/86063 lignes concordent (96.8%)  [text]
    ex: nous='618' vs référence='615'
    ex: nous='618' vs référence='219'
    ex: nous='618' vs référence='615'

## measurement_source_concept_id : 0/86063 lignes concordent (0.0%)  [concept]
    ex: nous=np.int64(3000330) vs référence=np.float64(2001031633.0)
    ex: nous=np.int64(3000330) vs référence=np.float64(2001031633.0)
    ex: nous=np.int64(3000330) vs référence=np.float64(2001031633.0)

## unit_source_value : 80688/80935 lignes concordent (99.7%)  [text]
    ex: nous='BPM' vs référence=nan
    ex: nous='BPM' vs référence=nan
    ex: nous='BPM' vs référence=nan

## value_source_value : 79652/86062 lignes concordent (92.6%)  [text]
    ex: nous='18' vs référence='26'
    ex: nous='22' vs référence='40'
    ex: nous='26' vs référence='18'

# Écarts de portée (champs exclus du score)

  value_as_concept_id : vide des deux côtés
  unit_concept_id : jamais renseigné chez nous

## Résumé
  Couverture de la référence : 10.5%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 78139/86063 (90.8%)
  Accord sémantique par champ (toutes les valeurs comparées) : 91.6%
  Accord de provenance (hors score) : 71.9%

---

# Comparaison ligne à ligne — observation

Clé naturelle : person + ['observation_concept_id', 'observation_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 80092 lignes
  Chez la référence : 22529 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 80092 lignes (0 exclues - patient non apparié)
  Chez la référence : 22529 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 60721 doublon(s) chez nous, 20847 chez la référence, sur (person + ['observation_concept_id', 'observation_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 0
  Clés UNIQUEMENT chez nous : 19371
  Clés UNIQUEMENT chez la référence : 1682
    ex: [(66, 40488239, datetime.date(2145, 12, 1)), (21, 40775801, datetime.date(2150, 8, 8)), (44, 40795740, datetime.date(2117, 8, 23))]
    ex: [(28, 4078442, datetime.date(2107, 3, 29)), (51, 0, datetime.date(2063, 7, 5)), (55, 4296248, datetime.date(2193, 10, 15))]

Lignes appariées (même personne + même clé naturelle) : 0
  Couverture de la référence : 0/22529 (0.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 0/80092 (0.0%) - part de nos lignes qui existent aussi chez la référence

Aucune ligne appariée : le contenu ne peut pas être comparé.

---

# Comparaison ligne à ligne — death

Clé naturelle : person + ['death_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 100 lignes
  Chez la référence : 92 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 100 lignes (0 exclues - patient non apparié)
  Chez la référence : 92 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 90
  Clés UNIQUEMENT chez nous : 10
  Clés UNIQUEMENT chez la référence : 2
    ex: [(63, datetime.date(2145, 3, 7)), (92, datetime.date(2107, 7, 13)), (75, datetime.date(2136, 3, 26))]
    ex: [(64, datetime.date(2155, 3, 11)), (74, datetime.date(2103, 5, 18))]
  Parmi elles, 2 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 90
  Couverture de la référence : 90/92 (97.8%) - part des lignes de la référence retrouvées chez nous
  Précision : 90/100 (90.0%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## death_datetime : 32/90 lignes concordent (35.6%)  [datetime]
    ex: nous=NaT vs référence=Timestamp('2165-08-12 00:00:00')
    ex: nous=NaT vs référence=Timestamp('2152-09-12 00:00:00')
    ex: nous=NaT vs référence=Timestamp('2195-11-24 00:00:00')

# Écarts de portée (champs exclus du score)

  cause_concept_id : vide des deux côtés
  cause_source_value : renseigné seulement chez nous
  cause_source_concept_id : vide des deux côtés

## Résumé
  Couverture de la référence : 97.8%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 32/90 (35.6%)
  Accord sémantique par champ (toutes les valeurs comparées) : 35.6%

---

# Comparaison ligne à ligne — observation_period

Clé naturelle : person + ['observation_period_start_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 129 lignes
  Chez la référence : 129 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 129 lignes (0 exclues - patient non apparié)
  Chez la référence : 129 lignes (0 exclues - patient non apparié)

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 119
  Clés UNIQUEMENT chez nous : 10
  Clés UNIQUEMENT chez la référence : 10
    ex: [(62, datetime.date(2159, 11, 17)), (65, datetime.date(2145, 7, 7)), (18, datetime.date(2129, 11, 24))]
    ex: [(62, datetime.date(2159, 11, 16)), (10, datetime.date(2132, 12, 4)), (64, datetime.date(2155, 3, 7))]
  Parmi elles, 9 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 119
  Couverture de la référence : 119/129 (92.2%) - part des lignes de la référence retrouvées chez nous
  Précision : 119/129 (92.2%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## observation_period_end_date : 119/119 lignes concordent (100.0%)  [date]

## Résumé
  Couverture de la référence : 92.2%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 119/119 (100.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 100.0%

---
