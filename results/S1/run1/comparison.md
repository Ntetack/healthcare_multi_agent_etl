# Full Comparison Report

## Executive Summary

| Table | Rows (B1) | Rows (B0) | Matched | Coverage of B0 | Content agreement | Provenance fields | Note |
|---|---|---|---|---|---|---|---|
| person | 114 | 114 | 114 | 114/114 (100.0%) | 109/114 (95.6%) | 100.0% |  |
| visit_occurrence | 6703 | 6110 | 6110 | 6110/6110 (100.0%) | 6098/6110 (99.8%) | 0.0% | non-unique key (246/7 dupes, paired by signature); 354 B1-only / 0 B0-only keys |
| condition_occurrence | 1985 | 1973 | 1973 | 1973/1973 (100.0%) | 1973/1973 (100.0%) | 100.0% | 12 B1-only / 0 B0-only keys |
| drug_exposure | 7616 | 7382 | 7382 | 7382/7382 (100.0%) | 0/7382 (0.0%) | 100.0% | non-unique key (47/47 dupes, paired by signature); 234 B1-only / 0 B0-only keys |
| procedure_occurrence | 11974 | 10154 | 10154 | 10154/10154 (100.0%) | 10154/10154 (100.0%) | 100.0% | non-unique key (22/22 dupes, paired by signature); 1820 B1-only / 0 B0-only keys |
| measurement | 55841 | 55833 | 55833 | 55833/55833 (100.0%) | 55339/55833 (99.1%) | 99.8% | non-unique key (1688/1682 dupes, paired by signature); 2 B1-only / 0 B0-only keys |
| observation | 39846 | 30324 | 30242 | 30242/30324 (99.7%) | 30242/30242 (100.0%) | 97.7% | non-unique key (208/26 dupes, paired by signature); 9422 B1-only / 82 B0-only keys |
| death | 14 | 14 | 0 | 0/14 (0.0%) | n/a | n/a | 14 events found with another date; 14 B1-only / 14 B0-only keys |
| observation_period | 6414 | 6110 | 6080 | 6080/6110 (99.5%) | 6069/6080 (99.8%) | n/a | non-unique key (0/18 dupes, paired by signature); 5 events found with another date; 334 B1-only / 12 B0-only keys |

**Coverage of B0 (B0 rows found in B1 / B0 rows): 117888/118014 (99.9%)**

**Content agreement (matched rows whose content fields all agree, weighted by rows): 109984/117888 (93.3%)**

**B0 rows reproduced with the same content (found AND agreeing): 109984/118000 (93.2%)**

Content agreement above covers the content fields only. Provenance fields (`*_source_value`, `*_source_concept_id`) keep the way the source wrote a value, which two faithful exports may do differently; they are in the per-field table below, with the content fields.

## Field agreement by table (unweighted mean over the compared fields)

| Table | Fields compared | Mean field agreement | Fields below 100% |
|---|---|---|---|
| person | 10 | 99.6% | race_concept_id |
| visit_occurrence | 4 | 74.9% | visit_end_date, visit_end_datetime, visit_source_value |
| condition_occurrence | 5 | 100.0% | - |
| drug_exposure | 6 | 80.1% | days_supply, verbatim_end_date |
| procedure_occurrence | 5 | 100.0% | - |
| measurement | 8 | 99.8% | value_as_number, value_source_value |
| observation | 4 | 98.2% | value_source_value |
| death | 0 | n/a | - |
| observation_period | 1 | 99.8% | observation_period_end_date |

The per-field detail with the cause of each disagreement is in the `*_fields.csv` file next to this report. Content and provenance fields both enter the mean; the file flags each field `content` or `provenance`.

## Per-Table Detail

# Row-level comparison — person

Natural key: person + []

## Raw volumes (before any filtering)
  B1: 114 rows
  B0: 114 rows
  Patient matches available (through the patient bridge) : 114

## Volumes after restriction to the common patients
  B1: 114 rows (0 excluded - patient not matched)
  B0: 114 rows (0 excluded - patient not matched)

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 114
  Keys ONLY in B1 : 0
  Keys ONLY in B0 : 0

Matched rows (same person + same natural key) : 114
  Coverage of B0: 114/114 (100.0%) - share of the B0 rows found in B1
  Row precision: 114/114 (100.0%) - share of the B1 rows that also exist in B0

