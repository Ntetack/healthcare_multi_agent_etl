# drug_exposure : investigation

## 1. Composition

| | Ours | Reference |
|---|---|---|
| rows | 27306 | 56715 |
| drug_concept_id = 0 | 51 | 32649 |
| distinct keys (patient, drug, start date, end date) | 11121 | 11851 |
| rows in keys holding 10+ rows | 13152 | 40817 |

Rows per key (describe): ours {'count': 11121.0, 'mean': 2.5, 'std': 6.7, 'min': 1.0, '50%': 1.0, '90%': 3.0, '99%': 45.0, 'max': 81.0} ; reference {'count': 11851.0, 'mean': 4.8, 'std': 15.5, 'min': 1.0, '50%': 1.0, '90%': 9.0, '99%': 73.0, 'max': 341.0}

Shape of drug_source_value (NDC = PRESCRIPTIONS, itemid-like = INPUTEVENTS or CHARTEVENTS, text = name).

| Shape | Ours | Reference |
|---|---|---|
| NDC (10-11 digits) | 0 | 8958 |
| empty | 0 | 1 |
| itemid-like (4-7 digits) | 16904 | 0 |
| other number | 6 | 1477 |
| text (drug name) | 10396 | 46279 |

drug_type_concept_id: ours {38000177: 27306} ; reference {38000180: 46279, 38000177: 10436}

Most frequent drugs.

| Ours | n | Reference | n |
|---|---|---|---|
| 19122121 Insulin | 2484 | 0 No matching concept | 32649 |
| 753626 propofol | 2390 | 3037253 Fluid intake intravascular Measured | 4336 |
| 1154029 fentanyl | 1880 | 753626 propofol | 2357 |
| 708298 midazolam | 1485 | 3006552 Fluid intake oral Estimated | 1925 |
| 42799739 glycerin 144 MG/ML / petrolatum 150 MG/ML / phenylephrine hydrochloride 2.5 MG/ML / pramoxine hydrochloride 10 MG/ML Rectal Cream | 1477 | 1154029 fentanyl | 1857 |
| 1367571 heparin | 833 | 708298 midazolam | 1738 |
| 1337860 dopamine | 809 | 1337860 dopamine | 807 |
| 19009608 sterile water | 562 | 19020994 nitroprusside | 533 |
| 19044738 Lasix | 559 | 1309944 amiodarone | 522 |
| 1309944 amiodarone | 522 | 19015726 cisatracurium | 333 |

Heaviest keys (rows sharing one patient + drug + start/end date).

Ours:
```
person_id  drug_concept_id  start_d     end_d     
915139     19122121         2171-08-04  2171-08-04    81
           753626           2171-08-04  2171-08-04    79
           19122121         2171-08-09  2171-08-09    75
           753626           2171-08-09  2171-08-09    75
915110     1337860          2129-11-30  2129-11-30    72
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
| A. patient + drug + start date + end date (current key) | 8139 (68.7%) | 8139 (73.2%) | 9456 (16.7%) | 9456 (34.6%) |
| B. patient + drug + start date | 7632 (79.8%) | 7632 (77.5%) | 13597 (24.0%) | 13597 (49.8%) |
| C. patient + drug + start date and time | 11917 (46.3%) | 11917 (61.7%) | 13588 (24.0%) | 13588 (49.8%) |
| D. patient + drug + start and end date and time | 8530 (23.1%) | 8530 (40.5%) | 9456 (16.7%) | 9456 (34.6%) |
| E. patient + drug, any date | 4097 (92.7%) | 4097 (87.9%) | 16520 (29.1%) | 16520 (60.5%) |

## 3. Reference rows whose patient + drug never appears on our side

28173 rows (49.7% of reference); drug 0 among them: 20810.

By source shape: text (drug name): 27211, other number: 869, NDC (10-11 digits): 92, empty: 1

| drug | n |
|---|---|
| 0 No matching concept | 20810 |
| 3037253 Fluid intake intravascular Measured | 4336 |
| 3006552 Fluid intake oral Estimated | 1925 |
| 19020994 nitroprusside | 285 |
| 708298 midazolam | 253 |
| 40141424 sodium chloride Prefilled Syringe | 209 |
| 3035875 Fluid intake urinary bladder irrigation Estimated | 119 |
| 4022173 Transfusion of red blood cells | 69 |
| 19049024 potassium | 40 |
| 3035591 Fluid intake intravascular Estimated | 40 |
| 4022171 Transfusion of fresh frozen plasma | 34 |
| 4130829 Platelet transfusion | 22 |
| 40161286 magnesium chloride / sodium bicarbonate / sodium chloride Injectable Solution [Normocarb HF 25] | 18 |
| 43012282 polydextrose | 7 |
| 35604554 nesiritide 1.5 MG | 3 |

## 4. Our rows whose patient + drug never appears in the reference

10717 rows (39.2% of ours); drug 0 among them: 0.

By source shape: itemid-like (4-7 digits): 9153, text (drug name): 1558, other number: 6

| drug | n |
|---|---|
| 19122121 Insulin | 2484 |
| 42799739 glycerin 144 MG/ML / petrolatum 150 MG/ML / phenylephrine hydrochloride 2.5 MG/ML / pramoxine hydrochloride 10 MG/ML Rectal Cream | 1477 |
| 1367571 heparin | 833 |
| 19009608 sterile water | 562 |
| 19044738 Lasix | 559 |
| 19111276 Solution | 492 |
| 4298217 Lactic acid | 382 |
| 1321341 norepinephrine | 380 |
| 19038591 Sandostatin | 333 |
| 19072153 morphine sulfate | 329 |
| 19049105 potassium chloride | 291 |
| 19011034 citrate | 222 |
| 19037038 calcium gluconate | 218 |
| 939506 sodium bicarbonate | 202 |
| 1707687 vancomycin | 198 |

## 5. Quantity on unambiguous pairs

7809 pairs; both quantities filled: 7367; they agree: 6914 (93.9%).
Quantity missing on our side only: 1; on the reference side only: 0.
Ratio ours/reference over pairs with both quantities (5/25/50/75/95 %): {0.05: 1.0, 0.25: 1.0, 0.5: 1.0, 0.75: 1.0, 0.95: 1.0}

Drugs with the most disagreements.

| drug | n |
|---|---|
| 753626 propofol | 171 |
| 1154029 fentanyl | 126 |
| 1337860 dopamine | 78 |
| 1309944 amiodarone | 25 |
| 1368671 milrinone | 14 |
| 1337720 dobutamine | 13 |
| 19015726 cisatracurium | 12 |
| 1328165 diltiazem | 8 |
| 1318137 nicardipine | 6 |

Examples (drug, ours, reference): [[753626.0, 15.756303, 15.0060028571], [753626.0, 31.5492678, 50.0782028571], [753626.0, 984.2441965, 20.2311242857], [753626.0, 19.999979, 285.7139857143], [753626.0, 32.16783588, 4.9950055714], [753626.0, 158.57201521, 10.158361], [753626.0, 3.512966, 50.1852285714], [753626.0, 810.66610856, 10.018118]]

## 6. End date on pairs with the same patient, drug and start time

| Our source shape | end date missing | same end date |
|---|---|---|
| itemid-like (4-7 digits) | 1344 | 412 |
| text (drug name) | 1 | 6123 |
