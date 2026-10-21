# Rapport de provenance — RUN-synthea_sample_fix2-5af299e8

## 1. Provenance au niveau des lignes (tables OMOP finales)

**condition_occurrence** — 1728 lignes au total
  - conditions: 1724 lignes (100%)
  - procedures: 4 lignes (0%)

**drug_exposure** — 5446 lignes au total
  - medications: 3850 lignes (71%)
  - immunizations: 1549 lignes (28%)
  - procedures: 45 lignes (1%)
  - allergies: 2 lignes (0%)

**measurement** — 46728 lignes au total
  - observations: 42557 lignes (91%)
  - procedures: 4170 lignes (9%)
  - encounters: 1 lignes (0%)

**observation** — 31885 lignes au total
  - observations: 23030 lignes (72%)
  - encounters: 3943 lignes (12%)
  - procedures: 3017 lignes (9%)
  - conditions: 1793 lignes (6%)
  - allergies: 102 lignes (0%)

**procedure_occurrence** — 10272 lignes au total
  - procedures: 8643 lignes (84%)
  - encounters: 1627 lignes (16%)
  - allergies: 1 lignes (0%)
  - observations: 1 lignes (0%)

**visit_occurrence** — 5571 lignes au total
  - encounters: 5571 lignes (100%)

## 2. Provenance au niveau des champs structurels

**condition_occurrence**
  - condition_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - condition_end_date ← conditions.STOP (confiance=0.95)
  - condition_end_date ← procedures.STOP (confiance=0.95)
  - condition_end_datetime ← conditions.STOP (confiance=0.95)
  - condition_end_datetime ← procedures.STOP (confiance=0.95)
  - condition_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - condition_source_value ← conditions.CODE (confiance=0.90)
  - condition_source_value ← procedures.CODE (confiance=0.90)
  - condition_start_date ← conditions.START (confiance=0.95)
  - condition_start_date ← procedures.START (confiance=0.95)
  - condition_start_datetime ← conditions.START (confiance=0.95)
  - condition_start_datetime ← procedures.START (confiance=0.95)
  - condition_status_concept_id: ❌ non résolu (Paired field 'condition_status_source_value' was not resolved in this batch.)
  - condition_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← conditions.PATIENT (confiance=0.90)
  - person_id ← procedures.PATIENT (confiance=0.95)
  - visit_detail_id ← conditions.ENCOUNTER (confiance=0.80)
  - visit_occurrence_id ← conditions.ENCOUNTER (confiance=0.85)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.95)

**death**
  - cause_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - cause_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - death_date ← patients.DEATHDATE (confiance=1.00)
  - death_datetime ← patients.DEATHDATE (confiance=0.95) 🔁 (résolu par reprise)
  - death_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← patients.Id (confiance=1.00)

**drug_exposure**
  - drug_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - drug_exposure_end_date ← allergies.STOP (confiance=0.60)
  - drug_exposure_end_date ← immunizations.DATE (confiance=0.80)
  - drug_exposure_end_date ← medications.STOP (confiance=0.95)
  - drug_exposure_end_date ← procedures.STOP (confiance=0.80)
  - drug_exposure_end_datetime ← immunizations.DATE (confiance=0.80)
  - drug_exposure_end_datetime ← medications.STOP (confiance=0.95)
  - drug_exposure_end_datetime ← procedures.STOP (confiance=0.90)
  - drug_exposure_start_date ← allergies.START (confiance=0.80)
  - drug_exposure_start_date ← immunizations.DATE (confiance=0.95)
  - drug_exposure_start_date ← medications.START (confiance=0.95)
  - drug_exposure_start_date ← procedures.START (confiance=0.80)
  - drug_exposure_start_datetime ← immunizations.DATE (confiance=0.95)
  - drug_exposure_start_datetime ← medications.START (confiance=0.95)
  - drug_exposure_start_datetime ← procedures.START (confiance=0.90)
  - drug_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - drug_source_value ← allergies.DESCRIPTION (confiance=0.40) 🔁 (résolu par reprise)
  - drug_source_value ← immunizations.CODE (confiance=0.85) 🔁 (résolu par reprise)
  - drug_source_value ← medications.CODE (confiance=0.90) 🔁 (résolu par reprise)
  - drug_source_value ← procedures.CODE (confiance=0.95) 🔁 (résolu par reprise)
  - drug_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← allergies.PATIENT (confiance=0.90)
  - person_id ← immunizations.PATIENT (confiance=0.95)
  - person_id ← medications.PATIENT (confiance=0.95)
  - person_id ← procedures.PATIENT (confiance=0.90)
  - quantity ← medications.DISPENSES (confiance=0.85)
  - refills ← medications.DISPENSES (confiance=0.60)
  - route_concept_id: ❌ non résolu (Paired field 'route_source_value' was not resolved in this batch.)
  - stop_reason ← medications.REASONCODE (confiance=0.75)
  - verbatim_end_date ← immunizations.DATE (confiance=0.90) 🔁 (résolu par reprise)
  - verbatim_end_date ← medications.STOP (confiance=0.95) 🔁 (résolu par reprise)
  - verbatim_end_date ← procedures.STOP (confiance=0.85) 🔁 (résolu par reprise)
  - visit_detail_id ← immunizations.ENCOUNTER (confiance=0.90)
  - visit_detail_id ← medications.ENCOUNTER (confiance=0.90)
  - visit_detail_id ← procedures.ENCOUNTER (confiance=0.70)
  - visit_occurrence_id ← allergies.ENCOUNTER (confiance=0.90) 🔁 (résolu par reprise)
  - visit_occurrence_id ← immunizations.ENCOUNTER (confiance=0.90) 🔁 (résolu par reprise)
  - visit_occurrence_id ← medications.ENCOUNTER (confiance=0.90) 🔁 (résolu par reprise)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.60) 🔁 (résolu par reprise)