# Content fields (what the row means)

## gender_concept_id : 114/114 lignes concordent (100.0%)  [concept]

## year_of_birth : 114/114 lignes concordent (100.0%)  [exact]

## month_of_birth : 114/114 lignes concordent (100.0%)  [exact]

## day_of_birth : 114/114 lignes concordent (100.0%)  [exact]

## birth_datetime : 114/114 lignes concordent (100.0%)  [datetime]

## race_concept_id : 108/113 lignes concordent (95.6%)  [concept]
    ex: B1=np.int64(8657) vs B0=np.int64(0)
    ex: B1=np.int64(8657) vs B0=np.int64(0)
    ex: B1=np.int64(8557) vs B0=np.int64(0)

## ethnicity_concept_id : 114/114 lignes concordent (100.0%)  [concept]

# Provenance fields (how the source writes it)

## gender_source_value : 114/114 lignes concordent (100.0%)  [text]

## race_source_value : 114/114 lignes concordent (100.0%)  [text]

## ethnicity_source_value : 114/114 lignes concordent (100.0%)  [text]

# Scope gaps (fields left out of the score)

  gender_source_concept_id : populated only in B1, outside the baseline scope (not populated)
  race_source_concept_id : populated only in B1, outside the baseline scope (not populated)
  ethnicity_source_concept_id : empty on both sides

## Summary
  Coverage of B0: 100.0%
  Row-level agreement (matched rows whose content fields ALL agree) : 109/114 (95.6%)
  Content agreement by value (all compared values) : 99.4%
  Mean field agreement (unweighted mean of the 10 compared fields) : 99.6%
  Provenance fields, agreement by value : 100.0%

---

# Row-level comparison — visit_occurrence

Natural key: person + ['visit_concept_id', 'visit_start_date']

## Raw volumes (before any filtering)
  B1: 6703 rows
  B0: 6110 rows
  Patient matches available (through the patient bridge) : 114

## Volumes after restriction to the common patients
  B1: 6703 rows (0 excluded - patient not matched)
  B0: 6110 rows (0 excluded - patient not matched)

⚠️  NON-UNIQUE KEY: 246 duplicate(s) in B1, 7 in B0, on (person + ['visit_concept_id', 'visit_start_date']). Rows sharing a key are paired by the SIGNATURE of their values (identical rows are paired together), but a key that really identifies a row - with a date or a time added - would make the comparison more reliable.

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 6103
  Keys ONLY in B1 : 354
  Keys ONLY in B0 : 0
    ex: [(102, 9203, datetime.date(2023, 2, 17)), (109, 9203, datetime.date(2020, 1, 21)), (109, 9203, datetime.date(2023, 11, 21))]

Matched rows (same person + same natural key) : 6110
  Coverage of B0: 6110/6110 (100.0%) - share of the B0 rows found in B1
  Row precision: 6110/6703 (91.2%) - share of the B1 rows that also exist in B0

# Content fields (what the row means)

## visit_start_datetime : 6110/6110 lignes concordent (100.0%)  [datetime]

## visit_end_date : 6098/6110 lignes concordent (99.8%)  [date]
    ex: B1=datetime.date(2022, 10, 26) vs B0=datetime.date(2022, 10, 27)
    ex: B1=datetime.date(2020, 4, 19) vs B0=datetime.date(2020, 4, 22)
    ex: B1=datetime.date(2020, 4, 21) vs B0=datetime.date(2020, 4, 22)

## visit_end_datetime : 6098/6110 lignes concordent (99.8%)  [datetime]
    ex: B1=Timestamp('2022-10-26 22:03:09') vs B0=Timestamp('2022-10-27 00:00:00')
    ex: B1=Timestamp('2020-04-19 16:23:42') vs B0=Timestamp('2020-04-22 00:00:00')
    ex: B1=Timestamp('2020-04-21 02:36:52') vs B0=Timestamp('2020-04-22 00:00:00')

# Provenance fields (how the source writes it)

## visit_source_value : 0/6110 lignes concordent (0.0%)  [text]
    ex: B1='410620009' vs B0='534f299e-c6a6-e37b-7900-1509a59f232a'
    ex: B1='410620009' vs B0='534f299e-c6a6-e37b-f9fe-c19c365276cf'
    ex: B1='185349003' vs B0='534f299e-c6a6-e37b-11ff-06138c31ba7f'

