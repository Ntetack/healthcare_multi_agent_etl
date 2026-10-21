# procedure_occurrence : investigation

## 1. Composition

| | Ours | Reference |
|---|---|---|
| rows | 5099 | 2815 |
| procedure_concept_id = 0 | 2 | 3 |

Rows per vocabulary of procedure_source_concept_id (this identifies the source table: ICD9Proc = PROCEDURES_ICD, CPT4 = CPTEVENTS, local/unknown ids = item based).

| Source vocabulary | Ours | Reference |
|---|---|---|
| CPT4 | 1497 | 1579 |
| ICD9CM | 2 | 0 |
| ICD9Proc | 503 | 0 |
| MIMIC Local Codes | 0 | 503 |
| MIMIC d_items | 0 | 730 |
| SNOMED | 3097 | 0 |
| no source concept | 0 | 3 |

Most frequent standard concepts.

| Ours | n | Reference | n |
|---|---|---|---|
| 4083171 Pain management | 2402 | 4027135 Subsequent hospital visit by physician | 579 |
| 2514441 Critical care, evaluation and management of the critically ill or critically injured patient; first 30-74 minutes | 303 | 45763734 Critical care physician service | 326 |
| 2514409 Subsequent hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date o... | 290 | 4214577 Inpatient care | 291 |
| 2514408 Subsequent hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the da... | 289 | 4049832 Insertion of peripheral venous cannula into peripheral vein | 176 |
| 4238681 Bathing patient in bed | 288 | 4163872 Plain X-ray of chest | 98 |
| 2314001 Ventilation assist and management, initiation of pressure or volume preset ventilators for assisted or controlled breathing; hospital inpatient/observation, each subsequent day | 262 | 4313303 Evaluation and management of inpatient | 71 |
| 4046481 Incentive spirometry | 189 | 2002174 Venous catheterization, not elsewhere classified | 56 |
| 4163872 Plain X-ray of chest | 101 | 4089048 New patient consultation | 56 |
| 2514407 Subsequent hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward or low level of medical decision making. When using total... | 71 | 4052413 Central venous cannula insertion | 53 |
| 2002174 Venous catheterization, not elsewhere classified | 56 | 4297090 Evaluation procedure | 48 |

## 2. Origin of procedure_date, by source vocabulary

### Ours

| source_vocab | no visit |
|---|---|
| CPT4 | 1497 |
| ICD9CM | 2 |
| ICD9Proc | 503 |
| SNOMED | 3097 |

### Reference

| source_vocab | = visit end | = visit start | inside the stay |
|---|---|---|---|
| CPT4 | 12 | 1199 | 368 |
| MIMIC Local Codes | 495 | 8 | 0 |
| MIMIC d_items | 18 | 225 | 487 |
| no source concept | 3 | 0 | 0 |

MIMIC-III PROCEDURES_ICD has no date column. A date on those rows is therefore derived (most plausibly from the admission); the two tables above show which convention each side used.

## 3. Coverage of the reference if the date may differ

| subset | rows | date within 0 d | date within 1 d | date within 3 d | date within 7 d | same patient+concept, any date |
|---|---|---|---|---|---|---|
| all reference rows | 2815 | 167 (5.9%) | 178 (6.3%) | 201 (7.1%) | 268 (9.5%) | 417 (14.8%) |
| reference rows with a concept (not 0) | 2812 | 167 (5.9%) | 178 (6.3%) | 201 (7.1%) | 268 (9.5%) | 417 (14.8%) |

## 4. Reference rows with no counterpart (same patient + concept, any date)

2398 rows (85.2% of reference); concept 0 among them: 3.

By source vocabulary: CPT4: 1550, MIMIC d_items: 581, MIMIC Local Codes: 266, no source concept: 1

| concept | n |
|---|---|
| 4027135 Subsequent hospital visit by physician | 579 |
| 45763734 Critical care physician service | 326 |
| 4214577 Inpatient care | 291 |
| 4049832 Insertion of peripheral venous cannula into peripheral vein | 176 |
| 4313303 Evaluation and management of inpatient | 71 |
| 4089048 New patient consultation | 56 |
| 4052413 Central venous cannula insertion | 53 |
| 4297090 Evaluation procedure | 48 |
| 4203130 Discharge from hospital | 46 |
| 4036803 General examination of patient | 43 |
| 4107893 Blood culture | 40 |
| 4180642 CT of site | 34 |
| 4163951 Electrocardiographic procedure | 34 |
| 2008238 Transfusion of packed cells | 30 |
| 4097246 Controlled ventilation procedure and therapy, initiation and management | 26 |

## 5. Our rows with no counterpart (same patient + concept, any date)

4675 rows (91.7% of ours); concept 0 among them: 2.

By source vocabulary: SNOMED: 2961, CPT4: 1471, ICD9Proc: 241, ICD9CM: 2

| concept | n |
|---|---|
| 4083171 Pain management | 2402 |
| 2514441 Critical care, evaluation and management of the critically ill or critically injured patient; first 30-74 minutes | 303 |
| 2514409 Subsequent hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date o... | 290 |
| 2514408 Subsequent hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the da... | 289 |
| 4238681 Bathing patient in bed | 288 |
| 2314001 Ventilation assist and management, initiation of pressure or volume preset ventilators for assisted or controlled breathing; hospital inpatient/observation, each subsequent day | 262 |
| 4046481 Incentive spirometry | 189 |
| 2514407 Subsequent hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward or low level of medical decision making. When using total... | 71 |
| 4302745 Irrigation of urinary bladder | 53 |
| 2213576 Dialysis procedure other than hemodialysis (eg, peritoneal dialysis, hemofiltration, or other continuous renal replacement therapies), with single evaluation by a physician or other qualified health care professional | 38 |
| 4125928 Packed blood cell transfusion | 30 |
| 2514414 Hospital inpatient or observation discharge day management; more than 30 minutes on the date of the encounter | 30 |
| 2314000 Ventilation assist and management, initiation of pressure or volume preset ventilators for assisted or controlled breathing; hospital inpatient/observation, initial day | 29 |
| 2514406 Initial hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of t... | 25 |
| 2514442 Critical care, evaluation and management of the critically ill or critically injured patient; each additional 30 minutes (List separately in addition to code for primary service) | 23 |
