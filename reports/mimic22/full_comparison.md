# Full Comparison Report

## Executive Summary

| Table | Rows (ours) | Rows (reference) | Matched | Coverage of the reference | Semantic agreement | Provenance (not scored) | Note |
|---|---|---|---|---|---|---|---|
| person | 100 | 100 | 100 | 100/100 (100.0%) | 100/100 (100.0%) | 99.5% |  |
| visit_occurrence | 129 | 129 | 119 | 119/129 (92.2%) | 37/119 (31.1%) | 100.0% | 9 events found with another date; 10 ours-only / 10 reference-only keys |
| condition_occurrence | 1743 | 1903 | 1423 | 1423/1903 (74.8%) | n/a | 99.9% | non-unique key (115/119 dupes, paired by signature); 121 events found with another date; 228 ours-only / 384 reference-only keys |
| drug_exposure | 28513 | 56715 | 9935 | 9935/56715 (17.5%) | 8948/9935 (90.1%) | 0.0% | non-unique key (15488/44819 dupes, paired by signature); 72 events found with another date; 4705 ours-only / 3576 reference-only keys |
| procedure_occurrence | 5099 | 2815 | 166 | 166/2815 (5.9%) | 131/166 (78.9%) | 8.7% | non-unique key (3126/996 dupes, paired by signature); 205 events found with another date; 1828 ours-only / 1674 reference-only keys |
| measurement | 116877 | 823220 | 101552 | 101552/823220 (12.3%) | 93614/101552 (92.2%) | 72.3% | non-unique key (57052/746654 dupes, paired by signature); 4839 ours-only / 21580 reference-only keys |
| observation | 65149 | 22529 | 2712 | 2712/22529 (12.0%) | 16/2712 (0.6%) | 1.0% | non-unique key (53603/20847 dupes, paired by signature); 19 events found with another date; 11222 ours-only / 1358 reference-only keys |
| death | 100 | 92 | 90 | 90/92 (97.8%) | 32/90 (35.6%) | n/a | 2 events found with another date; 10 ours-only / 2 reference-only keys |
| observation_period | 129 | 129 | 119 | 119/129 (92.2%) | 119/119 (100.0%) | n/a | 9 events found with another date; 10 ours-only / 10 reference-only keys |

**Coverage of the reference (rows found here / rows of the reference): 116216/907632 (12.8%)**

**Semantic agreement (matched rows whose meaning agrees, weighted by rows): 102997/114793 (89.7%)**

