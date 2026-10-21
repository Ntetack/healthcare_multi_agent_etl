# Structural Mapping Evaluation Report

## Summary (MAP only)

| Metric | Value |
|--------|-------|
| Gold fields (unique table.field) | 60 |
| Gold MAP rows (sources) | 158 |
| TP | 94 |
| FP (over-mapping) | 74 |
| FN (under-mapping) | 64 |
| **Micro Precision** | **0.5595** |
| **Micro Recall** | **0.5949** |
| **Micro F1** | **0.5767** |
| Macro Precision | 0.6194 |
| Macro Recall | 0.6405 |
| Macro F1 | 0.6086 |
| Over-mapping rate | 0.4405 |
| Under-mapping rate | 0.4051 |

### Per-field details

| Table | Field | Gold sources | Agent sources | P | R | F1 | TP | FP | FN |
|-------|-------|--------------|---------------|---|---|----|----|----|----|
| condition_occurrence | condition_end_date | ADMISSIONS.dischtime | PROCEDUREEVENTS_MV.endtime | 0.00 | 0.00 | 0.00 | 0 | 1 | 1 |
| condition_occurrence | condition_end_datetime | ADMISSIONS.dischtime | PROCEDUREEVENTS_MV.endtime | 0.00 | 0.00 | 0.00 | 0 | 1 | 1 |
| condition_occurrence | condition_source_value | ADMISSIONS.diagnosis, DIAGNOSES_ICD.icd9_code | CHARTEVENTS.itemid, DIAGNOSES_ICD.icd9_code, PROCEDUREEVENTS_MV.itemid | 0.33 | 0.50 | 0.40 | 1 | 2 | 1 |
| condition_occurrence | condition_start_date | ADMISSIONS.admittime, ADMISSIONS.edregtime | CHARTEVENTS.charttime, PROCEDUREEVENTS_MV.starttime | 0.00 | 0.00 | 0.00 | 0 | 2 | 2 |
| condition_occurrence | condition_start_datetime | ADMISSIONS.admittime, ADMISSIONS.edregtime | CHARTEVENTS.charttime, PROCEDUREEVENTS_MV.starttime | 0.00 | 0.00 | 0.00 | 0 | 2 | 2 |
| condition_occurrence | person_id | ADMISSIONS.subject_id, DIAGNOSES_ICD.subject_id | CHARTEVENTS.subject_id, DIAGNOSES_ICD.subject_id, PROCEDUREEVENTS_MV.subject_id | 0.33 | 0.50 | 0.40 | 1 | 2 | 1 |
| condition_occurrence | visit_occurrence_id | ADMISSIONS.hadm_id, DIAGNOSES_ICD.hadm_id | CHARTEVENTS.hadm_id, DIAGNOSES_ICD.hadm_id, PROCEDUREEVENTS_MV.hadm_id | 0.33 | 0.50 | 0.40 | 1 | 2 | 1 |
| death | death_date | ADMISSIONS.deathtime, PATIENTS.dod_ssn | PATIENTS.dod | 0.00 | 0.00 | 0.00 | 0 | 1 | 2 |
| death | death_datetime | ADMISSIONS.deathtime, PATIENTS.dod_ssn | ADMISSIONS.deathtime | 1.00 | 0.50 | 0.67 | 1 | 0 | 1 |
| death | person_id | ADMISSIONS.subject_id, PATIENTS.subject_id | PATIENTS.subject_id | 1.00 | 0.50 | 0.67 | 1 | 0 | 1 |
| drug_exposure | dose_unit_source_value | INPUTEVENTS_CV.amountuom, INPUTEVENTS_CV.rateuom, INPUTEVENTS_MV.amountuom, INPUTEVENTS_MV.rateuom, PRESCRIPTIONS.form_unit_disp | CHARTEVENTS.valueuom, INPUTEVENTS_CV.amountuom, INPUTEVENTS_MV.amountuom, PRESCRIPTIONS.dose_unit_rx | 0.50 | 0.40 | 0.44 | 2 | 2 | 3 |
| drug_exposure | drug_exposure_end_date | INPUTEVENTS_CV.charttime, INPUTEVENTS_MV.endtime, PRESCRIPTIONS.enddate | INPUTEVENTS_MV.endtime, PRESCRIPTIONS.enddate | 1.00 | 0.67 | 0.80 | 2 | 0 | 1 |
| drug_exposure | drug_exposure_end_datetime | INPUTEVENTS_CV.charttime, INPUTEVENTS_MV.endtime, PRESCRIPTIONS.enddate | INPUTEVENTS_MV.endtime, PRESCRIPTIONS.enddate | 1.00 | 0.67 | 0.80 | 2 | 0 | 1 |
| drug_exposure | drug_exposure_start_date | INPUTEVENTS_CV.charttime, INPUTEVENTS_MV.starttime, PRESCRIPTIONS.startdate | CHARTEVENTS.charttime, INPUTEVENTS_CV.charttime, INPUTEVENTS_MV.starttime, PRESCRIPTIONS.startdate | 0.75 | 1.00 | 0.86 | 3 | 1 | 0 |
| drug_exposure | drug_exposure_start_datetime | INPUTEVENTS_CV.charttime, INPUTEVENTS_MV.starttime, PRESCRIPTIONS.startdate | CHARTEVENTS.charttime, INPUTEVENTS_CV.charttime, INPUTEVENTS_MV.starttime, PRESCRIPTIONS.startdate | 0.75 | 1.00 | 0.86 | 3 | 1 | 0 |
| drug_exposure | drug_source_value | D_ITEMS.label, PRESCRIPTIONS.ndc | CHARTEVENTS.itemid, INPUTEVENTS_CV.itemid, INPUTEVENTS_MV.itemid, PRESCRIPTIONS.ndc | 0.25 | 0.50 | 0.33 | 1 | 3 | 1 |
| drug_exposure | person_id | INPUTEVENTS_CV.subject_id, INPUTEVENTS_MV.subject_id, PRESCRIPTIONS.subject_id | CHARTEVENTS.subject_id, INPUTEVENTS_CV.subject_id, INPUTEVENTS_MV.subject_id, PRESCRIPTIONS.subject_id | 0.75 | 1.00 | 0.86 | 3 | 1 | 0 |
| drug_exposure | quantity | INPUTEVENTS_CV.amount, INPUTEVENTS_CV.rate, INPUTEVENTS_MV.amount, INPUTEVENTS_MV.rate, PRESCRIPTIONS.form_val_disp | INPUTEVENTS_CV.amount, INPUTEVENTS_MV.amount, PRESCRIPTIONS.form_val_disp | 1.00 | 0.60 | 0.75 | 3 | 0 | 2 |
| drug_exposure | route_source_value | INPUTEVENTS_MV.ordercategorydescription, INPUTEVENTS_MV.ordercategoryname, PRESCRIPTIONS.route | INPUTEVENTS_CV.originalroute, INPUTEVENTS_MV.ordercategorydescription, PRESCRIPTIONS.route | 0.67 | 0.67 | 0.67 | 2 | 1 | 1 |
| drug_exposure | stop_reason | INPUTEVENTS_CV.stopped, INPUTEVENTS_MV.statusdescription | CHARTEVENTS.stopped, INPUTEVENTS_CV.stopped, INPUTEVENTS_MV.cancelreason | 0.33 | 0.50 | 0.40 | 1 | 2 | 1 |
| drug_exposure | visit_occurrence_id | INPUTEVENTS_CV.hadm_id, INPUTEVENTS_MV.hadm_id, PRESCRIPTIONS.hadm_id | CHARTEVENTS.hadm_id, INPUTEVENTS_CV.hadm_id, INPUTEVENTS_MV.hadm_id, PRESCRIPTIONS.hadm_id | 0.75 | 1.00 | 0.86 | 3 | 1 | 0 |
| measurement | measurement_date | CHARTEVENTS.charttime, CHARTEVENTS.storetime, INPUTEVENTS_MV.starttime, LABEVENTS.charttime, MICROBIOLOGYEVENTS.chartdate, MICROBIOLOGYEVENTS.charttime, OUTPUTEVENTS.charttime | CHARTEVENTS.charttime, LABEVENTS.charttime, MICROBIOLOGYEVENTS.chartdate, OUTPUTEVENTS.charttime, PROCEDUREEVENTS_MV.starttime | 0.80 | 0.57 | 0.67 | 4 | 1 | 3 |
| measurement | measurement_datetime | CHARTEVENTS.charttime, CHARTEVENTS.storetime, INPUTEVENTS_MV.starttime, LABEVENTS.charttime, MICROBIOLOGYEVENTS.charttime, OUTPUTEVENTS.charttime | CHARTEVENTS.charttime, LABEVENTS.charttime, MICROBIOLOGYEVENTS.charttime, OUTPUTEVENTS.charttime, PROCEDUREEVENTS_MV.starttime | 0.80 | 0.67 | 0.73 | 4 | 1 | 2 |
| measurement | measurement_source_value | CHARTEVENTS.itemid, D_ITEMS.label, LABEVENTS.itemid, MICROBIOLOGYEVENTS.ab_name, MICROBIOLOGYEVENTS.spec_type_desc | CHARTEVENTS.itemid, DIAGNOSES_ICD.icd9_code, LABEVENTS.itemid, MICROBIOLOGYEVENTS.ab_itemid, OUTPUTEVENTS.itemid, PROCEDUREEVENTS_MV.itemid | 0.33 | 0.40 | 0.36 | 2 | 4 | 3 |
| measurement | person_id | CHARTEVENTS.subject_id, INPUTEVENTS_MV.subject_id, LABEVENTS.subject_id, MICROBIOLOGYEVENTS.subject_id, OUTPUTEVENTS.subject_id | CHARTEVENTS.subject_id, DIAGNOSES_ICD.subject_id, LABEVENTS.subject_id, MICROBIOLOGYEVENTS.subject_id, OUTPUTEVENTS.subject_id, PROCEDUREEVENTS_MV.subject_id | 0.67 | 0.80 | 0.73 | 4 | 2 | 1 |
| measurement | unit_source_value | CHARTEVENTS.valueuom, LABEVENTS.valueuom, OUTPUTEVENTS.valueuom | CHARTEVENTS.valueuom, LABEVENTS.valueuom, OUTPUTEVENTS.valueuom, PROCEDUREEVENTS_MV.valueuom | 0.75 | 1.00 | 0.86 | 3 | 1 | 0 |
| measurement | value_as_number | CHARTEVENTS.value, CHARTEVENTS.valuenum, INPUTEVENTS_MV.patientweight, LABEVENTS.value, MICROBIOLOGYEVENTS.dilution_text, OUTPUTEVENTS.value | CHARTEVENTS.valuenum, LABEVENTS.valuenum, MICROBIOLOGYEVENTS.dilution_value, OUTPUTEVENTS.value, PROCEDUREEVENTS_MV.value | 0.40 | 0.33 | 0.36 | 2 | 3 | 4 |
| measurement | value_source_value | CHARTEVENTS.value, LABEVENTS.value, MICROBIOLOGYEVENTS.dilution_text, MICROBIOLOGYEVENTS.org_name | CHARTEVENTS.value, LABEVENTS.value, MICROBIOLOGYEVENTS.dilution_text, OUTPUTEVENTS.value, PROCEDUREEVENTS_MV.value | 0.60 | 0.75 | 0.67 | 3 | 2 | 1 |
| measurement | visit_occurrence_id | CHARTEVENTS.hadm_id, INPUTEVENTS_MV.hadm_id, LABEVENTS.hadm_id, MICROBIOLOGYEVENTS.hadm_id, OUTPUTEVENTS.hadm_id | CHARTEVENTS.hadm_id, DIAGNOSES_ICD.hadm_id, LABEVENTS.hadm_id, MICROBIOLOGYEVENTS.hadm_id, OUTPUTEVENTS.hadm_id, PROCEDUREEVENTS_MV.hadm_id | 0.67 | 0.80 | 0.73 | 4 | 2 | 1 |
| observation | observation_date | ADMISSIONS.admittime, ADMISSIONS.edregtime, CHARTEVENTS.charttime, DATETIMEEVENTS.charttime, DATETIMEEVENTS.value | CHARTEVENTS.charttime, CPTEVENTS.chartdate, DATETIMEEVENTS.charttime, PROCEDUREEVENTS_MV.starttime | 0.50 | 0.40 | 0.44 | 2 | 2 | 3 |
| observation | observation_datetime | ADMISSIONS.admittime, ADMISSIONS.edregtime, CHARTEVENTS.charttime, DATETIMEEVENTS.charttime, DATETIMEEVENTS.value | CHARTEVENTS.charttime, CPTEVENTS.chartdate, DATETIMEEVENTS.charttime, PROCEDUREEVENTS_MV.starttime | 0.50 | 0.40 | 0.44 | 2 | 2 | 3 |
| observation | observation_source_value | CHARTEVENTS.itemid | CHARTEVENTS.itemid, CPTEVENTS.cpt_cd, DATETIMEEVENTS.itemid, DIAGNOSES_ICD.icd9_code, PROCEDUREEVENTS_MV.itemid, PROCEDURES_ICD.icd9_code | 0.17 | 1.00 | 0.29 | 1 | 5 | 0 |
| observation | person_id | ADMISSIONS.subject_id, CHARTEVENTS.subject_id, DATETIMEEVENTS.subject_id, DRGCODES.subject_id | CHARTEVENTS.subject_id, CPTEVENTS.subject_id, DATETIMEEVENTS.subject_id, DIAGNOSES_ICD.subject_id, PROCEDUREEVENTS_MV.subject_id, PROCEDURES_ICD.subject_id | 0.33 | 0.50 | 0.40 | 2 | 4 | 2 |
| observation | value_as_number | CHARTEVENTS.valuenum | CHARTEVENTS.valuenum, PROCEDUREEVENTS_MV.value | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| observation | value_as_string | ADMISSIONS.ethnicity, ADMISSIONS.insurance, ADMISSIONS.language, ADMISSIONS.marital_status, ADMISSIONS.religion, CHARTEVENTS.value, DRGCODES.description | CHARTEVENTS.value, DATETIMEEVENTS.value, PROCEDUREEVENTS_MV.location | 0.33 | 0.14 | 0.20 | 1 | 2 | 6 |
| observation | visit_occurrence_id | ADMISSIONS.hadm_id, CHARTEVENTS.hadm_id, DATETIMEEVENTS.hadm_id, DRGCODES.hadm_id | CHARTEVENTS.hadm_id, CPTEVENTS.hadm_id, DATETIMEEVENTS.hadm_id, DIAGNOSES_ICD.hadm_id, PROCEDUREEVENTS_MV.hadm_id, PROCEDURES_ICD.hadm_id | 0.33 | 0.50 | 0.40 | 2 | 4 | 2 |
| observation_period | observation_period_end_date | ADMISSIONS.dischtime | PATIENTS.dod | 0.00 | 0.00 | 0.00 | 0 | 1 | 1 |
| observation_period | observation_period_start_date | ADMISSIONS.admittime, ADMISSIONS.edregtime | PATIENTS.dob | 0.00 | 0.00 | 0.00 | 0 | 1 | 2 |
| observation_period | person_id | ADMISSIONS.subject_id | PATIENTS.subject_id | 0.00 | 0.00 | 0.00 | 0 | 1 | 1 |
| person | birth_datetime | PATIENTS.dob | PATIENTS.dob | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | day_of_birth | PATIENTS.dob | PATIENTS.dob | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | gender_source_value | PATIENTS.gender | PATIENTS.gender | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | month_of_birth | PATIENTS.dob | PATIENTS.dob | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | person_source_value | PATIENTS.subject_id | PATIENTS.subject_id | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | race_source_value | ADMISSIONS.ethnicity | ADMISSIONS.ethnicity | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | year_of_birth | PATIENTS.dob | PATIENTS.dob | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| procedure_occurrence | person_id | CPTEVENTS.subject_id, PROCEDUREEVENTS_MV.subject_id, PROCEDURES_ICD.subject_id | CHARTEVENTS.subject_id, CPTEVENTS.subject_id, DIAGNOSES_ICD.subject_id, PROCEDUREEVENTS_MV.subject_id, PROCEDURES_ICD.subject_id | 0.60 | 1.00 | 0.75 | 3 | 2 | 0 |
| procedure_occurrence | procedure_date | ADMISSIONS.dischtime, CPTEVENTS.chartdate, PROCEDUREEVENTS_MV.starttime | CHARTEVENTS.charttime, CPTEVENTS.chartdate, PROCEDUREEVENTS_MV.starttime | 0.67 | 0.67 | 0.67 | 2 | 1 | 1 |
| procedure_occurrence | procedure_datetime | ADMISSIONS.dischtime, CPTEVENTS.chartdate, PROCEDUREEVENTS_MV.starttime | CHARTEVENTS.charttime, CPTEVENTS.chartdate, PROCEDUREEVENTS_MV.starttime | 0.67 | 0.67 | 0.67 | 2 | 1 | 1 |
| procedure_occurrence | procedure_source_value | CPTEVENTS.subsectionheader, D_ITEMS.label, PROCEDURES_ICD.icd9_code | CHARTEVENTS.itemid, CPTEVENTS.cpt_cd, DIAGNOSES_ICD.icd9_code, PROCEDUREEVENTS_MV.itemid, PROCEDURES_ICD.icd9_code | 0.20 | 0.33 | 0.25 | 1 | 4 | 2 |
| procedure_occurrence | quantity | PROCEDUREEVENTS_MV.value | PROCEDUREEVENTS_MV.value | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| procedure_occurrence | visit_occurrence_id | CPTEVENTS.hadm_id, PROCEDUREEVENTS_MV.hadm_id, PROCEDURES_ICD.hadm_id | CHARTEVENTS.hadm_id, CPTEVENTS.hadm_id, DIAGNOSES_ICD.hadm_id, PROCEDUREEVENTS_MV.hadm_id, PROCEDURES_ICD.hadm_id | 0.60 | 1.00 | 0.75 | 3 | 2 | 0 |
| visit_occurrence | admitted_from_source_value | ADMISSIONS.admission_location | ADMISSIONS.admission_location | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | discharged_to_source_value | ADMISSIONS.discharge_location | ADMISSIONS.discharge_location | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | person_id | ADMISSIONS.subject_id | ADMISSIONS.subject_id | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_end_date | ADMISSIONS.dischtime | ADMISSIONS.dischtime | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_end_datetime | ADMISSIONS.dischtime | ADMISSIONS.dischtime | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_source_value | ADMISSIONS.admission_type | ADMISSIONS.admission_type | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_start_date | ADMISSIONS.admittime, ADMISSIONS.edregtime | ADMISSIONS.admittime | 1.00 | 0.50 | 0.67 | 1 | 0 | 1 |
| visit_occurrence | visit_start_datetime | ADMISSIONS.admittime, ADMISSIONS.edregtime | ADMISSIONS.admittime | 1.00 | 0.50 | 0.67 | 1 | 0 | 1 |

