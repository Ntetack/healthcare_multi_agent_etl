# Structural Mapping Evaluation Report

## Summary (MAP only)

| Metric | Value |
|--------|-------|
| Gold fields (unique table.field) | 58 |
| Gold MAP rows (sources) | 82 |
| TP | 73 |
| FP (over-mapping) | 47 |
| FN (under-mapping) | 9 |
| **Micro Precision** | **0.6083** |
| **Micro Recall** | **0.8902** |
| **Micro F1** | **0.7228** |
| Macro Precision | 0.6523 |
| Macro Recall | 0.8707 |
| Macro F1 | 0.7187 |
| Over-mapping rate | 0.3917 |
| Under-mapping rate | 0.1098 |

### Per-field details

| Table | Field | Gold sources | Agent sources | P | R | F1 | TP | FP | FN |
|-------|-------|--------------|---------------|---|---|----|----|----|----|
| condition_occurrence | condition_end_date | conditions.STOP | conditions.STOP, procedures.STOP | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| condition_occurrence | condition_end_datetime | conditions.STOP | conditions.STOP, procedures.STOP | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| condition_occurrence | condition_source_value | conditions.CODE | conditions.CODE, procedures.CODE | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| condition_occurrence | condition_start_date | conditions.START | conditions.START, procedures.START | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| condition_occurrence | condition_start_datetime | conditions.START | conditions.START, procedures.START | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| condition_occurrence | person_id | conditions.PATIENT | conditions.PATIENT, procedures.PATIENT | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| condition_occurrence | visit_occurrence_id | conditions.ENCOUNTER | conditions.ENCOUNTER, procedures.ENCOUNTER | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| death | cause_source_value | encounters.REASONCODE | — | 0.00 | 0.00 | 0.00 | 0 | 0 | 1 |
| death | death_date | encounters.START | patients.DEATHDATE | 0.00 | 0.00 | 0.00 | 0 | 1 | 1 |
| death | death_datetime | encounters.START | patients.DEATHDATE | 0.00 | 0.00 | 0.00 | 0 | 1 | 1 |
| death | person_id | encounters.PATIENT | patients.Id | 0.00 | 0.00 | 0.00 | 0 | 1 | 1 |
| drug_exposure | drug_exposure_end_date | immunizations.DATE, medications.STOP | medications.STOP, procedures.STOP | 0.50 | 0.50 | 0.50 | 1 | 1 | 1 |
| drug_exposure | drug_exposure_end_datetime | immunizations.DATE, medications.STOP | medications.STOP, procedures.STOP | 0.50 | 0.50 | 0.50 | 1 | 1 | 1 |
| drug_exposure | drug_exposure_start_date | immunizations.DATE, medications.START | immunizations.DATE, medications.START, procedures.START | 0.67 | 1.00 | 0.80 | 2 | 1 | 0 |
| drug_exposure | drug_exposure_start_datetime | immunizations.DATE, medications.START | immunizations.DATE, medications.START, procedures.START | 0.67 | 1.00 | 0.80 | 2 | 1 | 0 |
| drug_exposure | drug_source_value | immunizations.CODE, medications.CODE | allergies.CODE, immunizations.CODE, medications.CODE, procedures.CODE | 0.50 | 1.00 | 0.67 | 2 | 2 | 0 |
| drug_exposure | person_id | immunizations.PATIENT, medications.PATIENT | allergies.PATIENT, immunizations.PATIENT, medications.PATIENT, procedures.PATIENT | 0.50 | 1.00 | 0.67 | 2 | 2 | 0 |
| drug_exposure | verbatim_end_date | immunizations.DATE, medications.STOP | medications.STOP | 1.00 | 0.50 | 0.67 | 1 | 0 | 1 |
| drug_exposure | visit_occurrence_id | immunizations.ENCOUNTER, medications.ENCOUNTER | allergies.ENCOUNTER, immunizations.ENCOUNTER, medications.ENCOUNTER, procedures.ENCOUNTER | 0.50 | 1.00 | 0.67 | 2 | 2 | 0 |
| measurement | measurement_date | observations.DATE, procedures.START | observations.DATE, procedures.START | 1.00 | 1.00 | 1.00 | 2 | 0 | 0 |
| measurement | measurement_datetime | observations.DATE, procedures.START | observations.DATE, procedures.START | 1.00 | 1.00 | 1.00 | 2 | 0 | 0 |
| measurement | measurement_source_value | observations.CODE, procedures.CODE | observations.CODE, procedures.CODE | 1.00 | 1.00 | 1.00 | 2 | 0 | 0 |
| measurement | measurement_time | observations.DATE, procedures.START | observations.DATE, procedures.START | 1.00 | 1.00 | 1.00 | 2 | 0 | 0 |
| measurement | person_id | observations.PATIENT, procedures.PATIENT | observations.PATIENT, procedures.PATIENT | 1.00 | 1.00 | 1.00 | 2 | 0 | 0 |
| measurement | unit_source_value | observations.UNITS | observations.UNITS | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| measurement | value_as_number | observations.VALUE | observations.VALUE | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| measurement | value_source_value | observations.VALUE | observations.VALUE, procedures.DESCRIPTION | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| measurement | visit_occurrence_id | observations.ENCOUNTER, procedures.ENCOUNTER | observations.ENCOUNTER, procedures.ENCOUNTER | 1.00 | 1.00 | 1.00 | 2 | 0 | 0 |
| observation | observation_date | allergies.START, conditions.START, observations.DATE | allergies.START, conditions.START, encounters.START, observations.DATE, procedures.START | 0.60 | 1.00 | 0.75 | 3 | 2 | 0 |
| observation | observation_datetime | allergies.START, conditions.START, observations.DATE | allergies.START, conditions.START, encounters.START, observations.DATE, procedures.START | 0.60 | 1.00 | 0.75 | 3 | 2 | 0 |
| observation | observation_source_value | allergies.CODE, conditions.CODE, observations.CODE | allergies.CODE, conditions.CODE, encounters.CODE, observations.CODE, procedures.CODE | 0.60 | 1.00 | 0.75 | 3 | 2 | 0 |
| observation | person_id | allergies.PATIENT, conditions.PATIENT, observations.PATIENT | allergies.PATIENT, conditions.PATIENT, encounters.PATIENT, observations.PATIENT, procedures.PATIENT | 0.60 | 1.00 | 0.75 | 3 | 2 | 0 |
| observation | value_source_value | observations.VALUE | allergies.REACTION1, conditions.CODE, observations.VALUE | 0.33 | 1.00 | 0.50 | 1 | 2 | 0 |
| observation | visit_occurrence_id | allergies.ENCOUNTER, conditions.ENCOUNTER, observations.ENCOUNTER | allergies.ENCOUNTER, conditions.ENCOUNTER, encounters.Id, observations.ENCOUNTER, procedures.ENCOUNTER | 0.60 | 1.00 | 0.75 | 3 | 2 | 0 |
| observation_period | observation_period_end_date | encounters.STOP | encounters.STOP | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| observation_period | observation_period_start_date | encounters.START | encounters.START | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| observation_period | person_id | encounters.PATIENT | patients.Id | 0.00 | 0.00 | 0.00 | 0 | 1 | 1 |
| person | birth_datetime | patients.BIRTHDATE | patients.BIRTHDATE | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | day_of_birth | patients.BIRTHDATE | patients.BIRTHDATE | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | ethnicity_source_value | patients.ETHNICITY | patients.ETHNICITY | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | gender_source_value | patients.GENDER | patients.GENDER | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | month_of_birth | patients.BIRTHDATE | patients.BIRTHDATE | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | person_source_value | patients.Id | patients.Id | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | race_source_value | patients.RACE | patients.RACE | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | year_of_birth | patients.BIRTHDATE | patients.BIRTHDATE | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| procedure_occurrence | person_id | procedures.PATIENT | encounters.PATIENT, observations.PATIENT, procedures.PATIENT | 0.33 | 1.00 | 0.50 | 1 | 2 | 0 |
| procedure_occurrence | procedure_date | procedures.START | encounters.START, observations.DATE, procedures.START | 0.33 | 1.00 | 0.50 | 1 | 2 | 0 |
| procedure_occurrence | procedure_datetime | procedures.START | encounters.START, observations.DATE, procedures.START | 0.33 | 1.00 | 0.50 | 1 | 2 | 0 |
| procedure_occurrence | procedure_end_date | procedures.STOP | encounters.STOP, procedures.STOP | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| procedure_occurrence | procedure_end_datetime | procedures.STOP | encounters.STOP, procedures.STOP | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| procedure_occurrence | procedure_source_value | procedures.CODE | encounters.CODE, observations.CODE, procedures.CODE | 0.33 | 1.00 | 0.50 | 1 | 2 | 0 |
| procedure_occurrence | visit_occurrence_id | procedures.ENCOUNTER | encounters.Id, observations.ENCOUNTER, procedures.ENCOUNTER | 0.33 | 1.00 | 0.50 | 1 | 2 | 0 |
| visit_occurrence | person_id | encounters.PATIENT | encounters.PATIENT | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_end_date | encounters.STOP | encounters.STOP | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_end_datetime | encounters.STOP | encounters.STOP | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_source_value | encounters.Id | encounters.CODE | 0.00 | 0.00 | 0.00 | 0 | 1 | 1 |
| visit_occurrence | visit_start_date | encounters.START | encounters.START | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_start_datetime | encounters.START | encounters.START | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |

