# Rapport de provenance — RUN-mimic4-892094c7

## 1. Provenance au niveau des lignes (tables OMOP finales)

**condition_occurrence** — 1743 lignes au total
  - DIAGNOSES_ICD: 1599 lignes (92%)
  - CHARTEVENTS: 137 lignes (8%)
  - PROCEDUREEVENTS_MV: 7 lignes (0%)

**drug_exposure** — 30997 lignes au total
  - INPUTEVENTS_CV: 12359 lignes (40%)
  - PRESCRIPTIONS: 8828 lignes (28%)
  - CHARTEVENTS: 5716 lignes (18%)
  - INPUTEVENTS_MV: 4094 lignes (13%)

**measurement** — 129018 lignes au total
  - LABEVENTS: 72984 lignes (57%)
  - CHARTEVENTS: 43844 lignes (34%)
  - OUTPUTEVENTS: 11320 lignes (9%)
  - MICROBIOLOGYEVENTS: 821 lignes (1%)
  - PROCEDUREEVENTS_MV: 44 lignes (0%)
  - DIAGNOSES_ICD: 5 lignes (0%)

**observation** — 80151 lignes au total
  - CHARTEVENTS: 64324 lignes (80%)
  - DATETIMEEVENTS: 15551 lignes (19%)
  - DIAGNOSES_ICD: 155 lignes (0%)
  - CPTEVENTS: 82 lignes (0%)
  - PROCEDUREEVENTS_MV: 36 lignes (0%)
  - PROCEDURES_ICD: 3 lignes (0%)

**procedure_occurrence** — 5099 lignes au total
  - CHARTEVENTS: 2932 lignes (58%)
  - CPTEVENTS: 1497 lignes (29%)
  - PROCEDURES_ICD: 503 lignes (10%)
  - PROCEDUREEVENTS_MV: 165 lignes (3%)
  - DIAGNOSES_ICD: 2 lignes (0%)

**visit_occurrence** — 129 lignes au total
  - ADMISSIONS: 129 lignes (100%)

## 2. Provenance au niveau des champs structurels

**condition_occurrence**
  - condition_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - condition_end_date ← PROCEDUREEVENTS_MV.endtime (confiance=0.85)
  - condition_end_datetime ← PROCEDUREEVENTS_MV.endtime (confiance=0.95)
  - condition_occurrence_id ← CHARTEVENTS.row_id (confiance=0.50) 🔁 (résolu par reprise)
  - condition_occurrence_id ← DIAGNOSES_ICD.row_id (confiance=0.60) 🔁 (résolu par reprise)
  - condition_occurrence_id ← PROCEDUREEVENTS_MV.row_id (confiance=0.90) 🔁 (résolu par reprise)
  - condition_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - condition_source_value ← CHARTEVENTS.itemid (confiance=0.85)
  - condition_source_value ← DIAGNOSES_ICD.icd9_code (confiance=1.00)
  - condition_source_value ← PROCEDUREEVENTS_MV.itemid (confiance=0.90)
  - condition_start_date ← CHARTEVENTS.charttime (confiance=0.85)
  - condition_start_date ← PROCEDUREEVENTS_MV.starttime (confiance=0.85)
  - condition_start_datetime ← CHARTEVENTS.charttime (confiance=0.85)
  - condition_start_datetime ← PROCEDUREEVENTS_MV.starttime (confiance=0.95)
  - condition_status_source_value ← CHARTEVENTS.resultstatus (confiance=0.70)
  - condition_status_source_value ← PROCEDUREEVENTS_MV.statusdescription (confiance=0.85)
  - condition_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← CHARTEVENTS.subject_id (confiance=0.95)
  - person_id ← DIAGNOSES_ICD.subject_id (confiance=1.00)
  - person_id ← PROCEDUREEVENTS_MV.subject_id (confiance=0.95)
  - stop_reason ← PROCEDUREEVENTS_MV.cancelreason (confiance=0.85) 🔁 (résolu par reprise)
  - visit_detail_id ← CHARTEVENTS.icustay_id (confiance=0.75)
  - visit_detail_id ← PROCEDUREEVENTS_MV.icustay_id (confiance=0.80)
  - visit_occurrence_id ← CHARTEVENTS.hadm_id (confiance=0.90)
  - visit_occurrence_id ← DIAGNOSES_ICD.hadm_id (confiance=0.90)
  - visit_occurrence_id ← PROCEDUREEVENTS_MV.hadm_id (confiance=0.90)

