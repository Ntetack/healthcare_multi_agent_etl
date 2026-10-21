# Full Comparison Report

## Executive Summary

| Table | Rows (ours) | Rows (reference) | Matched | Coverage of the reference | Semantic agreement | Provenance (not scored) | Note |
|---|---|---|---|---|---|---|---|
| person | 100 | 100 | 100 | 100/100 (100.0%) | 100/100 (100.0%) | 99.5% |  |
| visit_occurrence | 129 | 129 | 119 | 119/129 (92.2%) | 37/119 (31.1%) | 100.0% | 9 events found with another date; 10 ours-only / 10 reference-only keys |
| condition_occurrence | 1736 | 1903 | 133 | 133/1903 (7.0%) | n/a | 59.4% | non-unique key (114/1565 dupes, paired by signature); 8 events found with another date; 1507 ours-only / 223 reference-only keys |
| drug_exposure | 27318 | 56715 | 9458 | 9458/56715 (16.7%) | 8825/9458 (93.3%) | 0.0% | non-unique key (16330/44864 dupes, paired by signature); 58 events found with another date; 2847 ours-only / 3710 reference-only keys |
| procedure_occurrence | 1273 | 2815 | 9 | 9/2815 (0.3%) | n/a | 16.7% | non-unique key (228/996 dupes, paired by signature); 210 events found with another date; 1036 ours-only / 1810 reference-only keys |
| measurement | 112806 | 823220 | 86063 | 86063/823220 (10.5%) | 45534/86063 (52.9%) | 71.9% | non-unique key (54078/746654 dupes, paired by signature); 4455 ours-only / 22293 reference-only keys |
| observation | 95415 | 22529 | 6469 | 6469/22529 (28.7%) | 0/6469 (0.0%) | 12.8% | non-unique key (74853/20847 dupes, paired by signature); 40 events found with another date; 19936 ours-only / 1056 reference-only keys |
| death | 100 | 92 | 90 | 90/92 (97.8%) | 32/90 (35.6%) | n/a | 2 events found with another date; 10 ours-only / 2 reference-only keys |
| observation_period | 129 | 129 | 119 | 119/129 (92.2%) | 119/119 (100.0%) | n/a | 9 events found with another date; 10 ours-only / 10 reference-only keys |

**Coverage of the reference (rows found here / rows of the reference): 102560/907632 (11.3%)**

**Semantic agreement (matched rows whose meaning agrees, weighted by rows): 54647/102418 (53.4%)**

