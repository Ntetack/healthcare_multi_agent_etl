# Full Comparison Report

## Executive Summary

| Table | Rows (ours) | Rows (reference) | Matched | Coverage of the reference | Semantic agreement | Provenance (not scored) | Note |
|---|---|---|---|---|---|---|---|
| person | 100 | 100 | 100 | 100/100 (100.0%) | 100/100 (100.0%) | 99.5% |  |
| visit_occurrence | 129 | 129 | 119 | 119/129 (92.2%) | 37/119 (31.1%) | 100.0% | 9 events found with another date; 10 ours-only / 10 reference-only keys |
| condition_occurrence | - | - | - | - | - | - | missing key columns ['condition_start'] |
| drug_exposure | 28513 | 56715 | 9713 | 9713/56715 (17.1%) | 8957/9713 (92.2%) | 0.0% | non-unique key (5435/29255 dupes, paired by signature); 89 events found with another date; 14398 ours-only / 18780 reference-only keys |
| procedure_occurrence | 5099 | 2815 | 133 | 133/2815 (4.7%) | 133/133 (100.0%) | 0.0% | non-unique key (1651/911 dupes, paired by signature); 232 events found with another date; 3315 ours-only / 1771 reference-only keys |
| measurement | 116877 | 823220 | 101552 | 101552/823220 (12.3%) | 93614/101552 (92.2%) | 72.3% | non-unique key (57052/746654 dupes, paired by signature); 4839 ours-only / 21580 reference-only keys |
| observation | 65149 | 22529 | 594 | 594/22529 (2.6%) | 3/594 (0.5%) | 1.6% | non-unique key (8020/19870 dupes, paired by signature); 50 events found with another date; 56795 ours-only / 2325 reference-only keys |
| death | 100 | 92 | 90 | 90/92 (97.8%) | 32/90 (35.6%) | n/a | 2 events found with another date; 10 ours-only / 2 reference-only keys |
| observation_period | 129 | 129 | 119 | 119/129 (92.2%) | 119/119 (100.0%) | n/a | 9 events found with another date; 10 ours-only / 10 reference-only keys |

**Coverage of the reference (rows found here / rows of the reference): 112420/905729 (12.4%)**

**Semantic agreement (matched rows whose meaning agrees, weighted by rows): 102995/112420 (91.6%)**

**Reference rows reproduced with the same meaning (found AND agreeing): 102995/905729 (11.4%)**

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
    ex: [(10, 262, datetime.date(2132, 12, 5)), (62, 262, datetime.date(2159, 11, 17)), (65, 262, datetime.date(2145, 9, 6))]
    ex: [(18, 262, datetime.date(2129, 11, 23)), (62, 262, datetime.date(2159, 11, 16)), (65, 262, datetime.date(2145, 7, 6))]
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

Comparaison impossible : colonne(s) de clé absente(s) d'un des schémas : ['condition_start']

---

# Comparaison ligne à ligne — drug_exposure