**death**
  - cause_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - cause_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - cause_source_value ← ADMISSIONS.diagnosis (confiance=0.75) 🔁 (résolu par reprise)
  - death_date ← PATIENTS.dod (confiance=0.95)
  - death_datetime ← ADMISSIONS.deathtime (confiance=0.95)
  - death_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← PATIENTS.subject_id (confiance=0.95)

**drug_exposure**
  - dose_unit_source_value ← CHARTEVENTS.valueuom (confiance=0.50)
  - dose_unit_source_value ← INPUTEVENTS_CV.amountuom (confiance=0.90)
  - dose_unit_source_value ← INPUTEVENTS_MV.amountuom (confiance=0.95)
  - dose_unit_source_value ← PRESCRIPTIONS.dose_unit_rx (confiance=0.95)
  - drug_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - drug_exposure_end_date ← INPUTEVENTS_MV.endtime (confiance=0.95)
  - drug_exposure_end_date ← PRESCRIPTIONS.enddate (confiance=0.95)
  - drug_exposure_end_datetime ← INPUTEVENTS_MV.endtime (confiance=0.95)
  - drug_exposure_end_datetime ← PRESCRIPTIONS.enddate (confiance=0.95)
  - drug_exposure_id ← CHARTEVENTS.row_id (confiance=0.80) 🔁 (résolu par reprise)
  - drug_exposure_id ← INPUTEVENTS_CV.row_id (confiance=0.90) 🔁 (résolu par reprise)
  - drug_exposure_id ← INPUTEVENTS_MV.row_id (confiance=0.90) 🔁 (résolu par reprise)
  - drug_exposure_id ← PRESCRIPTIONS.row_id (confiance=0.80) 🔁 (résolu par reprise)
  - drug_exposure_start_date ← CHARTEVENTS.charttime (confiance=0.90)
  - drug_exposure_start_date ← INPUTEVENTS_CV.charttime (confiance=0.90)
  - drug_exposure_start_date ← INPUTEVENTS_MV.starttime (confiance=0.95)
  - drug_exposure_start_date ← PRESCRIPTIONS.startdate (confiance=0.95)
  - drug_exposure_start_datetime ← CHARTEVENTS.charttime (confiance=0.90)
  - drug_exposure_start_datetime ← INPUTEVENTS_CV.charttime (confiance=0.90)
  - drug_exposure_start_datetime ← INPUTEVENTS_MV.starttime (confiance=0.95)
  - drug_exposure_start_datetime ← PRESCRIPTIONS.startdate (confiance=0.95)
  - drug_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - drug_source_value ← CHARTEVENTS.itemid (confiance=0.70)
  - drug_source_value ← INPUTEVENTS_CV.itemid (confiance=0.95)
  - drug_source_value ← INPUTEVENTS_MV.itemid (confiance=0.95)
  - drug_source_value ← PRESCRIPTIONS.drug (confiance=0.90)
  - drug_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← CHARTEVENTS.subject_id (confiance=0.95)
  - person_id ← INPUTEVENTS_CV.subject_id (confiance=0.95)
  - person_id ← INPUTEVENTS_MV.subject_id (confiance=0.95)
  - person_id ← PRESCRIPTIONS.subject_id (confiance=0.95)
  - quantity ← INPUTEVENTS_CV.amount (confiance=0.95)
  - quantity ← INPUTEVENTS_MV.amount (confiance=0.90)
  - quantity ← PRESCRIPTIONS.form_val_disp (confiance=0.90)
  - route_source_value ← INPUTEVENTS_CV.originalroute (confiance=0.90)
  - route_source_value ← INPUTEVENTS_MV.ordercategorydescription (confiance=0.70)
  - route_source_value ← PRESCRIPTIONS.route (confiance=0.95)
  - sig ← INPUTEVENTS_MV.ordercategorydescription (confiance=0.80)
  - stop_reason ← CHARTEVENTS.stopped (confiance=0.60)
  - stop_reason ← INPUTEVENTS_CV.stopped (confiance=0.90)
  - stop_reason ← INPUTEVENTS_MV.statusdescription (confiance=0.60)
  - verbatim_end_date ← INPUTEVENTS_MV.endtime (confiance=0.95) 🔁 (résolu par reprise)
  - verbatim_end_date ← PRESCRIPTIONS.enddate (confiance=0.90) 🔁 (résolu par reprise)
  - visit_detail_id ← CHARTEVENTS.icustay_id (confiance=0.70)
  - visit_detail_id ← INPUTEVENTS_CV.icustay_id (confiance=0.95)
  - visit_detail_id ← INPUTEVENTS_MV.icustay_id (confiance=0.90)
  - visit_detail_id ← PRESCRIPTIONS.icustay_id (confiance=0.85)
  - visit_occurrence_id ← CHARTEVENTS.hadm_id (confiance=0.80)
  - visit_occurrence_id ← INPUTEVENTS_CV.hadm_id (confiance=0.95)
  - visit_occurrence_id ← INPUTEVENTS_MV.hadm_id (confiance=0.90)
  - visit_occurrence_id ← PRESCRIPTIONS.hadm_id (confiance=0.85)

