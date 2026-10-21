# Rapport de provenance — RUN-synthea_csv-fa46d08b

## 1. Provenance au niveau des lignes (tables OMOP finales)

**condition_occurrence** — 1985 lignes au total
  - conditions: 1982 lignes (100%)
  - procedures: 3 lignes (0%)

**drug_exposure** — 7616 lignes au total
  - medications: 6011 lignes (79%)
  - immunizations: 1567 lignes (21%)
  - procedures: 34 lignes (0%)
  - allergies: 4 lignes (0%)

**measurement** — 55920 lignes au total
  - observations: 51692 lignes (92%)
  - procedures: 4227 lignes (8%)
  - allergies: 1 lignes (0%)

**observation** — 39850 lignes au total
  - observations: 28123 lignes (71%)
  - encounters: 5078 lignes (13%)
  - procedures: 4397 lignes (11%)
  - conditions: 2166 lignes (5%)
  - allergies: 86 lignes (0%)

**procedure_occurrence** — 11977 lignes au total
  - procedures: 10258 lignes (86%)
  - encounters: 1712 lignes (14%)
  - observations: 4 lignes (0%)
  - allergies: 3 lignes (0%)

**visit_occurrence** — 6790 lignes au total
  - encounters: 6790 lignes (100%)

## 2. Provenance au niveau des champs structurels

**condition_occurrence**
  - condition_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - condition_end_date ← conditions.STOP (confiance=0.95)
  - condition_end_date ← procedures.STOP (confiance=0.90)
  - condition_end_datetime ← conditions.STOP (confiance=0.95)
  - condition_end_datetime ← procedures.STOP (confiance=0.95)
  - condition_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - condition_source_value ← conditions.CODE (confiance=0.85)
  - condition_source_value ← procedures.CODE (confiance=0.90)
  - condition_start_date ← conditions.START (confiance=0.95)
  - condition_start_date ← procedures.START (confiance=0.90)
  - condition_start_datetime ← conditions.START (confiance=0.95)
  - condition_start_datetime ← procedures.START (confiance=0.95)
  - condition_status_concept_id: ❌ non résolu (Paired field 'condition_status_source_value' was not resolved in this batch.)
  - condition_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← conditions.PATIENT (confiance=0.95)
  - person_id ← procedures.PATIENT (confiance=0.95)
  - visit_detail_id ← conditions.ENCOUNTER (confiance=0.90) 🔁 (résolu par reprise)
  - visit_detail_id ← procedures.ENCOUNTER (confiance=0.95) 🔁 (résolu par reprise)
  - visit_occurrence_id ← conditions.ENCOUNTER (confiance=0.90)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.95)

**death**
  - cause_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - cause_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - death_date ← patients.DEATHDATE (confiance=1.00)
  - death_datetime ← patients.DEATHDATE (confiance=0.90) 🔁 (résolu par reprise)
  - death_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← patients.Id (confiance=1.00)

**drug_exposure**
  - dose_unit_source_value ← medications.DESCRIPTION (confiance=0.70)
  - drug_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - drug_exposure_end_date ← allergies.STOP (confiance=0.90)
  - drug_exposure_end_date ← medications.STOP (confiance=0.95)
  - drug_exposure_end_date ← procedures.STOP (confiance=0.90)
  - drug_exposure_end_datetime ← allergies.STOP (confiance=0.60)
  - drug_exposure_end_datetime ← medications.STOP (confiance=0.95)
  - drug_exposure_end_datetime ← procedures.STOP (confiance=0.95)
  - drug_exposure_start_date ← allergies.START (confiance=0.95)
  - drug_exposure_start_date ← immunizations.DATE (confiance=0.90)
  - drug_exposure_start_date ← medications.START (confiance=0.95)
  - drug_exposure_start_date ← procedures.START (confiance=0.90)
  - drug_exposure_start_datetime ← allergies.START (confiance=0.60)
  - drug_exposure_start_datetime ← immunizations.DATE (confiance=0.90)
  - drug_exposure_start_datetime ← medications.START (confiance=0.95)
  - drug_exposure_start_datetime ← procedures.START (confiance=0.95)
  - drug_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - drug_source_value ← allergies.CODE (confiance=0.85)
  - drug_source_value ← immunizations.CODE (confiance=0.80)
  - drug_source_value ← medications.CODE (confiance=0.90)
  - drug_source_value ← procedures.CODE (confiance=0.85)
  - drug_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← allergies.PATIENT (confiance=0.95)
  - person_id ← immunizations.PATIENT (confiance=0.90)
  - person_id ← medications.PATIENT (confiance=0.95)
  - person_id ← procedures.PATIENT (confiance=0.95)
  - quantity ← medications.DISPENSES (confiance=0.95)
  - route_source_value ← medications.DESCRIPTION (confiance=0.70)
  - verbatim_end_date ← medications.STOP (confiance=0.95) 🔁 (résolu par reprise)
  - verbatim_end_date ← procedures.STOP (confiance=0.95) 🔁 (résolu par reprise)
  - visit_detail_id ← allergies.ENCOUNTER (confiance=0.95) 🔁 (résolu par reprise)
  - visit_detail_id ← immunizations.ENCOUNTER (confiance=0.85) 🔁 (résolu par reprise)
  - visit_detail_id ← medications.ENCOUNTER (confiance=0.95) 🔁 (résolu par reprise)
  - visit_detail_id ← procedures.ENCOUNTER (confiance=0.90) 🔁 (résolu par reprise)
  - visit_occurrence_id ← allergies.ENCOUNTER (confiance=0.90)
  - visit_occurrence_id ← immunizations.ENCOUNTER (confiance=0.85)
  - visit_occurrence_id ← medications.ENCOUNTER (confiance=0.95)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.90)