### Agent fields not in gold (informational)

| Table | Field | Agent sources |
|-------|-------|---------------|
| condition_occurrence | visit_detail_id | conditions.ENCOUNTER, procedures.ENCOUNTER |
| drug_exposure | dose_unit_source_value | medications.DESCRIPTION |
| drug_exposure | quantity | medications.DISPENSES |
| drug_exposure | route_source_value | medications.DESCRIPTION |
| drug_exposure | visit_detail_id | allergies.ENCOUNTER, medications.ENCOUNTER |
| measurement | visit_detail_id | observations.ENCOUNTER, procedures.ENCOUNTER |
| observation | qualifier_source_value | allergies.TYPE |
| observation | unit_source_value | observations.UNITS |
| observation | value_as_number | observations.VALUE, procedures.BASE_COST |
| observation | value_as_string | allergies.DESCRIPTION, conditions.DESCRIPTION, observations.VALUE, procedures.DESCRIPTION |
| observation | visit_detail_id | allergies.ENCOUNTER, conditions.ENCOUNTER, observations.ENCOUNTER, procedures.ENCOUNTER |
| person | person_id | patients.Id |
| procedure_occurrence | visit_detail_id | procedures.ENCOUNTER |

## Notes

- Only **structural MAP** pairs are scored (source_table + source_field).
- `*_concept_id` / `*_source_concept_id` / `*_type_concept_id` are excluded (semantic or fixed).
- TP = agent source ∈ gold sources for that field.
- FP = agent proposed a source not in gold (over-mapping).
- FN = gold source missing from agent (under-mapping).
