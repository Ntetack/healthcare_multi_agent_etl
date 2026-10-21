# Structural Mapping Evaluation Report

## Summary (MAP only)

| Metric | Value |
|--------|-------|
| Gold fields (unique table.field) | 60 |
| Gold MAP rows (sources) | 79 |
| TP | 69 |
| FP (over-mapping) | 55 |
| FN (under-mapping) | 10 |
| **Micro Precision** | **0.5565** |
| **Micro Recall** | **0.8734** |
| **Micro F1** | **0.6798** |
| Macro Precision | 0.5983 |
| Macro Recall | 0.8500 |
| Macro F1 | 0.6689 |
| Over-mapping rate | 0.4435 |
| Under-mapping rate | 0.1266 |

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
| death | death_date | encounters.START, patients.DEATHDATE | patients.DEATHDATE | 1.00 | 0.50 | 0.67 | 1 | 0 | 1 |
| death | death_datetime | encounters.START | patients.DEATHDATE | 0.00 | 0.00 | 0.00 | 0 | 1 | 1 |
| death | person_id | encounters.PATIENT, patients.Id | patients.Id | 1.00 | 0.50 | 0.67 | 1 | 0 | 1 |
| drug_exposure | days_supply | medications.START+STOP | — | 0.00 | 0.00 | 0.00 | 0 | 0 | 1 |
| drug_exposure | drug_exposure_end_date | medications.STOP | allergies.STOP, medications.STOP, procedures.STOP | 0.33 | 1.00 | 0.50 | 1 | 2 | 0 |
| drug_exposure | drug_exposure_end_datetime | medications.STOP | allergies.STOP, medications.STOP, procedures.STOP | 0.33 | 1.00 | 0.50 | 1 | 2 | 0 |
| drug_exposure | drug_exposure_start_date | immunizations.DATE, medications.START | allergies.START, immunizations.DATE, medications.START, procedures.START | 0.50 | 1.00 | 0.67 | 2 | 2 | 0 |
| drug_exposure | drug_exposure_start_datetime | immunizations.DATE, medications.START | allergies.START, immunizations.DATE, medications.START, procedures.START | 0.50 | 1.00 | 0.67 | 2 | 2 | 0 |
| drug_exposure | drug_source_value | immunizations.CODE, medications.CODE | allergies.CODE, immunizations.CODE, medications.CODE, procedures.CODE | 0.50 | 1.00 | 0.67 | 2 | 2 | 0 |
| drug_exposure | person_id | immunizations.PATIENT, medications.PATIENT | allergies.PATIENT, immunizations.PATIENT, medications.PATIENT, procedures.PATIENT | 0.50 | 1.00 | 0.67 | 2 | 2 | 0 |
| drug_exposure | quantity | medications.DISPENSES | medications.DISPENSES | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| drug_exposure | visit_occurrence_id | immunizations.ENCOUNTER, medications.ENCOUNTER | allergies.ENCOUNTER, immunizations.ENCOUNTER, medications.ENCOUNTER, procedures.ENCOUNTER | 0.50 | 1.00 | 0.67 | 2 | 2 | 0 |
| measurement | measurement_date | observations.DATE, procedures.START | allergies.START, observations.DATE, procedures.START | 0.67 | 1.00 | 0.80 | 2 | 1 | 0 |
| measurement | measurement_datetime | observations.DATE | allergies.START, observations.DATE, procedures.START | 0.33 | 1.00 | 0.50 | 1 | 2 | 0 |
| measurement | measurement_source_value | observations.CODE, procedures.CODE | allergies.CODE, observations.CODE, procedures.CODE | 0.67 | 1.00 | 0.80 | 2 | 1 | 0 |
| measurement | person_id | observations.PATIENT, procedures.PATIENT | allergies.PATIENT, observations.PATIENT, procedures.PATIENT | 0.67 | 1.00 | 0.80 | 2 | 1 | 0 |
| measurement | unit_source_value | observations.UNITS | observations.UNITS | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| measurement | value_as_number | observations.VALUE | observations.VALUE | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| measurement | value_source_value | observations.VALUE | allergies.DESCRIPTION, observations.VALUE | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| measurement | visit_occurrence_id | observations.ENCOUNTER, procedures.ENCOUNTER | allergies.ENCOUNTER, observations.ENCOUNTER, procedures.ENCOUNTER | 0.67 | 1.00 | 0.80 | 2 | 1 | 0 |
| observation | observation_date | allergies.START, conditions.START, observations.DATE | allergies.START, conditions.START, encounters.START, observations.DATE, procedures.START | 0.60 | 1.00 | 0.75 | 3 | 2 | 0 |
| observation | observation_source_value | allergies.CODE, conditions.CODE, observations.CODE | allergies.CODE, conditions.CODE, encounters.CODE, observations.CODE, procedures.CODE | 0.60 | 1.00 | 0.75 | 3 | 2 | 0 |
| observation | person_id | allergies.PATIENT, conditions.PATIENT, observations.PATIENT | allergies.PATIENT, conditions.PATIENT, encounters.PATIENT, observations.PATIENT, procedures.PATIENT | 0.60 | 1.00 | 0.75 | 3 | 2 | 0 |
| observation | visit_occurrence_id | allergies.ENCOUNTER, conditions.ENCOUNTER, observations.ENCOUNTER | allergies.ENCOUNTER, conditions.ENCOUNTER, encounters.Id, observations.ENCOUNTER, procedures.ENCOUNTER | 0.60 | 1.00 | 0.75 | 3 | 2 | 0 |
| observation_period | observation_period_end_date | encounters.STOP | encounters.STOP | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| observation_period | observation_period_start_date | encounters.START | encounters.START | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| observation_period | person_id | encounters.PATIENT | patients.Id | 0.00 | 0.00 | 0.00 | 0 | 1 | 1 |
| person | birth_datetime | patients.BIRTHDATE | patients.BIRTHDATE | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | day_of_birth | patients.BIRTHDATE | patients.BIRTHDATE | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | death_datetime | patients.DEATHDATE | — | 0.00 | 0.00 | 0.00 | 0 | 0 | 1 |
| person | ethnicity_source_value | patients.ETHNICITY | patients.ETHNICITY | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | gender_source_value | patients.GENDER | patients.GENDER | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | month_of_birth | patients.BIRTHDATE | patients.BIRTHDATE | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | person_id | patients.Id | patients.Id | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | person_source_value | patients.Id | patients.Id | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | race_source_value | patients.RACE | patients.RACE | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| person | year_of_birth | patients.BIRTHDATE | patients.BIRTHDATE | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| procedure_occurrence | person_id | procedures.PATIENT | allergies.PATIENT, encounters.PATIENT, observations.PATIENT, procedures.PATIENT | 0.25 | 1.00 | 0.40 | 1 | 3 | 0 |
| procedure_occurrence | procedure_date | procedures.START | allergies.START, encounters.START, observations.DATE, procedures.START | 0.25 | 1.00 | 0.40 | 1 | 3 | 0 |
| procedure_occurrence | procedure_datetime | procedures.START | encounters.START, observations.DATE, procedures.START | 0.33 | 1.00 | 0.50 | 1 | 2 | 0 |
| procedure_occurrence | procedure_end_date | procedures.STOP | encounters.STOP, procedures.STOP | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| procedure_occurrence | procedure_end_datetime | procedures.STOP | encounters.STOP, procedures.STOP | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| procedure_occurrence | procedure_source_value | procedures.CODE | allergies.CODE, encounters.CODE, observations.CODE, procedures.CODE | 0.25 | 1.00 | 0.40 | 1 | 3 | 0 |
| procedure_occurrence | provider_id | encounters.PROVIDER | — | 0.00 | 0.00 | 0.00 | 0 | 0 | 1 |
| procedure_occurrence | visit_occurrence_id | procedures.ENCOUNTER | allergies.ENCOUNTER, encounters.Id, observations.ENCOUNTER, procedures.ENCOUNTER | 0.25 | 1.00 | 0.40 | 1 | 3 | 0 |
| visit_occurrence | person_id | encounters.PATIENT | encounters.PATIENT | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | provider_id | encounters.PROVIDER | — | 0.00 | 0.00 | 0.00 | 0 | 0 | 1 |
| visit_occurrence | visit_end_date | encounters.STOP | encounters.STOP | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_end_datetime | encounters.STOP | encounters.STOP | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_source_value | encounters.Id | encounters.ENCOUNTERCLASS | 0.00 | 0.00 | 0.00 | 0 | 1 | 1 |
| visit_occurrence | visit_start_date | encounters.START | encounters.START | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_start_datetime | encounters.START | encounters.START | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |

