# Full Comparison Report

## Executive Summary

| Table | Rows (B1) | Rows (B0) | Matched | Coverage of B0 | Content agreement | Provenance (not scored) | Note |
|---|---|---|---|---|---|---|---|
| person | 100 | 100 | 0 | 0/100 (0.0%) | n/a | n/a | 100 B1-only / 100 B0-only keys |
| visit_occurrence | 129 | 129 | 119 | 119/129 (92.2%) | 37/119 (31.1%) | 100.0% | 9 events found with another date; 10 B1-only / 10 B0-only keys |
| condition_occurrence | 1743 | 1903 | 1423 | 1423/1903 (74.8%) | n/a | 99.9% | non-unique key (115/119 dupes, paired by signature); 121 events found with another date; 228 B1-only / 384 B0-only keys |
| drug_exposure | 28033 | 56715 | 9480 | 9480/56715 (16.7%) | 0/9480 (0.0%) | 50.4% | non-unique key (15175/44819 dupes, paired by signature); 70 events found with another date; 4705 B1-only / 3743 B0-only keys |
| procedure_occurrence | 5099 | 2815 | 166 | 166/2815 (5.9%) | 131/166 (78.9%) | 8.7% | non-unique key (3126/996 dupes, paired by signature); 205 events found with another date; 1828 B1-only / 1674 B0-only keys |
| measurement | 129018 | 823220 | 112872 | 112872/823220 (13.7%) | 44743/112872 (39.6%) | 67.6% | non-unique key (67419/746654 dupes, paired by signature); 5418 B1-only / 20385 B0-only keys |
| observation | 65641 | 22529 | 2712 | 2712/22529 (12.0%) | 16/2712 (0.6%) | 1.0% | non-unique key (53950/20847 dupes, paired by signature); 19 events found with another date; 11367 B1-only / 1358 B0-only keys |
| death | 129 | 92 | 90 | 90/92 (97.8%) | 39/90 (43.3%) | n/a | non-unique key (29/0 dupes, paired by signature); 2 events found with another date; 10 B1-only / 2 B0-only keys |
| observation_period | 129 | 129 | 119 | 119/129 (92.2%) | 119/119 (100.0%) | n/a | 9 events found with another date; 10 B1-only / 10 B0-only keys |

**Coverage of B0 (B0 rows found in B1 / B0 rows): 126981/907632 (14.0%)**

**Content agreement (matched rows whose content fields all agree, weighted by rows): 45085/125558 (35.9%)**

**B0 rows reproduced with the same content (found AND agreeing): 45085/905629 (5.0%)**

Provenance fields (`*_source_value`, `*_source_concept_id`) are listed per table but are not part of any figure above: they record how the source wrote a value, which two faithful exports may do differently.

## Field agreement by table (unweighted mean over the compared content fields)

| Table | Fields compared | Mean field agreement | Fields below 100% |
|---|---|---|---|
| person | 0 | n/a | - |
| visit_occurrence | 3 | 77.0% | visit_start_datetime |
| condition_occurrence | 0 | n/a | - |
| drug_exposure | 4 | 73.2% | drug_exposure_start_datetime, drug_exposure_end_datetime, quantity, route_concept_id |
| procedure_occurrence | 2 | 88.7% | procedure_datetime, quantity |
| measurement | 3 | 74.7% | measurement_datetime, value_as_number, unit_concept_id |
| observation | 3 | 7.2% | observation_datetime, value_as_number, value_as_string |
| death | 1 | 43.3% | death_datetime |
| observation_period | 1 | 100.0% | - |

The per-field detail with the cause of each disagreement is in the `*_fields.csv` file next to this report. Provenance fields are in that file too, flagged `provenance`, and are not part of the mean.

## Per-Table Detail

# Row-level comparison — person

Natural key: person + ['person_source_value']

## Raw volumes (before any filtering)
  B1: 100 rows
  B0: 100 rows
  Patient matches available (through the patient bridge) : 100

## Volumes after restriction to the common patients
  B1: 100 rows (0 excluded - patient not matched)
  B0: 100 rows (0 excluded - patient not matched)

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 0
  Keys ONLY in B1 : 100
  Keys ONLY in B0 : 100
    ex: [(39, '9561'), (77, '31395'), (18, '9504')]
    ex: [(78, '42302'), (84, '42458'), (55, '40286')]