**measurement**
  - meas_event_field_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - measurement_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - measurement_date ← allergies.START (confiance=0.90)
  - measurement_date ← observations.DATE (confiance=0.90)
  - measurement_date ← procedures.START (confiance=0.90)
  - measurement_datetime ← allergies.START (confiance=0.90)
  - measurement_datetime ← observations.DATE (confiance=0.95)
  - measurement_datetime ← procedures.START (confiance=0.95)
  - measurement_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - measurement_source_value ← allergies.CODE (confiance=0.85)
  - measurement_source_value ← observations.CODE (confiance=0.90)
  - measurement_source_value ← procedures.CODE (confiance=0.85)
  - measurement_time ← observations.DATE (confiance=0.85) 🔁 (résolu par reprise)
  - measurement_time ← procedures.START (confiance=0.95) 🔁 (résolu par reprise)
  - measurement_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - operator_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← allergies.PATIENT (confiance=0.95)
  - person_id ← observations.PATIENT (confiance=0.95)
  - person_id ← procedures.PATIENT (confiance=0.90)
  - unit_source_value ← observations.UNITS (confiance=0.95)
  - value_as_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - value_as_number ← observations.VALUE (confiance=0.85)
  - value_source_value ← allergies.DESCRIPTION (confiance=0.80)
  - value_source_value ← observations.VALUE (confiance=0.95)
  - visit_detail_id ← allergies.ENCOUNTER (confiance=0.85) 🔁 (résolu par reprise)
  - visit_detail_id ← observations.ENCOUNTER (confiance=0.95) 🔁 (résolu par reprise)
  - visit_detail_id ← procedures.ENCOUNTER (confiance=0.90) 🔁 (résolu par reprise)
  - visit_occurrence_id ← allergies.ENCOUNTER (confiance=0.95)
  - visit_occurrence_id ← observations.ENCOUNTER (confiance=0.90)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.90)