**measurement**
  - meas_event_field_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - measurement_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - measurement_date ← CHARTEVENTS.charttime (confiance=0.95)
  - measurement_date ← LABEVENTS.charttime (confiance=0.90)
  - measurement_date ← MICROBIOLOGYEVENTS.chartdate (confiance=0.95)
  - measurement_date ← OUTPUTEVENTS.charttime (confiance=0.90)
  - measurement_date ← PROCEDUREEVENTS_MV.starttime (confiance=0.90)
  - measurement_datetime ← CHARTEVENTS.charttime (confiance=0.95)
  - measurement_datetime ← LABEVENTS.charttime (confiance=0.95)
  - measurement_datetime ← MICROBIOLOGYEVENTS.charttime (confiance=0.95)
  - measurement_datetime ← OUTPUTEVENTS.charttime (confiance=0.95)
  - measurement_datetime ← PROCEDUREEVENTS_MV.starttime (confiance=0.95)
  - measurement_event_id ← LABEVENTS.row_id (confiance=0.80)
  - measurement_event_id ← MICROBIOLOGYEVENTS.row_id (confiance=0.95)
  - measurement_event_id ← OUTPUTEVENTS.row_id (confiance=0.85)
  - measurement_event_id ← PROCEDUREEVENTS_MV.orderid (confiance=0.85)
  - measurement_id ← CHARTEVENTS.row_id (confiance=0.90)
  - measurement_id ← LABEVENTS.row_id (confiance=0.95)
  - measurement_id ← MICROBIOLOGYEVENTS.row_id (confiance=0.80)
  - measurement_id ← OUTPUTEVENTS.row_id (confiance=0.95)
  - measurement_id ← PROCEDUREEVENTS_MV.row_id (confiance=0.85)
  - measurement_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - measurement_source_value ← CHARTEVENTS.itemid (confiance=1.00)
  - measurement_source_value ← LABEVENTS.itemid (confiance=0.85)
  - measurement_source_value ← MICROBIOLOGYEVENTS.ab_name (confiance=0.80)
  - measurement_source_value ← OUTPUTEVENTS.itemid (confiance=0.90)
  - measurement_source_value ← PROCEDUREEVENTS_MV.itemid (confiance=0.95)
  - measurement_time ← CHARTEVENTS.charttime (confiance=0.95)
  - measurement_time ← LABEVENTS.charttime (confiance=0.95)
  - measurement_time ← MICROBIOLOGYEVENTS.charttime (confiance=0.95)
  - measurement_time ← OUTPUTEVENTS.charttime (confiance=0.95)
  - measurement_time ← PROCEDUREEVENTS_MV.starttime (confiance=0.85)
  - measurement_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - operator_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← CHARTEVENTS.subject_id (confiance=1.00)
  - person_id ← DIAGNOSES_ICD.subject_id (confiance=0.95)
  - person_id ← LABEVENTS.subject_id (confiance=0.95)
  - person_id ← MICROBIOLOGYEVENTS.subject_id (confiance=0.95)
  - person_id ← OUTPUTEVENTS.subject_id (confiance=0.95)
  - person_id ← PROCEDUREEVENTS_MV.subject_id (confiance=0.95)
  - unit_source_value ← CHARTEVENTS.valueuom (confiance=1.00)
  - unit_source_value ← LABEVENTS.valueuom (confiance=0.95)
  - unit_source_value ← OUTPUTEVENTS.valueuom (confiance=0.95)
  - unit_source_value ← PROCEDUREEVENTS_MV.valueuom (confiance=0.95)
  - value_as_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - value_as_number ← CHARTEVENTS.valuenum (confiance=1.00)
  - value_as_number ← LABEVENTS.valuenum (confiance=0.95)
  - value_as_number ← MICROBIOLOGYEVENTS.dilution_value (confiance=0.90)
  - value_as_number ← OUTPUTEVENTS.value (confiance=0.95)
  - value_as_number ← PROCEDUREEVENTS_MV.value (confiance=0.95)
  - value_source_value ← CHARTEVENTS.value (confiance=1.00)
  - value_source_value ← LABEVENTS.value (confiance=0.95)
  - value_source_value ← MICROBIOLOGYEVENTS.dilution_text (confiance=0.90)
  - value_source_value ← OUTPUTEVENTS.value (confiance=0.95)
  - value_source_value ← PROCEDUREEVENTS_MV.value (confiance=0.80)
  - visit_detail_id ← CHARTEVENTS.icustay_id (confiance=0.80)
  - visit_detail_id ← MICROBIOLOGYEVENTS.hadm_id (confiance=0.80)
  - visit_detail_id ← OUTPUTEVENTS.icustay_id (confiance=0.90)
  - visit_detail_id ← PROCEDUREEVENTS_MV.icustay_id (confiance=0.90)
  - visit_occurrence_id ← CHARTEVENTS.hadm_id (confiance=0.90)
  - visit_occurrence_id ← DIAGNOSES_ICD.hadm_id (confiance=0.90)
  - visit_occurrence_id ← LABEVENTS.hadm_id (confiance=0.70)
  - visit_occurrence_id ← MICROBIOLOGYEVENTS.hadm_id (confiance=0.90)
  - visit_occurrence_id ← OUTPUTEVENTS.hadm_id (confiance=0.90)
  - visit_occurrence_id ← PROCEDUREEVENTS_MV.hadm_id (confiance=0.90)