Matched rows (same person + same natural key) : 0
  Coverage of B0: 0/100 (0.0%) - share of the B0 rows found in B1
  Row precision: 0/100 (0.0%) - share of the B1 rows that also exist in B0

No matched row: the content cannot be compared.

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
    ex: [(64, 262, datetime.date(2155, 3, 8)), (54, 262, datetime.date(2151, 8, 13)), (16, 262, datetime.date(2185, 4, 14))]
    ex: [(16, 262, datetime.date(2185, 4, 13)), (64, 262, datetime.date(2155, 3, 7)), (18, 262, datetime.date(2129, 11, 23))]
  Parmi elles, 9 combinaison(s) (personne + ['visit_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Matched rows (same person + same natural key) : 119
  Coverage of B0: 119/129 (92.2%) - share of the B0 rows found in B1
  Row precision: 119/129 (92.2%) - share of the B1 rows that also exist in B0

# Content fields (what the row means) - they make up the score

## visit_start_datetime : 37/119 lignes concordent (31.1%)  [datetime]
    ex: B1=Timestamp('2164-10-23 21:09:00') vs B0=Timestamp('2164-10-23 16:43:00')
    ex: B1=Timestamp('2149-05-26 17:19:00') vs B0=Timestamp('2149-05-26 12:08:00')
    ex: B1=Timestamp('2195-05-17 07:39:00') vs B0=Timestamp('2195-05-17 01:49:00')

## visit_end_date : 119/119 lignes concordent (100.0%)  [date]

## visit_end_datetime : 119/119 lignes concordent (100.0%)  [datetime]

# Provenance fields (how the source writes it) - reported apart, not scored

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
  Mean field agreement (unweighted mean of the 3 compared content fields) : 77.0%
  Provenance agreement (not scored) : 100.0%

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
    ex: [(82, 4125274, datetime.date(2165, 12, 19)), (67, 4125274, datetime.date(2201, 9, 28)), (88, 4125274, datetime.date(2173, 11, 28))]
    ex: [(74, 196653, datetime.date(2102, 8, 29)), (65, 319049, datetime.date(2145, 7, 6)), (88, 4318408, datetime.date(2173, 11, 27))]
  Parmi elles, 121 combinaison(s) (personne + ['condition_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Matched rows (same person + same natural key) : 1423
  Coverage of B0: 1423/1903 (74.8%) - share of the B0 rows found in B1
  Row precision: 1423/1743 (81.6%) - share of the B1 rows that also exist in B0

# Provenance fields (how the source writes it) - reported apart, not scored

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
  Provenance agreement (not scored) : 99.9%

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
    ex: [(46, 19136048, datetime.date(2192, 5, 3), datetime.date(2192, 5, 3)), (22, 19011035, datetime.date(2107, 1, 20), datetime.date(2107, 1, 20)), (47, 19011035, datetime.date(2171, 7, 12), datetime.date(2171, 7, 12))]
    ex: [(40, 0, datetime.date(2180, 1, 17), datetime.date(2180, 1, 19)), (8, 0, datetime.date(2139, 9, 24), None), (57, 0, datetime.date(2144, 12, 29), datetime.date(2144, 12, 30))]
  Parmi elles, 70 combinaison(s) (personne + ['drug_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Matched rows (same person + same natural key) : 9480
  Coverage of B0: 9480/56715 (16.7%) - share of the B0 rows found in B1
  Row precision: 9480/28033 (33.8%) - share of the B1 rows that also exist in B0

# Content fields (what the row means) - they make up the score

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

# Provenance fields (how the source writes it) - reported apart, not scored

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
  Mean field agreement (unweighted mean of the 4 compared content fields) : 73.2%
  Provenance agreement (not scored) : 50.4%

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
    ex: [(62, 2514441, datetime.date(2159, 11, 17)), (57, 2314001, datetime.date(2144, 7, 27)), (46, 2514409, datetime.date(2192, 4, 16))]
    ex: [(2, 2008250, datetime.date(2126, 8, 28)), (89, 4214577, datetime.date(2198, 7, 24)), (67, 4150627, datetime.date(2199, 1, 14))]
  Parmi elles, 205 combinaison(s) (personne + ['procedure_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Matched rows (same person + same natural key) : 166
  Coverage of B0: 166/2815 (5.9%) - share of the B0 rows found in B1
  Row precision: 166/5099 (3.3%) - share of the B1 rows that also exist in B0

# Content fields (what the row means) - they make up the score

## procedure_datetime : 131/166 lignes concordent (78.9%)  [datetime]
    ex: B1=NaT vs B0=Timestamp('2149-05-26 17:19:00')
    ex: B1=NaT vs B0=Timestamp('2185-04-14 00:23:00')
    ex: B1=NaT vs B0=Timestamp('2150-08-22 17:33:00')

## quantity : 133/135 lignes concordent (98.5%)  [number]
    ex: B1=np.float64(nan) vs B0=np.float64(3610.0)
    ex: B1=np.float64(nan) vs B0=np.float64(164.0)

# Provenance fields (how the source writes it) - reported apart, not scored

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
  Mean field agreement (unweighted mean of the 2 compared content fields) : 88.7%
  Provenance agreement (not scored) : 8.7%

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
    ex: [(98, 21492838, datetime.date(2123, 12, 2)), (81, 4143063, datetime.date(2147, 10, 4)), (67, 4353621, datetime.date(2199, 2, 6))]
    ex: [(18, 4337265, datetime.date(2129, 11, 24)), (90, 21494989, datetime.date(2176, 7, 14)), (48, 3017594, datetime.date(2198, 7, 3))]

Matched rows (same person + same natural key) : 112872
  Coverage of B0: 112872/823220 (13.7%) - share of the B0 rows found in B1
  Row precision: 112872/129018 (87.5%) - share of the B1 rows that also exist in B0

# Content fields (what the row means) - they make up the score

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

# Provenance fields (how the source writes it) - reported apart, not scored

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
  Mean field agreement (unweighted mean of the 3 compared content fields) : 74.7%
  Provenance agreement (not scored) : 67.6%

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
    ex: [(18, 4337265, datetime.date(2129, 11, 24)), (46, 0, datetime.date(2192, 5, 11)), (52, 4125860, datetime.date(2169, 5, 12))]
    ex: [(54, 44803968, datetime.date(2151, 8, 13)), (87, 42536500, datetime.date(2179, 4, 17)), (96, 4052017, datetime.date(2112, 5, 22))]
  Parmi elles, 19 combinaison(s) (personne + ['observation_concept_id']) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Matched rows (same person + same natural key) : 2712
  Coverage of B0: 2712/22529 (12.0%) - share of the B0 rows found in B1
  Row precision: 2712/65641 (4.1%) - share of the B1 rows that also exist in B0

# Content fields (what the row means) - they make up the score

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

# Provenance fields (how the source writes it) - reported apart, not scored

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
  Mean field agreement (unweighted mean of the 3 compared content fields) : 7.2%
  Provenance agreement (not scored) : 1.0%

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
    ex: [(100, datetime.date(2171, 4, 14)), (99, datetime.date(2182, 8, 3)), (75, datetime.date(2136, 3, 26))]
    ex: [(74, datetime.date(2103, 5, 18)), (64, datetime.date(2155, 3, 11))]
  Parmi elles, 2 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Matched rows (same person + same natural key) : 90
  Coverage of B0: 90/92 (97.8%) - share of the B0 rows found in B1
  Row precision: 90/129 (69.8%) - share of the B1 rows that also exist in B0

# Content fields (what the row means) - they make up the score

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
  Mean field agreement (unweighted mean of the 1 compared content fields) : 43.3%

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
    ex: [(54, datetime.date(2151, 8, 13)), (29, datetime.date(2192, 11, 20)), (64, datetime.date(2155, 3, 8))]
    ex: [(10, datetime.date(2132, 12, 4)), (65, datetime.date(2145, 9, 5)), (54, datetime.date(2151, 8, 12))]
  Parmi elles, 9 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Matched rows (same person + same natural key) : 119
  Coverage of B0: 119/129 (92.2%) - share of the B0 rows found in B1
  Row precision: 119/129 (92.2%) - share of the B1 rows that also exist in B0

# Content fields (what the row means) - they make up the score

## observation_period_end_date : 119/119 lignes concordent (100.0%)  [date]

  Columns missing from one of the two schemas (not compared) : ['observation_period_end_datetime', 'observation_period_start_datetime']

## Summary
  Coverage of B0: 92.2%
  Row-level agreement (matched rows whose content fields ALL agree) : 119/119 (100.0%)
  Content agreement by value (all compared values) : 100.0%
  Mean field agreement (unweighted mean of the 1 compared content fields) : 100.0%

---
