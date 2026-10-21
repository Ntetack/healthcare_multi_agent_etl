# procedure_occurrence : investigation

## 1. Composition

| | Ours | Reference |
|---|---|---|
| rows | 1337 | 2815 |
| procedure_concept_id = 0 | 2 | 3 |

Rows per vocabulary of procedure_source_concept_id (this identifies the source table: ICD9Proc = PROCEDURES_ICD, CPT4 = CPTEVENTS, local/unknown ids = item based).

| Source vocabulary | Ours | Reference |
|---|---|---|
| CPT4 | 291 | 1579 |
| ICD9CM | 2 | 0 |
| ICD9Proc | 503 | 0 |
| MIMIC Local Codes | 0 | 503 |
| MIMIC d_items | 0 | 730 |
| SNOMED | 541 | 0 |
| no source concept | 0 | 3 |

Most frequent standard concepts.

| Ours | n | Reference | n |
|---|---|---|---|
| 3526814 Bed bath | 288 | 4027135 Subsequent hospital visit by physician | 579 |
| 2314001 Ventilation assist and management, initiation of pressure or volume preset ventilators for assisted or controlled breathing; hospital inpatient/observation, each subsequent day | 262 | 45763734 Critical care physician service | 326 |
| 4046481 Incentive spirometry | 189 | 4214577 Inpatient care | 291 |
| 2002174 Venous catheterization, not elsewhere classified | 56 | 4049832 Insertion of peripheral venous cannula into peripheral vein | 176 |
| 2008005 Enteral infusion of concentrated nutritional substances | 32 | 4163872 Plain X-ray of chest | 98 |
| 4125928 Packed blood cell transfusion | 30 | 4313303 Evaluation and management of inpatient | 71 |
| 2314000 Ventilation assist and management, initiation of pressure or volume preset ventilators for assisted or controlled breathing; hospital inpatient/observation, initial day | 29 | 2002174 Venous catheterization, not elsewhere classified | 56 |
| 4013354 Insertion of endotracheal tube | 22 | 4089048 New patient consultation | 56 |
| 2008008 Continuous invasive mechanical ventilation for less than 96 consecutive hours | 21 | 4052413 Central venous cannula insertion | 53 |
| 2008009 Continuous invasive mechanical ventilation for 96 consecutive hours or more | 19 | 4297090 Evaluation procedure | 48 |

## 2. Origin of procedure_date, by source vocabulary

### Ours

| source_vocab | no visit |
|---|---|
| CPT4 | 291 |
| ICD9CM | 2 |
| ICD9Proc | 503 |
| SNOMED | 541 |

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
| all reference rows | 2815 | 43 (1.5%) | 54 (1.9%) | 78 (2.8%) | 145 (5.2%) | 294 (10.4%) |
| reference rows with a concept (not 0) | 2812 | 43 (1.5%) | 54 (1.9%) | 78 (2.8%) | 145 (5.2%) | 294 (10.5%) |

## 4. Reference rows with no counterpart (same patient + concept, any date)

2521 rows (89.6% of reference); concept 0 among them: 3.

By source vocabulary: CPT4: 1574, MIMIC d_items: 680, MIMIC Local Codes: 266, no source concept: 1

| concept | n |
|---|---|
| 4027135 Subsequent hospital visit by physician | 579 |
| 45763734 Critical care physician service | 326 |
| 4214577 Inpatient care | 291 |
| 4049832 Insertion of peripheral venous cannula into peripheral vein | 176 |
| 4163872 Plain X-ray of chest | 98 |
| 4313303 Evaluation and management of inpatient | 71 |
| 4089048 New patient consultation | 56 |
| 4052413 Central venous cannula insertion | 53 |
| 4297090 Evaluation procedure | 48 |
| 4203130 Discharge from hospital | 46 |
| 4036803 General examination of patient | 43 |
| 4107893 Blood culture | 40 |
| 4163951 Electrocardiographic procedure | 34 |
| 4180642 CT of site | 34 |
| 2008238 Transfusion of packed cells | 30 |

## 5. Our rows with no counterpart (same patient + concept, any date)

1042 rows (77.9% of ours); concept 0 among them: 2.

By source vocabulary: SNOMED: 508, CPT4: 291, ICD9Proc: 241, ICD9CM: 2

| concept | n |
|---|---|
| 3526814 Bed bath | 288 |
| 2314001 Ventilation assist and management, initiation of pressure or volume preset ventilators for assisted or controlled breathing; hospital inpatient/observation, each subsequent day | 262 |
| 4046481 Incentive spirometry | 189 |
| 4125928 Packed blood cell transfusion | 30 |
| 2314000 Ventilation assist and management, initiation of pressure or volume preset ventilators for assisted or controlled breathing; hospital inpatient/observation, initial day | 29 |
| 4202832 Intubation | 17 |
| 4021169 Total parenteral nutrition | 14 |
| 4013354 Insertion of endotracheal tube | 13 |
| 4231419 Abdominal paracentesis | 12 |
| 4120120 Hemodialysis | 11 |
| 4167261 Bronchoscopy and biopsy of bronchus | 10 |
| 4171675 Coronary angiography using two catheters | 8 |
| 4148375 Catheterization of both left and right heart | 7 |
| 4213288 Insertion of catheter into artery | 6 |
| 4230911 Echocardiography | 5 |
