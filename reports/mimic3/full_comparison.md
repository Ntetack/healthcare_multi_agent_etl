# Full Comparison Report

## Executive Summary

| Table | Rows (B1) | Rows (B0) | Matched | Coverage of B0 | Content agreement | Provenance fields | Note |
|---|---|---|---|---|---|---|---|
| person | 100 | 100 | 100 | 100/100 (100.0%) | 100/100 (100.0%) | 99.5% |  |
| visit_occurrence | 129 | 129 | 119 | 119/129 (92.2%) | 37/119 (31.1%) | 100.0% | 9 events found with another date; 10 B1-only / 10 B0-only keys |
| condition_occurrence | 1743 | 1903 | 1423 | 1423/1903 (74.8%) | n/a | 99.9% | non-unique key (115/119 dupes, paired by signature); 121 events found with another date; 228 B1-only / 384 B0-only keys |
| drug_exposure | 28033 | 56715 | 9480 | 9480/56715 (16.7%) | 0/9480 (0.0%) | 50.4% | non-unique key (15175/44819 dupes, paired by signature); 70 events found with another date; 4705 B1-only / 3743 B0-only keys |
| procedure_occurrence | 5099 | 2815 | 166 | 166/2815 (5.9%) | 131/166 (78.9%) | 8.7% | non-unique key (3126/996 dupes, paired by signature); 205 events found with another date; 1828 B1-only / 1674 B0-only keys |
| measurement | 129018 | 823220 | 112872 | 112872/823220 (13.7%) | 44743/112872 (39.6%) | 67.6% | non-unique key (67419/746654 dupes, paired by signature); 5418 B1-only / 20385 B0-only keys |
| observation | 65641 | 22529 | 2712 | 2712/22529 (12.0%) | 16/2712 (0.6%) | 1.0% | non-unique key (53950/20847 dupes, paired by signature); 19 events found with another date; 11367 B1-only / 1358 B0-only keys |
| death | 129 | 92 | 90 | 90/92 (97.8%) | 39/90 (43.3%) | n/a | non-unique key (29/0 dupes, paired by signature); 2 events found with another date; 10 B1-only / 2 B0-only keys |
| observation_period | 129 | 129 | 119 | 119/129 (92.2%) | 119/119 (100.0%) | n/a | 9 events found with another date; 10 B1-only / 10 B0-only keys |

**Coverage of B0 (B0 rows found in B1 / B0 rows): 127081/907632 (14.0%)**

**Content agreement (matched rows whose content fields all agree, weighted by rows): 45185/125658 (36.0%)**

**B0 rows reproduced with the same content (found AND agreeing): 45185/905729 (5.0%)**

Content agreement above covers the content fields only. Provenance fields (`*_source_value`, `*_source_concept_id`) keep the way the source wrote a value, which two faithful exports may do differently; they are in the per-field table below, with the content fields.

## Field agreement by table (unweighted mean over the compared fields)

| Table | Fields compared | Mean field agreement | Fields below 100% |
|---|---|---|---|
| person | 8 | 99.9% | race_source_value |
| visit_occurrence | 6 | 88.5% | visit_start_datetime |
| condition_occurrence | 2 | 99.9% | condition_source_value, condition_source_concept_id |
| drug_exposure | 8 | 61.8% | drug_exposure_start_datetime, drug_exposure_end_datetime, quantity, route_concept_id, drug_source_value, drug_source_concept_id, dose_unit_source_value, route_source_value |
| procedure_occurrence | 4 | 48.7% | procedure_datetime, quantity, procedure_source_value, procedure_source_concept_id |
| measurement | 7 | 70.9% | measurement_datetime, value_as_number, unit_concept_id, measurement_source_value, measurement_source_concept_id, unit_source_value, value_source_value |
| observation | 5 | 4.7% | observation_datetime, value_as_number, value_as_string, observation_source_value, observation_source_concept_id |
| death | 1 | 43.3% | death_datetime |
| observation_period | 1 | 100.0% | - |

