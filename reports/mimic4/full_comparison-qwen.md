# Full Comparison Report

## Executive Summary

| Table | Rows (ours) | Rows (reference) | Matched | Coverage of the reference | Semantic agreement | Provenance (not scored) | Note |
|---|---|---|---|---|---|---|---|
| person | 100 | 100 | 100 | 100/100 (100.0%) | 100/100 (100.0%) | 99.5% |  |
| visit_occurrence | 129 | 129 | 119 | 119/129 (92.2%) | 37/119 (31.1%) | 100.0% | 9 events found with another date; 10 ours-only / 10 reference-only keys |
| condition_occurrence | 1743 | 1903 | 1423 | 1423/1903 (74.8%) | n/a | 99.9% | non-unique key (115/119 dupes, paired by signature); 121 events found with another date; 228 ours-only / 384 reference-only keys |
| drug_exposure | 28033 | 56715 | 14498 | 14498/56715 (25.6%) | 8801/14498 (60.7%) | 0.0% | non-unique key (11144/30977 dupes, paired by signature); 55 events found with another date; 4257 ours-only / 13106 reference-only keys |
| procedure_occurrence | 5099 | 2815 | 133 | 133/2815 (4.7%) | 133/133 (100.0%) | 0.0% | non-unique key (1651/911 dupes, paired by signature); 232 events found with another date; 3315 ours-only / 1771 reference-only keys |
| measurement | 129018 | 823220 | 112872 | 112872/823220 (13.7%) | 44743/112872 (39.6%) | 67.6% | non-unique key (67419/746654 dupes, paired by signature); 5418 ours-only / 20385 reference-only keys |
| observation | 81121 | 22529 | 1222 | 1222/22529 (5.4%) | 3/1222 (0.2%) | 10.5% | non-unique key (17063/19870 dupes, paired by signature); 213 events found with another date; 63368 ours-only / 1969 reference-only keys |
| death | 129 | 92 | 90 | 90/92 (97.8%) | 39/90 (43.3%) | n/a | non-unique key (29/0 dupes, paired by signature); 2 events found with another date; 10 ours-only / 2 reference-only keys |
| observation_period | 129 | 129 | 119 | 119/129 (92.2%) | 119/119 (100.0%) | n/a | 9 events found with another date; 10 ours-only / 10 reference-only keys |

**Coverage of the reference (rows found here / rows of the reference): 130576/907632 (14.4%)**

**Semantic agreement (matched rows whose meaning agrees, weighted by rows): 53975/129153 (41.8%)**

**Reference rows reproduced with the same meaning (found AND agreeing): 53975/905729 (6.0%)**

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
    ex: [(26, 262, datetime.date(2188, 2, 8)), (18, 262, datetime.date(2129, 11, 24)), (65, 262, datetime.date(2145, 7, 7))]
    ex: [(18, 262, datetime.date(2129, 11, 23)), (29, 262, datetime.date(2192, 11, 19)), (10, 262, datetime.date(2132, 12, 4))]
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
    ex: [(62, 192357, datetime.date(2159, 11, 17)), (67, 4125274, datetime.date(2201, 5, 12)), (64, 320128, datetime.date(2155, 3, 8))]
    ex: [(90, 1340204, datetime.date(2176, 7, 14)), (65, 42537729, datetime.date(2145, 7, 6)), (99, 0, datetime.date(2180, 7, 19))]
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

Clé naturelle : person + ['drug_concept_id', 'drug_exposure_start_datetime']