# Scope gaps (fields left out of the score)

  admitted_from_concept_id : empty on both sides
  discharged_to_concept_id : empty on both sides
  visit_source_concept_id : empty on both sides
  admitted_from_source_value : empty on both sides
  discharged_to_source_value : empty on both sides

## Summary
  Coverage of B0: 100.0%
  Row-level agreement (matched rows whose content fields ALL agree) : 6098/6110 (99.8%)
  Content agreement by value (all compared values) : 99.9%
  Mean field agreement (unweighted mean of the 4 compared fields) : 74.9%
  Provenance fields, agreement by value : 0.0%

---

# Row-level comparison — condition_occurrence

Natural key: person + ['condition_concept_id', 'condition_start_date']

## Raw volumes (before any filtering)
  B1: 1985 rows
  B0: 1973 rows
  Patient matches available (through the patient bridge) : 114

## Volumes after restriction to the common patients
  B1: 1985 rows (0 excluded - patient not matched)
  B0: 1973 rows (0 excluded - patient not matched)

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 1973
  Keys ONLY in B1 : 12
  Keys ONLY in B0 : 0
    ex: [(103, 0, datetime.date(2022, 10, 7)), (10, 0, datetime.date(2007, 5, 2)), (57, 0, datetime.date(1998, 6, 4))]

Matched rows (same person + same natural key) : 1973
  Coverage of B0: 1973/1973 (100.0%) - share of the B0 rows found in B1
  Row precision: 1973/1985 (99.4%) - share of the B1 rows that also exist in B0

# Content fields (what the row means)

## condition_start_datetime : 1973/1973 lignes concordent (100.0%)  [datetime]

## condition_end_date : 1353/1353 lignes concordent (100.0%)  [date]

## condition_end_datetime : 1353/1353 lignes concordent (100.0%)  [datetime]

# Provenance fields (how the source writes it)

## condition_source_value : 1973/1973 lignes concordent (100.0%)  [text]

## condition_source_concept_id : 1973/1973 lignes concordent (100.0%)  [concept]

# Scope gaps (fields left out of the score)

  condition_status_concept_id : empty on both sides
  stop_reason : empty on both sides
  condition_status_source_value : empty on both sides

## Summary
  Coverage of B0: 100.0%
  Row-level agreement (matched rows whose content fields ALL agree) : 1973/1973 (100.0%)
  Content agreement by value (all compared values) : 100.0%
  Mean field agreement (unweighted mean of the 5 compared fields) : 100.0%
  Provenance fields, agreement by value : 100.0%

---

# Row-level comparison — drug_exposure

Natural key: person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']

## Raw volumes (before any filtering)
  B1: 7616 rows
  B0: 7382 rows
  Patient matches available (through the patient bridge) : 114

## Volumes after restriction to the common patients
  B1: 7616 rows (0 excluded - patient not matched)
  B0: 7382 rows (0 excluded - patient not matched)

⚠️  NON-UNIQUE KEY: 47 duplicate(s) in B1, 47 in B0, on (person + ['drug_concept_id', 'drug_exposure_start_date', 'drug_exposure_end_date']). Rows sharing a key are paired by the SIGNATURE of their values (identical rows are paired together), but a key that really identifies a row - with a date or a time added - would make the comparison more reliable.

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 7335
  Keys ONLY in B1 : 234
  Keys ONLY in B0 : 0
    ex: [(106, 37003436, datetime.date(2021, 4, 12), datetime.date(2021, 4, 12)), (5, 37003518, datetime.date(2021, 4, 30), datetime.date(2021, 4, 30)), (105, 37003518, datetime.date(2021, 5, 2), datetime.date(2021, 5, 2))]

Matched rows (same person + same natural key) : 7382
  Coverage of B0: 7382/7382 (100.0%) - share of the B0 rows found in B1
  Row precision: 7382/7616 (96.9%) - share of the B1 rows that also exist in B0

# Content fields (what the row means)

## drug_exposure_start_datetime : 7382/7382 lignes concordent (100.0%)  [datetime]

## drug_exposure_end_datetime : 7382/7382 lignes concordent (100.0%)  [datetime]

