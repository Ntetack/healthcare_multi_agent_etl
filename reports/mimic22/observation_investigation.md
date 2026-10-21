# observation : investigation

Matched patients: 100.

## 1. Composition

### Ours

Rows: 65149. Concept 0: 16646 (25.6%). Source value empty: 0 (0.0%). Distinct source values: 176. Distinct concepts (not 0): 79.

Rows with a number: 15284 (23.5%); with text: 64531 (99.1%); with a concept as value: 0 (0.0%).

Domains of the concepts (not 0): {'Observation': 48503}

Vocabularies: {'SNOMED': 36010, 'LOINC': 12338, 'CPT4': 82, 'OMOP Extension': 73}

Status of the concepts (not 0): {'standard': 48503}

| Type concept | Name | Rows | Concept 0 |
|---|---|---|---|
| 38000280 | Observation recorded from EHR | 65149 | 16646 |

| Most frequent concepts | n |
|---|---|
| 4117957 Activity | 4850 |
| 4232754 Activity tolerance | 4468 |
| 4183166 Orientation | 4019 |
| 4150612 Respiratory pattern | 3750 |
| 4337265 Bowel sounds | 3146 |
| 40757642 Behavior | 2556 |
| 4337391 Speaking | 2431 |
| 4146379 Cough reflex | 2081 |
| 21494983 Level of consciousness | 2062 |
| 21492835 Respiratory effort | 1999 |

### Reference

Rows: 22529. Concept 0: 6244 (27.7%). Source value empty: 16428 (72.9%). Distinct source values: 52. Distinct concepts (not 0): 16.

Rows with a number: 3770 (16.7%); with text: 22281 (98.9%); with a concept as value: 666 (3.0%).

Domains of the concepts (not 0): {'Procedure': 14549, 'Observation': 877, 'Condition': 859}

Vocabularies: {'SNOMED': 15492, 'CPT4': 470, 'LOINC': 323}

Status of the concepts (not 0): {'non-standard / deleted': 10905, 'standard': 4910, 'classification': 470}

| Type concept | Name | Rows | Concept 0 |
|---|---|---|---|
| 581413 | Observation from Measurement | 6101 | 6101 |
| 38000280 | Observation recorded from EHR | 16428 | 143 |

| Most frequent concepts | n |
|---|---|
| 4078442 Catheter procedure | 10776 |
| 42536500 Insertion of catheter into peripheral vein | 1328 |
| 4141149 Open insertion of central venous catheter | 988 |
| 4195428 Impaired skin integrity | 859 |
| 4213288 Insertion of catheter into artery | 634 |
| 45890031 Insertion of peripherally inserted central venous catheter (PICC), without subcutaneous port or pump (Deprecated) | 470 |
| 4296248 Cost containment | 297 |
| 36715149 Introduction of urinary catheter | 229 |
| 46235654 Primary insurance | 129 |
| 44803968 Ethnicity | 129 |

## 2. Item level: each source value on its own

A source value is a string compared as is (an ITEMID on one side and a label on the other would show up as two different items: read 'only on one side' with that in mind).

| Category | Items | Our rows | Reference rows |
|---|---|---|---|
| same concept | 0 | 0 | 0 |
| different concept | 0 | 0 | 0 |
| one side unmapped | 6 | 1250 | 1250 |
| only on our side | 170 | 63899 | 0 |
| only on the reference side | 46 | 0 | 4851 |

### Items mapped to another concept (largest first)

| item | our rows | our concept | reference rows | reference concept |
|---|---|---|---|---|

### Items only on our side (largest first)

| item | our rows | our concept | reference rows | reference concept |
|---|---|---|---|---|
| 224084 | 2894 | 4117957 Activity | 0 | - |
| 224086 | 2748 | 4232754 Activity tolerance | 0 | - |
| 224093 | 2655 | - | 0 | - |
| 226104 | 2062 | 21494983 Level of consciousness | 0 | - |
| 223898 | 2041 | 4183166 Orientation | 0 | - |
| 617 | 2018 | 4150612 Respiratory pattern | 0 | - |
| 479 | 1978 | 4183166 Orientation | 0 | - |
| 223902 | 1976 | 4337391 Speaking | 0 | - |
| 454 | 1965 | 4237719 Motor response | 0 | - |
| 31 | 1956 | 4117957 Activity | 0 | - |
| 226105 | 1734 | 40757642 Behavior | 0 | - |
| 223985 | 1732 | 4150612 Respiratory pattern | 0 | - |
| 32 | 1720 | 4232754 Activity tolerance | 0 | - |
| 223990 | 1716 | 21492835 Respiratory effort | 0 | - |
| 547 | 1704 | - | 0 | - |