**observation**
  - obs_event_field_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - observation_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - observation_date ← CHARTEVENTS.charttime (confiance=0.90)
  - observation_date ← CPTEVENTS.chartdate (confiance=0.95)
  - observation_date ← DATETIMEEVENTS.value (confiance=0.85)
  - observation_date ← PROCEDUREEVENTS_MV.starttime (confiance=0.90)
  - observation_datetime ← CHARTEVENTS.charttime (confiance=0.95)
  - observation_datetime ← CPTEVENTS.chartdate (confiance=0.95)
  - observation_datetime ← DATETIMEEVENTS.charttime (confiance=0.95)
  - observation_datetime ← PROCEDUREEVENTS_MV.starttime (confiance=0.95)
  - observation_event_id ← CHARTEVENTS.row_id (confiance=0.85)
  - observation_event_id ← CPTEVENTS.row_id (confiance=0.95)
  - observation_event_id ← DATETIMEEVENTS.hadm_id (confiance=0.85)
  - observation_event_id ← PROCEDUREEVENTS_MV.orderid (confiance=0.90)
  - observation_id ← CHARTEVENTS.row_id (confiance=0.90)
  - observation_id ← CPTEVENTS.row_id (confiance=0.95)
  - observation_id ← DATETIMEEVENTS.row_id (confiance=0.95)
  - observation_id ← DIAGNOSES_ICD.row_id (confiance=0.95)
  - observation_id ← PROCEDUREEVENTS_MV.row_id (confiance=0.65)
  - observation_id ← PROCEDURES_ICD.row_id (confiance=0.50)
  - observation_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - observation_source_value ← CHARTEVENTS.itemid (confiance=0.95)
  - observation_source_value ← CPTEVENTS.cpt_cd (confiance=0.85)
  - observation_source_value ← DATETIMEEVENTS.itemid (confiance=0.95)
  - observation_source_value ← DIAGNOSES_ICD.icd9_code (confiance=0.85)
  - observation_source_value ← PROCEDUREEVENTS_MV.itemid (confiance=0.95)
  - observation_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← CHARTEVENTS.subject_id (confiance=0.95)
  - person_id ← CPTEVENTS.subject_id (confiance=0.95)
  - person_id ← DATETIMEEVENTS.subject_id (confiance=0.95)
  - person_id ← DIAGNOSES_ICD.subject_id (confiance=0.95)
  - person_id ← PROCEDUREEVENTS_MV.subject_id (confiance=0.95)
  - person_id ← PROCEDURES_ICD.subject_id (confiance=0.90)
  - qualifier_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - qualifier_source_value ← CPTEVENTS.cpt_suffix (confiance=0.75)
  - qualifier_source_value ← PROCEDUREEVENTS_MV.locationcategory (confiance=0.80)
  - unit_source_value ← CHARTEVENTS.valueuom (confiance=0.95)
  - unit_source_value ← DATETIMEEVENTS.valueuom (confiance=0.95)
  - unit_source_value ← PROCEDUREEVENTS_MV.valueuom (confiance=0.95)
  - value_as_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - value_as_number ← CHARTEVENTS.valuenum (confiance=0.95)
  - value_as_number ← PROCEDUREEVENTS_MV.value (confiance=0.95)
  - value_as_string ← CHARTEVENTS.value (confiance=0.95)
  - value_as_string ← DATETIMEEVENTS.value (confiance=0.90)
  - value_as_string ← PROCEDUREEVENTS_MV.location (confiance=0.70)
  - value_source_value ← CHARTEVENTS.value (confiance=0.80)
  - value_source_value ← CPTEVENTS.description (confiance=0.70)
  - value_source_value ← DATETIMEEVENTS.value (confiance=0.85)
  - value_source_value ← PROCEDUREEVENTS_MV.ordercategoryname (confiance=0.65)
  - visit_detail_id ← CHARTEVENTS.icustay_id (confiance=0.85)
  - visit_detail_id ← CPTEVENTS.hadm_id (confiance=0.85)
  - visit_detail_id ← DATETIMEEVENTS.icustay_id (confiance=0.90)
  - visit_detail_id ← DIAGNOSES_ICD.hadm_id (confiance=0.85)
  - visit_detail_id ← PROCEDUREEVENTS_MV.icustay_id (confiance=0.85)
  - visit_occurrence_id ← CHARTEVENTS.hadm_id (confiance=0.90)
  - visit_occurrence_id ← CPTEVENTS.hadm_id (confiance=0.90)
  - visit_occurrence_id ← DATETIMEEVENTS.hadm_id (confiance=0.95)
  - visit_occurrence_id ← DIAGNOSES_ICD.hadm_id (confiance=0.90)
  - visit_occurrence_id ← PROCEDUREEVENTS_MV.hadm_id (confiance=0.90)
  - visit_occurrence_id ← PROCEDURES_ICD.hadm_id (confiance=0.80)