**Reference rows reproduced with the same meaning (found AND agreeing): 102997/905729 (11.4%)**

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
    ex: [(10, 262, datetime.date(2132, 12, 5)), (65, 262, datetime.date(2145, 9, 6)), (16, 262, datetime.date(2185, 4, 14))]
    ex: [(10, 262, datetime.date(2132, 12, 4)), (65, 262, datetime.date(2145, 7, 6)), (29, 262, datetime.date(2192, 11, 19))]
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
    ex: [(93, 4125274, datetime.date(2104, 9, 24)), (18, 432867, datetime.date(2129, 11, 24)), (64, 441829, datetime.date(2155, 3, 8))]
    ex: [(37, 0, datetime.date(2105, 5, 29)), (67, 46273937, datetime.date(2202, 5, 1)), (29, 30753, datetime.date(2192, 11, 19))]
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
  Chez nous : 28513 lignes
  Chez la référence : 56715 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 28513 lignes (0 exclues - patient non apparié)
  Chez la référence : 56715 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 15488 doublon(s) chez nous, 44819 chez la référence, sur (person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 8320
  Clés UNIQUEMENT chez nous : 4705
  Clés UNIQUEMENT chez la référence : 3576
    ex: [(38, 19071968, datetime.date(2120, 8, 25), datetime.date(2120, 8, 25)), (67, 19124906, datetime.date(2199, 2, 1), datetime.date(2199, 2, 1)), (98, 1797513, datetime.date(2123, 12, 19), datetime.date(2123, 12, 19))]
    ex: [(81, 0, datetime.date(2147, 10, 28), datetime.date(2147, 10, 28)), (71, 3037253, datetime.date(2166, 2, 17), datetime.date(2166, 2, 17)), (67, 3037253, datetime.date(2202, 1, 1), datetime.date(2202, 1, 1))]
  Parmi elles, 72 combinaison(s) (personne + ['drug_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 9935
  Couverture de la référence : 9935/56715 (17.5%) - part des lignes de la référence retrouvées chez nous
  Précision : 9935/28513 (34.8%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## drug_exposure_start_datetime : 9539/9935 lignes concordent (96.0%)  [datetime]
    ex: nous=Timestamp('2130-02-04 04:36:00') vs référence=Timestamp('2130-02-04 08:52:00')
    ex: nous=Timestamp('2130-02-04 12:18:00') vs référence=Timestamp('2130-02-04 11:15:00')
    ex: nous=Timestamp('2130-08-14 10:18:00') vs référence=Timestamp('2130-08-14 06:00:00')

## drug_exposure_end_datetime : 9501/9935 lignes concordent (95.6%)  [datetime]
    ex: nous=Timestamp('2130-02-04 10:00:00') vs référence=Timestamp('2130-02-04 08:53:00')
    ex: nous=Timestamp('2130-02-04 12:18:00') vs référence=Timestamp('2130-02-04 11:16:00')
    ex: nous=Timestamp('2130-08-14 10:19:00') vs référence=Timestamp('2130-08-14 06:01:00')

## quantity : 8420/9400 lignes concordent (89.6%)  [number]
    ex: nous=np.float64(0.045) vs référence=np.float64(250.0)
    ex: nous=np.float64(49.8000011444) vs référence=np.float64(1.0)
    ex: nous=np.float64(nan) vs référence=np.float64(50.0)

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## drug_source_value : 0/9935 lignes concordent (0.0%)  [text]
    ex: nous='Acetaminophen' vs référence='00677178110'
    ex: nous='Atorvastatin' vs référence='00071015623'
    ex: nous='Metronidazole' vs référence='51079012620'

## drug_source_concept_id : 0/9935 lignes concordent (0.0%)  [concept]
    ex: nous=np.int64(44841251) vs référence=np.float64(nan)
    ex: nous=np.int64(44907135) vs référence=np.float64(nan)
    ex: nous=np.int64(45376246) vs référence=np.float64(nan)

# Écarts de portée (champs exclus du score)

  days_supply : vide des deux côtés

## Résumé
  Couverture de la référence : 17.5%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 8948/9935 (90.1%)
  Accord sémantique par champ (toutes les valeurs comparées) : 93.8%
  Accord de provenance (hors score) : 0.0%

---

# Comparaison ligne à ligne — procedure_occurrence

Clé naturelle : person + ['procedure_concept_id', 'procedure_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 5099 lignes
  Chez la référence : 2815 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 5099 lignes (0 exclues - patient non apparié)
  Chez la référence : 2815 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 3126 doublon(s) chez nous, 996 chez la référence, sur (person + ['procedure_concept_id', 'procedure_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 145
  Clés UNIQUEMENT chez nous : 1828
  Clés UNIQUEMENT chez la référence : 1674
    ex: [(29, 2514409, datetime.date(2192, 11, 20)), (79, 2514406, datetime.date(2121, 12, 7)), (98, 4238681, datetime.date(2123, 12, 3))]
    ex: [(81, 4037672, datetime.date(2147, 10, 16)), (98, 4297090, datetime.date(2123, 11, 24)), (86, 4049832, datetime.date(2111, 1, 8))]
  Parmi elles, 205 combinaison(s) (personne + ['procedure_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 166
  Couverture de la référence : 166/2815 (5.9%) - part des lignes de la référence retrouvées chez nous
  Précision : 166/5099 (3.3%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## procedure_datetime : 131/166 lignes concordent (78.9%)  [datetime]
    ex: nous=NaT vs référence=Timestamp('2149-05-26 17:19:00')
    ex: nous=NaT vs référence=Timestamp('2185-04-14 00:23:00')
    ex: nous=NaT vs référence=Timestamp('2150-08-22 17:33:00')

## quantity : 133/135 lignes concordent (98.5%)  [number]
    ex: nous=np.float64(nan) vs référence=np.float64(3610.0)
    ex: nous=np.float64(nan) vs référence=np.float64(164.0)

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## procedure_source_value : 3/166 lignes concordent (1.8%)  [text]
    ex: nous='8181' vs référence='Musculoskeletal system'
    ex: nous='99274' vs référence='Confirmatory consultation for a new or established patient (deleted codes)'
    ex: nous='49080' vs référence='Digestive system'

## procedure_source_concept_id : 26/166 lignes concordent (15.7%)  [concept]
    ex: nous=np.int64(2005945) vs référence=np.int64(2103758)
    ex: nous=np.int64(2008008) vs référence=np.int64(2001018244)
    ex: nous=np.int64(2008356) vs référence=np.int64(2001017911)

## Résumé
  Couverture de la référence : 5.9%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 131/166 (78.9%)
  Accord sémantique par champ (toutes les valeurs comparées) : 87.7%
  Accord de provenance (hors score) : 8.7%

---

# Comparaison ligne à ligne — measurement

Clé naturelle : person + ['measurement_concept_id', 'measurement_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 116877 lignes
  Chez la référence : 823220 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 116877 lignes (0 exclues - patient non apparié)
  Chez la référence : 823220 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 57052 doublon(s) chez nous, 746654 chez la référence, sur (person + ['measurement_concept_id', 'measurement_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 54986
  Clés UNIQUEMENT chez nous : 4839
  Clés UNIQUEMENT chez la référence : 21580
    ex: [(47, 42527086, datetime.date(2171, 7, 14)), (47, 42527086, datetime.date(2171, 7, 24)), (17, 4151358, datetime.date(2152, 10, 7))]
    ex: [(52, 3038086, datetime.date(2169, 5, 7)), (48, 3016335, datetime.date(2198, 7, 6)), (81, 4337265, datetime.date(2147, 10, 6))]

Lignes appariées (même personne + même clé naturelle) : 101552
  Couverture de la référence : 101552/823220 (12.3%) - part des lignes de la référence retrouvées chez nous
  Précision : 101552/116877 (86.9%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## measurement_datetime : 94184/101552 lignes concordent (92.7%)  [datetime]
    ex: nous=Timestamp('2125-10-05 03:00:00') vs référence=Timestamp('2125-10-05 01:00:00')
    ex: nous=Timestamp('2125-10-05 04:00:00') vs référence=Timestamp('2125-10-05 01:00:00')
    ex: nous=Timestamp('2125-10-05 05:00:00') vs référence=Timestamp('2125-10-05 01:00:00')

## value_as_number : 88949/95610 lignes concordent (93.0%)  [number]
    ex: nous=np.float64(nan) vs référence=np.float64(2.0)
    ex: nous=np.float64(nan) vs référence=np.float64(50.0)
    ex: nous=np.float64(nan) vs référence=np.float64(1.0)

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## measurement_source_value : 98833/101552 lignes concordent (97.3%)  [text]
    ex: nous='618' vs référence='615'
    ex: nous='618' vs référence='219'
    ex: nous='618' vs référence='615'

## measurement_source_concept_id : 0/101552 lignes concordent (0.0%)  [concept]
    ex: nous=np.int64(3000330) vs référence=np.float64(2001031633.0)
    ex: nous=np.int64(3000330) vs référence=np.float64(2001031633.0)
    ex: nous=np.int64(3000330) vs référence=np.float64(2001031633.0)

## unit_source_value : 96177/96424 lignes concordent (99.7%)  [text]
    ex: nous='BPM' vs référence=nan
    ex: nous='BPM' vs référence=nan
    ex: nous='BPM' vs référence=nan

## value_source_value : 95122/101546 lignes concordent (93.7%)  [text]
    ex: nous='18' vs référence='26'
    ex: nous='22' vs référence='40'
    ex: nous='26' vs référence='18'

# Écarts de portée (champs exclus du score)

  value_as_concept_id : vide des deux côtés
  unit_concept_id : jamais renseigné chez nous

## Résumé
  Couverture de la référence : 12.3%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 93614/101552 (92.2%)
  Accord sémantique par champ (toutes les valeurs comparées) : 92.9%
  Accord de provenance (hors score) : 72.3%

---

# Comparaison ligne à ligne — observation

Clé naturelle : person + ['observation_concept_id', 'observation_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 65149 lignes
  Chez la référence : 22529 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 65149 lignes (0 exclues - patient non apparié)
  Chez la référence : 22529 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 53603 doublon(s) chez nous, 20847 chez la référence, sur (person + ['observation_concept_id', 'observation_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 324
  Clés UNIQUEMENT chez nous : 11222
  Clés UNIQUEMENT chez la référence : 1358
    ex: [(60, 4337265, datetime.date(2144, 10, 18)), (47, 4021165, datetime.date(2171, 8, 6)), (95, 4121035, datetime.date(2175, 10, 2))]
    ex: [(65, 4195428, datetime.date(2145, 7, 8)), (76, 36715149, datetime.date(2119, 10, 19)), (65, 4078442, datetime.date(2145, 7, 14))]
  Parmi elles, 19 combinaison(s) (personne + ['observation_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 2712
  Couverture de la référence : 2712/22529 (12.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 2712/65149 (4.2%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## observation_datetime : 488/2712 lignes concordent (18.0%)  [datetime]
    ex: nous=Timestamp('2164-10-23 22:40:00') vs référence=Timestamp('2164-10-23 21:10:00')
    ex: nous=Timestamp('2164-10-23 23:00:00') vs référence=Timestamp('2164-10-23 21:10:00')
    ex: nous=Timestamp('2126-08-14 21:00:00') vs référence=Timestamp('2126-08-14 22:20:00')

## value_as_number : 49/2027 lignes concordent (2.4%)  [number]
    ex: nous=np.float64(1.2) vs référence=np.float64(nan)
    ex: nous=np.float64(100.0) vs référence=np.float64(nan)
    ex: nous=np.float64(2.8) vs référence=np.float64(nan)

## value_as_string : 32/2708 lignes concordent (1.2%)  [text]
    ex: nous='MED' vs référence='A'
    ex: nous='ON' vs référence='Lidocaine'
    ex: nous='Supine' vs référence='RCA'

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## observation_source_value : 56/2712 lignes concordent (2.1%)  [text]
    ex: nous='919' vs référence='925'
    ex: nous='1622' vs référence='916'
    ex: nous='547' vs référence='926'

## observation_source_concept_id : 0/2712 lignes concordent (0.0%)  [concept]
    ex: nous=np.int64(1027551) vs référence=np.float64(2001019606.0)
    ex: nous=np.int64(1010397) vs référence=np.float64(2001019601.0)
    ex: nous=np.int64(37067617) vs référence=np.float64(2001019607.0)

# Écarts de portée (champs exclus du score)

  value_as_concept_id : vide des deux côtés
  unit_concept_id : renseigné seulement chez nous
  unit_source_value : renseigné seulement chez nous

## Résumé
  Couverture de la référence : 12.0%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 16/2712 (0.6%)
  Accord sémantique par champ (toutes les valeurs comparées) : 7.6%
  Accord de provenance (hors score) : 1.0%

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
    ex: [(75, datetime.date(2136, 3, 26)), (84, datetime.date(2147, 9, 8)), (63, datetime.date(2145, 3, 7))]
    ex: [(74, datetime.date(2103, 5, 18)), (64, datetime.date(2155, 3, 11))]
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
    ex: [(18, datetime.date(2129, 11, 24)), (29, datetime.date(2192, 11, 20)), (10, datetime.date(2132, 12, 5))]
    ex: [(10, datetime.date(2132, 12, 4)), (16, datetime.date(2185, 4, 13)), (62, datetime.date(2159, 11, 16))]
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