## days_supply : 0/7382 lignes concordent (0.0%)  [number]
    ex: B1=None vs B0=np.int64(18)
    ex: B1=None vs B0=np.int64(0)
    ex: B1=None vs B0=np.int64(0)

## verbatim_end_date : 5746/7117 lignes concordent (80.7%)  [date]
    ex: B1=None vs B0=datetime.date(2026, 3, 31)
    ex: B1=None vs B0=datetime.date(2025, 10, 28)
    ex: B1=None vs B0=datetime.date(2025, 12, 30)

# Provenance fields (how the source writes it)

## drug_source_value : 7382/7382 lignes concordent (100.0%)  [text]

## drug_source_concept_id : 7382/7382 lignes concordent (100.0%)  [concept]

# Scope gaps (fields left out of the score)

  quantity : populated only in B1, outside the baseline scope (it holds only 0)
  lot_number : outside the baseline scope (it holds only 0)
  refills : outside the baseline scope (it holds only 0)
  route_concept_id : empty on both sides
  sig : empty on both sides
  stop_reason : empty on both sides
  dose_unit_source_value : empty on both sides
  route_source_value : empty on both sides

## Summary
  Coverage of B0: 100.0%
  Row-level agreement (matched rows whose content fields ALL agree) : 0/7382 (0.0%)
  Content agreement by value (all compared values) : 70.1%
  Mean field agreement (unweighted mean of the 6 compared fields) : 80.1%
  Provenance fields, agreement by value : 100.0%

---

# Row-level comparison — procedure_occurrence

Natural key: person + ['procedure_concept_id', 'procedure_date']

## Raw volumes (before any filtering)
  B1: 11974 rows
  B0: 10154 rows
  Patient matches available (through the patient bridge) : 114

## Volumes after restriction to the common patients
  B1: 11974 rows (0 excluded - patient not matched)
  B0: 10154 rows (0 excluded - patient not matched)

⚠️  NON-UNIQUE KEY: 22 duplicate(s) in B1, 22 in B0, on (person + ['procedure_concept_id', 'procedure_date']). Rows sharing a key are paired by the SIGNATURE of their values (identical rows are paired together), but a key that really identifies a row - with a date or a time added - would make the comparison more reliable.

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 10132
  Keys ONLY in B1 : 1820
  Keys ONLY in B0 : 0
    ex: [(59, 4036803, datetime.date(2022, 7, 14)), (105, 4036803, datetime.date(2023, 10, 15)), (20, 4036803, datetime.date(2016, 2, 29))]

Matched rows (same person + same natural key) : 10154
  Coverage of B0: 10154/10154 (100.0%) - share of the B0 rows found in B1
  Row precision: 10154/11974 (84.8%) - share of the B1 rows that also exist in B0

# Content fields (what the row means)

## procedure_datetime : 10154/10154 lignes concordent (100.0%)  [datetime]

## procedure_end_date : 10154/10154 lignes concordent (100.0%)  [date]

## procedure_end_datetime : 10154/10154 lignes concordent (100.0%)  [datetime]

# Provenance fields (how the source writes it)

## procedure_source_value : 10154/10154 lignes concordent (100.0%)  [text]

## procedure_source_concept_id : 10154/10154 lignes concordent (100.0%)  [concept]

# Scope gaps (fields left out of the score)

  quantity : empty on both sides
  modifier_concept_id : empty on both sides
  modifier_source_value : empty on both sides

## Summary
  Coverage of B0: 100.0%
  Row-level agreement (matched rows whose content fields ALL agree) : 10154/10154 (100.0%)
  Content agreement by value (all compared values) : 100.0%
  Mean field agreement (unweighted mean of the 5 compared fields) : 100.0%
  Provenance fields, agreement by value : 100.0%

---

# Row-level comparison — measurement

Natural key: person + ['measurement_concept_id', 'measurement_date']

## Raw volumes (before any filtering)
  B1: 55841 rows
  B0: 55833 rows
  Patient matches available (through the patient bridge) : 114

## Volumes after restriction to the common patients
  B1: 55841 rows (0 excluded - patient not matched)
  B0: 55833 rows (0 excluded - patient not matched)