### Agent fields not in gold (informational)

| Table | Field | Agent sources |
|-------|-------|---------------|
| condition_occurrence | visit_detail_id | conditions.ENCOUNTER, procedures.ENCOUNTER |
| drug_exposure | dose_unit_source_value | medications.DESCRIPTION |
| drug_exposure | route_source_value | medications.DESCRIPTION |
| drug_exposure | verbatim_end_date | medications.STOP, procedures.STOP |
| drug_exposure | visit_detail_id | allergies.ENCOUNTER, immunizations.ENCOUNTER, medications.ENCOUNTER, procedures.ENCOUNTER |
| measurement | measurement_time | observations.DATE, procedures.START |
| measurement | visit_detail_id | allergies.ENCOUNTER, observations.ENCOUNTER, procedures.ENCOUNTER |
| observation | observation_datetime | allergies.START, conditions.START, encounters.START, observations.DATE, procedures.START |
| observation | observation_event_id | conditions.ENCOUNTER, encounters.Id |
| observation | observation_id | encounters.Id |
| observation | qualifier_source_value | allergies.TYPE |
| observation | unit_source_value | observations.UNITS |
| observation | value_as_number | observations.VALUE, procedures.BASE_COST |
| observation | value_as_string | allergies.DESCRIPTION, conditions.DESCRIPTION, encounters.DESCRIPTION, observations.VALUE, procedures.DESCRIPTION |
| observation | value_source_value | allergies.REACTION1, conditions.DESCRIPTION, observations.VALUE, procedures.DESCRIPTION |
| observation | visit_detail_id | allergies.ENCOUNTER, conditions.ENCOUNTER, encounters.Id, observations.ENCOUNTER, procedures.ENCOUNTER |
| procedure_occurrence | visit_detail_id | allergies.ENCOUNTER, encounters.Id, observations.ENCOUNTER, procedures.ENCOUNTER |
| visit_occurrence | visit_occurrence_id | encounters.Id |

## Notes

- Only **structural MAP** pairs are scored (source_table + source_field).
- `*_concept_id` / `*_source_concept_id` / `*_type_concept_id` are excluded (semantic or fixed).
- TP = agent source ∈ gold sources for that field.
- FP = agent proposed a source not in gold (over-mapping).
- FN = gold source missing from agent (under-mapping).
