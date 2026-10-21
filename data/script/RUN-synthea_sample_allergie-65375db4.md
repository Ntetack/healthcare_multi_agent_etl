# Mapping Evaluation Report

## Global Score

**Scoped Global Score: 0.7194**

Formula: `0.45 * Micro-F1 + 0.25 * (1 - OverMappingRate) + 0.20 * Micro-Recall + 0.10 * NO_MAPPING agreement`

## MAP fields (Precision / Recall / F1)

| Metric | Value |
|--------|-------|
| TP | 66 |
| FP (over-mapping) | 55 |
| FN (under-mapping) | 8 |
| Micro Precision | 0.5455 |
| Micro Recall | 0.8919 |
| Micro F1 | 0.6769 |
| Macro Precision | 0.6006 |
| Macro Recall | 0.8596 |
| Macro F1 | 0.6778 |
| Over-mapping rate | 0.4545 |
| Under-mapping rate | 0.1081 |

### Per-field MAP details

| Table | Field | Gold sources | Agent sources | P | R | F1 | TP | FP | FN |
|-------|-------|--------------|---------------|---|---|----|----|----|----|
| condition_occurrence | condition_end_date | conditions.STOP | conditions.STOP, procedures.STOP | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| condition_occurrence | condition_end_datetime | conditions.STOP | procedures.STOP | 0.00 | 0.00 | 0.00 | 0 | 1 | 1 |
| condition_occurrence | condition_source_value | conditions.CODE | conditions.CODE, procedures.CODE | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| condition_occurrence | condition_start_date | conditions.START | conditions.START, procedures.START | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| condition_occurrence | condition_start_datetime | conditions.START | procedures.START | 0.00 | 0.00 | 0.00 | 0 | 1 | 1 |
| condition_occurrence | person_id | conditions.PATIENT | conditions.PATIENT, procedures.PATIENT | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| condition_occurrence | visit_occurrence_id | conditions.ENCOUNTER | conditions.ENCOUNTER, procedures.ENCOUNTER | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| death | cause_source_value | encounters.REASONCODE | — | 0.00 | 0.00 | 0.00 | 0 | 0 | 1 |
| death | death_date | patients.DEATHDATE | patients.DEATHDATE | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| death | person_id | patients.Id | patients.Id | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| drug_exposure | drug_exposure_end_date | medications.STOP | allergies.STOP, medications.STOP, procedures.STOP | 0.33 | 1.00 | 0.50 | 1 | 2 | 0 |
| drug_exposure | drug_exposure_end_datetime | medications.STOP | allergies.STOP, medications.STOP, procedures.STOP | 0.33 | 1.00 | 0.50 | 1 | 2 | 0 |
| drug_exposure | drug_exposure_start_date | immunizations.DATE, medications.START | allergies.START, immunizations.DATE, medications.START, procedures.START | 0.50 | 1.00 | 0.67 | 2 | 2 | 0 |
| drug_exposure | drug_exposure_start_datetime | immunizations.DATE, medications.START | allergies.START, immunizations.DATE, medications.START, procedures.START | 0.50 | 1.00 | 0.67 | 2 | 2 | 0 |
| drug_exposure | drug_source_value | immunizations.CODE, medications.CODE | allergies.CODE, immunizations.CODE, medications.CODE, procedures.CODE | 0.50 | 1.00 | 0.67 | 2 | 2 | 0 |
| drug_exposure | person_id | immunizations.PATIENT, medications.PATIENT | allergies.PATIENT, immunizations.PATIENT, medications.PATIENT, procedures.PATIENT | 0.50 | 1.00 | 0.67 | 2 | 2 | 0 |
| drug_exposure | visit_occurrence_id | immunizations.ENCOUNTER, medications.ENCOUNTER | allergies.ENCOUNTER, immunizations.ENCOUNTER, medications.ENCOUNTER, procedures.ENCOUNTER | 0.50 | 1.00 | 0.67 | 2 | 2 | 0 |
| measurement | measurement_date | observations.DATE, procedures.START | encounters.START, observations.DATE, procedures.START | 0.67 | 1.00 | 0.80 | 2 | 1 | 0 |
| measurement | measurement_datetime | observations.DATE | encounters.START, observations.DATE, procedures.START | 0.33 | 1.00 | 0.50 | 1 | 2 | 0 |
| measurement | measurement_source_value | observations.CODE, procedures.CODE | encounters.CODE, observations.CODE, procedures.CODE | 0.67 | 1.00 | 0.80 | 2 | 1 | 0 |
| measurement | person_id | observations.PATIENT, procedures.PATIENT | encounters.PATIENT, observations.PATIENT, procedures.PATIENT | 0.67 | 1.00 | 0.80 | 2 | 1 | 0 |
| measurement | unit_source_value | observations.UNITS | observations.UNITS | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| measurement | value_as_number | observations.VALUE | observations.VALUE | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| measurement | value_source_value | observations.VALUE | observations.VALUE | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| measurement | visit_occurrence_id | observations.ENCOUNTER, procedures.ENCOUNTER | encounters.Id, observations.ENCOUNTER, procedures.ENCOUNTER | 0.67 | 1.00 | 0.80 | 2 | 1 | 0 |
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
| procedure_occurrence | procedure_end_date | procedures.STOP | allergies.STOP, encounters.STOP, procedures.STOP | 0.33 | 1.00 | 0.50 | 1 | 2 | 0 |
| procedure_occurrence | procedure_end_datetime | procedures.STOP | encounters.STOP, procedures.STOP | 0.50 | 1.00 | 0.67 | 1 | 1 | 0 |
| procedure_occurrence | procedure_source_value | procedures.CODE | allergies.CODE, encounters.CODE, observations.CODE, procedures.CODE | 0.25 | 1.00 | 0.40 | 1 | 3 | 0 |
| procedure_occurrence | visit_occurrence_id | procedures.ENCOUNTER | allergies.ENCOUNTER, encounters.Id, observations.ENCOUNTER, procedures.ENCOUNTER | 0.25 | 1.00 | 0.40 | 1 | 3 | 0 |
| visit_occurrence | person_id | encounters.PATIENT | patients.Id | 0.00 | 0.00 | 0.00 | 0 | 1 | 1 |
| visit_occurrence | provider_id | encounters.PROVIDER | — | 0.00 | 0.00 | 0.00 | 0 | 0 | 1 |
| visit_occurrence | visit_concept_id | encounters.ENCOUNTERCLASS | encounters.ENCOUNTERCLASS | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_end_date | encounters.STOP | encounters.STOP | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_end_datetime | encounters.STOP | encounters.STOP | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_source_value | encounters.Id | encounters.CODE | 0.00 | 0.00 | 0.00 | 0 | 1 | 1 |
| visit_occurrence | visit_start_date | encounters.START | encounters.START | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |
| visit_occurrence | visit_start_datetime | encounters.START | encounters.START | 1.00 | 1.00 | 1.00 | 1 | 0 | 0 |

