# Rapport de provenance — RUN-batch43-88536d5c

## 1. Provenance au niveau des lignes (tables OMOP finales)

**condition_occurrence** — 2595 lignes au total
  - DIAGNOSES_ICD: 1599 lignes (62%)
  - DATETIMEEVENTS: 859 lignes (33%)
  - CHARTEVENTS: 137 lignes (5%)

**drug_exposure** — 27318 lignes au total
  - INPUTEVENTS_CV: 12359 lignes (45%)
  - PRESCRIPTIONS: 10396 lignes (38%)
  - INPUTEVENTS_MV: 4106 lignes (15%)
  - CHARTEVENTS: 457 lignes (2%)

**measurement** — 112806 lignes au total
  - LABEVENTS: 72984 lignes (65%)
  - CHARTEVENTS: 39817 lignes (35%)
  - DIAGNOSES_ICD: 5 lignes (0%)

**observation** — 79864 lignes au total
  - CHARTEVENTS: 79228 lignes (99%)
  - INPUTEVENTS_CV: 270 lignes (0%)
  - INPUTEVENTS_MV: 208 lignes (0%)
  - DIAGNOSES_ICD: 155 lignes (0%)
  - PROCEDURES_ICD: 3 lignes (0%)

**procedure_occurrence** — 15822 lignes au total
  - DATETIMEEVENTS: 14549 lignes (92%)
  - PROCEDURES_ICD: 503 lignes (3%)
  - CHARTEVENTS: 477 lignes (3%)
  - CPTEVENTS: 291 lignes (2%)
  - DIAGNOSES_ICD: 2 lignes (0%)

**visit_occurrence** — 129 lignes au total
  - ADMISSIONS: 129 lignes (100%)

## 2. Provenance au niveau des champs structurels

**condition_occurrence**
  - condition_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - condition_end_date ← DATETIMEEVENTS.value (confiance=0.65)
  - condition_end_datetime ← DATETIMEEVENTS.value (confiance=0.65)
  - condition_occurrence_id ← CHARTEVENTS.row_id (confiance=0.60) 🔁 (résolu par reprise)
  - condition_occurrence_id ← DATETIMEEVENTS.row_id (confiance=0.90) 🔁 (résolu par reprise)
  - condition_occurrence_id ← DIAGNOSES_ICD.row_id (confiance=0.90) 🔁 (résolu par reprise)
  - condition_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - condition_source_value ← CHARTEVENTS.itemid (confiance=0.70)
  - condition_source_value ← DATETIMEEVENTS.itemid (confiance=0.70)
  - condition_source_value ← DIAGNOSES_ICD.icd9_code (confiance=0.95)
  - condition_start_date ← CHARTEVENTS.charttime (confiance=0.90)
  - condition_start_date ← DATETIMEEVENTS.charttime (confiance=0.80)
  - condition_start_datetime ← CHARTEVENTS.charttime (confiance=0.95)
  - condition_start_datetime ← DATETIMEEVENTS.charttime (confiance=0.80)
  - condition_status_source_value ← DATETIMEEVENTS.stopped (confiance=0.60)
  - condition_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← CHARTEVENTS.subject_id (confiance=0.95)
  - person_id ← DATETIMEEVENTS.subject_id (confiance=0.95)
  - person_id ← DIAGNOSES_ICD.subject_id (confiance=0.90)
  - stop_reason ← CHARTEVENTS.stopped (confiance=0.75)
  - stop_reason ← DATETIMEEVENTS.stopped (confiance=0.85)
  - visit_detail_id ← CHARTEVENTS.icustay_id (confiance=0.85) 🔁 (résolu par reprise)
  - visit_detail_id ← DATETIMEEVENTS.icustay_id (confiance=0.90) 🔁 (résolu par reprise)
  - visit_detail_id ← DIAGNOSES_ICD.hadm_id (confiance=0.40) 🔁 (résolu par reprise)
  - visit_occurrence_id ← CHARTEVENTS.hadm_id (confiance=0.90)
  - visit_occurrence_id ← DATETIMEEVENTS.hadm_id (confiance=0.90)
  - visit_occurrence_id ← DIAGNOSES_ICD.hadm_id (confiance=0.85)