The per-field detail with the cause of each disagreement is in the `*_fields.csv` file next to this report. Content and provenance fields both enter the mean; the file flags each field `content` or `provenance`.

## Per-Table Detail

# Row-level comparison — person

Natural key: person + []

## Raw volumes (before any filtering)
  B1: 100 rows
  B0: 100 rows
  Patient matches available (through the patient bridge) : 100

## Volumes after restriction to the common patients
  B1: 100 rows (0 excluded - patient not matched)
  B0: 100 rows (0 excluded - patient not matched)

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 100
  Keys ONLY in B1 : 0
  Keys ONLY in B0 : 0

Matched rows (same person + same natural key) : 100
  Coverage of B0: 100/100 (100.0%) - share of the B0 rows found in B1
  Row precision: 100/100 (100.0%) - share of the B1 rows that also exist in B0

# Content fields (what the row means)

## gender_concept_id : 100/100 lignes concordent (100.0%)  [concept]

## year_of_birth : 100/100 lignes concordent (100.0%)  [exact]

## month_of_birth : 100/100 lignes concordent (100.0%)  [exact]

## day_of_birth : 100/100 lignes concordent (100.0%)  [exact]

## birth_datetime : 100/100 lignes concordent (100.0%)  [datetime]

## race_concept_id : 100/100 lignes concordent (100.0%)  [concept]

# Provenance fields (how the source writes it)

## gender_source_value : 100/100 lignes concordent (100.0%)  [text]

## race_source_value : 99/100 lignes concordent (99.0%)  [text]
    ex: B1='AMERICAN INDIAN/ALASKA NATIVE FEDERALLY RECOGNIZED' vs B0='AMERICAN INDIAN/ALASKA NATIVE FEDERALLY RECOGNIZED TRIBE'

# Scope gaps (fields left out of the score)

  ethnicity_concept_id : populated only in B1
  ethnicity_source_value : populated only in B1
  gender_source_concept_id : populated only in B1
  race_source_concept_id : populated only in B1
  ethnicity_source_concept_id : populated only in B1

## Summary
  Coverage of B0: 100.0%
  Row-level agreement (matched rows whose content fields ALL agree) : 100/100 (100.0%)
  Content agreement by value (all compared values) : 100.0%
  Mean field agreement (unweighted mean of the 8 compared fields) : 99.9%
  Provenance fields, agreement by value : 99.5%

---

# Row-level comparison — visit_occurrence

Natural key: person + ['visit_concept_id', 'visit_start_date']

## Raw volumes (before any filtering)
  B1: 129 rows
  B0: 129 rows
  Patient matches available (through the patient bridge) : 100

