# Rapport de provenance — RUN-synthea_fhir-2227ef8f

## 1. Provenance au niveau des lignes (tables OMOP finales)

**condition_occurrence** — 1985 lignes au total
  - Condition: 1982 lignes (100%)
  - Procedure: 3 lignes (0%)

**drug_exposure** — 7624 lignes au total
  - MedicationRequest: 6011 lignes (79%)
  - Immunization: 1567 lignes (21%)
  - Procedure: 34 lignes (0%)
  - AllergyIntolerance: 12 lignes (0%)

**measurement** — 57621 lignes au total
  - Observation: 49990 lignes (87%)
  - Procedure: 4227 lignes (7%)
  - Observation_component: 3404 lignes (6%)

**observation** — 40979 lignes au total
  - Observation_component: 23485 lignes (57%)
  - Observation: 5771 lignes (14%)
  - Encounter: 5078 lignes (12%)
  - Procedure: 4397 lignes (11%)
  - Condition: 2166 lignes (5%)
  - AllergyIntolerance: 82 lignes (0%)

**procedure_occurrence** — 11974 lignes au total
  - Procedure: 10258 lignes (86%)
  - Encounter: 1712 lignes (14%)
  - Observation: 4 lignes (0%)

**visit_occurrence** — 6790 lignes au total
  - Encounter: 6790 lignes (100%)

## 2. Provenance au niveau des champs structurels

**condition_occurrence**
  - condition_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - condition_end_date ← Condition.abatementDateTime (confiance=0.85)
  - condition_end_date ← Procedure.performedPeriod.end (confiance=0.90)
  - condition_end_datetime ← Condition.abatementDateTime (confiance=0.85)
  - condition_end_datetime ← Procedure.performedPeriod.end (confiance=0.90)
  - condition_occurrence_id ← Condition.id (confiance=0.90)
  - condition_occurrence_id ← Procedure.id (confiance=0.95)
  - condition_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - condition_source_value ← Condition.code.code (confiance=0.95)
  - condition_source_value ← Procedure.code.code (confiance=0.80)
  - condition_start_date ← Condition.onsetDateTime (confiance=0.90)
  - condition_start_date ← Procedure.performedPeriod.start (confiance=0.90)
  - condition_start_datetime ← Condition.onsetDateTime (confiance=0.90)
  - condition_start_datetime ← Procedure.performedPeriod.start (confiance=0.90)
  - condition_status_source_value ← Condition.clinicalStatus.code (confiance=0.95)
  - condition_status_source_value ← Procedure.status (confiance=0.70)
  - condition_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← Condition.subject.id (confiance=0.95)
  - person_id ← Procedure.subject.id (confiance=0.95)
  - visit_detail_id ← Condition.encounter.id (confiance=0.50) 🔁 (résolu par reprise)
  - visit_detail_id ← Procedure.encounter.id (confiance=0.95) 🔁 (résolu par reprise)
  - visit_occurrence_id ← Condition.encounter.id (confiance=0.90)
  - visit_occurrence_id ← Procedure.encounter.id (confiance=0.90)

**death**
  - cause_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - cause_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - death_date ← Patient.deceasedDateTime (confiance=0.90)
  - death_datetime ← Patient.deceasedDateTime (confiance=0.95)
  - death_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← Patient.id (confiance=1.00)