**death**
  - cause_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - cause_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - cause_source_value ← ADMISSIONS.diagnosis (confiance=0.50) 🔁 (résolu par reprise)
  - death_date ← PATIENTS.dod (confiance=0.90)
  - death_datetime ← ADMISSIONS.deathtime (confiance=0.90)
  - death_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← PATIENTS.subject_id (confiance=0.95)

**drug_exposure**
  - dose_unit_source_value ← CHARTEVENTS.valueuom (confiance=0.50)
  - dose_unit_source_value ← INPUTEVENTS_CV.amountuom (confiance=0.90)
  - dose_unit_source_value ← INPUTEVENTS_MV.amountuom (confiance=0.95)
  - dose_unit_source_value ← PRESCRIPTIONS.dose_unit_rx (confiance=0.90)
  - drug_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - drug_exposure_end_date ← INPUTEVENTS_MV.endtime (confiance=0.95)
  - drug_exposure_end_date ← PRESCRIPTIONS.enddate (confiance=0.90)
  - drug_exposure_end_datetime ← INPUTEVENTS_MV.endtime (confiance=0.95)
  - drug_exposure_end_datetime ← PRESCRIPTIONS.enddate (confiance=0.90)
  - drug_exposure_id ← CHARTEVENTS.row_id (confiance=0.15)
  - drug_exposure_id ← INPUTEVENTS_MV.row_id (confiance=0.90)
  - drug_exposure_id ← PRESCRIPTIONS.row_id (confiance=0.90)
  - drug_exposure_start_date ← CHARTEVENTS.charttime (confiance=0.85)
  - drug_exposure_start_date ← INPUTEVENTS_CV.charttime (confiance=0.90)
  - drug_exposure_start_date ← INPUTEVENTS_MV.starttime (confiance=0.95)
  - drug_exposure_start_date ← PRESCRIPTIONS.startdate (confiance=0.90)
  - drug_exposure_start_datetime ← CHARTEVENTS.charttime (confiance=0.85)
  - drug_exposure_start_datetime ← INPUTEVENTS_CV.charttime (confiance=0.95)
  - drug_exposure_start_datetime ← INPUTEVENTS_MV.starttime (confiance=0.95)
  - drug_exposure_start_datetime ← PRESCRIPTIONS.startdate (confiance=0.90)
  - drug_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - drug_source_value ← INPUTEVENTS_CV.itemid (confiance=0.95)
  - drug_source_value ← INPUTEVENTS_MV.itemid (confiance=0.95)
  - drug_source_value ← PRESCRIPTIONS.drug (confiance=0.90)
  - drug_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← CHARTEVENTS.subject_id (confiance=0.95)
  - person_id ← INPUTEVENTS_CV.subject_id (confiance=0.95)
  - person_id ← INPUTEVENTS_MV.subject_id (confiance=0.95)
  - person_id ← PRESCRIPTIONS.subject_id (confiance=0.95)
  - quantity ← INPUTEVENTS_CV.amount (confiance=0.90) 🔁 (résolu par reprise)
  - quantity ← INPUTEVENTS_MV.amount (confiance=0.90) 🔁 (résolu par reprise)
  - quantity ← PRESCRIPTIONS.form_val_disp (confiance=0.90) 🔁 (résolu par reprise)
  - refills ← INPUTEVENTS_CV.newbottle (confiance=0.70)
  - route_source_value ← INPUTEVENTS_CV.originalroute (confiance=0.95)
  - route_source_value ← INPUTEVENTS_MV.ordercategorydescription (confiance=0.85)
  - route_source_value ← PRESCRIPTIONS.route (confiance=0.90)
  - stop_reason ← CHARTEVENTS.stopped (confiance=0.45)
  - stop_reason ← INPUTEVENTS_CV.stopped (confiance=0.85)
  - stop_reason ← INPUTEVENTS_MV.statusdescription (confiance=0.85)
  - verbatim_end_date ← INPUTEVENTS_MV.endtime (confiance=0.95) 🔁 (résolu par reprise)
  - verbatim_end_date ← PRESCRIPTIONS.enddate (confiance=0.90) 🔁 (résolu par reprise)
  - visit_detail_id ← CHARTEVENTS.icustay_id (confiance=0.90)
  - visit_detail_id ← INPUTEVENTS_CV.icustay_id (confiance=0.90)
  - visit_detail_id ← INPUTEVENTS_MV.icustay_id (confiance=0.90)
  - visit_detail_id ← PRESCRIPTIONS.icustay_id (confiance=0.85)
  - visit_occurrence_id ← CHARTEVENTS.hadm_id (confiance=0.90)
  - visit_occurrence_id ← INPUTEVENTS_CV.hadm_id (confiance=0.90)
  - visit_occurrence_id ← INPUTEVENTS_MV.hadm_id (confiance=0.90)
  - visit_occurrence_id ← PRESCRIPTIONS.hadm_id (confiance=0.85)