**Reference rows reproduced with the same meaning (found AND agreeing): 54647/902914 (6.1%)**

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
    ex: [(54, 262, datetime.date(2151, 8, 13)), (26, 262, datetime.date(2188, 2, 8)), (62, 262, datetime.date(2159, 11, 17))]
    ex: [(29, 262, datetime.date(2192, 11, 19)), (65, 262, datetime.date(2145, 9, 5)), (10, 262, datetime.date(2132, 12, 4))]
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
  Chez nous : 1736 lignes
  Chez la référence : 1903 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 1736 lignes (0 exclues - patient non apparié)
  Chez la référence : 1903 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 114 doublon(s) chez nous, 1565 chez la référence, sur (person + ['condition_concept_id', 'condition_start_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 115
  Clés UNIQUEMENT chez nous : 1507
  Clés UNIQUEMENT chez la référence : 223
    ex: [(57, 435788, datetime.date(2144, 12, 24)), (57, 4131791, datetime.date(2144, 7, 11)), (89, 46271022, datetime.date(2198, 6, 29))]
    ex: [(67, 0, datetime.date(2201, 9, 28)), (82, 0, datetime.date(2165, 12, 19)), (70, 0, datetime.date(2112, 2, 4))]
  Parmi elles, 8 combinaison(s) (personne + ['condition_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 133
  Couverture de la référence : 133/1903 (7.0%) - part des lignes de la référence retrouvées chez nous
  Précision : 133/1736 (7.7%) - part de nos lignes qui existent aussi chez la référence

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
  Chez nous : 27318 lignes
  Chez la référence : 56715 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 27318 lignes (0 exclues - patient non apparié)
  Chez la référence : 56715 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 16330 doublon(s) chez nous, 44864 chez la référence, sur (person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 8141
  Clés UNIQUEMENT chez nous : 2847
  Clés UNIQUEMENT chez la référence : 3710
    ex: [(16, 40231540, datetime.date(2185, 4, 14), datetime.date(2185, 4, 15)), (89, 997881, datetime.date(2198, 6, 30), datetime.date(2198, 6, 30)), (95, 1771162, datetime.date(2175, 10, 2), datetime.date(2175, 10, 2))]
    ex: [(67, 40141424, datetime.date(2199, 1, 13), datetime.date(2199, 1, 16)), (96, 3037253, datetime.date(2112, 5, 5), datetime.date(2112, 5, 6)), (48, 0, datetime.date(2198, 6, 29), datetime.date(2198, 7, 20))]
  Parmi elles, 58 combinaison(s) (personne + ['drug_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 9458
  Couverture de la référence : 9458/56715 (16.7%) - part des lignes de la référence retrouvées chez nous
  Précision : 9458/27318 (34.6%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## drug_exposure_start_datetime : 9404/9458 lignes concordent (99.4%)  [datetime]
    ex: nous=Timestamp('2144-07-13 16:52:00') vs référence=Timestamp('2144-07-13 19:32:00')
    ex: nous=Timestamp('2144-07-17 00:41:00') vs référence=Timestamp('2144-07-17 02:47:00')
    ex: nous=Timestamp('2144-07-17 02:47:00') vs référence=Timestamp('2144-07-17 07:29:00')

## drug_exposure_end_datetime : 9398/9458 lignes concordent (99.4%)  [datetime]
    ex: nous=Timestamp('2144-07-13 19:32:00') vs référence=Timestamp('2144-07-13 22:12:00')
    ex: nous=Timestamp('2144-07-17 07:31:00') vs référence=Timestamp('2144-07-17 02:48:00')
    ex: nous=Timestamp('2144-07-17 02:48:00') vs référence=Timestamp('2144-07-17 10:56:00')

## quantity : 8290/8923 lignes concordent (92.9%)  [number]
    ex: nous=np.float64(nan) vs référence=np.float64(40000.0)
    ex: nous=np.float64(100.0) vs référence=np.float64(40.0272168675)
    ex: nous=np.float64(250.0) vs référence=np.float64(25.0000014)

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## drug_source_value : 0/9458 lignes concordent (0.0%)  [text]
    ex: nous='Acetaminophen' vs référence='00677178110'
    ex: nous='Atorvastatin' vs référence='00071015623'
    ex: nous='Metronidazole' vs référence='51079012620'

## drug_source_concept_id : 0/9458 lignes concordent (0.0%)  [concept]
    ex: nous=np.int64(44841251) vs référence=np.float64(nan)
    ex: nous=np.int64(44907135) vs référence=np.float64(nan)
    ex: nous=np.int64(45376246) vs référence=np.float64(nan)

# Écarts de portée (champs exclus du score)

  days_supply : vide des deux côtés

## Résumé
  Couverture de la référence : 16.7%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 8825/9458 (93.3%)
  Accord sémantique par champ (toutes les valeurs comparées) : 97.3%
  Accord de provenance (hors score) : 0.0%

---

# Comparaison ligne à ligne — procedure_occurrence

Clé naturelle : person + ['procedure_concept_id', 'procedure_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 1273 lignes
  Chez la référence : 2815 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 1273 lignes (0 exclues - patient non apparié)
  Chez la référence : 2815 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 228 doublon(s) chez nous, 996 chez la référence, sur (person + ['procedure_concept_id', 'procedure_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 9
  Clés UNIQUEMENT chez nous : 1036
  Clés UNIQUEMENT chez la référence : 1810
    ex: [(60, 2008005, datetime.date(2144, 10, 15)), (46, 2314001, datetime.date(2192, 5, 15)), (72, 2008005, datetime.date(2127, 7, 23))]
    ex: [(66, 2000173, datetime.date(2145, 12, 18)), (89, 2001393, datetime.date(2198, 8, 7)), (66, 4080549, datetime.date(2145, 12, 10))]
  Parmi elles, 210 combinaison(s) (personne + ['procedure_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 9
  Couverture de la référence : 9/2815 (0.3%) - part des lignes de la référence retrouvées chez nous
  Précision : 9/1273 (0.7%) - part de nos lignes qui existent aussi chez la référence

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## procedure_source_value : 3/9 lignes concordent (33.3%)  [text]
    ex: nous='8181' vs référence='Musculoskeletal system'
    ex: nous='3491' vs référence='Respiratory system'
    ex: nous='8151' vs référence='Musculoskeletal system'

## procedure_source_concept_id : 0/9 lignes concordent (0.0%)  [concept]
    ex: nous=np.int64(2005945) vs référence=np.int64(2103758)
    ex: nous=np.int64(2008008) vs référence=np.int64(2001018244)
    ex: nous=np.int64(2008356) vs référence=np.int64(2001017911)

# Écarts de portée (champs exclus du score)

  procedure_datetime : jamais renseigné chez nous
  quantity : jamais renseigné chez nous

## Résumé
  Couverture de la référence : 0.3%
  Accord sémantique : aucun champ sémantique comparable.
  Accord de provenance (hors score) : 16.7%

---

# Comparaison ligne à ligne — measurement

Clé naturelle : person + ['measurement_concept_id', 'measurement_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 112806 lignes
  Chez la référence : 823220 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 112806 lignes (0 exclues - patient non apparié)
  Chez la référence : 823220 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 54078 doublon(s) chez nous, 746654 chez la référence, sur (person + ['measurement_concept_id', 'measurement_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 54273
  Clés UNIQUEMENT chez nous : 4455
  Clés UNIQUEMENT chez la référence : 22293
    ex: [(99, 3022217, datetime.date(2180, 7, 19)), (67, 4245261, datetime.date(2199, 2, 2)), (20, 45876226, datetime.date(2129, 5, 2))]
    ex: [(22, 21490712, datetime.date(2107, 1, 16)), (60, 4337265, datetime.date(2144, 10, 17)), (72, 3030354, datetime.date(2127, 9, 11))]

Lignes appariées (même personne + même clé naturelle) : 86063
  Couverture de la référence : 86063/823220 (10.5%) - part des lignes de la référence retrouvées chez nous
  Précision : 86063/112806 (76.3%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## measurement_datetime : 78709/86063 lignes concordent (91.5%)  [datetime]
    ex: nous=Timestamp('2125-10-05 03:00:00') vs référence=Timestamp('2125-10-05 01:00:00')
    ex: nous=Timestamp('2125-10-05 04:00:00') vs référence=Timestamp('2125-10-05 01:00:00')
    ex: nous=Timestamp('2125-10-05 05:00:00') vs référence=Timestamp('2125-10-05 01:00:00')

## value_as_number : 73479/80126 lignes concordent (91.7%)  [number]
    ex: nous=np.float64(nan) vs référence=np.float64(2.0)
    ex: nous=np.float64(nan) vs référence=np.float64(50.0)
    ex: nous=np.float64(nan) vs référence=np.float64(1.0)

## unit_concept_id : 40532/80772 lignes concordent (50.2%)  [concept]
    ex: nous=np.int64(8786) vs référence=np.float64(8889.0)
    ex: nous=np.int64(8786) vs référence=np.float64(8889.0)
    ex: nous=np.int64(8786) vs référence=np.float64(8889.0)

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

## Résumé
  Couverture de la référence : 10.5%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 45534/86063 (52.9%)
  Accord sémantique par champ (toutes les valeurs comparées) : 78.0%
  Accord de provenance (hors score) : 71.9%

---

# Comparaison ligne à ligne — observation

Clé naturelle : person + ['observation_concept_id', 'observation_date']

## Volumes bruts (avant tout filtrage)
  Chez nous : 95415 lignes
  Chez la référence : 22529 lignes
  Correspondances patient disponibles (via le pont patients.csv) : 100

## Volumes après restriction aux patients communs
  Chez nous : 95415 lignes (0 exclues - patient non apparié)
  Chez la référence : 22529 lignes (0 exclues - patient non apparié)

⚠️  CLÉ NON UNIQUE : 74853 doublon(s) chez nous, 20847 chez la référence, sur (person + ['observation_concept_id', 'observation_date']). Les lignes d'une même clé sont appariées par la SIGNATURE de leurs valeurs (les lignes identiques sont rapprochées entre elles), mais une clé qui identifie vraiment une ligne - avec une date ou une heure en plus - donnerait une comparaison plus fiable.

## Existence des lignes (avant de comparer leur contenu)
  Clés présentes des deux côtés : 626
  Clés UNIQUEMENT chez nous : 19936
  Clés UNIQUEMENT chez la référence : 1056
    ex: [(67, 40779364, datetime.date(2201, 5, 12)), (15, 4237719, datetime.date(2147, 2, 14)), (67, 1004172, datetime.date(2200, 3, 28))]
    ex: [(24, 40766231, datetime.date(2189, 9, 8)), (43, 40766231, datetime.date(2138, 6, 5)), (87, 0, datetime.date(2179, 4, 21))]
  Parmi elles, 40 combinaison(s) (personne + ['observation_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Lignes appariées (même personne + même clé naturelle) : 6469
  Couverture de la référence : 6469/22529 (28.7%) - part des lignes de la référence retrouvées chez nous
  Précision : 6469/95415 (6.8%) - part de nos lignes qui existent aussi chez la référence

# Champs sémantiques (ce que la ligne signifie) - ils composent le score

## observation_datetime : 5294/6469 lignes concordent (81.8%)  [datetime]
    ex: nous=Timestamp('2190-07-15 00:00:00') vs référence=NaT
    ex: nous=Timestamp('2150-08-27 16:00:00') vs référence=NaT
    ex: nous=Timestamp('2189-09-10 03:00:00') vs référence=NaT

## value_as_string : 0/6469 lignes concordent (0.0%)  [text]
    ex: nous='2163-05-14 00:00:00' vs référence='INV#1 Cap Change [MM]'
    ex: nous='2163-05-14 00:00:00' vs référence='INV#1 Cap Change [MM]'
    ex: nous='2163-05-14 00:00:00' vs référence='INV#1 Cap Change [MM]'

# Champs de provenance (la façon dont la source l'écrit) - rapportés, hors score

## observation_source_value : 0/6469 lignes concordent (0.0%)  [text]
    ex: nous='5684' vs référence=nan
    ex: nous='5685' vs référence=nan
    ex: nous='6703' vs référence=nan

## observation_source_concept_id : 1662/6469 lignes concordent (25.7%)  [concept]
    ex: nous=np.int64(2001020783) vs référence=np.float64(2001023513.0)
    ex: nous=np.int64(2001020784) vs référence=np.float64(2001023513.0)
    ex: nous=np.int64(2001023514) vs référence=np.float64(2001023513.0)

# Écarts de portée (champs exclus du score)

  value_as_number : jamais renseigné chez nous
  value_as_concept_id : vide des deux côtés
  unit_concept_id : vide des deux côtés
  unit_source_value : renseigné seulement chez nous

## Résumé
  Couverture de la référence : 28.7%
  Accord sémantique (lignes appariées dont TOUS les champs sémantiques concordent) : 0/6469 (0.0%)
  Accord sémantique par champ (toutes les valeurs comparées) : 40.9%
  Accord de provenance (hors score) : 12.8%

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
    ex: [(74, datetime.date(2105, 5, 18)), (63, datetime.date(2145, 3, 7)), (84, datetime.date(2147, 9, 8))]
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
    ex: [(64, datetime.date(2155, 3, 8)), (54, datetime.date(2151, 8, 13)), (18, datetime.date(2129, 11, 24))]
    ex: [(29, datetime.date(2192, 11, 19)), (62, datetime.date(2159, 11, 16)), (65, datetime.date(2145, 9, 5))]
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