**observation**
  - obs_event_field_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - observation_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - observation_date ← allergies.START (confiance=0.95)
  - observation_date ← conditions.START (confiance=0.90)
  - observation_date ← encounters.START (confiance=0.85)
  - observation_date ← observations.DATE (confiance=0.95)
  - observation_date ← procedures.START (confiance=0.90)
  - observation_datetime ← allergies.START (confiance=0.90)
  - observation_datetime ← conditions.START (confiance=0.90)
  - observation_datetime ← encounters.START (confiance=0.85)
  - observation_datetime ← observations.DATE (confiance=0.95)
  - observation_datetime ← procedures.START (confiance=0.90)
  - observation_event_id ← conditions.ENCOUNTER (confiance=0.60)
  - observation_event_id ← encounters.Id (confiance=0.80)
  - observation_id ← encounters.Id (confiance=0.70)
  - observation_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - observation_source_value ← allergies.CODE (confiance=0.85)
  - observation_source_value ← conditions.CODE (confiance=0.90)
  - observation_source_value ← encounters.CODE (confiance=0.80)
  - observation_source_value ← observations.CODE (confiance=0.85)
  - observation_source_value ← procedures.CODE (confiance=0.95)
  - observation_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← allergies.PATIENT (confiance=0.90)
  - person_id ← conditions.PATIENT (confiance=0.95)
  - person_id ← encounters.PATIENT (confiance=0.95)
  - person_id ← observations.PATIENT (confiance=0.95)
  - person_id ← procedures.PATIENT (confiance=0.95)
  - qualifier_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - qualifier_source_value ← allergies.TYPE (confiance=0.70)
  - unit_source_value ← observations.UNITS (confiance=0.95)
  - value_as_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - value_as_number ← observations.VALUE (confiance=0.90) 🔁 (résolu par reprise)
  - value_as_number ← procedures.BASE_COST (confiance=0.60) 🔁 (résolu par reprise)
  - value_as_string ← allergies.DESCRIPTION (confiance=0.80) 🔁 (résolu par reprise)
  - value_as_string ← conditions.DESCRIPTION (confiance=0.85) 🔁 (résolu par reprise)
  - value_as_string ← encounters.DESCRIPTION (confiance=0.60) 🔁 (résolu par reprise)
  - value_as_string ← observations.VALUE (confiance=0.90) 🔁 (résolu par reprise)
  - value_as_string ← procedures.DESCRIPTION (confiance=0.95) 🔁 (résolu par reprise)
  - value_source_value ← allergies.REACTION1 (confiance=0.70) 🔁 (résolu par reprise)
  - value_source_value ← conditions.DESCRIPTION (confiance=0.75) 🔁 (résolu par reprise)
  - value_source_value ← observations.VALUE (confiance=0.95) 🔁 (résolu par reprise)
  - value_source_value ← procedures.DESCRIPTION (confiance=0.90) 🔁 (résolu par reprise)
  - visit_detail_id ← allergies.ENCOUNTER (confiance=0.95) 🔁 (résolu par reprise)
  - visit_detail_id ← conditions.ENCOUNTER (confiance=0.85) 🔁 (résolu par reprise)
  - visit_detail_id ← encounters.Id (confiance=0.80) 🔁 (résolu par reprise)
  - visit_detail_id ← observations.ENCOUNTER (confiance=0.95) 🔁 (résolu par reprise)
  - visit_detail_id ← procedures.ENCOUNTER (confiance=0.95) 🔁 (résolu par reprise)
  - visit_occurrence_id ← allergies.ENCOUNTER (confiance=0.90)
  - visit_occurrence_id ← conditions.ENCOUNTER (confiance=0.90)
  - visit_occurrence_id ← encounters.Id (confiance=0.90)
  - visit_occurrence_id ← observations.ENCOUNTER (confiance=0.90)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.95)

**observation_period**
  - observation_period_end_date ← encounters.STOP (confiance=0.85)
  - observation_period_start_date ← encounters.START (confiance=0.85)
  - period_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← patients.Id (confiance=0.95)

**person**
  - birth_datetime ← patients.BIRTHDATE (confiance=0.95) 🔁 (résolu par reprise)
  - day_of_birth ← patients.BIRTHDATE (confiance=0.95)
  - ethnicity_source_value ← patients.ETHNICITY (confiance=0.95)
  - gender_source_value ← patients.GENDER (confiance=0.95)
  - month_of_birth ← patients.BIRTHDATE (confiance=0.95)
  - person_id ← patients.Id (confiance=0.95)
  - person_source_value ← patients.Id (confiance=0.90)
  - race_source_value ← patients.RACE (confiance=0.95)
  - year_of_birth ← patients.BIRTHDATE (confiance=0.95)

**procedure_occurrence**
  - modifier_concept_id: ❌ non résolu (Paired field 'modifier_source_value' was not resolved in this batch.)
  - person_id ← allergies.PATIENT (confiance=0.95)
  - person_id ← encounters.PATIENT (confiance=1.00)
  - person_id ← observations.PATIENT (confiance=0.95)
  - person_id ← procedures.PATIENT (confiance=0.95)
  - procedure_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - procedure_date ← allergies.START (confiance=0.85)
  - procedure_date ← encounters.START (confiance=0.90)
  - procedure_date ← observations.DATE (confiance=0.90)
  - procedure_date ← procedures.START (confiance=0.95)
  - procedure_datetime ← encounters.START (confiance=0.90)
  - procedure_datetime ← observations.DATE (confiance=0.90)
  - procedure_datetime ← procedures.START (confiance=0.95)
  - procedure_end_date ← encounters.STOP (confiance=0.80)
  - procedure_end_date ← procedures.STOP (confiance=0.95)
  - procedure_end_datetime ← encounters.STOP (confiance=0.80)
  - procedure_end_datetime ← procedures.STOP (confiance=0.95)
  - procedure_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - procedure_source_value ← allergies.CODE (confiance=0.80)
  - procedure_source_value ← encounters.CODE (confiance=0.95)
  - procedure_source_value ← observations.CODE (confiance=0.80)
  - procedure_source_value ← procedures.CODE (confiance=0.95)
  - procedure_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - visit_detail_id ← allergies.ENCOUNTER (confiance=0.90) 🔁 (résolu par reprise)
  - visit_detail_id ← encounters.Id (confiance=0.85) 🔁 (résolu par reprise)
  - visit_detail_id ← observations.ENCOUNTER (confiance=0.85) 🔁 (résolu par reprise)
  - visit_detail_id ← procedures.ENCOUNTER (confiance=0.90) 🔁 (résolu par reprise)
  - visit_occurrence_id ← allergies.ENCOUNTER (confiance=0.95)
  - visit_occurrence_id ← encounters.Id (confiance=0.90)
  - visit_occurrence_id ← observations.ENCOUNTER (confiance=0.85)
  - visit_occurrence_id ← procedures.ENCOUNTER (confiance=0.95)

