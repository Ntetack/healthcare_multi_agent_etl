# measurement : investigation

## 1. Composition

| | Ours | Reference |
|---|---|---|
| rows | 112850 | 823220 |
| concept 0 | 0 (0.0%) | 524057 (63.7%) |
| value_as_number empty | 10907 (9.7%) | 435590 (52.9%) |
| unit empty or 0 | 112806 (100.0%) | 535499 (65.0%) |
| source value empty | 0 (0.0%) | 13224 (1.6%) |
| distinct source values | 414 | 2030 |
| distinct concepts (not 0) | 405 | 527 |

Domains of the concepts (not 0). Ours: {'Measurement': 112850}. Reference: {'Measurement': 269327, 'Observation': 23155, 'Meas Value': 3488, 'Procedure': 3192, 'Condition': 1}.

| Ours, most frequent | n | Reference, most frequent | n |
|---|---|---|---|
| 45876226 Heart rate | 15490 | 3024171 Respiratory rate | 19340 |
| 3024171 Respiratory rate | 15086 | 3025315 Body weight | 17182 |
| 21492838 Skin integrity | 2839 | 3004249 Systolic blood pressure | 15961 |
| 3023314 Hematocrit [Volume Fraction] of Blood by Automated count | 2317 | 3027598 Mean blood pressure | 15941 |
| 3023103 Potassium [Moles/volume] in Serum or Plasma | 2279 | 3012888 Diastolic blood pressure | 15930 |
| 3019550 Sodium [Moles/volume] in Serum or Plasma | 2185 | 3027018 Heart rate | 15489 |
| 3016723 Creatinine [Mass/volume] in Serum or Plasma | 2175 | 3016502 Oxygen saturation in Arterial blood | 15470 |
| 3014576 Chloride [Moles/volume] in Serum or Plasma | 2160 | 3022318 Heart rate rhythm | 14507 |
| 3013682 Urea nitrogen [Mass/volume] in Serum or Plasma | 2158 | 3014315 Urine output | 9458 |
| 3000963 Hemoglobin [Mass/volume] in Blood | 2154 | 3020891 Body temperature | 7810 |

## 2. Item level: each source value on its own

697 source values carry a real concept on the reference side. Rows are reference rows.

| Our side | Items | Reference rows |
|---|---|---|
| same concept | 380 (54.5%) | 86062 (30.1%) |
| different concept | 21 (3.0%) | 21537 (7.5%) |
| ours unmapped | 0 (0.0%) | 0 (0.0%) |
| ours absent | 296 (42.5%) | 178340 (62.4%) |

Items the reference maps to more than one concept: 0.
Source values present on our side only: 13 items, 5161 rows (of which the reference has the item at concept 0: 4 items, 4322 rows; unmapped on our side too: 0 rows).

### Items mapped to another concept (largest first)

