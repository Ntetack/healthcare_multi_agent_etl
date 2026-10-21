# Rapport de provenance — RUN-synthea_sample-8ffb13cc

## 1. Provenance au niveau des lignes (tables OMOP finales)

**condition_occurrence** — 1728 lignes au total
  - conditions: 1724 lignes (100%)
  - procedures: 4 lignes (0%)

**drug_exposure** — 5444 lignes au total
  - medications: 3850 lignes (71%)
  - immunizations: 1549 lignes (28%)
  - procedures: 45 lignes (1%)

**measurement** — 46728 lignes au total
  - observations: 42557 lignes (91%)
  - procedures: 4170 lignes (9%)
  - encounters: 1 lignes (0%)

**observation** — 31783 lignes au total
  - observations: 23030 lignes (72%)
  - encounters: 3943 lignes (12%)
  - procedures: 3017 lignes (9%)
  - conditions: 1793 lignes (6%)

**procedure_occurrence** — 10271 lignes au total
  - procedures: 8643 lignes (84%)
  - encounters: 1627 lignes (16%)
  - observations: 1 lignes (0%)

## 2. Provenance au niveau des champs structurels

**condition_occurrence**
  - condition_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - condition_end_date ← conditions.STOP (confiance=0.95)
  - condition_end_date ← procedures.STOP (confiance=0.95)
  - condition_end_datetime ← conditions.STOP (confiance=0.70)
  - condition_end_datetime ← procedures.STOP (confiance=0.95)
  - condition_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - condition_source_value ← conditions.CODE (confiance=0.95)
  - condition_source_value ← procedures.CODE (confiance=0.80)
  - condition_start_date ← conditions.START (confiance=0.95)
  - condition_start_date ← procedures.START (confiance=0.95)
  - condition_start_datetime ← conditions.START (confiance=0.70)
  - condition_start_datetime ← procedures.START (confiance=0.95)
  - condition_status_concept_id: ❌ non résolu (Paired field 'condition_status_source_value' was not resolved in this batch.)
  - condition_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← conditions.PATIENT (confiance=0.90)
  - person_id ← procedures.PATIENT (confiance=0.90)
  - visit_occurrence_id ← conditions.ENCOUNTER (confiance=0.85)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.90)

**death**
  - cause_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - cause_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - death_date ← patients.DEATHDATE (confiance=1.00)
  - death_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← patients.Id (confiance=1.00)

**drug_exposure**
  - drug_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - drug_exposure_end_date ← medications.STOP (confiance=0.90)
  - drug_exposure_end_date ← procedures.STOP (confiance=0.60)
  - drug_exposure_end_datetime ← medications.STOP (confiance=0.95)
  - drug_exposure_end_datetime ← procedures.STOP (confiance=0.60)
  - drug_exposure_start_date ← immunizations.DATE (confiance=0.95)
  - drug_exposure_start_date ← medications.START (confiance=0.90)
  - drug_exposure_start_date ← procedures.START (confiance=0.60)
  - drug_exposure_start_datetime ← immunizations.DATE (confiance=0.95)
  - drug_exposure_start_datetime ← medications.START (confiance=0.95)
  - drug_exposure_start_datetime ← procedures.START (confiance=0.60)
  - drug_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - drug_source_value ← immunizations.DESCRIPTION (confiance=0.85)
  - drug_source_value ← medications.CODE (confiance=0.90)
  - drug_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← immunizations.PATIENT (confiance=0.95)
  - person_id ← medications.PATIENT (confiance=0.95)
  - person_id ← procedures.PATIENT (confiance=0.70)
  - refills ← medications.DISPENSES (confiance=0.70)
  - route_concept_id: ❌ non résolu (Paired field 'route_source_value' was not resolved in this batch.)
  - sig ← medications.DESCRIPTION (confiance=0.80)
  - visit_occurrence_id ← immunizations.ENCOUNTER (confiance=0.90)
  - visit_occurrence_id ← medications.ENCOUNTER (confiance=0.95)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.70)

**measurement**
  - meas_event_field_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - measurement_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - measurement_date ← encounters.START (confiance=0.85)
  - measurement_date ← observations.DATE (confiance=0.90)
  - measurement_date ← procedures.START (confiance=0.70)
  - measurement_datetime ← encounters.START (confiance=0.90)
  - measurement_datetime ← observations.DATE (confiance=0.95)
  - measurement_datetime ← procedures.START (confiance=0.90)
  - measurement_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - measurement_source_value ← encounters.CODE (confiance=0.75)
  - measurement_source_value ← observations.CODE (confiance=0.85)
  - measurement_source_value ← procedures.CODE (confiance=0.60)
  - measurement_time ← encounters.START (confiance=0.80)
  - measurement_time ← observations.DATE (confiance=0.90)
  - measurement_time ← procedures.START (confiance=0.70)
  - measurement_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - operator_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← encounters.PATIENT (confiance=0.95)
  - person_id ← observations.PATIENT (confiance=0.95)
  - person_id ← procedures.PATIENT (confiance=0.80)
  - unit_source_value ← observations.UNITS (confiance=0.95)
  - value_as_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - value_as_number ← observations.VALUE (confiance=0.95)
  - value_source_value ← observations.VALUE (confiance=0.95)
  - visit_detail_id ← encounters.Id (confiance=0.85)
  - visit_occurrence_id ← encounters.Id (confiance=0.95)
  - visit_occurrence_id ← observations.ENCOUNTER (confiance=0.90)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.80)