**observation_period**
  - observation_period_end_date ← ADMISSIONS.dischtime (confiance=0.90)
  - observation_period_start_date ← ADMISSIONS.admittime (confiance=0.90)
  - period_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← PATIENTS.subject_id (confiance=1.00)

**person**
  - birth_datetime ← PATIENTS.dob (confiance=1.00)
  - day_of_birth ← PATIENTS.dob (confiance=0.90)
  - ethnicity_source_value ← ADMISSIONS.ethnicity (confiance=0.80)
  - gender_source_value ← PATIENTS.gender (confiance=1.00)
  - month_of_birth ← PATIENTS.dob (confiance=0.90)
  - person_id ← PATIENTS.subject_id (confiance=1.00)
  - person_source_value ← PATIENTS.subject_id (confiance=0.90)
  - race_source_value ← ADMISSIONS.ethnicity (confiance=0.95) 🔁 (résolu par reprise)
  - year_of_birth ← PATIENTS.dob (confiance=0.90)

**procedure_occurrence**
  - modifier_source_value ← CPTEVENTS.cpt_suffix (confiance=0.50)
  - modifier_source_value ← PROCEDUREEVENTS_MV.location (confiance=0.90)
  - person_id ← CHARTEVENTS.subject_id (confiance=0.95)
  - person_id ← CPTEVENTS.subject_id (confiance=0.95)
  - person_id ← DIAGNOSES_ICD.subject_id (confiance=0.95)
  - person_id ← PROCEDUREEVENTS_MV.subject_id (confiance=0.95)
  - person_id ← PROCEDURES_ICD.subject_id (confiance=0.95)
  - procedure_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - procedure_date ← CHARTEVENTS.charttime (confiance=0.90)
  - procedure_date ← CPTEVENTS.chartdate (confiance=0.95)
  - procedure_date ← PROCEDUREEVENTS_MV.starttime (confiance=0.85)
  - procedure_datetime ← CHARTEVENTS.charttime (confiance=0.95)
  - procedure_datetime ← CPTEVENTS.chartdate (confiance=0.95)
  - procedure_datetime ← PROCEDUREEVENTS_MV.starttime (confiance=0.95)
  - procedure_end_date ← CHARTEVENTS.charttime (confiance=0.60)
  - procedure_end_date ← PROCEDUREEVENTS_MV.endtime (confiance=0.85)
  - procedure_end_datetime ← CHARTEVENTS.charttime (confiance=0.60)
  - procedure_end_datetime ← PROCEDUREEVENTS_MV.endtime (confiance=0.95)
  - procedure_occurrence_id ← CHARTEVENTS.row_id (confiance=0.90) 🔁 (résolu par reprise)
  - procedure_occurrence_id ← CPTEVENTS.row_id (confiance=0.80) 🔁 (résolu par reprise)
  - procedure_occurrence_id ← DIAGNOSES_ICD.row_id (confiance=0.60) 🔁 (résolu par reprise)
  - procedure_occurrence_id ← PROCEDUREEVENTS_MV.row_id (confiance=0.95) 🔁 (résolu par reprise)
  - procedure_occurrence_id ← PROCEDURES_ICD.row_id (confiance=0.90) 🔁 (résolu par reprise)
  - procedure_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - procedure_source_value ← CHARTEVENTS.itemid (confiance=0.75)
  - procedure_source_value ← CPTEVENTS.cpt_cd (confiance=0.95)
  - procedure_source_value ← DIAGNOSES_ICD.icd9_code (confiance=0.50)
  - procedure_source_value ← PROCEDUREEVENTS_MV.itemid (confiance=0.95)
  - procedure_source_value ← PROCEDURES_ICD.icd9_code (confiance=0.95)
  - procedure_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - quantity ← PROCEDUREEVENTS_MV.value (confiance=0.60)
  - visit_detail_id ← CHARTEVENTS.icustay_id (confiance=0.85) 🔁 (résolu par reprise)
  - visit_detail_id ← DIAGNOSES_ICD.hadm_id (confiance=0.40) 🔁 (résolu par reprise)
  - visit_detail_id ← PROCEDUREEVENTS_MV.icustay_id (confiance=0.85) 🔁 (résolu par reprise)
  - visit_detail_id ← PROCEDURES_ICD.hadm_id (confiance=0.85) 🔁 (résolu par reprise)
  - visit_occurrence_id ← CHARTEVENTS.hadm_id (confiance=0.85)
  - visit_occurrence_id ← CPTEVENTS.hadm_id (confiance=0.90)
  - visit_occurrence_id ← DIAGNOSES_ICD.hadm_id (confiance=0.85)
  - visit_occurrence_id ← PROCEDUREEVENTS_MV.hadm_id (confiance=0.90)
  - visit_occurrence_id ← PROCEDURES_ICD.hadm_id (confiance=0.90)