Clé naturelle : person + ['drug_concept_id', 'drug_exposure_start_datetime', 'drug_exposure_end_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 28513 lignes
  Chez la référence : 56715 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 28513 lignes (0 exclues - patient non apparié)
  Chez la référence : 56715 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 5435 doublon(s) chez nous, 29255 chez la référence, sur (person + ['drug_concept_id', 'drug_exposure_start_datetime', 'drug_exposure_end_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 8680
  Clés UNIQUEMENT chez nous : 14398
  Clés UNIQUEMENT chez la référence : 18780
    ex: [(98, 1321341, Timestamp('2123-12-04 18:30:00'), datetime.date(2123, 12, 4)), (15, 1560524, Timestamp('2147-02-14 04:54:00'), datetime.date(2147, 2, 14)), (22, 1309944, Timestamp('2107-01-27 16:00:00'), datetime.date(2107, 1, 27))]
    ex: [(67, 3037253, Timestamp('2201-11-18 21:28:00'), datetime.date(2201, 11, 18)), (81, 0, Timestamp('2147-10-03 20:20:00'), datetime.date(2147, 10, 3)), (26, 0, Timestamp('2188-02-24 13:00:00'), None)]
  Parmi elles, 89 combinaison(s) (personne + ['drug_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 9713
  Couverture de la référence : 9713/56715 (17.1%) - part des lignes de la référence retrouvées chez nous
  Précision : 9713/28513 (34.1%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## drug_exposure_end_datetime : 9699/9713 lignes concordent (99.9%)  [datetime]
    ex: nous=Timestamp('2144-07-13 14:20:00') vs référence=Timestamp('2144-07-13 23:56:00')
    ex: nous=Timestamp('2144-07-16 14:07:00') vs référence=Timestamp('2144-07-16 16:00:00')
    ex: nous=Timestamp('2144-07-19 01:00:00') vs référence=Timestamp('2144-07-19 00:21:00')

## quantity : 8422/9178 lignes concordent (91.8%)  [number]
    ex: nous=np.float64(0.045) vs référence=np.float64(250.0)
    ex: nous=np.float64(49.9999980927) vs référence=np.float64(2.0)
    ex: nous=np.float64(3.0) vs référence=np.float64(1.0)

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## drug_source_value : 0/9713 lignes concordent (0.0%)  [text]
    ex: nous='Acetaminophen' vs référence='00677178110'
    ex: nous='Atorvastatin' vs référence='00071015623'
    ex: nous='Metronidazole' vs référence='51079012620'

## drug_source_concept_id : 0/9713 lignes concordent (0.0%)  [concept]
    ex: nous=np.int64(44841251) vs référence=np.float64(nan)
    ex: nous=np.int64(44907135) vs référence=np.float64(nan)
    ex: nous=np.int64(45376246) vs référence=np.float64(nan)

# Écarts de portée (champs exclus du score)

  days_supply : vide des deux côtés

## Résumé
  Couverture de la référence : 17.1%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 8957/9713 (92.2%)
  Accord sémantique par champ (toutes les valeurs comparées) : 95.9%
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
    ex: [(46, 2514441, NaT), (100, 4083171, Timestamp('2170-12-16 20:33:00')), (67, 4083171, Timestamp('2200-11-02 11:30:00'))]
    ex: [(81, 2000154, Timestamp('2147-11-04 19:30:00')), (26, 2008250, Timestamp('2188-02-27 18:41:00')), (76, 4049832, Timestamp('2119-10-30 16:03:00'))]
  Parmi elles, 232 combinaison(s) (personne + ['procedure_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 133
  Couverture de la référence : 133/2815 (4.7%) - part des lignes de la référence retrouvées chez nous
  Précision : 133/5099 (2.6%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

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
    ex: [(67, 21492838, datetime.date(2201, 9, 28)), (13, 3022217, datetime.date(2144, 2, 17)), (66, 4143063, datetime.date(2145, 12, 7))]
    ex: [(46, 3011087, datetime.date(2192, 5, 11)), (46, 3016335, datetime.date(2192, 5, 9)), (97, 3014315, datetime.date(2178, 5, 15))]

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

Clé naturelle : person + ['observation_concept_id', 'observation_datetime']

## Volumes bruts (avant tout filtrage)
  Chez nous : 65149 lignes
  Chez la référence : 22529 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 65149 lignes (0 exclues - patient non apparié)
  Chez la référence : 22529 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 8020 doublon(s) chez nous, 19870 chez la référence, sur (person + ['observation_concept_id', 'observation_datetime']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 334
  Clés UNIQUEMENT chez nous : 56795
  Clés UNIQUEMENT chez la référence : 2325
    ex: [(60, 4021165, Timestamp('2144-10-20 16:15:00')), (40, 4150612, Timestamp('2180-01-29 04:00:00')), (22, 3007397, Timestamp('2107-01-23 20:50:00'))]
    ex: [(22, 44803968, Timestamp('2107-01-16 11:33:00')), (44, 4296248, Timestamp('2117-08-21 05:00:00')), (56, 0, Timestamp('2163-11-21 18:34:00'))]
  Parmi elles, 50 combinaison(s) (personne + ['observation_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 594
  Couverture de la référence : 594/22529 (2.6%) - part des lignes de la référence retrouvées chez nous
  Précision : 594/65149 (0.9%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## value_as_number : 1/467 lignes concordent (0.2%)  [number]
    ex: nous=np.float64(nan) vs référence=np.float64(0.0)
    ex: nous=np.float64(nan) vs référence=np.float64(0.0)
    ex: nous=np.float64(nan) vs référence=np.float64(0.0)

## value_as_string : 3/594 lignes concordent (0.5%)  [text]
    ex: nous='MED' vs référence='A'
    ex: nous='MED' vs référence='No Known Drug Allergies'
    ex: nous='MED' vs référence='No Known Drug Allergies'

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## observation_source_value : 19/594 lignes concordent (3.2%)  [text]
    ex: nous='919' vs référence='925'
    ex: nous='919' vs référence='916'
    ex: nous='919' vs référence='916'

## observation_source_concept_id : 0/594 lignes concordent (0.0%)  [concept]
    ex: nous=np.int64(1027551) vs référence=np.float64(2001019606.0)
    ex: nous=np.int64(1027551) vs référence=np.float64(2001019601.0)
    ex: nous=np.int64(1027551) vs référence=np.float64(2001019601.0)

# Écarts de portée (champs exclus du score)

  value_as_concept_id : vide des deux côtés
  unit_concept_id : vide des deux côtés
  unit_source_value : renseigné seulement chez nous

## Résumé
  Couverture de la référence : 2.6%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 3/594 (0.5%)
  Accord sémantique par champ (toutes les valeurs comparées) : 0.4%
  Accord de provenance (hors score) : 1.6%

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
    ex: [(92, datetime.date(2107, 7, 13)), (100, datetime.date(2171, 4, 14)), (73, datetime.date(2117, 4, 4))]
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
    ex: [(26, datetime.date(2188, 2, 8)), (29, datetime.date(2192, 11, 20)), (65, datetime.date(2145, 7, 7))]
    ex: [(65, datetime.date(2145, 9, 5)), (29, datetime.date(2192, 11, 19)), (16, datetime.date(2185, 4, 13))]
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