### Items only on the reference side (largest first)

| item | our rows | our concept | reference rows | reference concept |
|---|---|---|---|---|
| 226543 | 0 | - | 417 | - |
| 225811 | 0 | - | 384 | - |
| 227688 | 0 | - | 229 | - |
| 225103 | 0 | - | 195 | - |
| 225092 | 0 | - | 151 | - |
| 225137 | 0 | - | 143 | - |
| 225135 | 0 | - | 140 | - |
| 225094 | 0 | - | 135 | - |
| 225131 | 0 | - | 132 | - |
| 226180 | 0 | - | 122 | - |
| 225078 | 0 | - | 120 | - |
| 225118 | 0 | - | 118 | - |
| 225067 | 0 | - | 115 | - |
| 225074 | 0 | - | 114 | - |
| 225126 | 0 | - | 113 | - |

## 3. Our rows with a real concept, one category each

48503 rows.

| Category | Rows | Share |
|---|---|---|
| A. same concept, same datetime | 0 | 0.0% |
| B. same concept, same day, other time | 0 | 0.0% |
| C. same concept, other day | 0 | 0.0% |
| D. item mapped identically, this patient has no such row | 0 | 0.0% |
| E. item mapped to another concept on the other side | 0 | 0.0% |
| F. item present on the other side but unmapped (concept 0) | 756 | 1.6% |
| G. item absent on the other side | 47747 | 98.4% |
| H. row without source value | 0 | 0.0% |

## 3. Reference rows with a real concept, one category each

16285 rows.

| Category | Rows | Share |
|---|---|---|
| A. same concept, same datetime | 0 | 0.0% |
| B. same concept, same day, other time | 0 | 0.0% |
| C. same concept, other day | 0 | 0.0% |
| D. item mapped identically, this patient has no such row | 0 | 0.0% |
| E. item mapped to another concept on the other side | 0 | 0.0% |
| F. item present on the other side but unmapped (concept 0) | 0 | 0.0% |
| G. item absent on the other side | 0 | 0.0% |
| H. row without source value | 16285 | 100.0% |

## 4. Where the reference puts what we hold only in observation

63899 of our rows have a source value absent from the reference's observation. First reference table (in the order measurement, drug_exposure, procedure_occurrence, condition_occurrence) in which that source value appears:

| Reference table | Our rows | Items |
|---|---|---|
| condition_occurrence | 155 | 70 |
| measurement | 60840 | 70 |
| nowhere | 2901 | 28 |
| procedure_occurrence | 3 | 2 |

Largest source values (condition_occurrence).

| item | our rows |
|---|---|
| V5861 | 18 |
| V5867 | 8 |
| V1251 | 7 |
| V103 | 7 |
| V1582 | 6 |
| V4582 | 6 |
| V153 | 4 |
| V1302 | 3 |
| V1201 | 3 |
| E9331 | 3 |

Largest source values (measurement).

| item | our rows |
|---|---|
| 224084 | 2894 |
| 224086 | 2748 |
| 224093 | 2655 |
| 226104 | 2062 |
| 223898 | 2041 |
| 617 | 2018 |
| 479 | 1978 |
| 223902 | 1976 |
| 454 | 1965 |
| 31 | 1956 |

Largest source values (nowhere).

| item | our rows |
|---|---|
| 227073 | 542 |
| 1523 | 391 |
| 227467 | 317 |
| 1530 | 286 |
| 30051 | 270 |
| 816 | 263 |
| 225667 | 195 |
| 225797 | 191 |
| 227456 | 74 |
| 226515 | 71 |

Largest source values (procedure_occurrence).

| item | our rows |
|---|---|
| 8964 | 2 |
| 8960 | 1 |

## 5. Our rows that carry a numeric value

15284 rows (23.5% of ours). A number is normally a measurement.

| Concept | Rows |
|---|---|
| 0 ? | 5873 |
| 4237719 Motor response | 1960 |
| 4021165 Skin care | 1282 |
| 3018668 Mental status | 1134 |
| 1469588 Pain level | 980 |
| 4139635 Plateau pressure | 836 |
| 3007397 Ventilator type | 704 |
| 4024742 Eye care | 650 |
| 4009397 Anion gap | 542 |
| 4125860 Calcium electrolyte | 453 |
