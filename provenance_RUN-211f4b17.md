# Rapport de provenance — RUN-211f4b17

## 1. Provenance au niveau des lignes (tables OMOP finales)

**condition_occurrence** — 2050 lignes au total
  - conditions: 2047 lignes (100%)
  - procedures: 2 lignes (0%)
  - encounters: 1 lignes (0%)

**drug_exposure** — 7434 lignes au total
  - medications: 5665 lignes (76%)
  - immunizations: 1734 lignes (23%)
  - procedures: 35 lignes (0%)

**measurement** — 64585 lignes au total
  - observations: 59970 lignes (93%)
  - procedures: 4615 lignes (7%)

**observation** — 39973 lignes au total
  - observations: 27710 lignes (69%)
  - encounters: 6147 lignes (15%)
  - procedures: 3968 lignes (10%)
  - conditions: 2148 lignes (5%)

**procedure_occurrence** — 13170 lignes au total
  - procedures: 11281 lignes (86%)
  - encounters: 1886 lignes (14%)
  - observations: 3 lignes (0%)

## 2. Provenance au niveau des champs structurels

**condition_occurrence**
  - condition_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - condition_end_date ← conditions.STOP (confiance=0.95)
  - condition_end_date ← encounters.STOP (confiance=0.85)
  - condition_end_date ← procedures.STOP (confiance=0.85)
  - condition_end_datetime ← conditions.STOP (confiance=0.80)
  - condition_end_datetime ← encounters.STOP (confiance=0.90)
  - condition_end_datetime ← procedures.STOP (confiance=0.85)
  - condition_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - condition_source_value ← conditions.CODE (confiance=0.90)
  - condition_source_value ← encounters.REASONCODE (confiance=0.95)
  - condition_source_value ← procedures.REASONCODE (confiance=0.80)
  - condition_start_date ← conditions.START (confiance=0.95)
  - condition_start_date ← encounters.START (confiance=0.85)
  - condition_start_date ← procedures.START (confiance=0.90)
  - condition_start_datetime ← conditions.START (confiance=0.80)
  - condition_start_datetime ← encounters.START (confiance=0.90)
  - condition_start_datetime ← procedures.START (confiance=0.90)
  - condition_status_concept_id: ❌ non résolu (Paired field 'condition_status_source_value' was not resolved in this batch.)
  - condition_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← conditions.PATIENT (confiance=0.90)
  - person_id ← encounters.PATIENT (confiance=0.95)
  - person_id ← procedures.PATIENT (confiance=0.95)
  - provider_id ← encounters.PROVIDER (confiance=0.95)
  - visit_occurrence_id ← conditions.ENCOUNTER (confiance=0.90)
  - visit_occurrence_id ← encounters.Id (confiance=0.90)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.95)

**death**
  - cause_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - cause_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - death_date ← patients.DEATHDATE (confiance=0.95)
  - death_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← patients.Id (confiance=0.95)

**drug_exposure**
  - drug_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - drug_exposure_end_date ← medications.STOP (confiance=0.90)
  - drug_exposure_end_date ← procedures.STOP (confiance=0.50)
  - drug_exposure_end_datetime ← medications.STOP (confiance=0.90)
  - drug_exposure_end_datetime ← procedures.STOP (confiance=0.50)
  - drug_exposure_start_date ← immunizations.DATE (confiance=0.95)
  - drug_exposure_start_date ← medications.START (confiance=0.90)
  - drug_exposure_start_date ← procedures.START (confiance=0.50)
  - drug_exposure_start_datetime ← immunizations.DATE (confiance=0.95)
  - drug_exposure_start_datetime ← medications.START (confiance=0.90)
  - drug_exposure_start_datetime ← procedures.START (confiance=0.50)
  - drug_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - drug_source_value ← immunizations.CODE (confiance=0.85)
  - drug_source_value ← medications.CODE (confiance=0.80)
  - drug_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← immunizations.PATIENT (confiance=0.90)
  - person_id ← medications.PATIENT (confiance=0.90)
  - person_id ← procedures.PATIENT (confiance=0.70)
  - quantity ← medications.DISPENSES (confiance=0.70)
  - route_concept_id: ❌ non résolu (Paired field 'route_source_value' was not resolved in this batch.)
  - sig ← medications.DESCRIPTION (confiance=0.60)
  - visit_occurrence_id ← immunizations.ENCOUNTER (confiance=0.90)
  - visit_occurrence_id ← medications.ENCOUNTER (confiance=0.90)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.70)

