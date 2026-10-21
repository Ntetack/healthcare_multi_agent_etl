# drug_exposure : reference rows with a real drug

Reference rows (matched patients): 56715. Retained: 24169 (42.6%). Filters: drug_concept_id <> 0.
Our rows (matched patients): 27306.

## 1. What we hold for each retained reference row

| Category | Rows | Share |
|---|---|---|
| 0a. no start date, drug found for the patient | 3032 | 12.5% |
| 0b. no start date, drug not found for the patient | 109 | 0.5% |
| 1. same drug, same start date | 13597 | 56.3% |
| 2. same drug, other date | 74 | 0.3% |
| 3. another real drug, same start date | 7337 | 30.4% |
| 4. only unmapped rows (0 or empty) that day | 0 | 0.0% |
| 5. patient present, nothing that day, drug absent | 20 | 0.1% |
| 6. patient absent from our drug_exposure | 0 | 0.0% |

Right drug and right day: 13597 (56.3%). Right drug, any day: 16703 (69.1%).

Among category 1 rows with a start time on both sides, the time of day agrees on 13537 (99.6%).

## 2. By shape of the reference drug_source_value

| Shape | 0a | 0b | 1 | 2 | 3 | 4 | 5 | 6 | Total |
|---|---|---|---|---|---|---|---|---|---|
| NDC (10-11 digits) | 0 | 0 | 8787 | 0 | 40 | 0 | 0 | 0 | 8827 |
| empty | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| other number | 0 | 0 | 0 | 0 | 239 | 0 | 0 | 0 | 239 |
| text (drug name) | 3032 | 109 | 4810 | 74 | 7057 | 0 | 20 | 0 | 15102 |

Categories are numbered as in section 1.

## 3. Disagreements: another real drug on the same patient and day

Pairs counted once per reference row. Look first for pairs where the two drugs are clearly different substances (a wrong mapping) versus the same substance at another level (ingredient, clinical drug, brand).

| Reference drug | Our drug | Domain of ours | Rows |
|---|---|---|---|
| 3037253 Fluid intake intravascular Measured | 42799739 glycerin 144 MG/ML / petrolatum 150 MG/ML / phenylephrine hydrochloride 2.5 MG/ML / pramoxine hydrochloride 10 MG/ML Rectal Cream | Drug | 3213 |
| 3037253 Fluid intake intravascular Measured | 19111276 Solution | Drug | 2770 |
| 3037253 Fluid intake intravascular Measured | 1707687 vancomycin | Drug | 2187 |
| 3037253 Fluid intake intravascular Measured | 4298217 Lactic acid | Drug | 2027 |
| 3037253 Fluid intake intravascular Measured | 19049105 potassium chloride | Drug | 1840 |
| 3037253 Fluid intake intravascular Measured | 1321341 norepinephrine | Drug | 1492 |
| 3037253 Fluid intake intravascular Measured | 1154029 fentanyl | Drug | 1412 |
| 3037253 Fluid intake intravascular Measured | 40221385 100 ML sodium chloride 9 MG/ML Injection | Drug | 1255 |
| 3006552 Fluid intake oral Estimated | 42799739 glycerin 144 MG/ML / petrolatum 150 MG/ML / phenylephrine hydrochloride 2.5 MG/ML / pramoxine hydrochloride 10 MG/ML Rectal Cream | Drug | 1165 |
| 3037253 Fluid intake intravascular Measured | 40220357 1000 ML sodium chloride 9 MG/ML Injection | Drug | 1162 |
| 3037253 Fluid intake intravascular Measured | 36249737 250 ML glucose 50 MG/ML Injection | Drug | 1160 |
| 3037253 Fluid intake intravascular Measured | 40221350 200 ML vancomycin 5 MG/ML Injection | Drug | 1089 |
| 3037253 Fluid intake intravascular Measured | 19009608 sterile water | Drug | 1088 |
| 3037253 Fluid intake intravascular Measured | 19093848 magnesium sulfate | Drug | 966 |
| 3006552 Fluid intake oral Estimated | 1707687 vancomycin | Drug | 931 |
| 3037253 Fluid intake intravascular Measured | 753626 propofol | Drug | 917 |
| 3037253 Fluid intake intravascular Measured | 1797513 ciprofloxacin | Drug | 906 |
| 3037253 Fluid intake intravascular Measured | 40221387 500 ML sodium chloride 9 MG/ML Injection | Drug | 898 |
| 3006552 Fluid intake oral Estimated | 19111276 Solution | Drug | 843 |
| 3037253 Fluid intake intravascular Measured | 40221386 250 ML sodium chloride 9 MG/ML Injection | Drug | 825 |
| 3037253 Fluid intake intravascular Measured | 46275280 50 ML magnesium sulfate 40 MG/ML Injection | Drug | 811 |
| 3037253 Fluid intake intravascular Measured | 19011034 citrate | Drug | 811 |
| 3037253 Fluid intake intravascular Measured | 35603429 fentanyl 0.05 MG/ML Injection | Drug | 793 |
| 3037253 Fluid intake intravascular Measured | 1707164 metronidazole | Drug | 790 |
| 3037253 Fluid intake intravascular Measured | 1718752 50 ML potassium chloride 0.4 MEQ/ML Injection | Drug | 778 |

## 4. Reference drugs we most often lack altogether

Categories 0b, 5 and 6 (and 4: only unmapped rows that day).

| Drug | Rows |
|---|---|
| 19020994 nitroprusside | 126 |
| 3037253 Fluid intake intravascular Measured | 2 |
| 3006552 Fluid intake oral Estimated | 1 |

## 5. Coverage under the five keys, retained reference only

Rows paired with the comparator's rule, min(rows ours, rows reference) per common key.

| Key | Reference rows paired | Our rows paired |
|---|---|---|
| A. patient + drug + start date + end date (current key) | 9405 (38.9%) | 9405 (34.4%) |
| B. patient + drug + start date | 13546 (56.0%) | 13546 (49.6%) |
| C. patient + drug + start date and time | 13537 (56.0%) | 13537 (49.6%) |
| D. patient + drug + start and end date and time | 9405 (38.9%) | 9405 (34.4%) |
| E. patient + drug, any date | 16469 (68.1%) | 16469 (60.3%) |

## 6. Our rows outside the evaluation

| | Rows |
|---|---|
| all our rows | 27306 |
| on a patient + day where the reference holds a real drug | 27149 |
| on a patient + day where the reference holds only concept 0 | 154 |
| on a patient + day absent from the reference | 3 |

The second line is the part of our output that this comparison cannot judge, because the reference never named the drug there.
