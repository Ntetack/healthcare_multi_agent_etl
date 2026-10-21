# Full Comparison Report

## Executive Summary

| Table | Rows (ours) | Rows (reference) | Matched | Coverage of the reference | Semantic agreement | Provenance (not scored) | Note |
|---|---|---|---|---|---|---|---|
| person | 100 | 100 | 100 | 100/100 (100.0%) | 100/100 (100.0%) | 99.5% |  |
| visit_occurrence | 129 | 129 | 119 | 119/129 (92.2%) | 37/119 (31.1%) | 100.0% | 9 events found with another date; 10 ours-only / 10 reference-only keys |
| condition_occurrence | 1743 | 1903 | 1423 | 1423/1903 (74.8%) | n/a | 99.9% | non-unique key (115/119 dupes, paired by signature); 121 events found with another date; 228 ours-only / 384 reference-only keys |
| drug_exposure | 25738 | 56715 | 9446 | 9446/56715 (16.7%) | 8946/9446 (94.7%) | 0.0% | non-unique key (15681/44819 dupes, paired by signature); 58 events found with another date; 1928 ours-only / 3767 reference-only keys |
| procedure_occurrence | 2543 | 2815 | 66 | 66/2815 (2.3%) | 33/66 (50.0%) | 22.0% | non-unique key (996/996 dupes, paired by signature); 206 events found with another date; 1487 ours-only / 1759 reference-only keys |
| measurement | 112850 | 823220 | 86063 | 86063/823220 (10.5%) | 78139/86063 (90.8%) | 71.9% | non-unique key (54078/746654 dupes, paired by signature); 4499 ours-only / 22293 reference-only keys |
| observation | 80174 | 22529 | 0 | 0/22529 (0.0%) | n/a | n/a | non-unique key (60738/20847 dupes, paired by signature); 19436 ours-only / 1682 reference-only keys |
| death | 100 | 92 | 90 | 90/92 (97.8%) | 32/90 (35.6%) | n/a | 2 events found with another date; 10 ours-only / 2 reference-only keys |
| observation_period | 129 | 129 | 119 | 119/129 (92.2%) | 119/119 (100.0%) | n/a | 9 events found with another date; 10 ours-only / 10 reference-only keys |

**Coverage of the reference (rows found here / rows of the reference): 97426/907632 (10.7%)**

**Semantic agreement (matched rows whose meaning agrees, weighted by rows): 87406/96003 (91.0%)**

**Reference rows reproduced with the same meaning (found AND agreeing): 87406/883200 (9.9%)**

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
  Clés présentes des deux côtés : 100
  Clés UNIQUEMENT chez nous : 0
  Clés UNIQUEMENT chez la référence : 0