**measurement**
  - meas_event_field_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - measurement_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - measurement_date ← observations.DATE (confiance=0.90)
  - measurement_date ← procedures.START (confiance=0.90)
  - measurement_datetime ← observations.DATE (confiance=0.95)
  - measurement_datetime ← procedures.START (confiance=0.95)
  - measurement_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - measurement_source_value ← observations.CODE (confiance=0.95)
  - measurement_source_value ← procedures.CODE (confiance=0.85)
  - measurement_time ← procedures.START (confiance=0.90)
  - measurement_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - operator_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← observations.PATIENT (confiance=0.90)
  - person_id ← procedures.PATIENT (confiance=0.85)
  - unit_source_value ← observations.UNITS (confiance=0.95)
  - value_as_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - value_as_number ← observations.VALUE (confiance=0.95)
  - value_source_value ← observations.VALUE (confiance=0.90)
  - visit_occurrence_id ← observations.ENCOUNTER (confiance=0.85)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.85)

**observation**
  - obs_event_field_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - observation_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - observation_date ← conditions.START (confiance=0.80)
  - observation_date ← encounters.START (confiance=0.80)
  - observation_date ← observations.DATE (confiance=0.95)
  - observation_date ← procedures.START (confiance=0.80)
  - observation_datetime ← encounters.START (confiance=0.80)
  - observation_datetime ← observations.DATE (confiance=0.95)
  - observation_datetime ← procedures.START (confiance=0.95)
  - observation_event_id ← encounters.Id (confiance=0.80)
  - observation_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - observation_source_value ← conditions.CODE (confiance=0.85)
  - observation_source_value ← encounters.CODE (confiance=0.80)
  - observation_source_value ← observations.CODE (confiance=0.95)
  - observation_source_value ← procedures.CODE (confiance=0.90)
  - observation_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← conditions.PATIENT (confiance=0.90)
  - person_id ← encounters.PATIENT (confiance=0.90)
  - person_id ← observations.PATIENT (confiance=0.95)
  - person_id ← procedures.PATIENT (confiance=0.95)
  - provider_id ← encounters.PROVIDER (confiance=0.95)
  - qualifier_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - unit_source_value ← observations.UNITS (confiance=0.95)
  - value_as_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - value_as_number ← observations.VALUE (confiance=0.90)
  - value_as_string ← conditions.DESCRIPTION (confiance=0.70)
  - value_as_string ← observations.VALUE (confiance=0.90)
  - value_as_string ← procedures.DESCRIPTION (confiance=0.70)
  - value_source_value ← observations.VALUE (confiance=0.95)
  - value_source_value ← procedures.DESCRIPTION (confiance=0.60)
  - visit_detail_id ← encounters.Id (confiance=0.75)
  - visit_occurrence_id ← conditions.ENCOUNTER (confiance=0.90)
  - visit_occurrence_id ← encounters.Id (confiance=0.85)
  - visit_occurrence_id ← observations.ENCOUNTER (confiance=0.95)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.95)

**observation_period**
  - observation_period_end_date ← encounters.STOP (confiance=0.80)
  - observation_period_start_date ← encounters.START (confiance=0.80)
  - period_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← patients.Id (confiance=1.00)

**person**
  - birth_datetime ← patients.BIRTHDATE (confiance=0.90)
  - day_of_birth ← patients.BIRTHDATE (confiance=0.95)
  - ethnicity_source_value ← patients.ETHNICITY (confiance=0.95)
  - gender_source_value ← patients.GENDER (confiance=0.95)
  - month_of_birth ← patients.BIRTHDATE (confiance=0.95)
  - person_id ← patients.Id (confiance=0.95)
  - person_source_value ← patients.Id (confiance=0.95)
  - race_source_value ← patients.RACE (confiance=0.95)
  - year_of_birth ← patients.BIRTHDATE (confiance=0.95)