**drug_exposure**
  - drug_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - drug_exposure_end_date ← Procedure.performedPeriod.end (confiance=0.85)
  - drug_exposure_end_datetime ← Procedure.performedPeriod.end (confiance=0.90)
  - drug_exposure_id ← Immunization.id (confiance=0.95)
  - drug_exposure_id ← MedicationRequest.id (confiance=0.95)
  - drug_exposure_start_date ← Procedure.performedPeriod.start (confiance=0.85)
  - drug_exposure_start_date ← Immunization.occurrenceDateTime (confiance=0.90)
  - drug_exposure_start_date ← MedicationRequest.authoredOn (confiance=0.85)
  - drug_exposure_start_datetime ← Procedure.performedPeriod.start (confiance=0.90)
  - drug_exposure_start_datetime ← Immunization.occurrenceDateTime (confiance=0.95)
  - drug_exposure_start_datetime ← MedicationRequest.authoredOn (confiance=0.85)
  - drug_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - drug_source_value ← Procedure.code.display (confiance=0.60)
  - drug_source_value ← Immunization.vaccineCode.code (confiance=0.95)
  - drug_source_value ← MedicationRequest.medicationCodeableConcept.code (confiance=0.80)
  - drug_source_value ← AllergyIntolerance.code.text (confiance=0.85)
  - drug_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← Procedure.subject.id (confiance=0.95)
  - person_id ← Immunization.patient.id (confiance=0.95)
  - person_id ← MedicationRequest.subject.id (confiance=0.95)
  - person_id ← AllergyIntolerance.patient.id (confiance=0.95)
  - route_concept_id: ❌ non résolu (Paired field 'route_source_value' was not resolved in this batch.)
  - sig ← MedicationRequest.dosageInstruction.text (confiance=0.95)
  - visit_detail_id ← Immunization.encounter.id (confiance=0.95)
  - visit_detail_id ← MedicationRequest.encounter.id (confiance=0.95)
  - visit_occurrence_id ← Procedure.encounter.id (confiance=0.90)
  - visit_occurrence_id ← Immunization.encounter.id (confiance=0.90)
  - visit_occurrence_id ← MedicationRequest.encounter.id (confiance=0.95)

**measurement**
  - meas_event_field_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - measurement_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - measurement_date ← Observation.effectiveDateTime (confiance=0.90)
  - measurement_date ← Observation_component.parent.effectiveDateTime (confiance=0.90)
  - measurement_date ← Procedure.performedPeriod.start (confiance=0.85)
  - measurement_datetime ← Observation.effectiveDateTime (confiance=0.90)
  - measurement_datetime ← Observation_component.parent.effectiveDateTime (confiance=0.95)
  - measurement_datetime ← Procedure.performedPeriod.start (confiance=0.85)
  - measurement_event_id ← Observation.id (confiance=0.85)
  - measurement_event_id ← Observation_component.id (confiance=0.80)
  - measurement_event_id ← Procedure.id (confiance=0.80)
  - measurement_id ← Observation.id (confiance=0.95)
  - measurement_id ← Observation_component.id (confiance=0.90)
  - measurement_id ← Procedure.id (confiance=0.90)
  - measurement_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - measurement_source_value ← Observation.code.code (confiance=0.90)
  - measurement_source_value ← Observation_component.code.code (confiance=0.90)
  - measurement_source_value ← Procedure.code.code (confiance=0.80)
  - measurement_time ← Observation.effectiveDateTime (confiance=0.95) 🔁 (résolu par reprise)
  - measurement_time ← Observation_component.parent.effectiveDateTime (confiance=0.95) 🔁 (résolu par reprise)
  - measurement_time ← Procedure.performedPeriod.start (confiance=0.90) 🔁 (résolu par reprise)
  - measurement_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - operator_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← Observation.subject.id (confiance=0.95)
  - person_id ← Observation_component.parent.subject.id (confiance=0.95)
  - person_id ← Procedure.subject.id (confiance=0.95)
  - unit_source_value ← Observation.valueQuantity.code (confiance=0.90)
  - unit_source_value ← Observation_component.valueQuantity.unit (confiance=0.90)
  - value_as_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - value_as_number ← Observation.valueQuantity.value (confiance=0.95)
  - value_as_number ← Observation_component.valueQuantity.value (confiance=0.95)
  - value_source_value ← Observation.valueString (confiance=0.90)
  - value_source_value ← Observation_component.valueString (confiance=0.80)
  - visit_detail_id ← Observation.encounter.id (confiance=0.85) 🔁 (résolu par reprise)
  - visit_detail_id ← Observation_component.parent.encounter.id (confiance=0.60) 🔁 (résolu par reprise)
  - visit_detail_id ← Procedure.encounter.id (confiance=0.90) 🔁 (résolu par reprise)
  - visit_occurrence_id ← Observation.encounter.id (confiance=0.95)
  - visit_occurrence_id ← Observation_component.parent.encounter.id (confiance=0.90)
  - visit_occurrence_id ← Procedure.encounter.id (confiance=0.90)