**visit_occurrence**
  - admitted_from_concept_id: ❌ non résolu (Paired field 'admitted_from_source_value' was not resolved in this batch.)
  - discharged_to_concept_id: ❌ non résolu (Paired field 'discharged_to_source_value' was not resolved in this batch.)
  - person_id ← encounters.PATIENT (confiance=0.95)
  - visit_end_date ← encounters.STOP (confiance=0.90)
  - visit_end_datetime ← encounters.STOP (confiance=0.95)
  - visit_occurrence_id ← encounters.Id (confiance=0.95)
  - visit_source_value ← encounters.ENCOUNTERCLASS (confiance=0.85)
  - visit_start_date ← encounters.START (confiance=0.90)
  - visit_start_datetime ← encounters.START (confiance=0.95)
  - visit_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )

## 3. Provenance au niveau des valeurs (champs codés, mécanisme 1)

**allergies**
  - allergies.CODE: 21 valeurs distinctes, 100% résolues
      -> observation: 18 valeurs
      -> drug_exposure: 1 valeurs
      -> procedure_occurrence: 1 valeurs
      -> measurement: 1 valeurs

**conditions**
  - conditions.CODE: 197 valeurs distinctes, 98% résolues
      -> condition_occurrence: 156 valeurs
      -> observation: 41 valeurs

**encounters**
  - encounters.CODE: 46 valeurs distinctes, 98% résolues
      -> observation: 39 valeurs
      -> procedure_occurrence: 7 valeurs

**immunizations**
  - immunizations.CODE: 21 valeurs distinctes, 100% résolues
      -> drug_exposure: 21 valeurs

**medications**
  - medications.CODE: 146 valeurs distinctes, 100% résolues
      -> drug_exposure: 146 valeurs

**observations**
  - observations.CODE: 246 valeurs distinctes, 96% résolues
      -> measurement: 192 valeurs
      -> observation: 50 valeurs
      -> AUCUN: 3 valeurs
      -> procedure_occurrence: 1 valeurs

**patients**
  - _Déclarée, mais aucune valeur distincte produite pour ce batch._

**procedures**
  - procedures.CODE: 275 valeurs distinctes, 100% résolues
      -> procedure_occurrence: 167 valeurs
      -> observation: 54 valeurs
      -> measurement: 49 valeurs
      -> drug_exposure: 2 valeurs
      -> condition_occurrence: 2 valeurs
      -> AUCUN: 1 valeurs

## 4. Résolutions via mapping figé (fixed_value_mappings)

**person.ethnicity_concept_id** — 2 valeur(s) couverte(s) par le CSV
  - 'nonhispanic' -> concept_id=38003564
  - 'hispanic' -> concept_id=38003563

**person.race_concept_id** — 6 valeur(s) couverte(s) par le CSV
  - 'white' -> concept_id=8527
  - 'asian' -> concept_id=8515
  - 'black' -> concept_id=8516
  - 'native' -> concept_id=8657
  - 'hawaiian' -> concept_id=8557
  - 'other' -> concept_id=0

**visit_occurrence.visit_concept_id** — 7 valeur(s) couverte(s) par le CSV
  - 'wellness' -> concept_id=9202
  - 'outpatient' -> concept_id=9202
  - 'ambulatory' -> concept_id=9202
  - 'emergency' -> concept_id=9203
  - 'urgentcare' -> concept_id=9203
  - 'inpatient' -> concept_id=9201
  - 'home' -> concept_id=581476

## 5. Jointures de vocabulaire local

_Aucun champ 'local' déclaré dans ce batch._