**procedure_occurrence**
  - modifier_concept_id: ❌ non résolu (Paired field 'modifier_source_value' was not resolved in this batch.)
  - person_id ← encounters.PATIENT (confiance=0.90)
  - person_id ← observations.PATIENT (confiance=0.95)
  - person_id ← procedures.PATIENT (confiance=0.95)
  - procedure_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - procedure_date ← encounters.START (confiance=0.80)
  - procedure_date ← observations.DATE (confiance=0.95)
  - procedure_date ← procedures.START (confiance=0.95)
  - procedure_datetime ← encounters.START (confiance=0.80)
  - procedure_datetime ← observations.DATE (confiance=0.95)
  - procedure_datetime ← procedures.START (confiance=0.95)
  - procedure_end_date ← encounters.STOP (confiance=0.70)
  - procedure_end_date ← procedures.STOP (confiance=0.95)
  - procedure_end_datetime ← encounters.STOP (confiance=0.70)
  - procedure_end_datetime ← procedures.STOP (confiance=0.95)
  - procedure_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - procedure_source_value ← encounters.CODE (confiance=0.90)
  - procedure_source_value ← observations.CODE (confiance=0.85)
  - procedure_source_value ← procedures.CODE (confiance=0.95)
  - procedure_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - provider_id ← encounters.PROVIDER (confiance=0.90)
  - visit_detail_id ← encounters.Id (confiance=0.60)
  - visit_occurrence_id ← encounters.Id (confiance=0.60)
  - visit_occurrence_id ← observations.ENCOUNTER (confiance=0.90)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.95)

**visit_occurrence**
  - admitted_from_concept_id: ❌ non résolu (Paired field 'admitted_from_source_value' was not resolved in this batch.)
  - care_site_id ← encounters.ORGANIZATION (confiance=0.90)
  - discharged_to_concept_id: ❌ non résolu (Paired field 'discharged_to_source_value' was not resolved in this batch.)
  - person_id ← patients.Id (confiance=1.00)
  - provider_id ← encounters.PROVIDER (confiance=1.00)
  - visit_end_date ← encounters.STOP (confiance=1.00)
  - visit_end_datetime ← encounters.STOP (confiance=1.00)
  - visit_occurrence_id ← encounters.Id (confiance=0.90)
  - visit_source_value ← encounters.CODE (confiance=0.95)
  - visit_start_date ← encounters.START (confiance=1.00)
  - visit_start_datetime ← encounters.START (confiance=1.00)
  - visit_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )

## 3. Provenance au niveau des valeurs (champs codés, mécanisme 1)

**conditions**
  - conditions.CODE: 199 valeurs distinctes, 98% résolues
      -> condition_occurrence: 160 valeurs
      -> observation: 39 valeurs

**encounters**
  - encounters.CODE: 47 valeurs distinctes, 98% résolues
      -> observation: 37 valeurs
      -> procedure_occurrence: 9 valeurs
      -> condition_occurrence: 1 valeurs

**immunizations**
  - immunizations.CODE: 21 valeurs distinctes, 100% résolues
      -> drug_exposure: 21 valeurs

**medications**
  - medications.CODE: 139 valeurs distinctes, 100% résolues
      -> drug_exposure: 139 valeurs

**observations**
  - observations.CODE: 219 valeurs distinctes, 99% résolues
      -> measurement: 168 valeurs
      -> observation: 44 valeurs
      -> AUCUN: 5 valeurs
      -> procedure_occurrence: 2 valeurs

**procedures**
  - procedures.CODE: 217 valeurs distinctes, 100% résolues
      -> procedure_occurrence: 129 valeurs
      -> measurement: 46 valeurs
      -> observation: 38 valeurs
      -> drug_exposure: 2 valeurs
      -> AUCUN: 1 valeurs
      -> condition_occurrence: 1 valeurs