**measurement**
  - meas_event_field_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - measurement_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - measurement_date ← encounters.START (confiance=0.90)
  - measurement_date ← observations.DATE (confiance=0.95)
  - measurement_date ← procedures.START (confiance=0.95)
  - measurement_datetime ← encounters.START (confiance=0.90)
  - measurement_datetime ← observations.DATE (confiance=0.95)
  - measurement_datetime ← procedures.START (confiance=0.95)
  - measurement_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - measurement_source_value ← encounters.CODE (confiance=0.65)
  - measurement_source_value ← observations.CODE (confiance=0.90)
  - measurement_source_value ← procedures.CODE (confiance=0.95)
  - measurement_time ← encounters.START (confiance=0.90)
  - measurement_time ← observations.DATE (confiance=0.90)
  - measurement_time ← procedures.START (confiance=0.90)
  - measurement_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - operator_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← encounters.PATIENT (confiance=0.95)
  - person_id ← observations.PATIENT (confiance=0.95)
  - person_id ← procedures.PATIENT (confiance=0.95)
  - unit_source_value ← observations.UNITS (confiance=0.95)
  - value_as_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - value_as_number ← observations.VALUE (confiance=0.95) 🔁 (résolu par reprise)
  - value_as_number ← procedures.BASE_COST (confiance=0.40) 🔁 (résolu par reprise)
  - value_source_value ← encounters.CODE (confiance=0.75) 🔁 (résolu par reprise)
  - value_source_value ← observations.VALUE (confiance=0.95) 🔁 (résolu par reprise)
  - value_source_value ← procedures.DESCRIPTION (confiance=0.60) 🔁 (résolu par reprise)
  - visit_detail_id ← encounters.Id (confiance=0.85) 🔁 (résolu par reprise)
  - visit_detail_id ← observations.ENCOUNTER (confiance=0.85) 🔁 (résolu par reprise)
  - visit_detail_id ← procedures.ENCOUNTER (confiance=0.90) 🔁 (résolu par reprise)
  - visit_occurrence_id ← encounters.Id (confiance=0.95)
  - visit_occurrence_id ← observations.ENCOUNTER (confiance=0.90)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.90)