**measurement**
  - meas_event_field_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - measurement_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - measurement_date ← CHARTEVENTS.charttime (confiance=0.90)
  - measurement_date ← LABEVENTS.charttime (confiance=0.90)
  - measurement_datetime ← CHARTEVENTS.charttime (confiance=0.95)
  - measurement_datetime ← LABEVENTS.charttime (confiance=0.95)
  - measurement_event_id ← CHARTEVENTS.row_id (confiance=0.85)
  - measurement_id ← CHARTEVENTS.row_id (confiance=0.95)
  - measurement_id ← DIAGNOSES_ICD.row_id (confiance=0.90)
  - measurement_id ← LABEVENTS.row_id (confiance=0.95)
  - measurement_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - measurement_source_value ← CHARTEVENTS.itemid (confiance=0.90)
  - measurement_source_value ← DIAGNOSES_ICD.icd9_code (confiance=0.70)
  - measurement_source_value ← LABEVENTS.itemid (confiance=0.90)
  - measurement_time ← CHARTEVENTS.charttime (confiance=0.95)
  - measurement_time ← LABEVENTS.charttime (confiance=0.90)
  - measurement_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - operator_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← CHARTEVENTS.subject_id (confiance=0.95)
  - person_id ← DIAGNOSES_ICD.subject_id (confiance=0.80)
  - person_id ← LABEVENTS.subject_id (confiance=0.95)
  - unit_source_value ← CHARTEVENTS.valueuom (confiance=0.95)
  - unit_source_value ← LABEVENTS.valueuom (confiance=0.95)
  - value_as_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - value_as_number ← CHARTEVENTS.valuenum (confiance=0.95)
  - value_as_number ← LABEVENTS.valuenum (confiance=0.95)
  - value_source_value ← CHARTEVENTS.value (confiance=0.95)
  - value_source_value ← LABEVENTS.value (confiance=0.95)
  - visit_detail_id ← CHARTEVENTS.icustay_id (confiance=0.95)
  - visit_detail_id ← DIAGNOSES_ICD.hadm_id (confiance=0.60)
  - visit_occurrence_id ← CHARTEVENTS.hadm_id (confiance=0.95)
  - visit_occurrence_id ← DIAGNOSES_ICD.hadm_id (confiance=0.75)
  - visit_occurrence_id ← LABEVENTS.hadm_id (confiance=0.95)