Lignes appariées (même personne + même clé naturelle) : 100
  Couverture de la référence : 100/100 (100.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 100/100 (100.0%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## gender_concept_id : 100/100 lignes concordent (100.0%)  [concept]

## year_of_birth : 100/100 lignes concordent (100.0%)  [exact]

## month_of_birth : 100/100 lignes concordent (100.0%)  [exact]

## day_of_birth : 100/100 lignes concordent (100.0%)  [exact]

## birth_datetime : 100/100 lignes concordent (100.0%)  [datetime]

## race_concept_id : 100/100 lignes concordent (100.0%)  [concept]

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## gender_source_value : 100/100 lignes concordent (100.0%)  [text]

## race_source_value : 99/100 lignes concordent (99.0%)  [text]
    ex: nous='AMERICAN INDIAN/ALASKA NATIVE FEDERALLY RECOGNIZED' vs référence='AMERICAN INDIAN/ALASKA NATIVE FEDERALLY RECOGNIZED TRIBE'

# Écarts de portée (champs exclus du score)

  ethnicity_concept_id : renseigné seulement chez nous
  ethnicity_source_value : renseigné seulement chez nous
  gender_source_concept_id : renseigné seulement chez nous
  race_source_concept_id : renseigné seulement chez nous
  ethnicity_source_concept_id : renseigné seulement chez nous

## Résumé
  Couverture de la référence : 100.0%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 100/100 (100.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 100.0%
  Accord de provenance (hors score) : 99.5%

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
    ex: [(29, 262, datetime.date(2192, 11, 20)), (65, 262, datetime.date(2145, 7, 7)), (18, 262, datetime.date(2129, 11, 24))]
    ex: [(16, 262, datetime.date(2185, 4, 13)), (65, 262, datetime.date(2145, 9, 5)), (29, 262, datetime.date(2192, 11, 19))]
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

⚠️  CLÉ NON UNIQUE : 115 doublon(s) chez nous, 119 chez la référence, sur (person + ['condition_concept_id', 'condition_start_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 1400
  Clés UNIQUEMENT chez nous : 228
  Clés UNIQUEMENT chez la référence : 384
    ex: [(62, 198809, datetime.date(2159, 11, 17)), (77, 4125274, datetime.date(2162, 1, 16)), (10, 320128, datetime.date(2132, 12, 5))]
    ex: [(68, 0, datetime.date(2151, 9, 12)), (10, 434610, datetime.date(2132, 12, 4)), (65, 42537729, datetime.date(2145, 7, 6))]
  Parmi elles, 121 combinaison(s) (personne + ['condition_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 1423
  Couverture de la référence : 1423/1903 (74.8%) - part des lignes de la référence retrouvées chez nous
  Précision : 1423/1743 (81.6%) - part de nos lignes qui existent aussi chez la référence

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## condition_source_value : 1421/1423 lignes concordent (99.9%)  [text]
    ex: nous='E9504' vs référence='E9503'
    ex: nous='78720' vs référence='43882'

## condition_source_concept_id : 1421/1423 lignes concordent (99.9%)  [concept]
    ex: nous=np.int64(44822618) vs référence=np.float64(44830707.0)
    ex: nous=np.int64(44828158) vs référence=np.float64(44819717.0)

# Écarts de portée (champs exclus du score)

  condition_start_datetime : jamais renseigné chez nous
  condition_end_date : jamais renseigné chez nous
  condition_end_datetime : jamais renseigné chez nous

## Résumé
  Couverture de la référence : 74.8%
  Accord sémantique : aucun champ sémantique comparable.
  Accord de provenance (hors score) : 99.9%

---

# Comparaison ligne à ligne — drug_exposure

Clé naturelle : person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 25738 lignes
  Chez la référence : 56715 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 25738 lignes (0 exclues - patient non apparié)
  Chez la référence : 56715 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 15681 doublon(s) chez nous, 44819 chez la référence, sur (person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 8129
  Clés UNIQUEMENT chez nous : 1928
  Clés UNIQUEMENT chez la référence : 3767
    ex: [(57, 19049105, datetime.date(2144, 7, 26), datetime.date(2144, 7, 26)), (72, 19072153, datetime.date(2127, 10, 26), datetime.date(2127, 10, 26)), (5, 19037038, datetime.date(2163, 5, 15), datetime.date(2163, 5, 15))]
    ex: [(53, 0, datetime.date(2155, 12, 20), datetime.date(2155, 12, 21)), (61, 0, datetime.date(2184, 8, 4), datetime.date(2184, 8, 4)), (56, 0, datetime.date(2163, 11, 24), datetime.date(2163, 11, 25))]
  Parmi elles, 58 combinaison(s) (personne + ['drug_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 9446
  Couverture de la référence : 9446/56715 (16.7%) - part des lignes de la référence retrouvées chez nous
  Précision : 9446/25738 (36.7%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## drug_exposure_start_datetime : 9392/9446 lignes concordent (99.4%)  [datetime]
    ex: nous=Timestamp('2144-07-13 16:52:00') vs référence=Timestamp('2144-07-13 19:32:00')
    ex: nous=Timestamp('2144-07-17 00:41:00') vs référence=Timestamp('2144-07-17 02:47:00')
    ex: nous=Timestamp('2144-07-17 02:47:00') vs référence=Timestamp('2144-07-17 07:29:00')

## drug_exposure_end_datetime : 9386/9446 lignes concordent (99.4%)  [datetime]
    ex: nous=Timestamp('2144-07-13 19:32:00') vs référence=Timestamp('2144-07-13 22:12:00')
    ex: nous=Timestamp('2144-07-17 07:31:00') vs référence=Timestamp('2144-07-17 02:48:00')
    ex: nous=Timestamp('2144-07-17 02:48:00') vs référence=Timestamp('2144-07-17 10:56:00')

## quantity : 8417/8911 lignes concordent (94.5%)  [number]
    ex: nous=np.float64(nan) vs référence=np.float64(40000.0)
    ex: nous=np.float64(538.205958) vs référence=np.float64(40.0272168675)
    ex: nous=np.float64(0.0308333351) vs référence=np.float64(25.0000014)

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## drug_source_value : 0/9446 lignes concordent (0.0%)  [text]
    ex: nous='Acetaminophen' vs référence='00677178110'
    ex: nous='Atorvastatin' vs référence='00071015623'
    ex: nous='Metronidazole' vs référence='51079012620'

## drug_source_concept_id : 0/9446 lignes concordent (0.0%)  [concept]
    ex: nous=np.int64(44841251) vs référence=np.float64(nan)
    ex: nous=np.int64(44907135) vs référence=np.float64(nan)
    ex: nous=np.int64(45376246) vs référence=np.float64(nan)

# Écarts de portée (champs exclus du score)

  days_supply : vide des deux côtés

## Résumé
  Couverture de la référence : 16.7%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 8946/9446 (94.7%)
  Accord sémantique par champ (toutes les valeurs comparées) : 97.8%
  Accord de provenance (hors score) : 0.0%

---

# Comparaison ligne à ligne — procedure_occurrence

Clé naturelle : person + ['procedure_concept_id', 'procedure_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 2543 lignes
  Chez la référence : 2815 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 2543 lignes (0 exclues - patient non apparié)
  Chez la référence : 2815 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 996 doublon(s) chez nous, 996 chez la référence, sur (person + ['procedure_concept_id', 'procedure_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 60
  Clés UNIQUEMENT chez nous : 1487
  Clés UNIQUEMENT chez la référence : 1759
    ex: [(32, 2514441, datetime.date(2124, 1, 12)), (71, 3526814, datetime.date(2166, 2, 14)), (40, 2002174, datetime.date(2180, 1, 14))]
    ex: [(67, 2008005, datetime.date(2202, 9, 23)), (67, 4163872, datetime.date(2199, 1, 14)), (67, 4052413, datetime.date(2200, 3, 23))]
  Parmi elles, 206 combinaison(s) (personne + ['procedure_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 66
  Couverture de la référence : 66/2815 (2.3%) - part des lignes de la référence retrouvées chez nous
  Précision : 66/2543 (2.6%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## procedure_datetime : 33/66 lignes concordent (50.0%)  [datetime]
    ex: nous=NaT vs référence=Timestamp('2149-05-26 17:19:00')
    ex: nous=NaT vs référence=Timestamp('2185-04-14 00:23:00')
    ex: nous=NaT vs référence=Timestamp('2150-08-22 17:33:00')

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## procedure_source_value : 3/66 lignes concordent (4.5%)  [text]
    ex: nous='8181' vs référence='Musculoskeletal system'
    ex: nous='99274' vs référence='Confirmatory consultation for a new or established patient (deleted codes)'
    ex: nous='49080' vs référence='Digestive system'

## procedure_source_concept_id : 26/66 lignes concordent (39.4%)  [concept]
    ex: nous=np.int64(2005945) vs référence=np.int64(2103758)
    ex: nous=np.int64(2008008) vs référence=np.int64(2001018244)
    ex: nous=np.int64(2008356) vs référence=np.int64(2001017911)

# Écarts de portée (champs exclus du score)

  quantity : jamais renseigné chez nous

## Résumé
  Couverture de la référence : 2.3%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 33/66 (50.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 50.0%
  Accord de provenance (hors score) : 22.0%

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
    ex: [(72, 4143063, datetime.date(2127, 10, 8)), (40, 21492838, datetime.date(2180, 2, 1)), (47, 3022217, datetime.date(2171, 8, 10))]
    ex: [(98, 21490854, datetime.date(2123, 12, 3)), (81, 3020716, datetime.date(2147, 10, 25)), (98, 3022318, datetime.date(2123, 12, 9))]

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
  Chez nous : 80174 lignes
  Chez la référence : 22529 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 80174 lignes (0 exclues - patient non apparié)
  Chez la référence : 22529 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 60738 doublon(s) chez nous, 20847 chez la référence, sur (person + ['observation_concept_id', 'observation_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 0
  Clés UNIQUEMENT chez nous : 19436
  Clés UNIQUEMENT chez la référence : 1682
    ex: [(71, 40779364, datetime.date(2166, 2, 14)), (81, 4183166, datetime.date(2147, 10, 20)), (88, 1030148, datetime.date(2173, 11, 27))]
    ex: [(46, 4078442, datetime.date(2192, 5, 12)), (3, 46235654, datetime.date(2125, 10, 4)), (66, 0, datetime.date(2145, 12, 13))]

Lignes appariées (même personne + même clé naturelle) : 0
  Couverture de la référence : 0/22529 (0.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 0/80174 (0.0%) - part de nos lignes qui existent aussi chez la référence

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
    ex: [(73, datetime.date(2117, 4, 4)), (99, datetime.date(2182, 8, 3)), (63, datetime.date(2145, 3, 7))]
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
    ex: [(29, datetime.date(2192, 11, 20)), (65, datetime.date(2145, 9, 6)), (54, datetime.date(2151, 8, 13))]
    ex: [(65, datetime.date(2145, 7, 6)), (26, datetime.date(2188, 2, 7)), (65, datetime.date(2145, 9, 5))]
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