**observation**
  - obs_event_field_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - observation_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - observation_date ← allergies.START (confiance=0.95)
  - observation_date ← conditions.START (confiance=0.90)
  - observation_date ← encounters.START (confiance=0.90)
  - observation_date ← observations.DATE (confiance=0.90)
  - observation_date ← procedures.START (confiance=0.90)
  - observation_datetime ← allergies.START (confiance=0.70)
  - observation_datetime ← conditions.START (confiance=0.60)
  - observation_datetime ← encounters.START (confiance=0.90)
  - observation_datetime ← observations.DATE (confiance=0.90)
  - observation_datetime ← procedures.START (confiance=0.95)
  - observation_event_id ← encounters.Id (confiance=0.80)
  - observation_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - observation_source_value ← allergies.DESCRIPTION (confiance=0.90)
  - observation_source_value ← conditions.CODE (confiance=0.90)
  - observation_source_value ← encounters.CODE (confiance=0.80)
  - observation_source_value ← observations.CODE (confiance=0.90)
  - observation_source_value ← procedures.CODE (confiance=0.90)
  - observation_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← allergies.PATIENT (confiance=0.95)
  - person_id ← conditions.PATIENT (confiance=0.95)
  - person_id ← encounters.PATIENT (confiance=0.95)
  - person_id ← observations.PATIENT (confiance=0.90)
  - person_id ← procedures.PATIENT (confiance=0.95)
  - qualifier_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - qualifier_source_value ← allergies.SEVERITY1 (confiance=0.85)
  - qualifier_source_value ← encounters.ENCOUNTERCLASS (confiance=0.50)
  - unit_source_value ← observations.UNITS (confiance=0.90)
  - value_as_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - value_as_number ← encounters.TOTAL_CLAIM_COST (confiance=0.60)
  - value_as_number ← observations.VALUE (confiance=0.80)
  - value_as_string ← allergies.DESCRIPTION (confiance=0.80)
  - value_as_string ← conditions.DESCRIPTION (confiance=0.85)
  - value_as_string ← encounters.DESCRIPTION (confiance=0.70)
  - value_as_string ← observations.VALUE (confiance=0.80)
  - value_as_string ← procedures.DESCRIPTION (confiance=0.70)
  - value_source_value ← allergies.DESCRIPTION (confiance=0.80) 🔁 (résolu par reprise)
  - value_source_value ← encounters.DESCRIPTION (confiance=0.75) 🔁 (résolu par reprise)
  - value_source_value ← observations.VALUE (confiance=0.98) 🔁 (résolu par reprise)
  - value_source_value ← procedures.DESCRIPTION (confiance=0.75) 🔁 (résolu par reprise)
  - visit_detail_id ← allergies.ENCOUNTER (confiance=0.85) 🔁 (résolu par reprise)
  - visit_detail_id ← conditions.ENCOUNTER (confiance=0.80) 🔁 (résolu par reprise)
  - visit_detail_id ← encounters.Id (confiance=0.85) 🔁 (résolu par reprise)
  - visit_detail_id ← observations.ENCOUNTER (confiance=0.95) 🔁 (résolu par reprise)
  - visit_detail_id ← procedures.ENCOUNTER (confiance=0.85) 🔁 (résolu par reprise)
  - visit_occurrence_id ← allergies.ENCOUNTER (confiance=0.95)
  - visit_occurrence_id ← conditions.ENCOUNTER (confiance=0.90)
  - visit_occurrence_id ← encounters.Id (confiance=0.95)
  - visit_occurrence_id ← observations.ENCOUNTER (confiance=0.90)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.90)

**observation_period**
  - observation_period_end_date ← patients.DEATHDATE (confiance=0.80)
  - observation_period_start_date ← encounters.START (confiance=0.85)
  - period_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← patients.Id (confiance=0.95)

**person**
  - birth_datetime ← patients.BIRTHDATE (confiance=0.95) 🔁 (résolu par reprise)
  - day_of_birth ← patients.BIRTHDATE (confiance=0.95)
  - ethnicity_source_value ← patients.ETHNICITY (confiance=0.95)
  - gender_source_value ← patients.GENDER (confiance=0.95)
  - month_of_birth ← patients.BIRTHDATE (confiance=0.95)
  - person_id ← patients.Id (confiance=0.90)
  - person_source_value ← patients.Id (confiance=0.95)
  - race_source_value ← patients.RACE (confiance=0.95)
  - year_of_birth ← patients.BIRTHDATE (confiance=0.95)