### Agent fields not in gold (informational)

| Table | Field | Agent sources |
|-------|-------|---------------|
| condition_occurrence | condition_occurrence_id | CHARTEVENTS.row_id, DIAGNOSES_ICD.row_id, PROCEDUREEVENTS_MV.row_id |
| condition_occurrence | condition_status_source_value | CHARTEVENTS.resultstatus, PROCEDUREEVENTS_MV.statusdescription |
| condition_occurrence | stop_reason | CHARTEVENTS.stopped |
| condition_occurrence | visit_detail_id | CHARTEVENTS.icustay_id, PROCEDUREEVENTS_MV.icustay_id |
| drug_exposure | drug_exposure_id | CHARTEVENTS.row_id, INPUTEVENTS_CV.row_id, INPUTEVENTS_MV.row_id, PRESCRIPTIONS.row_id |
| drug_exposure | verbatim_end_date | INPUTEVENTS_MV.endtime, PRESCRIPTIONS.enddate |
| drug_exposure | visit_detail_id | CHARTEVENTS.icustay_id, INPUTEVENTS_CV.icustay_id, INPUTEVENTS_MV.icustay_id, PRESCRIPTIONS.icustay_id |
| measurement | measurement_event_id | CHARTEVENTS.row_id, DIAGNOSES_ICD.row_id, LABEVENTS.row_id, MICROBIOLOGYEVENTS.row_id, PROCEDUREEVENTS_MV.orderid |
| measurement | measurement_id | CHARTEVENTS.row_id, DIAGNOSES_ICD.row_id, LABEVENTS.row_id, MICROBIOLOGYEVENTS.row_id, OUTPUTEVENTS.row_id, PROCEDUREEVENTS_MV.row_id |
| measurement | measurement_time | CHARTEVENTS.charttime, LABEVENTS.charttime, MICROBIOLOGYEVENTS.charttime, OUTPUTEVENTS.charttime, PROCEDUREEVENTS_MV.starttime |
| measurement | visit_detail_id | CHARTEVENTS.icustay_id, DIAGNOSES_ICD.hadm_id, MICROBIOLOGYEVENTS.hadm_id, OUTPUTEVENTS.icustay_id, PROCEDUREEVENTS_MV.icustay_id |
| observation | observation_event_id | CHARTEVENTS.row_id, CPTEVENTS.ticket_id_seq, DATETIMEEVENTS.hadm_id, PROCEDUREEVENTS_MV.orderid |
| observation | observation_id | CHARTEVENTS.row_id, CPTEVENTS.row_id, DATETIMEEVENTS.row_id, DIAGNOSES_ICD.row_id, PROCEDUREEVENTS_MV.row_id, PROCEDURES_ICD.row_id |
| observation | qualifier_source_value | CHARTEVENTS.warning, CPTEVENTS.subsectionheader, PROCEDUREEVENTS_MV.location |
| observation | unit_source_value | CHARTEVENTS.valueuom, DATETIMEEVENTS.valueuom, PROCEDUREEVENTS_MV.valueuom |
| observation | value_source_value | CHARTEVENTS.value, CPTEVENTS.description, DATETIMEEVENTS.value, DIAGNOSES_ICD.icd9_code, PROCEDUREEVENTS_MV.value |
| observation | visit_detail_id | CHARTEVENTS.icustay_id, CPTEVENTS.hadm_id, DATETIMEEVENTS.icustay_id, DIAGNOSES_ICD.hadm_id, PROCEDUREEVENTS_MV.icustay_id, PROCEDURES_ICD.hadm_id |
| observation_period | observation_period_id | ADMISSIONS.hadm_id |
| person | ethnicity_source_value | ADMISSIONS.ethnicity |
| person | person_id | PATIENTS.subject_id |
| procedure_occurrence | modifier_source_value | CPTEVENTS.cpt_suffix |
| procedure_occurrence | procedure_end_date | PROCEDUREEVENTS_MV.endtime |
| procedure_occurrence | procedure_end_datetime | PROCEDUREEVENTS_MV.endtime |
| procedure_occurrence | procedure_occurrence_id | CHARTEVENTS.row_id, CPTEVENTS.row_id, DIAGNOSES_ICD.row_id, PROCEDUREEVENTS_MV.row_id, PROCEDURES_ICD.row_id |
| procedure_occurrence | visit_detail_id | CHARTEVENTS.icustay_id, CPTEVENTS.hadm_id, PROCEDUREEVENTS_MV.icustay_id |
| visit_occurrence | visit_occurrence_id | ADMISSIONS.hadm_id |

## Notes

- Only **structural MAP** pairs are scored (source_table + source_field).
- `*_concept_id` / `*_source_concept_id` / `*_type_concept_id` are excluded (semantic or fixed).
- TP = agent source ∈ gold sources for that field.
- FP = agent proposed a source not in gold (over-mapping).
- FN = gold source missing from agent (under-mapping).