**visit_occurrence**
  - admitted_from_source_value ← ADMISSIONS.admission_location (confiance=0.95)
  - discharged_to_source_value ← ADMISSIONS.discharge_location (confiance=0.95)
  - person_id ← ADMISSIONS.subject_id (confiance=0.95)
  - visit_end_date ← ADMISSIONS.dischtime (confiance=0.90)
  - visit_end_datetime ← ADMISSIONS.dischtime (confiance=0.90)
  - visit_occurrence_id ← ADMISSIONS.hadm_id (confiance=0.95)
  - visit_source_value ← ADMISSIONS.admission_type (confiance=0.80)
  - visit_start_date ← ADMISSIONS.admittime (confiance=0.90)
  - visit_start_datetime ← ADMISSIONS.admittime (confiance=0.90)
  - visit_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )

## 3. Provenance au niveau des valeurs (champs codés, mécanisme 1)

**ADMISSIONS**
  - _Déclarée, mais aucune valeur distincte produite pour ce batch._

**CHARTEVENTS**
  - CHARTEVENTS.itemid: 1516 valeurs distinctes, 7% résolues
      -> AUCUN: 1414 valeurs
      -> observation: 56 valeurs
      -> drug_exposure: 19 valeurs
      -> measurement: 18 valeurs
      -> condition_occurrence: 5 valeurs
      -> procedure_occurrence: 4 valeurs