**observation**
  - obs_event_field_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - observation_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - observation_date ← CHARTEVENTS.charttime (confiance=0.90)
  - observation_date ← CPTEVENTS.chartdate (confiance=0.90)
  - observation_date ← INPUTEVENTS_CV.charttime (confiance=0.90)
  - observation_date ← INPUTEVENTS_MV.starttime (confiance=0.85)
  - observation_datetime ← CHARTEVENTS.charttime (confiance=0.95)
  - observation_datetime ← CPTEVENTS.chartdate (confiance=0.90)
  - observation_datetime ← INPUTEVENTS_CV.charttime (confiance=0.90)
  - observation_datetime ← INPUTEVENTS_MV.starttime (confiance=0.90)
  - observation_event_id ← CPTEVENTS.row_id (confiance=0.90) 🔁 (résolu par reprise)
  - observation_event_id ← INPUTEVENTS_CV.orderid (confiance=0.85) 🔁 (résolu par reprise)
  - observation_event_id ← INPUTEVENTS_MV.orderid (confiance=0.80) 🔁 (résolu par reprise)
  - observation_event_id ← PROCEDURES_ICD.row_id (confiance=0.30) 🔁 (résolu par reprise)
  - observation_id ← CHARTEVENTS.row_id (confiance=0.95) 🔁 (résolu par reprise)
  - observation_id ← CPTEVENTS.row_id (confiance=0.90) 🔁 (résolu par reprise)
  - observation_id ← DIAGNOSES_ICD.row_id (confiance=0.30) 🔁 (résolu par reprise)
  - observation_id ← INPUTEVENTS_CV.row_id (confiance=0.90) 🔁 (résolu par reprise)
  - observation_id ← INPUTEVENTS_MV.row_id (confiance=0.95) 🔁 (résolu par reprise)
  - observation_id ← PROCEDURES_ICD.row_id (confiance=0.40) 🔁 (résolu par reprise)
  - observation_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - observation_source_value ← CHARTEVENTS.itemid (confiance=0.95)
  - observation_source_value ← CPTEVENTS.cpt_cd (confiance=0.85)
  - observation_source_value ← DIAGNOSES_ICD.icd9_code (confiance=0.90)
  - observation_source_value ← INPUTEVENTS_CV.itemid (confiance=0.95)
  - observation_source_value ← INPUTEVENTS_MV.itemid (confiance=0.95)
  - observation_source_value ← PROCEDURES_ICD.icd9_code (confiance=0.95)
  - observation_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← CHARTEVENTS.subject_id (confiance=0.95)
  - person_id ← CPTEVENTS.subject_id (confiance=0.95)
  - person_id ← DIAGNOSES_ICD.subject_id (confiance=0.90)
  - person_id ← INPUTEVENTS_CV.subject_id (confiance=0.95)
  - person_id ← INPUTEVENTS_MV.subject_id (confiance=0.95)
  - person_id ← PROCEDURES_ICD.subject_id (confiance=0.95)
  - qualifier_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - qualifier_source_value ← CPTEVENTS.subsectionheader (confiance=0.85)
  - qualifier_source_value ← INPUTEVENTS_CV.originalroute (confiance=0.85)
  - qualifier_source_value ← INPUTEVENTS_MV.ordercategorydescription (confiance=0.75)
  - unit_source_value ← CHARTEVENTS.valueuom (confiance=0.95)
  - unit_source_value ← INPUTEVENTS_CV.amountuom (confiance=0.90)
  - unit_source_value ← INPUTEVENTS_MV.amountuom (confiance=0.85)
  - value_as_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - value_as_number ← CHARTEVENTS.valuenum (confiance=0.95)
  - value_as_number ← INPUTEVENTS_CV.amount (confiance=0.85)
  - value_as_number ← INPUTEVENTS_MV.amount (confiance=0.85)
  - value_as_string ← CHARTEVENTS.value (confiance=0.95)
  - value_as_string ← CPTEVENTS.description (confiance=0.75)
  - value_as_string ← INPUTEVENTS_CV.stopped (confiance=0.75)
  - value_as_string ← INPUTEVENTS_MV.ordercategorydescription (confiance=0.65)
  - value_source_value ← CHARTEVENTS.value (confiance=0.80)
  - value_source_value ← CPTEVENTS.cpt_cd (confiance=0.95)
  - value_source_value ← DIAGNOSES_ICD.icd9_code (confiance=0.20)
  - value_source_value ← INPUTEVENTS_CV.amount (confiance=0.80)
  - value_source_value ← INPUTEVENTS_MV.itemid (confiance=0.75)
  - visit_detail_id ← CHARTEVENTS.icustay_id (confiance=0.90) 🔁 (résolu par reprise)
  - visit_detail_id ← INPUTEVENTS_CV.icustay_id (confiance=0.90) 🔁 (résolu par reprise)
  - visit_detail_id ← INPUTEVENTS_MV.icustay_id (confiance=0.90) 🔁 (résolu par reprise)
  - visit_detail_id ← PROCEDURES_ICD.hadm_id (confiance=0.30) 🔁 (résolu par reprise)
  - visit_occurrence_id ← CHARTEVENTS.hadm_id (confiance=0.90)
  - visit_occurrence_id ← CPTEVENTS.hadm_id (confiance=0.90)
  - visit_occurrence_id ← DIAGNOSES_ICD.hadm_id (confiance=0.80)
  - visit_occurrence_id ← INPUTEVENTS_CV.hadm_id (confiance=0.90)
  - visit_occurrence_id ← INPUTEVENTS_MV.hadm_id (confiance=0.90)
  - visit_occurrence_id ← PROCEDURES_ICD.hadm_id (confiance=0.95)