**observation**
  - obs_event_field_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - observation_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - observation_date ← Encounter.period.start (confiance=0.90)
  - observation_date ← Condition.onsetDateTime (confiance=0.85)
  - observation_date ← Observation.effectiveDateTime (confiance=0.90)
  - observation_date ← Observation_component.parent.effectiveDateTime (confiance=0.90)
  - observation_date ← Procedure.performedPeriod.start (confiance=0.90)
  - observation_date ← AllergyIntolerance.recordedDate (confiance=0.90)
  - observation_datetime ← Encounter.period.start (confiance=0.90)
  - observation_datetime ← Condition.onsetDateTime (confiance=0.85)
  - observation_datetime ← Observation.effectiveDateTime (confiance=0.95)
  - observation_datetime ← Observation_component.parent.effectiveDateTime (confiance=0.90)
  - observation_datetime ← Procedure.performedPeriod.start (confiance=0.90)
  - observation_datetime ← AllergyIntolerance.recordedDate (confiance=0.90)
  - observation_event_id ← Encounter.id (confiance=0.85)
  - observation_event_id ← Observation_component.parent.id (confiance=0.70)
  - observation_event_id ← Procedure.id (confiance=0.80)
  - observation_id ← Condition.id (confiance=0.90) 🔁 (résolu par reprise)
  - observation_id ← Observation.id (confiance=0.95) 🔁 (résolu par reprise)
  - observation_id ← Observation_component.id (confiance=0.80) 🔁 (résolu par reprise)
  - observation_id ← Procedure.id (confiance=0.95) 🔁 (résolu par reprise)
  - observation_id ← AllergyIntolerance.id (confiance=0.90) 🔁 (résolu par reprise)
  - observation_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - observation_source_value ← Encounter.type.code (confiance=0.85)
  - observation_source_value ← Condition.code.code (confiance=0.95)
  - observation_source_value ← Observation.code.code (confiance=0.90)
  - observation_source_value ← Observation_component.code.code (confiance=0.95)
  - observation_source_value ← Procedure.code.display (confiance=0.85)
  - observation_source_value ← AllergyIntolerance.code.code (confiance=0.85)
  - observation_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← Encounter.subject.id (confiance=0.95)
  - person_id ← Condition.subject.id (confiance=0.95)
  - person_id ← Observation.subject.id (confiance=0.95)
  - person_id ← Observation_component.parent.subject.id (confiance=0.95)
  - person_id ← Procedure.subject.id (confiance=0.95)
  - person_id ← AllergyIntolerance.patient.id (confiance=0.95)
  - qualifier_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - qualifier_source_value ← AllergyIntolerance.type (confiance=0.75)
  - unit_source_value ← Observation.valueQuantity.code (confiance=0.85)
  - unit_source_value ← Observation_component.valueQuantity.unit (confiance=0.90)
  - value_as_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - value_as_number ← Observation.valueQuantity.value (confiance=0.95)
  - value_as_number ← Observation_component.valueQuantity.value (confiance=0.95)
  - value_as_string ← Observation.valueString (confiance=0.90)
  - value_as_string ← Observation_component.valueString (confiance=0.80)
  - value_as_string ← Procedure.code.display (confiance=0.70)
  - value_as_string ← AllergyIntolerance.code.text (confiance=0.80)
  - value_source_value ← Encounter.type.text (confiance=0.85)
  - value_source_value ← Observation.valueString (confiance=0.70)
  - value_source_value ← Observation_component.valueString (confiance=0.80)
  - value_source_value ← Procedure.code.display (confiance=0.80)
  - value_source_value ← AllergyIntolerance.reaction.severity (confiance=0.75)
  - visit_detail_id ← Encounter.id (confiance=0.80)
  - visit_detail_id ← Condition.encounter.id (confiance=0.85)
  - visit_detail_id ← Observation.encounter.id (confiance=0.90)
  - visit_detail_id ← Observation_component.parent.encounter.id (confiance=0.80)
  - visit_detail_id ← Procedure.encounter.id (confiance=0.90)
  - visit_occurrence_id ← Encounter.id (confiance=0.90)
  - visit_occurrence_id ← Condition.encounter.id (confiance=0.95)
  - visit_occurrence_id ← Observation.encounter.id (confiance=0.90)
  - visit_occurrence_id ← Observation_component.parent.encounter.id (confiance=0.90)
  - visit_occurrence_id ← Procedure.encounter.id (confiance=0.95)