⚠️  NON-UNIQUE KEY: 1688 duplicate(s) in B1, 1682 in B0, on (person + ['measurement_concept_id', 'measurement_date']). Rows sharing a key are paired by the SIGNATURE of their values (identical rows are paired together), but a key that really identifies a row - with a date or a time added - would make the comparison more reliable.

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 54151
  Keys ONLY in B1 : 2
  Keys ONLY in B0 : 0
    ex: [(90, 0, datetime.date(2020, 4, 10)), (90, 0, datetime.date(2020, 4, 8))]

Matched rows (same person + same natural key) : 55833
  Coverage of B0: 55833/55833 (100.0%) - share of the B0 rows found in B1
  Row precision: 55833/55841 (100.0%) - share of the B1 rows that also exist in B0

# Content fields (what the row means)

## measurement_datetime : 55833/55833 lignes concordent (100.0%)  [datetime]

## value_as_number : 43594/44087 lignes concordent (98.9%)  [number]
    ex: B1=np.float64(16.0) vs B0=np.float64(13.1)
    ex: B1=np.float64(13.1) vs B0=np.float64(16.0)
    ex: B1=np.float64(40.0) vs B0=np.float64(32.4)

## unit_concept_id : 38683/38684 lignes concordent (100.0%)  [concept]
    ex: B1=np.int64(0) vs B0=np.int64(8848)

## measurement_time : 55833/55833 lignes concordent (100.0%)  [exact]

# Provenance fields (how the source writes it)

## measurement_source_value : 55833/55833 lignes concordent (100.0%)  [text]

## measurement_source_concept_id : 55833/55833 lignes concordent (100.0%)  [concept]

## unit_source_value : 51454/51454 lignes concordent (100.0%)  [text]

## value_source_value : 51121/51606 lignes concordent (99.1%)  [text]
    ex: B1='16.0' vs B0='13.1'
    ex: B1='13.1' vs B0='16.0'
    ex: B1='40.0' vs B0='32.4'

# Scope gaps (fields left out of the score)

  value_as_concept_id : empty on both sides
  meas_event_field_concept_id : empty on both sides
  operator_concept_id : empty on both sides
  range_high : empty on both sides
  range_low : empty on both sides
  unit_source_concept_id : populated only in B1, outside the baseline scope (not populated)

## Summary
  Coverage of B0: 100.0%
  Row-level agreement (matched rows whose content fields ALL agree) : 55339/55833 (99.1%)
  Content agreement by value (all compared values) : 99.7%
  Mean field agreement (unweighted mean of the 8 compared fields) : 99.8%
  Provenance fields, agreement by value : 99.8%

---

# Row-level comparison — observation

Natural key: person + ['observation_concept_id', 'observation_date']

## Raw volumes (before any filtering)
  B1: 39846 rows
  B0: 30324 rows
  Patient matches available (through the patient bridge) : 114

## Volumes after restriction to the common patients
  B1: 39846 rows (0 excluded - patient not matched)
  B0: 30324 rows (0 excluded - patient not matched)

⚠️  NON-UNIQUE KEY: 208 duplicate(s) in B1, 26 in B0, on (person + ['observation_concept_id', 'observation_date']). Rows sharing a key are paired by the SIGNATURE of their values (identical rows are paired together), but a key that really identifies a row - with a date or a time added - would make the comparison more reliable.

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 30216
  Keys ONLY in B1 : 9422
  Keys ONLY in B0 : 82
    ex: [(110, 0, datetime.date(2006, 7, 19)), (31, 4085798, datetime.date(1995, 7, 14)), (40, 4256369, datetime.date(1983, 4, 16))]
    ex: [(89, 4138133, datetime.date(1997, 8, 13)), (5, 42536288, datetime.date(1977, 11, 26)), (74, 4224654, datetime.date(1993, 11, 26))]

Matched rows (same person + same natural key) : 30242
  Coverage of B0: 30242/30324 (99.7%) - share of the B0 rows found in B1
  Row precision: 30242/39846 (75.9%) - share of the B1 rows that also exist in B0

# Content fields (what the row means)

## observation_datetime : 30242/30242 lignes concordent (100.0%)  [datetime]

# Provenance fields (how the source writes it)

## observation_source_value : 30242/30242 lignes concordent (100.0%)  [text]

## observation_source_concept_id : 30242/30242 lignes concordent (100.0%)  [concept]