| item | reference concept | ref rows | our rows | our concept |
|---|---|---|---|---|
| 220045 | 3027018 Heart rate | 8093 | 8094 | 45876226 Heart rate |
| 211 | 3027018 Heart rate | 7396 | 7396 | 45876226 Heart rate |
| 220074 | 21490675 Central venous pressure (CVP) | 1656 | 1742 | 4323687 Central venous pressure |
| 51237 | 3034795 Deprecated INR in Platelet poor plasma by Coagulation assay | 1378 | 1378 | 3022217 INR in Platelet poor plasma by Coagulation assay |
| 444 | 3028354 Mean pressure Respiratory system airway Calculated | 931 | 931 | 42527086 Mean airway pressure |
| 224697 | 3028354 Mean pressure Respiratory system airway Calculated | 788 | 790 | 42527086 Mean airway pressure |
| 116 | 21490712 Left ventricular Cardiac index | 666 | 666 | 4208254 Cardiac index |
| 50911 | 3036345 Deprecated Creatine kinase.MB | 319 | 319 | 4265595 Creatine kinase measurement |
| 50920 | 3030354 Glomerular filtration rate [Volume Rate/Area] in Serum or Plasma by Creatinine-based formula (MDRD)/1.73 sq M | 207 | 207 | 46236952 Glomerular filtration rate [Volume Rate/Area] in Serum, Plasma or Blood by Creatinine-based formula (MDRD)/1.73 sq M |
| 51010 | 3006751 Deprecated Cobalamin [Mass/volume] in Serum | 38 | 38 | 3000593 Cobalamin (Vitamin B12) [Mass/volume] in Serum or Plasma |
| 50905 | 3004169 Deprecated Cholesterol.in LDL [Mass/volume] in Serum or Plasma | 24 | 24 | 3028437 Cholesterol in LDL [Mass/volume] in Serum or Plasma |
| 51360 | 3022356 Deprecated Polymorphonuclear cells/100 leukocytes in Cerebral spinal fluid | 12 | 12 | 3042847 Granulocytes/Leukocytes in Cerebral spinal fluid |
| 51436 | 3025450 Deprecated Polymorphonuclear cells/100 leukocytes in Body fluid | 10 | 10 | 44786800 Granulocytes/Leukocytes in Body fluid |
| 50942 | 3016557 Deprecated Hepatitis B virus core Ab [Units/volume] in Serum by Immunoassay | 7 | 7 | 1469566 Hepatitis B virus core Ab [Units/volume] in Serum or Plasma by Immunoassay |
| 51180 | 3000298 Deprecated CD4 cells [#/volume] in Blood | 3 | 3 | 3028167 CD3+CD4+ (T4 helper) cells [#/volume] in Blood |

### Items present on our side but unmapped

| item | reference concept | ref rows | our rows |
|---|---|---|---|

### Items absent on our side

| item | reference concept | ref rows | our rows |
|---|---|---|---|
| 220277 | 3016502 Oxygen saturation in Arterial blood | 8049 | 0 |
| 220048 | 3022318 Heart rate rhythm | 7412 | 0 |
| 646 | 3016502 Oxygen saturation in Arterial blood | 7262 | 0 |
| 212 | 3022318 Heart rate rhythm | 7095 | 0 |
| 128 | 4127294 Resuscitation status | 6967 | 0 |
| 220181 | 3027598 Mean blood pressure | 4891 | 0 |
| 220179 | 3004249 Systolic blood pressure | 4880 | 0 |
| 220180 | 3012888 Diastolic blood pressure | 4875 | 0 |
| Urine Out Foley | 3014315 Urine output | 4741 | 0 |
| 51 | 3004249 Systolic blood pressure | 4519 | 0 |
| 8368 | 3012888 Diastolic blood pressure | 4504 | 0 |
| 52 | 3027598 Mean blood pressure | 4473 | 0 |
| Foley | 3014315 Urine output | 4138 | 0 |
| 581 | 3025315 Body weight | 3373 | 0 |
| 455 | 3004249 Systolic blood pressure | 3214 | 0 |

## 3. Reference rows with a real concept, one category each

299163 rows.

| Category | Rows | Share |
|---|---|---|
| A. same concept, same datetime | 88806 | 29.7% |
| B. same concept, same day, other time | 1510 | 0.5% |
| C. same concept, other day | 12 | 0.0% |
| D. item mapped identically, this patient has no such row | 0 | 0.0% |
| E. item mapped to another concept on our side | 21537 | 7.2% |
| F. item present on our side but unmapped (concept 0) | 0 | 0.0% |
| G. item absent on our side | 174074 | 58.2% |
| H. reference row without source value | 13224 | 4.4% |

Reproduced to the minute (A): 88806 (29.7%).

## 4. Volume per item, for items mapped identically

380 items; reference rows 86062, our rows 86063.
Ratio ours/reference per item (5/25/50/75/95 %): {0.05: 1.0, 0.25: 1.0, 0.5: 1.0, 0.75: 1.0, 0.95: 1.0}.
Items with ratio >= 0.95: 380; with ratio < 0.5: 0.

Largest losses (items where we keep fewer rows than the reference).

None: for every item mapped identically we keep at least as many rows.

## 5. Values on unambiguous pairs

86052 pairs. Both values filled: 79871; they agree: 79871 (100.0%).
Value missing on our side only: 241; on the reference side only: 0; on both: 5940.
Ratio ours/reference where both are filled and differ (5/25/50/75/95 %): {}.
Units (concept): both filled 0, agree n/a; missing on our side only 80921; on the reference side only 0.

Items where we lack the value and the reference has it.

| item | concept | pairs |
|---|---|---|
| 51003 | Troponin T.cardiac [Mass/volume] in Serum or Plasma | 65 |
| 51476 | Epithelial cells [#/area] in Urine sediment by Microscopy high power field | 31 |
| 51493 | Erythrocytes [#/volume] in Urine sediment by Microscopy high power field | 24 |
| 51100 | Sodium [Moles/volume] in Urine | 20 |
| 51516 | Leukocytes [#/area] in Urine sediment by Microscopy high power field | 14 |
| 50935 | Haptoglobin [Mass/volume] in Serum or Plasma | 10 |
| 51196 | Fibrin D-dimer FEU [Mass/volume] in Platelet poor plasma | 5 |
| 50835 | Albumin [Mass/volume] in Peritoneal fluid | 5 |

Items with differing values (median ours/reference).

| item | concept | pairs | median ratio |
|---|---|---|---|

## 6. Time of day on unambiguous pairs (same patient, concept, day, item)

43565 pairs; same datetime: 43565 (100.0%).
Offset ours minus reference, in hours (most frequent): {0.0: 43565}