## FIXED fields (`*_type_concept_id`)

**Accuracy: 1.0000** (8/8)

| Table | Field | Expected value | Mentioned | Proposed source? | OK |
|-------|-------|----------------|-----------|------------------|----|
| condition_occurrence | condition_type_concept_id | 32827 | True | False | True |
| death | death_type_concept_id | 32817 | True | False | True |
| drug_exposure | drug_type_concept_id | 32838 | True | False | True |
| measurement | measurement_type_concept_id | 32827 | True | False | True |
| observation | observation_type_concept_id | 38000280 | True | False | True |
| observation_period | period_type_concept_id | 32882 | True | False | True |
| procedure_occurrence | procedure_type_concept_id | 32827 | True | False | True |
| visit_occurrence | visit_type_concept_id | 32827 | True | False | True |

## NO_MAPPING fields

**Agreement: 1.0000** (9/9)

| Table | Field | Agent proposed source? | Sources | OK |
|-------|-------|------------------------|---------|----|
| condition_occurrence | condition_status_source_value | False | — | True |
| condition_occurrence | provider_id | False | — | True |
| drug_exposure | quantity | False | — | True |
| drug_exposure | route_source_value | False | — | True |
| procedure_occurrence | modifier_source_value | False | — | True |
| procedure_occurrence | quantity | False | — | True |
| visit_occurrence | admitted_from_source_value | False | — | True |
| visit_occurrence | care_site_id | False | — | True |
| visit_occurrence | discharge_to_source_value | False | — | True |

## Notes

- Semantic fields (`*_concept_id`, `*_source_concept_id` except type) are **out of scope**.
- FIXED fields are successful when the agent acknowledges the field without attaching a source column.
- Over-mapping = agent sources not in gold; under-mapping = gold sources missing from agent.