**observation_period**
  - observation_period_end_date ← Encounter.period.end (confiance=0.90)
  - observation_period_start_date ← Encounter.period.start (confiance=0.90)
  - period_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - person_id ← Patient.id (confiance=1.00)

**person**
  - birth_datetime ← Patient.birthDate (confiance=0.90)
  - day_of_birth ← Patient.birthDate (confiance=0.95)
  - ethnicity_source_value ← Patient.extension.us-core-ethnicity.ombCategory.display (confiance=0.90)
  - gender_source_value ← Patient.gender (confiance=0.95)
  - month_of_birth ← Patient.birthDate (confiance=0.95)
  - person_id ← Patient.id (confiance=0.80)
  - person_source_value ← Patient.id (confiance=0.90)
  - race_source_value ← Patient.extension.us-core-race.ombCategory.display (confiance=0.90)
  - year_of_birth ← Patient.birthDate (confiance=0.95)

**procedure_occurrence**
  - modifier_concept_id: ❌ non résolu (Paired field 'modifier_source_value' was not resolved in this batch.)
  - person_id ← Encounter.subject.id (confiance=0.95)
  - person_id ← Observation.subject.id (confiance=0.95)
  - person_id ← Procedure.subject.id (confiance=0.95)
  - procedure_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - procedure_date ← Encounter.period.start (confiance=0.90)
  - procedure_date ← Observation.effectiveDateTime (confiance=0.90)
  - procedure_date ← Procedure.performedPeriod.start (confiance=0.95)
  - procedure_datetime ← Encounter.period.start (confiance=0.90)
  - procedure_datetime ← Observation.effectiveDateTime (confiance=0.90)
  - procedure_datetime ← Procedure.performedPeriod.start (confiance=0.95)
  - procedure_end_date ← Encounter.period.end (confiance=0.85)
  - procedure_end_date ← Procedure.performedPeriod.end (confiance=0.95)
  - procedure_end_datetime ← Encounter.period.end (confiance=0.85)
  - procedure_end_datetime ← Procedure.performedPeriod.end (confiance=0.95)
  - procedure_occurrence_id ← Encounter.id (confiance=0.80) 🔁 (résolu par reprise)
  - procedure_occurrence_id ← Procedure.id (confiance=0.90) 🔁 (résolu par reprise)
  - procedure_source_concept_id: ❌ non résolu (Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - not)
  - procedure_source_value ← Encounter.type.code (confiance=0.85)
  - procedure_source_value ← Observation.code.code (confiance=0.85)
  - procedure_source_value ← Procedure.code.code (confiance=0.95)
  - procedure_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )
  - quantity ← Observation.valueQuantity.value (confiance=0.70)
  - visit_detail_id ← Encounter.id (confiance=0.90) 🔁 (résolu par reprise)
  - visit_detail_id ← Observation.encounter.id (confiance=0.60) 🔁 (résolu par reprise)
  - visit_detail_id ← Procedure.encounter.id (confiance=0.95) 🔁 (résolu par reprise)
  - visit_occurrence_id ← Encounter.id (confiance=0.80)
  - visit_occurrence_id ← Observation.encounter.id (confiance=0.90)
  - visit_occurrence_id ← Procedure.encounter.id (confiance=0.95)