**CPTEVENTS**
  - CPTEVENTS.cpt_cd: 74 valeurs distinctes, 100% résolues
      -> procedure_occurrence: 65 valeurs
      -> observation: 9 valeurs

**DATETIMEEVENTS**
  - DATETIMEEVENTS.itemid: 160 valeurs distinctes, 51% résolues
      -> observation: 81 valeurs
      -> AUCUN: 79 valeurs

**DIAGNOSES_ICD**
  - DIAGNOSES_ICD.icd9_code: 581 valeurs distinctes, 98% résolues
      -> condition_occurrence: 507 valeurs
      -> observation: 70 valeurs
      -> measurement: 2 valeurs
      -> procedure_occurrence: 2 valeurs

**DRGCODES**
  - _Déclarée, mais aucune valeur distincte produite pour ce batch._

**D_ITEMS**
  - _Déclarée, mais aucune valeur distincte produite pour ce batch._

**D_LABITEMS**
  - _Déclarée, mais aucune valeur distincte produite pour ce batch._

**INPUTEVENTS_CV**
  - INPUTEVENTS_CV.itemid: 79 valeurs distinctes, 22% résolues
      -> AUCUN: 55 valeurs
      -> drug_exposure: 24 valeurs

**INPUTEVENTS_MV**
  - INPUTEVENTS_MV.itemid: 135 valeurs distinctes, 38% résolues
      -> AUCUN: 82 valeurs
      -> drug_exposure: 53 valeurs

**LABEVENTS**
  - LABEVENTS.itemid: 390 valeurs distinctes, 100% résolues
      -> measurement: 389 valeurs
      -> AUCUN: 1 valeurs

**MICROBIOLOGYEVENTS**
  - MICROBIOLOGYEVENTS.ab_itemid: 28 valeurs distinctes, 89% résolues
      -> measurement: 25 valeurs
      -> AUCUN: 3 valeurs

**OUTPUTEVENTS**
  - OUTPUTEVENTS.itemid: 124 valeurs distinctes, 52% résolues
      -> AUCUN: 62 valeurs
      -> measurement: 62 valeurs