**observation**
  - obs_event_field_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - observation_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - observation_date ← conditions.START (confiance=0.95)
  - observation_date ← encounters.START (confiance=0.85)
  - observation_date ← observations.DATE (confiance=0.90)
  - observation_date ← procedures.START (confiance=0.90)
  - observation_datetime ← encounters.START (confiance=0.85)
  - observation_datetime ← observations.DATE (confiance=0.90)
  - observation_datetime ← procedures.START (confiance=0.95)
  - observation_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - observation_source_value ← conditions.CODE (confiance=0.95)
  - observation_source_value ← encounters.CODE (confiance=0.85)
  - observation_source_value ← observations.CODE (confiance=0.95)
  - observation_source_value ← procedures.CODE (confiance=0.85)
  - observation_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← conditions.PATIENT (confiance=0.85)
  - person_id ← encounters.PATIENT (confiance=0.95)
  - person_id ← observations.PATIENT (confiance=0.95)
  - person_id ← procedures.PATIENT (confiance=0.95)
  - qualifier_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - unit_source_value ← observations.UNITS (confiance=0.95)
  - value_as_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - value_as_number ← observations.VALUE (confiance=0.85)
  - value_as_string ← observations.VALUE (confiance=0.85)
  - value_as_string ← procedures.DESCRIPTION (confiance=0.80)
  - value_source_value ← conditions.DESCRIPTION (confiance=0.85)
  - value_source_value ← encounters.DESCRIPTION (confiance=0.75)
  - value_source_value ← observations.VALUE (confiance=0.85)
  - visit_occurrence_id ← conditions.ENCOUNTER (confiance=0.90)
  - visit_occurrence_id ← encounters.Id (confiance=0.90)
  - visit_occurrence_id ← observations.ENCOUNTER (confiance=0.85)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.90)

**observation_period**
  - observation_period_end_date ← patients.DEATHDATE (confiance=0.80)
  - period_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← patients.Id (confiance=1.00)

**person**
  - birth_datetime ← patients.BIRTHDATE (confiance=0.85)
  - day_of_birth ← patients.BIRTHDATE (confiance=0.90)
  - ethnicity_source_value ← patients.ETHNICITY (confiance=0.95)
  - gender_source_value ← patients.GENDER (confiance=0.95)
  - month_of_birth ← patients.BIRTHDATE (confiance=0.90)
  - person_id ← patients.Id (confiance=0.90)
  - person_source_value ← patients.Id (confiance=0.95)
  - race_source_value ← patients.RACE (confiance=0.95)
  - year_of_birth ← patients.BIRTHDATE (confiance=0.90)

**procedure_occurrence**
  - modifier_concept_id: ❌ non résolu (Paired field 'modifier_source_value' was not resolved in this batch.)
  - person_id ← encounters.PATIENT (confiance=0.95)
  - person_id ← observations.PATIENT (confiance=0.95)
  - person_id ← procedures.PATIENT (confiance=0.90)
  - procedure_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - procedure_date ← encounters.START (confiance=0.95)
  - procedure_date ← observations.DATE (confiance=0.95)
  - procedure_date ← procedures.START (confiance=0.95)
  - procedure_datetime ← encounters.START (confiance=0.95)
  - procedure_datetime ← observations.DATE (confiance=0.95)
  - procedure_datetime ← procedures.START (confiance=0.95)
  - procedure_end_date ← encounters.STOP (confiance=0.95)
  - procedure_end_date ← procedures.STOP (confiance=0.95)
  - procedure_end_datetime ← encounters.STOP (confiance=0.95)
  - procedure_end_datetime ← procedures.STOP (confiance=0.95)
  - procedure_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - procedure_source_value ← encounters.CODE (confiance=0.90)
  - procedure_source_value ← observations.CODE (confiance=0.95)
  - procedure_source_value ← procedures.CODE (confiance=0.95)
  - procedure_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - visit_occurrence_id ← encounters.Id (confiance=0.85)
  - visit_occurrence_id ← observations.ENCOUNTER (confiance=0.95)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.85)

**visit_occurrence**
  - admitted_from_concept_id: ❌ non résolu (Paired field 'admitted_from_source_value' was not resolved in this batch.)
  - discharged_to_concept_id: ❌ non résolu (Paired field 'discharged_to_source_value' was not resolved in this batch.)
  - person_id ← patients.Id (confiance=1.00)
  - visit_end_date ← encounters.STOP (confiance=1.00)
  - visit_end_datetime ← encounters.STOP (confiance=1.00)
  - visit_source_value ← encounters.CODE (confiance=0.95)
  - visit_start_date ← encounters.START (confiance=1.00)
  - visit_start_datetime ← encounters.START (confiance=1.00)
  - visit_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )

## 3. Provenance au niveau des valeurs (champs codés, mécanisme 1)

**conditions**
  - conditions.CODE: 186 valeurs distinctes, 98% résolues
      -> condition_occurrence: 154 valeurs
      -> observation: 32 valeurs

**encounters**
  - encounters.CODE: 44 valeurs distinctes, 98% résolues
      -> observation: 34 valeurs
      -> procedure_occurrence: 9 valeurs
      -> measurement: 1 valeurs

**immunizations**
  - immunizations.CODE: 22 valeurs distinctes, 100% résolues
      -> drug_exposure: 22 valeurs

**medications**
  - medications.CODE: 146 valeurs distinctes, 100% résolues
      -> drug_exposure: 146 valeurs

**observations**
  - observations.CODE: 243 valeurs distinctes, 96% résolues
      -> measurement: 188 valeurs
      -> observation: 51 valeurs
      -> AUCUN: 3 valeurs
      -> procedure_occurrence: 1 valeurs

**procedures**
  - procedures.CODE: 265 valeurs distinctes, 100% résolues
      -> procedure_occurrence: 150 valeurs
      -> observation: 56 valeurs
      -> measurement: 54 valeurs
      -> drug_exposure: 2 valeurs
      -> condition_occurrence: 2 valeurs
      -> AUCUN: 1 valeurs