**visit_occurrence**
  - admitted_from_concept_id: ❌ non résolu (Paired field 'admitted_from_source_value' was not resolved in this batch.)
  - discharged_to_source_value ← Encounter.hospitalization.dischargeDisposition.display (confiance=0.90)
  - person_id ← Encounter.subject.id (confiance=1.00)
  - visit_end_date ← Encounter.period.end (confiance=1.00)
  - visit_end_datetime ← Encounter.period.end (confiance=1.00)
  - visit_occurrence_id ← Encounter.id (confiance=1.00)
  - visit_source_value ← Encounter.type.display (confiance=0.90)
  - visit_start_date ← Encounter.period.start (confiance=1.00)
  - visit_start_datetime ← Encounter.period.start (confiance=1.00)
  - visit_type_concept_id: ❌ non résolu (No paired source_value field for this table - likely record provenance (needs a )

## 3. Provenance au niveau des valeurs (champs codés, mécanisme 1)

**AllergyIntolerance**
  - AllergyIntolerance.code.code: 21 valeurs distinctes, 100% résolues
      -> observation: 15 valeurs
      -> drug_exposure: 6 valeurs

**Condition**
  - Condition.code.code: 197 valeurs distinctes, 98% résolues
      -> condition_occurrence: 156 valeurs
      -> observation: 41 valeurs

**Encounter**
  - Encounter.type.code: 46 valeurs distinctes, 98% résolues
      -> observation: 39 valeurs
      -> procedure_occurrence: 7 valeurs

**Immunization**
  - Immunization.vaccineCode.code: 21 valeurs distinctes, 100% résolues
      -> drug_exposure: 21 valeurs

**Location**
  - _Déclarée, mais aucune valeur distincte produite pour ce batch._

**MedicationRequest**
  - MedicationRequest.medicationCodeableConcept.code: 146 valeurs distinctes, 100% résolues
      -> drug_exposure: 146 valeurs

**Observation**
  - Observation.code.code: 220 valeurs distinctes, 97% résolues
      -> measurement: 190 valeurs
      -> observation: 29 valeurs
      -> procedure_occurrence: 1 valeurs

**Observation_component**
  - Observation_component.code.code: 29 valeurs distinctes, 100% résolues
      -> observation: 25 valeurs
      -> measurement: 4 valeurs

**Organization**
  - _Déclarée, mais aucune valeur distincte produite pour ce batch._

**Patient**
  - _Déclarée, mais aucune valeur distincte produite pour ce batch._

**Practitioner**
  - _Déclarée, mais aucune valeur distincte produite pour ce batch._

**PractitionerRole**
  - _Déclarée, mais aucune valeur distincte produite pour ce batch._

**Procedure**
  - Procedure.code.code: 275 valeurs distinctes, 100% résolues
      -> procedure_occurrence: 167 valeurs
      -> observation: 54 valeurs
      -> measurement: 49 valeurs
      -> drug_exposure: 2 valeurs
      -> condition_occurrence: 2 valeurs
      -> AUCUN: 1 valeurs

## 4. Résolutions via mapping figé (fixed_value_mappings)

**person.ethnicity_concept_id** — 2 valeur(s) couverte(s) par le CSV
  - '2186-5' -> concept_id=38003564
  - '2135-2' -> concept_id=38003563

**person.race_concept_id** — 5 valeur(s) couverte(s) par le CSV
  - '2106-3' -> concept_id=8527
  - '2054-5' -> concept_id=8516
  - '2028-9' -> concept_id=8515
  - '1002-5' -> concept_id=8657
  - '2076-8' -> concept_id=8557

**visit_occurrence.visit_concept_id** — 3 valeur(s) couverte(s) par le CSV
  - 'AMB' -> concept_id=9202
  - 'EMER' -> concept_id=9203
  - 'IMP' -> concept_id=9201

## 5. Jointures de vocabulaire local

_Aucun champ 'local' déclaré dans ce batch._
