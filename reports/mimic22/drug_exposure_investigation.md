# drug_exposure : investigation

## 1. Composition

| | Ours | Reference |
|---|---|---|
| rows | 28513 | 56715 |
| drug_concept_id = 0 | 1806 | 32546 |
| distinct keys (patient, drug, start date, end date) | 13025 | 11896 |
| rows in keys holding 10+ rows | 10885 | 40723 |

Rows per key (describe): ours {'count': 13025.0, 'mean': 2.2, 'std': 5.5, 'min': 1.0, '50%': 1.0, '90%': 3.0, '99%': 37.0, 'max': 79.0} ; reference {'count': 11896.0, 'mean': 4.8, 'std': 15.5, 'min': 1.0, '50%': 1.0, '90%': 9.0, '99%': 73.0, 'max': 341.0}

Shape of drug_source_value (NDC = PRESCRIPTIONS, itemid-like = INPUTEVENTS or CHARTEVENTS, text = name).

| Shape | Ours | Reference |
|---|---|---|
| NDC (10-11 digits) | 0 | 8958 |
| empty | 0 | 1 |
| itemid-like (4-7 digits) | 18683 | 0 |
| other number | 1002 | 1477 |
| text (drug name) | 8828 | 46279 |

drug_type_concept_id: ours {38000177: 28513} ; reference {38000180: 46279, 38000177: 10436}

Most frequent drugs.

| Ours | n | Reference | n |
|---|---|---|---|
| 753626 propofol | 2390 | 0 No matching concept | 32546 |
| 1154029 fentanyl | 1880 | 3037253 Fluid intake intravascular Measured | 4336 |
| 0 No matching concept | 1806 | 753626 propofol | 2357 |
| 708298 midazolam | 1485 | 3006552 Fluid intake oral Estimated | 1925 |
| 1367571 heparin | 945 | 1154029 fentanyl | 1857 |
| 19071968 creatinine | 915 | 708298 midazolam | 1738 |
| 19124906 magnesium | 899 | 1337860 dopamine | 807 |
| 36862556 HEMOGLOBIN | 893 | 19020994 nitroprusside | 533 |
| 1337860 dopamine | 809 | 1309944 amiodarone | 522 |
| 1560524 glucose | 698 | 19015726 cisatracurium | 333 |

Heaviest keys (rows sharing one patient + drug + start/end date).

Ours:
```
person_id  drug_concept_id  start_d     end_d     
915139     753626           2171-08-04  2171-08-04    79
                            2171-08-09  2171-08-09    75
915110     1337860          2129-11-30  2129-11-30    72
           1309944          2129-11-30  2129-11-30    71
915120     708298           2107-03-25  2107-03-25    66
```
Reference:
```
person_id  drug_concept_id  start_d  end_d     
915097     0                NaT      2163-05-15    341
915110     0                NaT      2129-11-28    275
915113     0                NaT      2150-08-25    267
                                     2150-08-26    255
915110     0                NaT      2129-11-29    252
```

## 2. Coverage of the reference under five keys

Distinct keys: how many reference keys exist on our side. Rows: sum over common keys of min(rows ours, rows reference), the way the comparator pairs them.

| Key | Reference keys found | Our keys found in reference | Reference rows paired | Our rows paired |
|---|---|---|---|---|
| A. patient + drug + start date + end date (current key) | 8320 (69.9%) | 8320 (63.9%) | 9935 (17.5%) | 9935 (34.8%) |
| B. patient + drug + start date | 7810 (81.4%) | 7810 (64.4%) | 15030 (26.5%) | 15030 (52.7%) |
| C. patient + drug + start date and time | 12851 (49.9%) | 12851 (57.4%) | 14746 (26.0%) | 14746 (51.7%) |
| D. patient + drug + start and end date and time | 8777 (23.8%) | 8777 (37.0%) | 9706 (17.1%) | 9706 (34.0%) |
| E. patient + drug, any date | 4123 (92.9%) | 4123 (82.7%) | 18275 (32.2%) | 18275 (64.1%) |

## 3. Reference rows whose patient + drug never appears on our side

13489 rows (23.8% of reference); drug 0 among them: 6023.

By source shape: text (drug name): 12910, other number: 504, NDC (10-11 digits): 74, empty: 1

| drug | n |
|---|---|
| 0 No matching concept | 6023 |
| 3037253 Fluid intake intravascular Measured | 4336 |
| 3006552 Fluid intake oral Estimated | 1925 |
| 19020994 nitroprusside | 285 |
| 708298 midazolam | 253 |
| 40141424 sodium chloride Prefilled Syringe | 209 |
| 3035875 Fluid intake urinary bladder irrigation Estimated | 119 |
| 35884360 Heparin Sodium | 103 |
| 4022173 Transfusion of red blood cells | 69 |
| 19049024 potassium | 40 |
| 3035591 Fluid intake intravascular Estimated | 40 |
| 4022171 Transfusion of fresh frozen plasma | 34 |
| 4130829 Platelet transfusion | 22 |
| 40161286 magnesium chloride / sodium bicarbonate / sodium chloride Injectable Solution [Normocarb HF 25] | 18 |
| 43012282 polydextrose | 7 |

## 4. Our rows whose patient + drug never appears in the reference

10169 rows (35.7% of ours); drug 0 among them: 0.

By source shape: itemid-like (4-7 digits): 9173, other number: 996

| drug | n |
|---|---|
| 1367571 heparin | 945 |
| 19071968 creatinine | 915 |
| 19124906 magnesium | 899 |
| 36862556 HEMOGLOBIN | 893 |
| 1560524 glucose | 698 |
| 19010309 water | 562 |
| 19049024 potassium | 536 |
| 19046180 carbon dioxide | 472 |
| 19136048 sodium | 415 |
| 19011035 lactate | 382 |
| 1321341 norepinephrine | 380 |
| 1110410 morphine | 329 |
| 19018544 calcium | 324 |
| 19049105 potassium chloride | 291 |
| 19011034 citrate | 222 |

## 5. Quantity on unambiguous pairs

8012 pairs; both quantities filled: 7570; they agree: 6908 (91.3%).
Quantity missing on our side only: 1; on the reference side only: 0.
Ratio ours/reference over pairs with both quantities (5/25/50/75/95 %): {0.05: 1.0, 0.25: 1.0, 0.5: 1.0, 0.75: 1.0, 0.95: 1.0}

Drugs with the most disagreements.

| drug | n |
|---|---|
| 0 No matching concept | 209 |
| 753626 propofol | 171 |
| 1154029 fentanyl | 126 |
| 1337860 dopamine | 78 |
| 1309944 amiodarone | 25 |
| 1368671 milrinone | 14 |
| 1337720 dobutamine | 13 |
| 19015726 cisatracurium | 12 |
| 1328165 diltiazem | 8 |
| 1318137 nicardipine | 6 |

Examples (drug, ours, reference): [[753626.0, 15.756303, 15.0060028571], [753626.0, 31.5492678, 50.0782028571], [0.0, 0.910109239, 0.3000360086], [753626.0, 984.2441965, 20.2311242857], [753626.0, 19.999979, 285.7139857143], [753626.0, 32.16783588, 4.9950055714], [0.0, 5.157286056, 0.5000600486], [753626.0, 158.57201521, 10.158361]]

## 6. End date on pairs with the same patient, drug and start time

| Our source shape | end date missing | ours ends later | same end date |
|---|---|---|---|
| itemid-like (4-7 digits) | 1464 | 1 | 556 |
| other number | 2 | 0 | 0 |
| text (drug name) | 1 | 0 | 6121 |
