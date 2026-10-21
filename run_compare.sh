# ─── 1. Pointer votre base vers le bon user/password ───
export DATABASE_URL="postgresql://postgres:12345@localhost:5432/omopdb"

# ─── 2. Lancer les 9 comparaisons ───
BATCH=synthea_sample_allergie
PATIENTS="data/raw/hospital_a/${BATCH}/patients.csv"
OUTDIR="reports/${BATCH}"
mkdir -p "$OUTDIR"

COMMON="--our-schema omop_temp \
--patients-csv $PATIENTS \
--our-source-column Id --their-source-column Id \
--their-db-host localhost --their-db-name omop_cdm --their-schema cdm_synthea10 \
--their-db-user synthea_user --their-db-password changeme"

python scripts/compare_content.py --mode row_content --table person \
  --fields gender_concept_id,year_of_birth,month_of_birth,day_of_birth,race_concept_id,ethnicity_concept_id,gender_source_value,race_source_value,ethnicity_source_value,person_source_value \
  --natural-key person_source_value $COMMON --output "$OUTDIR/person.md"

python scripts/compare_content.py --mode row_content --table visit_occurrence \
  --fields visit_concept_id,visit_start_date,visit_end_date,visit_source_value,visit_source_concept_id \
  --natural-key visit_concept_id,visit_start_date \
  --exclude-fields visit_type_concept_id $COMMON --output "$OUTDIR/visit_occurrence.md"

python scripts/compare_content.py --mode row_content --table condition_occurrence \
  --fields condition_concept_id,condition_source_value,condition_source_concept_id,condition_start_date,condition_end_date \
  --natural-key condition_concept_id,condition_start_date \
  --exclude-fields condition_type_concept_id $COMMON --output "$OUTDIR/condition_occurrence.md"

python scripts/compare_content.py --mode row_content --table drug_exposure \
  --fields drug_concept_id,drug_source_value,drug_source_concept_id,drug_exposure_start_date,drug_exposure_end_date,quantity \
  --natural-key drug_concept_id,drug_exposure_start_date,drug_exposure_end_date \
  --exclude-fields drug_type_concept_id $COMMON --output "$OUTDIR/drug_exposure.md"

python scripts/compare_content.py --mode row_content --table procedure_occurrence \
  --fields procedure_concept_id,procedure_source_value,procedure_source_concept_id,procedure_date,quantity \
  --natural-key procedure_concept_id,procedure_date \
  --exclude-fields procedure_type_concept_id $COMMON --output "$OUTDIR/procedure_occurrence.md"

python scripts/compare_content.py --mode row_content --table measurement \
  --fields measurement_concept_id,measurement_date,value_as_number,unit_concept_id,measurement_source_value \
  --natural-key measurement_concept_id,measurement_date \
  --exclude-fields measurement_type_concept_id $COMMON --output "$OUTDIR/measurement.md"

python scripts/compare_content.py --mode row_content --table observation \
  --fields observation_concept_id,observation_date,value_as_number,value_as_string,observation_source_value \
  --natural-key observation_concept_id,observation_date \
  --exclude-fields observation_type_concept_id $COMMON --output "$OUTDIR/observation.md"

python scripts/compare_content.py --mode row_content --table death \
  --fields death_date,death_datetime,cause_concept_id,cause_source_value \
  --natural-key death_date \
  --exclude-fields death_type_concept_id $COMMON --output "$OUTDIR/death.md"

python scripts/compare_content.py --mode row_content --table observation_period \
  --fields observation_period_start_date,observation_period_end_date \
  --natural-key observation_period_start_date \
  --exclude-fields period_type_concept_id $COMMON --output "$OUTDIR/observation_period.md"