**PATIENTS**
  - _Déclarée, mais aucune valeur distincte produite pour ce batch._

**PRESCRIPTIONS**
  - PRESCRIPTIONS.ndc: 997 valeurs distinctes, 97% résolues
      -> drug_exposure: 977 valeurs
      -> AUCUN: 20 valeurs

**PROCEDUREEVENTS_MV**
  - PROCEDUREEVENTS_MV.itemid: 64 valeurs distinctes, 47% résolues
      -> AUCUN: 39 valeurs
      -> procedure_occurrence: 16 valeurs
      -> observation: 3 valeurs
      -> measurement: 3 valeurs
      -> condition_occurrence: 3 valeurs

**PROCEDURES_ICD**
  - PROCEDURES_ICD.icd9_code: 164 valeurs distinctes, 99% résolues
      -> procedure_occurrence: 162 valeurs
      -> observation: 2 valeurs

## 4. Résolutions via mapping figé (fixed_value_mappings)

**person.ethnicity_concept_id** — 9 valeur(s) couverte(s) par le CSV
  - 'BLACK/AFRICAN AMERICAN' -> concept_id=38003564
  - 'UNKNOWN/NOT SPECIFIED' -> concept_id=38003564
  - 'WHITE' -> concept_id=38003564
  - 'OTHER' -> concept_id=38003564
  - 'ASIAN' -> concept_id=38003564
  - 'HISPANIC OR LATINO' -> concept_id=38003563
  - 'HISPANIC/LATINO - PUERTO RICAN' -> concept_id=38003563
  - 'UNABLE TO OBTAIN' -> concept_id=38003564
  - 'AMERICAN INDIAN/ALASKA NATIVE FEDERALLY RECOGNIZED TRIBE' -> concept_id=38003564

**person.race_concept_id** — 9 valeur(s) couverte(s) par le CSV
  - 'BLACK/AFRICAN AMERICAN' -> concept_id=38003599
  - 'UNKNOWN/NOT SPECIFIED' -> concept_id=4218674
  - 'WHITE' -> concept_id=8527
  - 'OTHER' -> concept_id=4087921
  - 'ASIAN' -> concept_id=8515
  - 'HISPANIC OR LATINO' -> concept_id=4188159
  - 'HISPANIC/LATINO - PUERTO RICAN' -> concept_id=4188159
  - 'UNABLE TO OBTAIN' -> concept_id=4218674
  - 'AMERICAN INDIAN/ALASKA NATIVE FEDERALLY RECOGNIZED TRIBE' -> concept_id=8657

**visit_occurrence.visit_concept_id** — 3 valeur(s) couverte(s) par le CSV
  - 'EMERGENCY' -> concept_id=262
  - 'ELECTIVE' -> concept_id=9201
  - 'URGENT' -> concept_id=262

## 5. Jointures de vocabulaire local

**Réussies :**
  - CHARTEVENTS.itemid -> D_ITEMS.label (text, vocabulaire(s)=['LOINC', 'SNOMED'])
  - DATETIMEEVENTS.itemid -> D_ITEMS.label (text, vocabulaire(s)=['SNOMED'])
  - INPUTEVENTS_CV.itemid -> D_ITEMS.label (text, vocabulaire(s)=['RxNorm'])
  - INPUTEVENTS_MV.itemid -> D_ITEMS.label (text, vocabulaire(s)=['RxNorm'])
  - LABEVENTS.itemid -> D_LABITEMS.loinc_code (code, vocabulaire(s)=['LOINC'])
  - MICROBIOLOGYEVENTS.ab_itemid -> D_ITEMS.label (text, vocabulaire(s)=['RxNorm', 'LOINC'])
  - OUTPUTEVENTS.itemid -> D_ITEMS.label (text, vocabulaire(s)=['LOINC'])
  - PROCEDUREEVENTS_MV.itemid -> D_ITEMS.label (text, vocabulaire(s)=['SNOMED', 'LOINC'])