**observation_period**
  - observation_period_end_date ← PATIENTS.dod (confiance=0.85)
  - observation_period_start_date ← ADMISSIONS.admittime (confiance=0.80)
  - period_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← PATIENTS.subject_id (confiance=0.95)

**person**
  - birth_datetime ← PATIENTS.dob (confiance=0.95)
  - day_of_birth ← PATIENTS.dob (confiance=0.90)
  - ethnicity_source_value ← ADMISSIONS.ethnicity (confiance=0.90)
  - gender_source_value ← PATIENTS.gender (confiance=0.95)
  - month_of_birth ← PATIENTS.dob (confiance=0.90)
  - person_id ← PATIENTS.subject_id (confiance=0.95)
  - person_source_value ← PATIENTS.subject_id (confiance=0.85)
  - race_source_value ← ADMISSIONS.ethnicity (confiance=0.95) 🔁 (résolu par reprise)
  - year_of_birth ← PATIENTS.dob (confiance=0.90)

**procedure_occurrence**
  - modifier_source_value ← CPTEVENTS.cpt_suffix (confiance=0.85)
  - person_id ← CHARTEVENTS.subject_id (confiance=0.95)
  - person_id ← CPTEVENTS.subject_id (confiance=0.95)
  - person_id ← DATETIMEEVENTS.subject_id (confiance=0.95)
  - person_id ← DIAGNOSES_ICD.subject_id (confiance=0.95)
  - person_id ← PROCEDURES_ICD.subject_id (confiance=0.95)
  - procedure_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - procedure_date ← CHARTEVENTS.charttime (confiance=0.80)
  - procedure_date ← CPTEVENTS.chartdate (confiance=0.90)
  - procedure_date ← DATETIMEEVENTS.charttime (confiance=0.90)
  - procedure_datetime ← CHARTEVENTS.charttime (confiance=0.80)
  - procedure_datetime ← CPTEVENTS.chartdate (confiance=0.90)
  - procedure_datetime ← DATETIMEEVENTS.charttime (confiance=0.90)
  - procedure_end_date ← CPTEVENTS.chartdate (confiance=0.65)
  - procedure_end_datetime ← CPTEVENTS.chartdate (confiance=0.65)
  - procedure_occurrence_id ← CHARTEVENTS.row_id (confiance=0.50) 🔁 (résolu par reprise)
  - procedure_occurrence_id ← CPTEVENTS.row_id (confiance=0.90) 🔁 (résolu par reprise)
  - procedure_occurrence_id ← DATETIMEEVENTS.row_id (confiance=0.80) 🔁 (résolu par reprise)
  - procedure_occurrence_id ← DIAGNOSES_ICD.row_id (confiance=0.80) 🔁 (résolu par reprise)
  - procedure_occurrence_id ← PROCEDURES_ICD.row_id (confiance=0.90) 🔁 (résolu par reprise)
  - procedure_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - procedure_source_value ← CHARTEVENTS.itemid (confiance=0.70)
  - procedure_source_value ← CPTEVENTS.cpt_cd (confiance=0.95)
  - procedure_source_value ← DATETIMEEVENTS.itemid (confiance=0.90)
  - procedure_source_value ← DIAGNOSES_ICD.icd9_code (confiance=0.60)
  - procedure_source_value ← PROCEDURES_ICD.icd9_code (confiance=0.95)
  - procedure_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - visit_detail_id ← CHARTEVENTS.icustay_id (confiance=0.85)
  - visit_detail_id ← DATETIMEEVENTS.icustay_id (confiance=0.85)
  - visit_occurrence_id ← CHARTEVENTS.hadm_id (confiance=0.90)
  - visit_occurrence_id ← CPTEVENTS.hadm_id (confiance=0.85)
  - visit_occurrence_id ← DATETIMEEVENTS.hadm_id (confiance=0.90)
  - visit_occurrence_id ← DIAGNOSES_ICD.hadm_id (confiance=0.85)
  - visit_occurrence_id ← PROCEDURES_ICD.hadm_id (confiance=0.75)