**procedure_occurrence**
  - modifier_concept_id: ❌ non résolu (Paired field 'modifier_source_value' was not resolved in this batch.)
  - person_id ← allergies.PATIENT (confiance=0.95)
  - person_id ← encounters.PATIENT (confiance=0.95)
  - person_id ← observations.PATIENT (confiance=0.95)
  - person_id ← procedures.PATIENT (confiance=0.95)
  - procedure_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - procedure_date ← allergies.START (confiance=0.85)
  - procedure_date ← encounters.START (confiance=0.90)
  - procedure_date ← observations.DATE (confiance=0.95)
  - procedure_date ← procedures.START (confiance=0.95)
  - procedure_datetime ← allergies.START (confiance=0.75)
  - procedure_datetime ← encounters.START (confiance=0.90)
  - procedure_datetime ← observations.DATE (confiance=0.95)
  - procedure_datetime ← procedures.START (confiance=0.95)
  - procedure_end_date ← allergies.STOP (confiance=0.60)
  - procedure_end_date ← encounters.STOP (confiance=0.90)
  - procedure_end_date ← procedures.STOP (confiance=0.95)
  - procedure_end_datetime ← encounters.STOP (confiance=0.90)
  - procedure_end_datetime ← procedures.STOP (confiance=0.95)
  - procedure_occurrence_id ← encounters.Id (confiance=0.90)
  - procedure_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - procedure_source_value ← allergies.CODE (confiance=0.95)
  - procedure_source_value ← encounters.CODE (confiance=0.90)
  - procedure_source_value ← observations.CODE (confiance=0.90)
  - procedure_source_value ← procedures.CODE (confiance=0.95)
  - procedure_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - visit_detail_id ← allergies.ENCOUNTER (confiance=0.80) 🔁 (résolu par reprise)
  - visit_detail_id ← encounters.Id (confiance=0.80) 🔁 (résolu par reprise)
  - visit_detail_id ← procedures.ENCOUNTER (confiance=0.80) 🔁 (résolu par reprise)
  - visit_occurrence_id ← allergies.ENCOUNTER (confiance=0.95)
  - visit_occurrence_id ← encounters.Id (confiance=0.95)
  - visit_occurrence_id ← observations.ENCOUNTER (confiance=0.85)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.95)

**visit_occurrence**
  - admitted_from_concept_id: ❌ non résolu (Paired field 'admitted_from_source_value' was not resolved in this batch.)
  - discharged_to_concept_id: ❌ non résolu (Paired field 'discharged_to_source_value' was not resolved in this batch.)
  - person_id ← patients.Id (confiance=0.95)
  - visit_end_date ← encounters.STOP (confiance=0.95)
  - visit_end_datetime ← encounters.STOP (confiance=0.95)
  - visit_occurrence_id ← encounters.Id (confiance=0.90)
  - visit_source_value ← encounters.DESCRIPTION (confiance=0.80)
  - visit_start_date ← encounters.START (confiance=0.95)
  - visit_start_datetime ← encounters.START (confiance=0.95)
  - visit_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )

## 3. Provenance au niveau des valeurs (champs codés, mécanisme 1)

**allergies**
  - allergies.CODE: 19 valeurs distinctes, 100% résolues
      -> observation: 17 valeurs
      -> drug_exposure: 1 valeurs
      -> procedure_occurrence: 1 valeurs

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

**patients**
  - _Déclarée, mais aucune valeur distincte produite pour ce batch._

**procedures**
  - procedures.CODE: 265 valeurs distinctes, 100% résolues
      -> procedure_occurrence: 150 valeurs
      -> observation: 56 valeurs
      -> measurement: 54 valeurs
      -> drug_exposure: 2 valeurs
      -> condition_occurrence: 2 valeurs
      -> AUCUN: 1 valeurs

## 4. Résolutions via mapping figé (fixed_value_mappings)

**person.ethnicity_concept_id** — 2 valeur(s) couverte(s) par le CSV
  - 'nonhispanic' -> concept_id=38003564
  - 'hispanic' -> concept_id=38003563

**person.race_concept_id** — 3 valeur(s) couverte(s) par le CSV
  - 'white' -> concept_id=8527
  - 'black' -> concept_id=8516
  - 'asian' -> concept_id=8515

**visit_occurrence.visit_concept_id** — 7 valeur(s) couverte(s) par le CSV
  - 'wellness' -> concept_id=9202
  - 'ambulatory' -> concept_id=9202
  - 'outpatient' -> concept_id=9202
  - 'emergency' -> concept_id=9203
  - 'urgentcare' -> concept_id=9203
  - 'inpatient' -> concept_id=9201
  - 'home' -> concept_id=581476

## 5. Jointures de vocabulaire local

_Aucun champ 'local' déclaré dans ce batch._
