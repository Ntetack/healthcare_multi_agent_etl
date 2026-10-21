# Structural Mapping Evaluation Report

## Summary (MAP only)

| Metric | Value |
|--------|-------|
| Gold fields (unique table.field) | 67 |
| Gold MAP rows (sources) | 153 |
| TP | 105 |
| FP (over-mapping) | 90 |
| FN (under-mapping) | 48 |
| **Micro Precision** | **0.5385** |
| **Micro Recall** | **0.6863** |
| **Micro F1** | **0.6034** |
| Macro Precision | 0.6902 |
| Macro Recall | 0.7956 |
| Macro F1 | 0.7150 |
| Over-mapping rate | 0.4615 |
| Under-mapping rate | 0.3137 |

### Per-field details

| Table | Field | Gold sources | Agent sources | P | R | F1 | TP | FP | FN |
|-------|-------|--------------|---------------|---|---|----|----|----|----|
| condition_occurrence | condition_occurrence_id | ADMISSIONS.hadm_id, DIAGNOSES_ICD.row_id | CHARTEVENTS.row_id, DIAGNOSES_ICD.row_id | 0.50 | 0.50 | 0.50 | 1 | 1 | 1 |
| condition_occurrence | condition_source_value | ADMISSIONS.diagnosis, DIAGNOSES_ICD.icd9_code | CHARTEVENTS.itemid, DIAGNOSES_ICD.icd9_code, PROCEDUREEVENTS_MV.ordercategoryname | 0.33 | 0.50 | 0.40 | 1 | 2 | 1 |
| condition_occurrence | condition_start_date | ADMISSIONS.admittime | CHARTEVENTS.charttime, PROCEDUREEVENTS_MV.starttime | 0.00 | 0.00 | 0.00 | 0 | 2 | 1 |
| condition_occurrence | person_id | ADMISSIONS.subject_id, DIAGNOSES_ICD.subject_id | CHARTEVENTS.subject_id, DIAGNOSES_ICD.subject_id, PROCEDUREEVENTS_MV.subject_id | 0.33 | 0.50 | 0.40 | 1 | 2 | 1 |
| condition_occurrence | visit_occurrence_id | ADMISSIONS.hadm_id, DIAGNOSES_ICD.hadm_id | CHARTEVENTS.hadm_id, DIAGNOSES_ICD.hadm_id, PROCEDUREEVENTS_MV.hadm_id | 0.33 | 0.50 | 0.40 | 1 | 2 | 1 |
| death | cause_source_value | ADMISSIONS.diagnosis | ADMISSIONS.diagnosis | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| death | death_date | PATIENTS.dod | PATIENTS.dod | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| death | death_datetime | ADMISSIONS.deathtime, PATIENTS.dod | ADMISSIONS.deathtime | 1.00 | 0.50 | 0.67 | 1 | 0 | 1 |
| death | person_id | PATIENTS.subject_id | PATIENTS.subject_id | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| drug_exposure | dose_unit_source_value | INPUTEVENTS_CV.amountuom, INPUTEVENTS_MV.amountuom, PRESCRIPTIONS.dose_unit_rx | CHARTEVENTS.valueuom, INPUTEVENTS_CV.amountuom, INPUTEVENTS_MV.amountuom, PRESCRIPTIONS.dose_unit_rx | 0.75 | 1.00 | 0.86 | 3 | 1 | 0 |
| drug_exposure | drug_exposure_end_date | INPUTEVENTS_MV.endtime, PRESCRIPTIONS.enddate | INPUTEVENTS_CV.charttime, INPUTEVENTS_MV.endtime, PRESCRIPTIONS.enddate | 0.67 | 1.00 | 0.80 | 2 | 1 | 0 |
| drug_exposure | drug_exposure_end_datetime | INPUTEVENTS_MV.endtime, PRESCRIPTIONS.enddate | INPUTEVENTS_CV.charttime, INPUTEVENTS_MV.endtime, PRESCRIPTIONS.enddate | 0.67 | 1.00 | 0.80 | 2 | 1 | 0 |
| drug_exposure | drug_exposure_id | INPUTEVENTS_CV.row_id, INPUTEVENTS_MV.row_id, PRESCRIPTIONS.row_id | CHARTEVENTS.row_id, INPUTEVENTS_CV.row_id, PRESCRIPTIONS.row_id | 0.67 | 0.67 | 0.67 | 2 | 1 | 1 |
| drug_exposure | drug_exposure_start_date | INPUTEVENTS_MV.starttime, PRESCRIPTIONS.startdate | CHARTEVENTS.charttime, INPUTEVENTS_CV.charttime, INPUTEVENTS_MV.starttime, PRESCRIPTIONS.startdate | 0.50 | 1.00 | 0.67 | 2 | 2 | 0 |
| drug_exposure | drug_exposure_start_datetime | INPUTEVENTS_CV.charttime, INPUTEVENTS_MV.starttime, PRESCRIPTIONS.startdate | CHARTEVENTS.charttime, INPUTEVENTS_CV.charttime, INPUTEVENTS_MV.starttime, PRESCRIPTIONS.startdate | 0.75 | 1.00 | 0.86 | 3 | 1 | 0 |
| drug_exposure | drug_source_value | D_ITEMS.label, INPUTEVENTS_CV.itemid, INPUTEVENTS_MV.itemid, PRESCRIPTIONS.drug, PRESCRIPTIONS.ndc | CHARTEVENTS.itemid, INPUTEVENTS_CV.itemid, INPUTEVENTS_MV.itemid, PRESCRIPTIONS.drug | 0.75 | 0.60 | 0.67 | 3 | 1 | 2 |
| drug_exposure | person_id | INPUTEVENTS_CV.subject_id, INPUTEVENTS_MV.subject_id, PRESCRIPTIONS.subject_id | CHARTEVENTS.subject_id, INPUTEVENTS_CV.subject_id, INPUTEVENTS_MV.subject_id, PRESCRIPTIONS.subject_id | 0.75 | 1.00 | 0.86 | 3 | 1 | 0 |
| drug_exposure | quantity | INPUTEVENTS_CV.amount, INPUTEVENTS_MV.amount, PRESCRIPTIONS.dose_val_rx | INPUTEVENTS_CV.amount, INPUTEVENTS_MV.amount, PRESCRIPTIONS.form_val_disp | 0.67 | 0.67 | 0.67 | 2 | 1 | 1 |
| drug_exposure | route_source_value | INPUTEVENTS_CV.originalroute, INPUTEVENTS_MV.ordercategorydescription, PRESCRIPTIONS.route | INPUTEVENTS_CV.originalroute, INPUTEVENTS_MV.ordercategorydescription, PRESCRIPTIONS.route | 1.00 | 1.00 | 1.00 | 3 | 0 | 0 |
| drug_exposure | visit_occurrence_id | INPUTEVENTS_CV.hadm_id, INPUTEVENTS_MV.hadm_id, PRESCRIPTIONS.hadm_id | CHARTEVENTS.hadm_id, INPUTEVENTS_CV.hadm_id, INPUTEVENTS_MV.hadm_id, PRESCRIPTIONS.hadm_id | 0.75 | 1.00 | 0.86 | 3 | 1 | 0 |
| measurement | measurement_date | CHARTEVENTS.storetime, LABEVENTS.charttime, MICROBIOLOGYEVENTS.chartdate | CHARTEVENTS.charttime, LABEVENTS.charttime, PROCEDUREEVENTS_MV.starttime | 0.33 | 0.33 | 0.33 | 1 | 2 | 2 |
| measurement | measurement_datetime | CHARTEVENTS.storetime, LABEVENTS.charttime, MICROBIOLOGYEVENTS.charttime, OUTPUTEVENTS.charttime | CHARTEVENTS.charttime, LABEVENTS.charttime, PROCEDUREEVENTS_MV.starttime | 0.33 | 0.25 | 0.29 | 1 | 2 | 3 |
| measurement | measurement_id | CHARTEVENTS.row_id, INPUTEVENTS_MV.row_id, LABEVENTS.row_id, MICROBIOLOGYEVENTS.row_id, OUTPUTEVENTS.row_id | CHARTEVENTS.row_id, DIAGNOSES_ICD.row_id, LABEVENTS.row_id, PROCEDUREEVENTS_MV.row_id | 0.50 | 0.40 | 0.44 | 2 | 2 | 3 |
| measurement | measurement_source_value | CHARTEVENTS.itemid, D_ITEMS.itemid, D_LABITEMS.itemid, LABEVENTS.itemid, MICROBIOLOGYEVENTS.ab_name, MICROBIOLOGYEVENTS.org_name, MICROBIOLOGYEVENTS.spec_type_desc, OUTPUTEVENTS.itemid | CHARTEVENTS.itemid, LABEVENTS.itemid, PROCEDUREEVENTS_MV.itemid | 0.67 | 0.25 | 0.36 | 2 | 1 | 6 |
| measurement | person_id | CHARTEVENTS.subject_id, LABEVENTS.subject_id, MICROBIOLOGYEVENTS.subject_id, OUTPUTEVENTS.subject_id | CHARTEVENTS.subject_id, DIAGNOSES_ICD.subject_id, LABEVENTS.subject_id, PROCEDUREEVENTS_MV.subject_id | 0.50 | 0.50 | 0.50 | 2 | 2 | 2 |
| measurement | unit_source_value | CHARTEVENTS.valueuom, LABEVENTS.valueuom, OUTPUTEVENTS.valueuom | CHARTEVENTS.valueuom, LABEVENTS.valueuom, PROCEDUREEVENTS_MV.valueuom | 0.67 | 0.67 | 0.67 | 2 | 1 | 1 |
| measurement | value_as_number | CHARTEVENTS.valuenum, LABEVENTS.valuenum, MICROBIOLOGYEVENTS.dilution_text, OUTPUTEVENTS.value | CHARTEVENTS.valuenum, LABEVENTS.valuenum, PROCEDUREEVENTS_MV.value | 0.67 | 0.50 | 0.57 | 2 | 1 | 2 |
| measurement | value_source_value | CHARTEVENTS.value, LABEVENTS.value, MICROBIOLOGYEVENTS.dilution_text, OUTPUTEVENTS.value | CHARTEVENTS.value, LABEVENTS.value, PROCEDUREEVENTS_MV.value | 0.67 | 0.50 | 0.57 | 2 | 1 | 2 |
| measurement | visit_occurrence_id | CHARTEVENTS.hadm_id, LABEVENTS.hadm_id, MICROBIOLOGYEVENTS.hadm_id, OUTPUTEVENTS.hadm_id | CHARTEVENTS.hadm_id, DIAGNOSES_ICD.hadm_id, LABEVENTS.hadm_id, PROCEDUREEVENTS_MV.hadm_id | 0.50 | 0.50 | 0.50 | 2 | 2 | 2 |
| observation | observation_date | ADMISSIONS.dischtime, DATETIMEEVENTS.charttime | CHARTEVENTS.charttime, CPTEVENTS.chartdate, DATETIMEEVENTS.charttime, INPUTEVENTS_CV.charttime, INPUTEVENTS_MV.starttime, PROCEDUREEVENTS_MV.starttime | 0.17 | 0.50 | 0.25 | 1 | 5 | 1 |
| observation | observation_datetime | CHARTEVENTS.charttime, DATETIMEEVENTS.charttime | CHARTEVENTS.charttime, CPTEVENTS.chartdate, DATETIMEEVENTS.charttime, INPUTEVENTS_CV.charttime, INPUTEVENTS_MV.starttime, PROCEDUREEVENTS_MV.starttime | 0.33 | 1.00 | 0.50 | 2 | 4 | 0 |
| observation | observation_id | ADMISSIONS.hadm_id, CHARTEVENTS.row_id, DATETIMEEVENTS.row_id, DRGCODES.row_id | CHARTEVENTS.row_id, CPTEVENTS.row_id, DATETIMEEVENTS.row_id, INPUTEVENTS_CV.row_id, INPUTEVENTS_MV.row_id, PROCEDUREEVENTS_MV.row_id, PROCEDURES_ICD.row_id | 0.29 | 0.50 | 0.36 | 2 | 5 | 2 |
| observation | observation_source_value | ADMISSIONS.insurance, ADMISSIONS.language, ADMISSIONS.marital_status, ADMISSIONS.religion, CHARTEVENTS.itemid, DATETIMEEVENTS.itemid, DRGCODES.description, DRGCODES.drg_code, D_ITEMS.label | CHARTEVENTS.itemid, CPTEVENTS.cpt_cd, DATETIMEEVENTS.itemid, DIAGNOSES_ICD.icd9_code, INPUTEVENTS_CV.itemid, INPUTEVENTS_MV.itemid, PROCEDUREEVENTS_MV.itemid, PROCEDURES_ICD.icd9_code | 0.25 | 0.22 | 0.24 | 2 | 6 | 7 |
| observation | person_id | CHARTEVENTS.subject_id, DATETIMEEVENTS.subject_id, DRGCODES.subject_id | CHARTEVENTS.subject_id, CPTEVENTS.subject_id, DATETIMEEVENTS.subject_id, DIAGNOSES_ICD.subject_id, INPUTEVENTS_CV.subject_id, INPUTEVENTS_MV.subject_id, PROCEDUREEVENTS_MV.subject_id, PROCEDURES_ICD.subject_id | 0.25 | 0.67 | 0.36 | 2 | 6 | 1 |
| observation | value_as_number | CHARTEVENTS.valuenum | CHARTEVENTS.valuenum, INPUTEVENTS_CV.amount, INPUTEVENTS_MV.amount, PROCEDUREEVENTS_MV.value | 0.25 | 1.00 | 0.40 | 1 | 3 | 0 |
| observation | value_as_string | CHARTEVENTS.value, DATETIMEEVENTS.value | CHARTEVENTS.value, CPTEVENTS.description, DATETIMEEVENTS.value, INPUTEVENTS_CV.stopped, INPUTEVENTS_MV.ordercategorydescription, PROCEDUREEVENTS_MV.ordercategoryname | 0.33 | 1.00 | 0.50 | 2 | 4 | 0 |
| observation | value_source_value | DATETIMEEVENTS.value | CHARTEVENTS.value, CPTEVENTS.description, DATETIMEEVENTS.value, INPUTEVENTS_CV.itemid, INPUTEVENTS_MV.ordercategoryname, PROCEDUREEVENTS_MV.value, PROCEDURES_ICD.icd9_code | 0.14 | 1.00 | 0.25 | 1 | 6 | 0 |
| observation | visit_occurrence_id | CHARTEVENTS.hadm_id, DATETIMEEVENTS.hadm_id, DRGCODES.hadm_id | CHARTEVENTS.hadm_id, CPTEVENTS.hadm_id, DATETIMEEVENTS.hadm_id, DIAGNOSES_ICD.hadm_id, INPUTEVENTS_CV.hadm_id, INPUTEVENTS_MV.hadm_id, PROCEDUREEVENTS_MV.hadm_id, PROCEDURES_ICD.hadm_id | 0.25 | 0.67 | 0.36 | 2 | 6 | 1 |
| observation_period | observation_period_end_date | ADMISSIONS.dischtime | ADMISSIONS.dischtime | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| observation_period | observation_period_start_date | ADMISSIONS.admittime | ADMISSIONS.admittime | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| observation_period | person_id | ADMISSIONS.subject_id | PATIENTS.subject_id | 0.00 | 0.00 | 0.00 | 0 | 1 | 1 |
| person | birth_datetime | PATIENTS.dob | PATIENTS.dob | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | day_of_birth | PATIENTS.dob | PATIENTS.dob | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | ethnicity_source_value | ADMISSIONS.ethnicity | ADMISSIONS.ethnicity | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | gender_source_value | PATIENTS.gender | PATIENTS.gender | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | month_of_birth | PATIENTS.dob | PATIENTS.dob | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | person_id | PATIENTS.subject_id | PATIENTS.subject_id | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | person_source_value | PATIENTS.subject_id | PATIENTS.subject_id | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | race_source_value | ADMISSIONS.ethnicity | ADMISSIONS.ethnicity | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | year_of_birth | PATIENTS.dob | PATIENTS.dob | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| procedure_occurrence | modifier_source_value | CPTEVENTS.cpt_suffix | CPTEVENTS.cpt_suffix | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| procedure_occurrence | person_id | CPTEVENTS.subject_id, PROCEDUREEVENTS_MV.subject_id, PROCEDURES_ICD.subject_id | CHARTEVENTS.subject_id, CPTEVENTS.subject_id, DIAGNOSES_ICD.subject_id, PROCEDUREEVENTS_MV.subject_id, PROCEDURES_ICD.subject_id | 0.60 | 1.00 | 0.75 | 3 | 2 | 0 |
| procedure_occurrence | procedure_date | ADMISSIONS.admittime, CPTEVENTS.chartdate, PROCEDUREEVENTS_MV.starttime | CHARTEVENTS.charttime, CPTEVENTS.chartdate, PROCEDUREEVENTS_MV.starttime | 0.67 | 0.67 | 0.67 | 2 | 1 | 1 |
| procedure_occurrence | procedure_datetime | CPTEVENTS.chartdate, PROCEDUREEVENTS_MV.starttime | CHARTEVENTS.charttime, CPTEVENTS.chartdate, PROCEDUREEVENTS_MV.starttime | 0.67 | 1.00 | 0.80 | 2 | 1 | 0 |
| procedure_occurrence | procedure_end_datetime | PROCEDUREEVENTS_MV.endtime | PROCEDUREEVENTS_MV.endtime | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| procedure_occurrence | procedure_occurrence_id | CPTEVENTS.row_id, PROCEDUREEVENTS_MV.row_id, PROCEDURES_ICD.row_id | CHARTEVENTS.row_id, CPTEVENTS.row_id, DIAGNOSES_ICD.row_id, PROCEDUREEVENTS_MV.row_id, PROCEDURES_ICD.row_id | 0.60 | 1.00 | 0.75 | 3 | 2 | 0 |
| procedure_occurrence | procedure_source_value | CPTEVENTS.cpt_cd, D_ITEMS.label, PROCEDUREEVENTS_MV.itemid, PROCEDURES_ICD.icd9_code | CHARTEVENTS.itemid, CPTEVENTS.cpt_cd, DIAGNOSES_ICD.icd9_code, PROCEDUREEVENTS_MV.itemid, PROCEDURES_ICD.icd9_code | 0.60 | 0.75 | 0.67 | 3 | 2 | 1 |
| procedure_occurrence | visit_occurrence_id | CPTEVENTS.hadm_id, PROCEDUREEVENTS_MV.hadm_id, PROCEDURES_ICD.hadm_id | CHARTEVENTS.hadm_id, CPTEVENTS.hadm_id, DIAGNOSES_ICD.hadm_id, PROCEDUREEVENTS_MV.hadm_id, PROCEDURES_ICD.hadm_id | 0.60 | 1.00 | 0.75 | 3 | 2 | 0 |
| visit_occurrence | admitted_from_source_value | ADMISSIONS.admission_location | ADMISSIONS.admission_location | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | discharged_to_source_value | ADMISSIONS.discharge_location | ADMISSIONS.discharge_location | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | person_id | ADMISSIONS.subject_id | ADMISSIONS.subject_id | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_end_date | ADMISSIONS.dischtime | ADMISSIONS.dischtime | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_end_datetime | ADMISSIONS.dischtime | ADMISSIONS.dischtime | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_occurrence_id | ADMISSIONS.hadm_id | ADMISSIONS.hadm_id | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_source_value | ADMISSIONS.admission_type | ADMISSIONS.admission_type | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_start_date | ADMISSIONS.admittime | ADMISSIONS.admittime | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_start_datetime | ADMISSIONS.admittime | ADMISSIONS.admittime | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |

### Agent fields not in gold (informational)

| Table | Field | Agent sources |
|-------|-------|---------------|
| condition_occurrence | condition_end_date | PROCEDUREEVENTS_MV.endtime |
| condition_occurrence | condition_end_datetime | PROCEDUREEVENTS_MV.endtime |
| condition_occurrence | condition_start_datetime | CHARTEVENTS.charttime, PROCEDUREEVENTS_MV.starttime |
| condition_occurrence | condition_status_source_value | CHARTEVENTS.stopped, PROCEDUREEVENTS_MV.statusdescription |
| condition_occurrence | visit_detail_id | CHARTEVENTS.icustay_id, DIAGNOSES_ICD.hadm_id, PROCEDUREEVENTS_MV.icustay_id |
| drug_exposure | sig | INPUTEVENTS_CV.originalroute |
| drug_exposure | stop_reason | CHARTEVENTS.stopped, INPUTEVENTS_CV.stopped, INPUTEVENTS_MV.cancelreason |
| drug_exposure | verbatim_end_date | INPUTEVENTS_MV.endtime, PRESCRIPTIONS.enddate |
| drug_exposure | visit_detail_id | CHARTEVENTS.icustay_id, INPUTEVENTS_CV.icustay_id, INPUTEVENTS_MV.icustay_id, PRESCRIPTIONS.icustay_id |
| measurement | measurement_event_id | PROCEDUREEVENTS_MV.orderid |
| measurement | measurement_time | CHARTEVENTS.charttime, LABEVENTS.charttime, PROCEDUREEVENTS_MV.starttime |
| measurement | visit_detail_id | CHARTEVENTS.icustay_id, PROCEDUREEVENTS_MV.icustay_id |
| observation | observation_event_id | CHARTEVENTS.hadm_id, CPTEVENTS.row_id, DATETIMEEVENTS.hadm_id, INPUTEVENTS_CV.orderid, INPUTEVENTS_MV.orderid, PROCEDUREEVENTS_MV.orderid |
| observation | qualifier_source_value | CHARTEVENTS.resultstatus, CPTEVENTS.cpt_suffix, INPUTEVENTS_CV.originalroute, INPUTEVENTS_MV.ordercategorydescription, PROCEDUREEVENTS_MV.location |
| observation | unit_source_value | CHARTEVENTS.valueuom, DATETIMEEVENTS.valueuom, INPUTEVENTS_CV.amountuom, INPUTEVENTS_MV.amountuom, PROCEDUREEVENTS_MV.valueuom |
| observation | visit_detail_id | CHARTEVENTS.icustay_id, DATETIMEEVENTS.icustay_id, INPUTEVENTS_CV.icustay_id, INPUTEVENTS_MV.icustay_id, PROCEDUREEVENTS_MV.icustay_id, PROCEDURES_ICD.hadm_id |
| observation_period | observation_period_id | ADMISSIONS.row_id |
| procedure_occurrence | procedure_end_date | PROCEDUREEVENTS_MV.endtime |
| procedure_occurrence | quantity | PROCEDUREEVENTS_MV.value |
| procedure_occurrence | visit_detail_id | CHARTEVENTS.icustay_id, DIAGNOSES_ICD.hadm_id, PROCEDUREEVENTS_MV.icustay_id |

## Notes

- Only **structural MAP** pairs are scored (source_table + source_field).
- `*_concept_id` / `*_source_concept_id` / `*_type_concept_id` are excluded (semantic or fixed).
- TP = agent source ∈ gold sources for that field.
- FP = agent proposed a source not in gold (over-mapping).
- FN = gold source missing from agent (under-mapping).