**visit_occurrence**
  - admitted_from_source_value ← ADMISSIONS.admission_location (confiance=0.95)
  - discharged_to_source_value ← ADMISSIONS.discharge_location (confiance=0.95)
  - person_id ← ADMISSIONS.subject_id (confiance=0.95)
  - visit_end_date ← ADMISSIONS.dischtime (confiance=0.90)
  - visit_end_datetime ← ADMISSIONS.dischtime (confiance=0.90)
  - visit_occurrence_id ← ADMISSIONS.hadm_id (confiance=0.95)
  - visit_source_value ← ADMISSIONS.admission_type (confiance=0.85)
  - visit_start_date ← ADMISSIONS.admittime (confiance=0.90)
  - visit_start_datetime ← ADMISSIONS.admittime (confiance=0.90)
  - visit_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )

## 3. Provenance au niveau des valeurs (champs codés, mécanisme 1)

**ADMISSIONS**
  - _Déclarée, mais aucune valeur distincte produite pour ce batch._

**CHARTEVENTS**
  - CHARTEVENTS.itemid: 1516 valeurs distinctes, 8% résolues
      -> AUCUN: 1413 valeurs
      -> observation: 80 valeurs
      -> measurement: 11 valeurs
      -> drug_exposure: 5 valeurs
      -> condition_occurrence: 5 valeurs
      -> procedure_occurrence: 2 valeurs

**CPTEVENTS**
  - CPTEVENTS.cpt_cd: 74 valeurs distinctes, 100% résolues
      -> procedure_occurrence: 65 valeurs
      -> observation: 9 valeurs

**DATETIMEEVENTS**
  - DATETIMEEVENTS.itemid: 80 valeurs distinctes, 100% résolues
      -> procedure_occurrence: 73 valeurs
      -> condition_occurrence: 4 valeurs
      -> AUCUN: 3 valeurs

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
  - INPUTEVENTS_CV.itemid: 79 valeurs distinctes, 42% résolues
      -> AUCUN: 54 valeurs
      -> drug_exposure: 24 valeurs
      -> observation: 1 valeurs

**INPUTEVENTS_MV**
  - INPUTEVENTS_MV.itemid: 135 valeurs distinctes, 48% résolues
      -> AUCUN: 78 valeurs
      -> drug_exposure: 55 valeurs
      -> observation: 2 valeurs

**LABEVENTS**
  - LABEVENTS.itemid: 390 valeurs distinctes, 100% résolues
      -> measurement: 389 valeurs
      -> AUCUN: 1 valeurs

**MICROBIOLOGYEVENTS**
  - _Déclarée, mais aucune valeur distincte produite pour ce batch._

**OUTPUTEVENTS**
  - _Déclarée, mais aucune valeur distincte produite pour ce batch._

**PATIENTS**
  - _Déclarée, mais aucune valeur distincte produite pour ce batch._

**PRESCRIPTIONS**
  - PRESCRIPTIONS.ndc: 997 valeurs distinctes, 99% résolues
      -> drug_exposure: 995 valeurs
      -> AUCUN: 2 valeurs

**PROCEDUREEVENTS_MV**
  - _Déclarée, mais aucune valeur distincte produite pour ce batch._

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
  - DATETIMEEVENTS.itemid -> D_ITEMS.label (text, vocabulaire(s)=—)
  - INPUTEVENTS_CV.itemid -> D_ITEMS.label (text, vocabulaire(s)=['RxNorm', 'LOINC', 'SNOMED'])
  - INPUTEVENTS_MV.itemid -> D_ITEMS.label (text, vocabulaire(s)=['RxNorm', 'LOINC', 'SNOMED'])
  - LABEVENTS.itemid -> D_LABITEMS.loinc_code (code, vocabulaire(s)=['LOINC'])
  - OUTPUTEVENTS.itemid -> D_ITEMS.label (text, vocabulaire(s)=—)
  - PROCEDUREEVENTS_MV.itemid -> D_ITEMS.label (text, vocabulaire(s)=—)

**Échouées :**
  - MICROBIOLOGYEVENTS.ab_itemid
      -> Join to 'D_ITEMS' via ab_itemid/itemid failed the minimum real-overlap check (MIN_JOIN_OVERLAP) - proposed keys likely don't actually correspond