## Volumes bruts (avant tout filtrage)
  Chez nous : 28033 lignes
  Chez la référence : 56715 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 28033 lignes (0 exclues - patient non apparié)
  Chez la référence : 56715 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 11144 doublon(s) chez nous, 30977 chez la référence, sur (person + ['drug_concept_id', 'drug_exposure_start_datetime']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 12632
  Clés UNIQUEMENT chez nous : 4257
  Clés UNIQUEMENT chez la référence : 13106
    ex: [(40, 1367571, Timestamp('2180-01-29 12:00:00')), (71, 914335, Timestamp('2166-02-17 14:45:00')), (67, 19037038, Timestamp('2198-10-30 17:10:00'))]
    ex: [(47, 0, Timestamp('2171-07-23 15:00:00')), (72, 3037253, Timestamp('2127-10-09 02:25:00')), (57, 0, Timestamp('2144-12-29 21:05:00'))]
  Parmi elles, 55 combinaison(s) (personne + ['drug_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 14498
  Couverture de la référence : 14498/56715 (25.6%) - part des lignes de la référence retrouvées chez nous
  Précision : 14498/28033 (51.7%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## drug_exposure_start_date : 14485/14498 lignes concordent (99.9%)  [date]
    ex: nous=datetime.date(2139, 9, 22) vs référence=None
    ex: nous=datetime.date(2138, 4, 2) vs référence=None
    ex: nous=datetime.date(2129, 3, 3) vs référence=None

## drug_exposure_end_datetime : 9442/14498 lignes concordent (65.1%)  [datetime]
    ex: nous=Timestamp('2125-10-05 01:51:00') vs référence=Timestamp('2125-10-06 00:00:00')
    ex: nous=Timestamp('2125-10-05 01:51:00') vs référence=NaT
    ex: nous=Timestamp('2125-10-05 02:52:00') vs référence=NaT

## quantity : 9363/13935 lignes concordent (67.2%)  [number]
    ex: nous=np.float64(0.045) vs référence=np.float64(250.0)
    ex: nous=np.float64(nan) vs référence=np.float64(250.0)
    ex: nous=np.float64(nan) vs référence=np.float64(0.0080000004)

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## drug_source_value : 0/14498 lignes concordent (0.0%)  [text]
    ex: nous='ACET325' vs référence='00677178110'
    ex: nous='ATOR20' vs référence='00071015623'
    ex: nous='METR500' vs référence='51079012620'

## drug_source_concept_id : 0/14498 lignes concordent (0.0%)  [concept]
    ex: nous=np.int64(44841251) vs référence=np.float64(nan)
    ex: nous=np.int64(44907135) vs référence=np.float64(nan)
    ex: nous=np.int64(45376246) vs référence=np.float64(nan)

# Écarts de portée (champs exclus du score)

  days_supply : vide des deux côtés

## Résumé
  Couverture de la référence : 25.6%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 8801/14498 (60.7%)
  Accord sémantique par champ (toutes les valeurs comparées) : 77.5%
  Accord de provenance (hors score) : 0.0%

---

# Comparaison ligne à ligne — procedure_occurrence

Clé naturelle : person + ['procedure_concept_id', 'procedure_datetime']

## Volumes bruts (avant tout filtrage)
  Chez nous : 5099 lignes
  Chez la référence : 2815 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 5099 lignes (0 exclues - patient non apparié)
  Chez la référence : 2815 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 1651 doublon(s) chez nous, 911 chez la référence, sur (person + ['procedure_concept_id', 'procedure_datetime']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 133
  Clés UNIQUEMENT chez nous : 3315
  Clés UNIQUEMENT chez la référence : 1771
    ex: [(81, 4083171, Timestamp('2147-10-15 00:00:00')), (46, 2514441, NaT), (81, 2314001, Timestamp('2147-10-11 00:00:00'))]
    ex: [(53, 4049832, Timestamp('2155-12-16 18:30:00')), (72, 4214577, Timestamp('2127-10-07 00:00:00')), (8, 4089048, Timestamp('2139-09-22 10:58:00'))]
  Parmi elles, 232 combinaison(s) (personne + ['procedure_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 133
  Couverture de la référence : 133/2815 (4.7%) - part des lignes de la référence retrouvées chez nous
  Précision : 133/5099 (2.6%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## procedure_date : 133/133 lignes concordent (100.0%)  [date]

## quantity : 133/133 lignes concordent (100.0%)  [number]

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## procedure_source_value : 0/133 lignes concordent (0.0%)  [text]
    ex: nous='225400' vs référence='Bronchoscopy'
    ex: nous='225459' vs référence='Chest X-Ray'
    ex: nous='225459' vs référence='Chest X-Ray'

## procedure_source_concept_id : 0/133 lignes concordent (0.0%)  [concept]
    ex: nous=np.int64(4032404) vs référence=np.int64(2001029086)
    ex: nous=np.int64(3525904) vs référence=np.int64(2001029180)
    ex: nous=np.int64(3525904) vs référence=np.int64(2001029180)

## Résumé
  Couverture de la référence : 4.7%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 133/133 (100.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 100.0%
  Accord de provenance (hors score) : 0.0%

---

# Comparaison ligne à ligne — measurement

Clé naturelle : person + ['measurement_concept_id', 'measurement_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 129018 lignes
  Chez la référence : 823220 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 129018 lignes (0 exclues - patient non apparié)
  Chez la référence : 823220 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 67419 doublon(s) chez nous, 746654 chez la référence, sur (person + ['measurement_concept_id', 'measurement_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 56181
  Clés UNIQUEMENT chez nous : 5418
  Clés UNIQUEMENT chez la référence : 20385
    ex: [(67, 3022217, datetime.date(2201, 5, 17)), (44, 3022217, datetime.date(2117, 8, 21)), (81, 21492838, datetime.date(2147, 10, 17))]
    ex: [(67, 3016502, datetime.date(2200, 11, 1)), (96, 3009094, datetime.date(2112, 5, 25)), (38, 3036277, datetime.date(2120, 8, 24))]

Lignes appariées (même personne + même clé naturelle) : 112872
  Couverture de la référence : 112872/823220 (13.7%) - part des lignes de la référence retrouvées chez nous
  Précision : 112872/129018 (87.5%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## measurement_datetime : 105504/112872 lignes concordent (93.5%)  [datetime]
    ex: nous=Timestamp('2125-10-05 03:00:00') vs référence=Timestamp('2125-10-05 01:00:00')
    ex: nous=Timestamp('2125-10-05 04:00:00') vs référence=Timestamp('2125-10-05 01:00:00')
    ex: nous=Timestamp('2125-10-05 05:00:00') vs référence=Timestamp('2125-10-05 01:00:00')

## value_as_number : 99902/106770 lignes concordent (93.6%)  [number]
    ex: nous=np.float64(nan) vs référence=np.float64(2.0)
    ex: nous=np.float64(nan) vs référence=np.float64(50.0)
    ex: nous=np.float64(nan) vs référence=np.float64(1.0)

## unit_concept_id : 39892/107534 lignes concordent (37.1%)  [concept]
    ex: nous=np.int64(0) vs référence=np.float64(8889.0)
    ex: nous=np.int64(0) vs référence=np.float64(8889.0)
    ex: nous=np.int64(0) vs référence=np.float64(8889.0)

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## measurement_source_value : 98833/112872 lignes concordent (87.6%)  [text]
    ex: nous='40054' vs référence='Stool Out Stool'
    ex: nous='40055' vs référence='Urine Out Foley'
    ex: nous='40069' vs référence='Urine Out Void'

## measurement_source_concept_id : 0/112872 lignes concordent (0.0%)  [concept]
    ex: nous=np.int64(3000330) vs référence=np.float64(2001031633.0)
    ex: nous=np.int64(3000330) vs référence=np.float64(2001031633.0)
    ex: nous=np.int64(3000330) vs référence=np.float64(2001031633.0)

## unit_source_value : 107450/107697 lignes concordent (99.8%)  [text]
    ex: nous='BPM' vs référence=nan
    ex: nous='BPM' vs référence=nan
    ex: nous='BPM' vs référence=nan

## value_source_value : 95122/112706 lignes concordent (84.4%)  [text]
    ex: nous='100' vs référence=nan
    ex: nous='10' vs référence=nan
    ex: nous='400' vs référence=nan

# Écarts de portée (champs exclus du score)

  value_as_concept_id : vide des deux côtés

## Résumé
  Couverture de la référence : 13.7%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 44743/112872 (39.6%)
  Accord sémantique par champ (toutes les valeurs comparées) : 75.0%
  Accord de provenance (hors score) : 67.6%

---

# Comparaison ligne à ligne — observation

Clé naturelle : person + ['observation_concept_id', 'observation_datetime']

## Volumes bruts (avant tout filtrage)
  Chez nous : 81121 lignes
  Chez la référence : 22529 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 81121 lignes (0 exclues - patient non apparié)
  Chez la référence : 22529 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 17063 doublon(s) chez nous, 19870 chez la référence, sur (person + ['observation_concept_id', 'observation_datetime']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 690
  Clés UNIQUEMENT chez nous : 63368
  Clés UNIQUEMENT chez la référence : 1969
    ex: [(87, 4221803, Timestamp('2179-04-20 12:00:00')), (47, 1989127, Timestamp('2171-08-13 01:00:00')), (66, 4117957, Timestamp('2145-12-06 06:00:00'))]
    ex: [(57, 40766231, Timestamp('2144-07-11 15:02:00')), (54, 42536500, Timestamp('2151-08-12 13:12:00')), (91, 42536500, Timestamp('2186-02-09 23:03:00'))]
  Parmi elles, 213 combinaison(s) (personne + ['observation_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 1222
  Couverture de la référence : 1222/22529 (5.4%) - part des lignes de la référence retrouvées chez nous
  Précision : 1222/81121 (1.5%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## observation_date : 1222/1222 lignes concordent (100.0%)  [date]

## value_as_number : 1/606 lignes concordent (0.2%)  [number]
    ex: nous=np.float64(nan) vs référence=np.float64(1.0)
    ex: nous=np.float64(nan) vs référence=np.float64(13.0)
    ex: nous=np.float64(nan) vs référence=np.float64(1.0)

## value_as_string : 3/1222 lignes concordent (0.2%)  [text]
    ex: nous='MED' vs référence='A'
    ex: nous='MED' vs référence='No Known Drug Allergies'
    ex: nous='MED' vs référence='No Known Drug Allergies'

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## observation_source_value : 19/1222 lignes concordent (1.6%)  [text]
    ex: nous='919' vs référence='925'
    ex: nous='919' vs référence='916'
    ex: nous='919' vs référence='916'

## observation_source_concept_id : 237/1222 lignes concordent (19.4%)  [concept]
    ex: nous=np.int64(1027551) vs référence=np.float64(2001019606.0)
    ex: nous=np.int64(1027551) vs référence=np.float64(2001019601.0)
    ex: nous=np.int64(1027551) vs référence=np.float64(2001019601.0)

# Écarts de portée (champs exclus du score)

  value_as_concept_id : vide des deux côtés
  unit_concept_id : vide des deux côtés
  unit_source_value : renseigné seulement chez nous

## Résumé
  Couverture de la référence : 5.4%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 3/1222 (0.2%)
  Accord sémantique par champ (toutes les valeurs comparées) : 40.2%
  Accord de provenance (hors score) : 10.5%

---

# Comparaison ligne à ligne — death

Clé naturelle : person + ['death_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 129 lignes
  Chez la référence : 92 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 129 lignes (0 exclues - patient non apparié)
  Chez la référence : 92 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 29 doublon(s) chez nous, 0 chez la référence, sur (person + ['death_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 90
  Clés UNIQUEMENT chez nous : 10
  Clés UNIQUEMENT chez la référence : 2
    ex: [(99, datetime.date(2182, 8, 3)), (75, datetime.date(2136, 3, 26)), (82, datetime.date(2166, 5, 30))]
    ex: [(64, datetime.date(2155, 3, 11)), (74, datetime.date(2103, 5, 18))]
  Parmi elles, 2 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 90
  Couverture de la référence : 90/92 (97.8%) - part des lignes de la référence retrouvées chez nous
  Précision : 90/129 (69.8%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## death_datetime : 39/90 lignes concordent (43.3%)  [datetime]
    ex: nous=NaT vs référence=Timestamp('2165-08-12 00:00:00')
    ex: nous=NaT vs référence=Timestamp('2152-09-12 00:00:00')
    ex: nous=NaT vs référence=Timestamp('2195-11-24 00:00:00')

# Écarts de portée (champs exclus du score)

  cause_concept_id : vide des deux côtés
  cause_source_value : vide des deux côtés
  cause_source_concept_id : vide des deux côtés

## Résumé
  Couverture de la référence : 97.8%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 39/90 (43.3%)
  Accord sémantique par champ (toutes les valeurs comparées) : 43.3%

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
    ex: [(16, datetime.date(2185, 4, 14)), (29, datetime.date(2192, 11, 20)), (54, datetime.date(2151, 8, 13))]
    ex: [(64, datetime.date(2155, 3, 7)), (16, datetime.date(2185, 4, 13)), (54, datetime.date(2151, 8, 12))]
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