## Volumes after restriction to the common patients
  B1: 129 rows (0 excluded - patient not matched)
  B0: 129 rows (0 excluded - patient not matched)

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 119
  Keys ONLY in B1 : 10
  Keys ONLY in B0 : 10
    ex: [(16, 262, datetime.date(2185, 4, 14)), (65, 262, datetime.date(2145, 9, 6)), (62, 262, datetime.date(2159, 11, 17))]
    ex: [(54, 262, datetime.date(2151, 8, 12)), (29, 262, datetime.date(2192, 11, 19)), (10, 262, datetime.date(2132, 12, 4))]
  Parmi elles, 9 combinaison(s) (personne + ['visit_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Matched rows (same person + same natural key) : 119
  Coverage of B0: 119/129 (92.2%) - share of the B0 rows found in B1
  Row precision: 119/129 (92.2%) - share of the B1 rows that also exist in B0

# Content fields (what the row means)

## visit_start_datetime : 37/119 lignes concordent (31.1%)  [datetime]
    ex: B1=Timestamp('2164-10-23 21:09:00') vs B0=Timestamp('2164-10-23 16:43:00')
    ex: B1=Timestamp('2149-05-26 17:19:00') vs B0=Timestamp('2149-05-26 12:08:00')
    ex: B1=Timestamp('2195-05-17 07:39:00') vs B0=Timestamp('2195-05-17 01:49:00')

## visit_end_date : 119/119 lignes concordent (100.0%)  [date]

## visit_end_datetime : 119/119 lignes concordent (100.0%)  [datetime]

# Provenance fields (how the source writes it)

## visit_source_value : 119/119 lignes concordent (100.0%)  [text]

## admitted_from_source_value : 119/119 lignes concordent (100.0%)  [text]

## discharged_to_source_value : 119/119 lignes concordent (100.0%)  [text]

# Scope gaps (fields left out of the score)

  admitted_from_concept_id : never populated in B1
  discharged_to_concept_id : never populated in B1
  visit_source_concept_id : never populated in B1
  Columns missing from one of the two schemas (not compared) : ['admitting_concept_id', 'discharge_to_source_concept_id']

## Summary
  Coverage of B0: 92.2%
  Row-level agreement (matched rows whose content fields ALL agree) : 37/119 (31.1%)
  Content agreement by value (all compared values) : 77.0%
  Mean field agreement (unweighted mean of the 6 compared fields) : 88.5%
  Provenance fields, agreement by value : 100.0%

---

# Row-level comparison — condition_occurrence

Natural key: person + ['condition_concept_id', 'condition_start_date']

## Raw volumes (before any filtering)
  B1: 1743 rows
  B0: 1903 rows
  Patient matches available (through the patient bridge) : 100

## Volumes after restriction to the common patients
  B1: 1743 rows (0 excluded - patient not matched)
  B0: 1903 rows (0 excluded - patient not matched)

⚠️  NON-UNIQUE KEY: 115 duplicate(s) in B1, 119 in B0, on (person + ['condition_concept_id', 'condition_start_date']). Rows sharing a key are paired by the SIGNATURE of their values (identical rows are paired together), but a key that really identifies a row - with a date or a time added - would make the comparison more reliable.

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 1400
  Keys ONLY in B1 : 228
  Keys ONLY in B0 : 384
    ex: [(13, 434814, datetime.date(2144, 2, 9)), (54, 320128, datetime.date(2151, 8, 13)), (29, 432595, datetime.date(2192, 11, 20))]
    ex: [(18, 196236, datetime.date(2129, 11, 23)), (85, 1340204, datetime.date(2128, 11, 4)), (65, 46270376, datetime.date(2145, 9, 5))]
  Parmi elles, 121 combinaison(s) (personne + ['condition_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Matched rows (same person + same natural key) : 1423
  Coverage of B0: 1423/1903 (74.8%) - share of the B0 rows found in B1
  Row precision: 1423/1743 (81.6%) - share of the B1 rows that also exist in B0

# Provenance fields (how the source writes it)

## condition_source_value : 1421/1423 lignes concordent (99.9%)  [text]
    ex: B1='E9504' vs B0='E9503'
    ex: B1='78720' vs B0='43882'

## condition_source_concept_id : 1421/1423 lignes concordent (99.9%)  [concept]
    ex: B1=np.int64(44822618) vs B0=np.float64(44830707.0)
    ex: B1=np.int64(44828158) vs B0=np.float64(44819717.0)

# Scope gaps (fields left out of the score)

  condition_start_datetime : never populated in B1
  condition_end_date : never populated in B1
  condition_end_datetime : never populated in B1
  condition_status_concept_id : empty on both sides
  stop_reason : empty on both sides
  condition_status_source_value : empty on both sides

## Summary
  Coverage of B0: 74.8%
  Content agreement: no comparable content field.
  Provenance fields, agreement by value : 99.9%

---

# Row-level comparison — drug_exposure

Natural key: person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']

## Raw volumes (before any filtering)
  B1: 28033 rows
  B0: 56715 rows
  Patient matches available (through the patient bridge) : 100

## Volumes after restriction to the common patients
  B1: 28033 rows (0 excluded - patient not matched)
  B0: 56715 rows (0 excluded - patient not matched)

⚠️  NON-UNIQUE KEY: 15175 duplicate(s) in B1, 44819 in B0, on (person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']). Rows sharing a key are paired by the SIGNATURE of their values (identical rows are paired together), but a key that really identifies a row - with a date or a time added - would make the comparison more reliable.

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 8153
  Keys ONLY in B1 : 4705
  Keys ONLY in B0 : 3743
    ex: [(67, 19093848, datetime.date(2199, 2, 4), datetime.date(2199, 2, 4)), (57, 1707687, datetime.date(2144, 7, 22), datetime.date(2144, 7, 22)), (26, 753626, datetime.date(2188, 2, 14), datetime.date(2188, 2, 14))]
    ex: [(21, 0, None, datetime.date(2150, 8, 22)), (67, 3006552, datetime.date(2201, 11, 18), datetime.date(2201, 11, 19)), (41, 0, None, datetime.date(2148, 1, 15))]
  Parmi elles, 70 combinaison(s) (personne + ['drug_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Matched rows (same person + same natural key) : 9480
  Coverage of B0: 9480/56715 (16.7%) - share of the B0 rows found in B1
  Row precision: 9480/28033 (33.8%) - share of the B1 rows that also exist in B0

# Content fields (what the row means)

## drug_exposure_start_datetime : 9424/9480 lignes concordent (99.4%)  [datetime]
    ex: B1=Timestamp('2130-02-04 12:18:00') vs B0=Timestamp('2130-02-04 08:52:00')
    ex: B1=Timestamp('2144-07-13 16:52:00') vs B0=Timestamp('2144-07-13 19:32:00')
    ex: B1=Timestamp('2144-07-17 00:41:00') vs B0=Timestamp('2144-07-17 02:47:00')

## drug_exposure_end_datetime : 9416/9480 lignes concordent (99.3%)  [datetime]
    ex: B1=Timestamp('2130-02-04 12:18:00') vs B0=Timestamp('2130-02-04 08:53:00')
    ex: B1=Timestamp('2144-07-28 05:14:00') vs B0=Timestamp('2144-07-28 04:00:00')
    ex: B1=Timestamp('2144-07-13 19:32:00') vs B0=Timestamp('2144-07-13 22:12:00')

## quantity : 8418/8945 lignes concordent (94.1%)  [number]
    ex: B1=np.float64(0.045) vs B0=np.float64(250.0)
    ex: B1=np.float64(49.8000011444) vs B0=np.float64(1.0)
    ex: B1=np.float64(nan) vs B0=np.float64(50.0)

## route_concept_id : 0/9480 lignes concordent (0.0%)  [concept]
    ex: B1=np.int64(0) vs B0=np.int64(4128794)
    ex: B1=np.int64(0) vs B0=np.int64(4128794)
    ex: B1=np.int64(0) vs B0=np.int64(4128794)

# Provenance fields (how the source writes it)

## drug_source_value : 8796/9480 lignes concordent (92.8%)  [text]
    ex: B1='30172' vs B0='0'
    ex: B1='30133' vs B0='0'
    ex: B1='30133' vs B0='0'

## drug_source_concept_id : 0/9480 lignes concordent (0.0%)  [concept]
    ex: B1=np.int64(44841251) vs B0=np.float64(nan)
    ex: B1=np.int64(44907135) vs B0=np.float64(nan)
    ex: B1=np.int64(45376246) vs B0=np.float64(nan)

## dose_unit_source_value : 1537/9480 lignes concordent (16.2%)  [text]
    ex: B1='mg' vs B0='TAB'
    ex: B1='mg' vs B0='TAB'
    ex: B1='mg' vs B0='TAB'

## route_source_value : 8772/9480 lignes concordent (92.5%)  [text]
    ex: B1='Intravenous Push' vs B0='IV DRIP'
    ex: B1='IV DRIP' vs B0='IV'
    ex: B1='IV' vs B0='IV DRIP'

# Scope gaps (fields left out of the score)

  days_supply : empty on both sides
  lot_number : empty on both sides
  refills : empty on both sides
  sig : empty on both sides
  stop_reason : never populated in B1
  verbatim_end_date : populated only in B1
  Columns missing from one of the two schemas (not compared) : ['quantity_source_value']

## Summary
  Coverage of B0: 16.7%
  Row-level agreement (matched rows whose content fields ALL agree) : 0/9480 (0.0%)
  Content agreement by value (all compared values) : 72.9%
  Mean field agreement (unweighted mean of the 8 compared fields) : 61.8%
  Provenance fields, agreement by value : 50.4%

---

# Row-level comparison — procedure_occurrence

Natural key: person + ['procedure_concept_id', 'procedure_date']

## Raw volumes (before any filtering)
  B1: 5099 rows
  B0: 2815 rows
  Patient matches available (through the patient bridge) : 100

## Volumes after restriction to the common patients
  B1: 5099 rows (0 excluded - patient not matched)
  B0: 2815 rows (0 excluded - patient not matched)

⚠️  NON-UNIQUE KEY: 3126 duplicate(s) in B1, 996 in B0, on (person + ['procedure_concept_id', 'procedure_date']). Rows sharing a key are paired by the SIGNATURE of their values (identical rows are paired together), but a key that really identifies a row - with a date or a time added - would make the comparison more reliable.

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 145
  Keys ONLY in B1 : 1828
  Keys ONLY in B0 : 1674
    ex: [(66, 4238681, datetime.date(2145, 12, 9)), (77, 4083171, datetime.date(2162, 1, 17)), (46, 2314001, datetime.date(2192, 5, 14))]
    ex: [(74, 4207611, datetime.date(2102, 8, 29)), (45, 2008241, datetime.date(2115, 5, 15)), (67, 4049832, datetime.date(2199, 2, 10))]
  Parmi elles, 205 combinaison(s) (personne + ['procedure_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Matched rows (same person + same natural key) : 166
  Coverage of B0: 166/2815 (5.9%) - share of the B0 rows found in B1
  Row precision: 166/5099 (3.3%) - share of the B1 rows that also exist in B0

# Content fields (what the row means)

## procedure_datetime : 131/166 lignes concordent (78.9%)  [datetime]
    ex: B1=NaT vs B0=Timestamp('2149-05-26 17:19:00')
    ex: B1=NaT vs B0=Timestamp('2185-04-14 00:23:00')
    ex: B1=NaT vs B0=Timestamp('2150-08-22 17:33:00')

## quantity : 133/135 lignes concordent (98.5%)  [number]
    ex: B1=np.float64(nan) vs B0=np.float64(3610.0)
    ex: B1=np.float64(nan) vs B0=np.float64(164.0)

# Provenance fields (how the source writes it)

## procedure_source_value : 3/166 lignes concordent (1.8%)  [text]
    ex: B1='8181' vs B0='Musculoskeletal system'
    ex: B1='99274' vs B0='Confirmatory consultation for a new or established patient (deleted codes)'
    ex: B1='49080' vs B0='Digestive system'

## procedure_source_concept_id : 26/166 lignes concordent (15.7%)  [concept]
    ex: B1=np.int64(2005945) vs B0=np.int64(2103758)
    ex: B1=np.int64(2008008) vs B0=np.int64(2001018244)
    ex: B1=np.int64(2008356) vs B0=np.int64(2001017911)

# Scope gaps (fields left out of the score)

  modifier_concept_id : empty on both sides
  procedure_end_date : populated only in B1
  procedure_end_datetime : populated only in B1
  modifier_source_value : empty on both sides

## Summary
  Coverage of B0: 5.9%
  Row-level agreement (matched rows whose content fields ALL agree) : 131/166 (78.9%)
  Content agreement by value (all compared values) : 87.7%
  Mean field agreement (unweighted mean of the 4 compared fields) : 48.7%
  Provenance fields, agreement by value : 8.7%

---

# Row-level comparison — measurement

Natural key: person + ['measurement_concept_id', 'measurement_date']

## Raw volumes (before any filtering)
  B1: 129018 rows
  B0: 823220 rows
  Patient matches available (through the patient bridge) : 100

## Volumes after restriction to the common patients
  B1: 129018 rows (0 excluded - patient not matched)
  B0: 823220 rows (0 excluded - patient not matched)

⚠️  NON-UNIQUE KEY: 67419 duplicate(s) in B1, 746654 in B0, on (person + ['measurement_concept_id', 'measurement_date']). Rows sharing a key are paired by the SIGNATURE of their values (identical rows are paired together), but a key that really identifies a row - with a date or a time added - would make the comparison more reliable.

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 56181
  Keys ONLY in B1 : 5418
  Keys ONLY in B0 : 20385
    ex: [(76, 4143063, datetime.date(2119, 11, 3)), (98, 4265708, datetime.date(2123, 11, 26)), (57, 46236952, datetime.date(2144, 8, 17))]
    ex: [(57, 3034795, datetime.date(2144, 10, 23)), (28, 3016502, datetime.date(2107, 3, 25)), (81, 3027598, datetime.date(2147, 10, 15))]

Matched rows (same person + same natural key) : 112872
  Coverage of B0: 112872/823220 (13.7%) - share of the B0 rows found in B1
  Row precision: 112872/129018 (87.5%) - share of the B1 rows that also exist in B0

# Content fields (what the row means)

## measurement_datetime : 105504/112872 lignes concordent (93.5%)  [datetime]
    ex: B1=Timestamp('2125-10-05 03:00:00') vs B0=Timestamp('2125-10-05 01:00:00')
    ex: B1=Timestamp('2125-10-05 04:00:00') vs B0=Timestamp('2125-10-05 01:00:00')
    ex: B1=Timestamp('2125-10-05 05:00:00') vs B0=Timestamp('2125-10-05 01:00:00')

## value_as_number : 99902/106770 lignes concordent (93.6%)  [number]
    ex: B1=np.float64(nan) vs B0=np.float64(2.0)
    ex: B1=np.float64(nan) vs B0=np.float64(50.0)
    ex: B1=np.float64(nan) vs B0=np.float64(1.0)

## unit_concept_id : 39892/107534 lignes concordent (37.1%)  [concept]
    ex: B1=np.int64(0) vs B0=np.float64(8889.0)
    ex: B1=np.int64(0) vs B0=np.float64(8889.0)
    ex: B1=np.int64(0) vs B0=np.float64(8889.0)

# Provenance fields (how the source writes it)

## measurement_source_value : 98833/112872 lignes concordent (87.6%)  [text]
    ex: B1='40054' vs B0='Stool Out Stool'
    ex: B1='40055' vs B0='Urine Out Foley'
    ex: B1='40069' vs B0='Urine Out Void'

## measurement_source_concept_id : 0/112872 lignes concordent (0.0%)  [concept]
    ex: B1=np.int64(3000330) vs B0=np.float64(2001031633.0)
    ex: B1=np.int64(3000330) vs B0=np.float64(2001031633.0)
    ex: B1=np.int64(3000330) vs B0=np.float64(2001031633.0)

## unit_source_value : 107450/107697 lignes concordent (99.8%)  [text]
    ex: B1='BPM' vs B0=nan
    ex: B1='BPM' vs B0=nan
    ex: B1='BPM' vs B0=nan

## value_source_value : 95122/112706 lignes concordent (84.4%)  [text]
    ex: B1='100' vs B0=nan
    ex: B1='10' vs B0=nan
    ex: B1='400' vs B0=nan

# Scope gaps (fields left out of the score)

  value_as_concept_id : empty on both sides
  meas_event_field_concept_id : empty on both sides
  measurement_time : populated only in B1
  operator_concept_id : never populated in B1
  range_high : never populated in B1
  range_low : never populated in B1
  unit_source_concept_id : populated only in B1

## Summary
  Coverage of B0: 13.7%
  Row-level agreement (matched rows whose content fields ALL agree) : 44743/112872 (39.6%)
  Content agreement by value (all compared values) : 75.0%
  Mean field agreement (unweighted mean of the 7 compared fields) : 70.9%
  Provenance fields, agreement by value : 67.6%

---

# Row-level comparison — observation

Natural key: person + ['observation_concept_id', 'observation_date']

## Raw volumes (before any filtering)
  B1: 65641 rows
  B0: 22529 rows
  Patient matches available (through the patient bridge) : 100

## Volumes after restriction to the common patients
  B1: 65641 rows (0 excluded - patient not matched)
  B0: 22529 rows (0 excluded - patient not matched)

⚠️  NON-UNIQUE KEY: 53950 duplicate(s) in B1, 20847 in B0, on (person + ['observation_concept_id', 'observation_date']). Rows sharing a key are paired by the SIGNATURE of their values (identical rows are paired together), but a key that really identifies a row - with a date or a time added - would make the comparison more reliable.

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 324
  Keys ONLY in B1 : 11367
  Keys ONLY in B0 : 1358
    ex: [(81, 4021165, datetime.date(2147, 10, 16)), (15, 4150612, datetime.date(2147, 2, 14)), (96, 4097169, datetime.date(2112, 5, 29))]
    ex: [(53, 46235654, datetime.date(2155, 12, 16)), (71, 46235654, datetime.date(2166, 2, 12)), (52, 4213288, datetime.date(2169, 5, 12))]
  Parmi elles, 19 combinaison(s) (personne + ['observation_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Matched rows (same person + same natural key) : 2712
  Coverage of B0: 2712/22529 (12.0%) - share of the B0 rows found in B1
  Row precision: 2712/65641 (4.1%) - share of the B1 rows that also exist in B0

# Content fields (what the row means)

## observation_datetime : 488/2712 lignes concordent (18.0%)  [datetime]
    ex: B1=Timestamp('2164-10-23 22:40:00') vs B0=Timestamp('2164-10-23 21:10:00')
    ex: B1=Timestamp('2164-10-23 23:00:00') vs B0=Timestamp('2164-10-23 21:10:00')
    ex: B1=Timestamp('2126-08-14 21:00:00') vs B0=Timestamp('2126-08-14 22:20:00')

## value_as_number : 49/2027 lignes concordent (2.4%)  [number]
    ex: B1=np.float64(1.2) vs B0=np.float64(nan)
    ex: B1=np.float64(100.0) vs B0=np.float64(nan)
    ex: B1=np.float64(2.8) vs B0=np.float64(nan)

## value_as_string : 32/2708 lignes concordent (1.2%)  [text]
    ex: B1='MED' vs B0='A'
    ex: B1='ON' vs B0='Lidocaine'
    ex: B1='Supine' vs B0='RCA'

# Provenance fields (how the source writes it)

## observation_source_value : 56/2712 lignes concordent (2.1%)  [text]
    ex: B1='919' vs B0='925'
    ex: B1='1622' vs B0='916'
    ex: B1='547' vs B0='926'

## observation_source_concept_id : 0/2712 lignes concordent (0.0%)  [concept]
    ex: B1=np.int64(1027551) vs B0=np.float64(2001019606.0)
    ex: B1=np.int64(1010397) vs B0=np.float64(2001019601.0)
    ex: B1=np.int64(37067617) vs B0=np.float64(2001019607.0)

# Scope gaps (fields left out of the score)

  value_as_concept_id : empty on both sides
  unit_concept_id : populated only in B1
  obs_event_field_concept_id : empty on both sides
  qualifier_concept_id : empty on both sides
  unit_source_value : populated only in B1
  qualifier_source_value : populated only in B1
  value_source_value : populated only in B1

## Summary
  Coverage of B0: 12.0%
  Row-level agreement (matched rows whose content fields ALL agree) : 16/2712 (0.6%)
  Content agreement by value (all compared values) : 7.6%
  Mean field agreement (unweighted mean of the 5 compared fields) : 4.7%
  Provenance fields, agreement by value : 1.0%

---

# Row-level comparison — death

Natural key: person + ['death_date']

## Raw volumes (before any filtering)
  B1: 129 rows
  B0: 92 rows
  Patient matches available (through the patient bridge) : 100

## Volumes after restriction to the common patients
  B1: 129 rows (0 excluded - patient not matched)
  B0: 92 rows (0 excluded - patient not matched)

⚠️  NON-UNIQUE KEY: 29 duplicate(s) in B1, 0 in B0, on (person + ['death_date']). Rows sharing a key are paired by the SIGNATURE of their values (identical rows are paired together), but a key that really identifies a row - with a date or a time added - would make the comparison more reliable.

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 90
  Keys ONLY in B1 : 10
  Keys ONLY in B0 : 2
    ex: [(73, datetime.date(2117, 4, 4)), (99, datetime.date(2182, 8, 3)), (100, datetime.date(2171, 4, 14))]
    ex: [(64, datetime.date(2155, 3, 11)), (74, datetime.date(2103, 5, 18))]
  Parmi elles, 2 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Matched rows (same person + same natural key) : 90
  Coverage of B0: 90/92 (97.8%) - share of the B0 rows found in B1
  Row precision: 90/129 (69.8%) - share of the B1 rows that also exist in B0

# Content fields (what the row means)

## death_datetime : 39/90 lignes concordent (43.3%)  [datetime]
    ex: B1=NaT vs B0=Timestamp('2165-08-12 00:00:00')
    ex: B1=NaT vs B0=Timestamp('2152-09-12 00:00:00')
    ex: B1=NaT vs B0=Timestamp('2195-11-24 00:00:00')

# Scope gaps (fields left out of the score)

  cause_concept_id : empty on both sides
  cause_source_value : empty on both sides
  cause_source_concept_id : empty on both sides

## Summary
  Coverage of B0: 97.8%
  Row-level agreement (matched rows whose content fields ALL agree) : 39/90 (43.3%)
  Content agreement by value (all compared values) : 43.3%
  Mean field agreement (unweighted mean of the 1 compared fields) : 43.3%

---

# Row-level comparison — observation_period

Natural key: person + ['observation_period_start_date']

## Raw volumes (before any filtering)
  B1: 129 rows
  B0: 129 rows
  Patient matches available (through the patient bridge) : 100

## Volumes after restriction to the common patients
  B1: 129 rows (0 excluded - patient not matched)
  B0: 129 rows (0 excluded - patient not matched)

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 119
  Keys ONLY in B1 : 10
  Keys ONLY in B0 : 10
    ex: [(62, datetime.date(2159, 11, 17)), (54, datetime.date(2151, 8, 13)), (65, datetime.date(2145, 9, 6))]
    ex: [(26, datetime.date(2188, 2, 7)), (54, datetime.date(2151, 8, 12)), (18, datetime.date(2129, 11, 23))]
  Parmi elles, 9 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Matched rows (same person + same natural key) : 119
  Coverage of B0: 119/129 (92.2%) - share of the B0 rows found in B1
  Row precision: 119/129 (92.2%) - share of the B1 rows that also exist in B0

# Content fields (what the row means)

## observation_period_end_date : 119/119 lignes concordent (100.0%)  [date]

  Columns missing from one of the two schemas (not compared) : ['observation_period_end_datetime', 'observation_period_start_datetime']

## Summary
  Coverage of B0: 92.2%
  Row-level agreement (matched rows whose content fields ALL agree) : 119/119 (100.0%)
  Content agreement by value (all compared values) : 100.0%
  Mean field agreement (unweighted mean of the 1 compared fields) : 100.0%

---