## value_source_value : 28123/30242 lignes concordent (93.0%)  [text]
    ex: B1='314529007' vs B0=nan
    ex: B1='314529007' vs B0=nan
    ex: B1='314529007' vs B0=nan

# Scope gaps (fields left out of the score)

  value_as_number : populated only in B1, outside the baseline scope (not populated)
  value_as_string : populated only in B1, outside the baseline scope (not populated)
  value_as_concept_id : empty on both sides
  unit_concept_id : empty on both sides
  obs_event_field_concept_id : empty on both sides
  qualifier_concept_id : empty on both sides
  unit_source_value : populated only in B1, outside the baseline scope (not populated)
  qualifier_source_value : empty on both sides

## Summary
  Coverage of B0: 99.7%
  Row-level agreement (matched rows whose content fields ALL agree) : 30242/30242 (100.0%)
  Content agreement by value (all compared values) : 100.0%
  Mean field agreement (unweighted mean of the 4 compared fields) : 98.2%
  Provenance fields, agreement by value : 97.7%

---

# Row-level comparison — death

Natural key: person + ['death_date']

## Raw volumes (before any filtering)
  B1: 14 rows
  B0: 14 rows
  Patient matches available (through the patient bridge) : 114

## Volumes after restriction to the common patients
  B1: 14 rows (0 excluded - patient not matched)
  B0: 14 rows (0 excluded - patient not matched)

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 0
  Keys ONLY in B1 : 14
  Keys ONLY in B0 : 14
    ex: [(40, datetime.date(1987, 9, 2)), (46, datetime.date(1983, 7, 1)), (87, datetime.date(1987, 8, 21))]
    ex: [(96, datetime.date(2025, 12, 21)), (40, datetime.date(1987, 9, 4)), (81, datetime.date(1992, 11, 26))]
  Parmi elles, 14 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Matched rows (same person + same natural key) : 0
  Coverage of B0: 0/14 (0.0%) - share of the B0 rows found in B1
  Row precision: 0/14 (0.0%) - share of the B1 rows that also exist in B0

No matched row: the content cannot be compared.

---

# Row-level comparison — observation_period

Natural key: person + ['observation_period_start_date']

## Raw volumes (before any filtering)
  B1: 6414 rows
  B0: 6110 rows
  Patient matches available (through the patient bridge) : 114

## Volumes after restriction to the common patients
  B1: 6414 rows (0 excluded - patient not matched)
  B0: 6110 rows (0 excluded - patient not matched)

⚠️  NON-UNIQUE KEY: 0 duplicate(s) in B1, 18 in B0, on (person + ['observation_period_start_date']). Rows sharing a key are paired by the SIGNATURE of their values (identical rows are paired together), but a key that really identifies a row - with a date or a time added - would make the comparison more reliable.

## Existence des rows (avant de comparer leur contenu)
  Keys present on both sides : 6080
  Keys ONLY in B1 : 334
  Keys ONLY in B0 : 12
    ex: [(46, datetime.date(1976, 2, 21)), (110, datetime.date(2012, 7, 18)), (108, datetime.date(1988, 11, 3))]
    ex: [(108, datetime.date(1985, 3, 31)), (36, datetime.date(2023, 8, 30)), (75, datetime.date(2016, 1, 6))]
  Parmi elles, 5 combinaison(s) (personne + []) existent des DEUX côtés avec une AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente.

Matched rows (same person + same natural key) : 6080
  Coverage of B0: 6080/6110 (99.5%) - share of the B0 rows found in B1
  Row precision: 6080/6414 (94.8%) - share of the B1 rows that also exist in B0

# Content fields (what the row means)

## observation_period_end_date : 6069/6080 lignes concordent (99.8%)  [date]
    ex: B1=datetime.date(1988, 2, 18) vs B0=datetime.date(1988, 2, 11)
    ex: B1=datetime.date(1973, 9, 5) vs B0=datetime.date(1973, 8, 31)
    ex: B1=datetime.date(2016, 1, 7) vs B0=datetime.date(2016, 1, 6)

## Summary
  Coverage of B0: 99.5%
  Row-level agreement (matched rows whose content fields ALL agree) : 6069/6080 (99.8%)
  Content agreement by value (all compared values) : 99.8%
  Mean field agreement (unweighted mean of the 1 compared fields) : 99.8%

---
