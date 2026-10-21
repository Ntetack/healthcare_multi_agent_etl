# Complete Setup and Execution Guide

This guide walks through every step needed to run this multi-agent ETL
framework from a completely empty environment: creating the database,
installing the OMOP CDM schema, downloading and loading the
vocabulary, configuring the project, and running the pipeline. Follow
the steps in order; each one depends on the previous.

## 1. Prerequisites

Install the following before starting:

- **PostgreSQL** (any recent version), running and reachable
- **Python 3.12**
- **R** (required only for the Validation Agent's Data Quality
  Dashboard step)
- `psql` command-line client available in your terminal

Verify each is installed:

```bash
psql --version
python3 --version
Rscript --version
```

## 2. Clone the Project and Install Python Dependencies

```bash
cd healthcare_multi_agent_etl
pip install -r requirements.txt --break-system-packages
```

If `requirements.txt` does not exist or is incomplete, install at
minimum:

```bash
pip install sqlalchemy psycopg2-binary pandas python-dotenv langgraph langchain-core --break-system-packages
pip install langchain-groq langchain-mistralai  # or whichever LLM provider you use
```

## 3. Create the PostgreSQL Database

**Naming convention used throughout this guide:** the four schema
names (`cdm_vocab`, `omop_temp`, `omop`, `staging`) are fixed and must
never be renamed — the project's code refers to them literally. The
**database name** itself, however, is entirely up to you; this guide
uses the placeholder `<your_database_name>` everywhere a real command
is shown. Replace it consistently with your own choice (for example
`omopdb`, `healthcare_etl`, or any name you prefer) in every command
below, and in `.env` (step 7).

```bash
sudo -u postgres psql -c "CREATE DATABASE <your_database_name>;"
```

Confirm you can connect:

```bash
psql -h localhost -U postgres -d <your_database_name> -c "SELECT 1;"
```

## 4. Create the Required Schemas

This project uses five schemas inside `<your_database_name>`. Unlike
the database name, **these five schema names must be created exactly
as shown** — they are not configurable:

- `cdm_vocab` — the full OMOP vocabulary, loaded once from Athena
- `omop_temp` — per-batch staging area for OMOP-shaped tables,
  validated before promotion
- `omop` — the final, cumulative store
- `staging` — enriched source tables written by the Mapping Agent
- `pipeline_meta` — internal bookkeeping used by the Profiling Agent to
  track which batches have already been processed for each source
  (not an OMOP schema at all - purely this project's own state)

```bash
psql -h localhost -U postgres -d <your_database_name> -c "
CREATE SCHEMA IF NOT EXISTS cdm_vocab;
CREATE SCHEMA IF NOT EXISTS omop_temp;
CREATE SCHEMA IF NOT EXISTS omop;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS pipeline_meta;

CREATE TABLE IF NOT EXISTS pipeline_meta.processed_folders (
    source_name TEXT NOT NULL,
    folder_path TEXT NOT NULL,
    execution_id TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    PRIMARY KEY (source_name, folder_path)
);
"
```

Without this table, running the pipeline fails immediately at the
Profiling stage with `relation "pipeline_meta.processed_folders" does
not exist` - the Root Cause Analyzer correctly flags this as fatal and
requiring human intervention, since no batch can even be discovered
without it.

## 5. Install the OMOP CDM v5.4 Table Structure

Install the official OHDSI `CommonDataModel` R package, then generate
and execute the DDL for both `omop_temp` and `omop`.

```r
install.packages("remotes")
remotes::install_github("OHDSI/CommonDataModel")

library(CommonDataModel)

# Download the JDBC driver once - createConnectionDetails() requires
# pathToDriver to be set explicitly, or it fails with
# "The `pathToDriver` argument hasn't been specified."
DatabaseConnector::downloadJdbcDrivers("postgresql", pathToDriver = "~/jdbc_drivers")

# Repeat once per schema (omop_temp, then omop)
executeDdl(
  connectionDetails = DatabaseConnector::createConnectionDetails(
    dbms = "postgresql",
    server = "localhost/<your_database_name>",
    user = "postgres",
    password = "<your_password>",
    pathToDriver = "~/jdbc_drivers"
  ),
  cdmVersion = "5.4",
  cdmDatabaseSchema = "omop_temp"
)
```

Repeat with `cdmDatabaseSchema = "omop"` for the final schema.

This step also enables the `pg_trgm` PostgreSQL extension used by this
project's fuzzy vocabulary search. If it is not already enabled:

```bash
psql -h localhost -U postgres -d <your_database_name> -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

**Important:** depending on the exact `CommonDataModel` version and
options used, the installed DDL may include real foreign key
constraints between `omop_temp`'s clinical tables and its vocabulary
tables (`concept`, `vocabulary`, ...). If step 9 (vocabulary sync)
later fails with `cannot truncate a table referenced in a foreign key
constraint`, drop every foreign key constraint in `omop_temp` first -
this schema is refreshed batch by batch by design in this project, and
never relies on database-level referential integrity (the pipeline's
own application-level checks serve that role instead):

```bash
psql -h localhost -U postgres -d <your_database_name> -c "
DO \$\$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT conname, conrelid::regclass AS table_name
        FROM pg_constraint
        WHERE contype = 'f'
          AND connamespace = 'omop_temp'::regnamespace
    LOOP
        EXECUTE format('ALTER TABLE %s DROP CONSTRAINT %I', r.table_name, r.conname);
    END LOOP;
END \$\$;
"
```

## 6. Download the OMOP Vocabulary From Athena

1. Go to <https://athena.ohdsi.org> and create a free account.
2. Select every vocabulary this project needs:
   - `SNOMED`, `ICD9CM`, `ICD9Proc`, `ICD10CM`, `CPT4`, `LOINC`,
     `RxNorm`, `NDC`, `CVX`, `UCUM`
   - Plus the fixed OMOP vocabularies that come bundled automatically
     (`Gender`, `Race`, `Ethnicity`, `Visit`, `Type Concept`, ...)
3. Click **Download**. Athena processes this asynchronously and emails
   you a link once ready (this can take several minutes to a few
   hours).
4. Download and unzip the export to a local folder, for example
   `~/Downloads/athena-vocabulary/`.

### 6a. Special step required for CPT4 only

CPT4 is licensed by the AMA. OHDSI cannot bundle its real code
descriptions in the standard export. A separate step is required:

1. Create a free UMLS account at <https://uts.nlm.nih.gov/uts/>.
2. In your unzipped Athena export folder, locate `cpt4.jar`.
3. Run:

```bash
java -jar cpt4.jar 5
```

You will be prompted for your UMLS API key. This tool downloads the
real CPT-4 descriptions and merges them into your local `CONCEPT.csv`
before you load the vocabulary. Skip this step only if you do not need
CPT4 codes (for example, MIMIC-III's `cptevents.csv`).

**Note:** the UMLS license request itself can take up to a few days to
be approved. You can proceed with every other step of this guide while
waiting, and come back to load CPT4 later (see the self-healing sync
step below, which lets you add a vocabulary after the fact without
starting over).

## 7. Configure the `.env` File

Create a `.env` file at the project root:

```env
# --- LLM provider selection (see app/models/config.py) ---
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile

GROQ_API_KEY=<your_key>
MISTRAL_API_KEY=<your_key_if_used>

# --- PostgreSQL: OMOP_TEMP and OMOP_FINAL live in the same DB, different schemas ---
DB_HOST=localhost
DB_PORT=5432
DB_NAME=<your_database_name>
DB_USER=postgres
DB_PASSWORD=<your_password>
OMOP_TEMP_SCHEMA=omop_temp
OMOP_FINAL_SCHEMA=omop

# --- DQD (R) ---
RSCRIPT_BIN=Rscript
DQD_OUTPUT_DIR=runs

# --- CDM ---
CDM_VERSION=5.4
```

**Important:** if `DB_PASSWORD` (or any other variable here) is also
set as an exported shell environment variable on your machine, the
shell variable silently takes priority over `.env` and this project
will connect with the wrong credentials without any obvious error. If
you hit an unexplained authentication failure, check with:

```bash
echo "DB_PASSWORD=$DB_PASSWORD"
```

and `unset DB_PASSWORD` (or the relevant variable) if it is set.

## 8. Load the Vocabulary Into `cdm_vocab`

```bash
python database/scripts/load_vocabulary.py --input-dir ~/Downloads/athena-vocabulary
```

This step fully replaces the contents of `cdm_vocab` on every run — it
is not incremental. If you are adding a vocabulary after an initial
load (for example, adding CPT4 or NDC later), download a fresh,
complete export containing everything you need (old and new
vocabularies together), not just the new one alone.

Verify every numeric/date column loaded with the correct type (not as
raw text):

```bash
python scripts/verify_vocab_types.py
```

Expected output: `Tout est correctement typé` / all columns correctly
typed.

## 9. Synchronize `omop_temp` With `cdm_vocab`

The Mapping Agent searches `cdm_vocab` directly, but the Validation
Agent's Data Quality Dashboard needs the same vocabulary data mirrored
inside `omop_temp` itself.

```bash
cat database/sql/005_populate_omop_temp_vocab.sql | sudo -u postgres psql -d <your_database_name>
```

This script is self-healing: it compares row counts between
`cdm_vocab` and `omop_temp` and automatically refreshes any table
where they differ. It is always safe to re-run, including after
loading a new vocabulary later.

## 10. Verify Your `metadata.yaml` Declarations Against the Real Vocabulary

Before running any batch, confirm that every `standard:` value you
plan to declare in a batch's `metadata.yaml` actually corresponds to a
real, loaded vocabulary — not an OMOP *domain* name mistaken for a
vocabulary name (a real, recurring source of errors: `Condition`,
`Drug`, `Unit`, and `Route` are domains, not vocabularies; the correct
vocabulary names are different and must be looked up).

```bash
python scripts/verify_standard_to_vocabulary.py
```

Address any `❌` or `⚠️` result before proceeding — either fix the
vocabulary name used in the code, or return to step 6 to download a
vocabulary you are missing.

## 11. Prepare Your Source Data

Place your raw source files under:

```
data/raw/<source_name>/<batch_name>/
```

For example:

```
data/raw/hospital_a/batch007/patients.csv
data/raw/hospital_a/batch007/conditions.csv
data/raw/hospital_a/batch007/encounters.csv
...
```

## 12. Write `metadata.yaml` for the Batch

Create `data/raw/<source_name>/<batch_name>/metadata.yaml`, declaring:

- Every source file present, and the `standard` vocabulary for each
  coded field it contains
- Any internal reference field (an id that must be joined to a
  dictionary table before it becomes a real code) as `standard: local`
- The `type_concepts` section, with each `*_type_concept_id` value
  confirmed against your own loaded vocabulary (never guessed):

```sql
SELECT concept_id, concept_name
FROM cdm_vocab.concept
WHERE vocabulary_id = 'Type Concept' AND concept_name ILIKE '%EHR%';
```

Refer to an existing `metadata.yaml` in this project (for example
under `data/raw/hospital_a/`) as a template.

## 13. Run the Pipeline

```bash
python -m app.main --source <source_name>
```

This automatically discovers the next unprocessed batch for that
source, and runs Profiling, Mapping, Transformation, Loading, and
Validation in sequence, with automatic failure recovery through the
Coordinator and Root Cause Analyzer agents.

The run's name is generated automatically and includes the batch name,
for example `RUN-batch007-a1b2c3d4`.

### Optional: monitor progress in real time

In a second terminal, once you have the execution id from the first
terminal's output:

```bash
python scripts/watch_run.py RUN-batch007-a1b2c3d4
```

### Optional: run only part of the pipeline for testing

```bash
python scripts/test_profiling_only.py --source <source_name>
python scripts/test_profiling_and_mapping.py --source <source_name>
python scripts/test_profiling_mapping_transformation.py --source <source_name>
python scripts/test_full_pipeline_to_loading.py --source <source_name>
```

Note that these scripts stop before Validation — no
`runs/<execution_id>/validation/` folder will be produced by them.

## 14. Run the Data Quality Dashboard Manually (if needed)

The Validation Agent runs this automatically as part of step 13, but
you can also run it manually against an existing `omop_temp` state:

```bash
Rscript database/scripts/run_dqd.R \
  --cdmSchema omop_temp \
  --outputFolder runs/<execution_id>/validation \
  --cdmSourceName <execution_id>
```

This script is self-contained: it downloads its own JDBC driver into
`database/jdbc_drivers/` on first run (skipping the download on later
runs if already present), and reads `.env` itself regardless of which
directory you run it from.

The R package `DataQualityDashboard` must be installed once beforehand:

```r
remotes::install_github("OHDSI/DataQualityDashboard")
```

### View the results in the Shiny dashboard

```bash
ls runs/<execution_id>/validation/
Rscript -e 'DataQualityDashboard::viewDqDashboard(normalizePath("runs/<execution_id>/validation/<the_json_file>.json"))'
```

Always use an absolute path (via `normalizePath()`), and avoid stray
quotation marks in the path if copy-pasting from a shell command that
contained parentheses.

## 15. Inspect What Actually Happened

Several tools are available for understanding a completed run in
detail:

```bash
# Provenance: which source table/field/value produced which result, at every level
python scripts/provenance_report.py <execution_id>

# A numeric snapshot of omop_temp's current state, saved to CSV
python scripts/omop_temp_snapshot.py --label "my_run"
```

## 16. Troubleshooting Checklist

| Symptom | Likely cause | Where to look |
|---|---|---|
| `password authentication failed` | A shell-exported `DB_PASSWORD` overriding `.env` | Step 7's note |
| `checkPathToDriver()` error in R | JDBC driver missing | Step 14 handles this automatically now |
| A vocabulary search always fails for a specific field | A domain name used instead of a real vocabulary name | Step 10 |
| `visit_occurrence` (or another table) ends up empty | A required concept or date was never resolved for any row — check the Loading result's `dropped_missing_concept` / `dropped_missing_date` diagnostics | `runs/<execution_id>/loading_load_temp/result.json` |
| A newly added vocabulary doesn't seem to be found | `omop_temp` was never re-synchronized after loading it | Re-run step 9 |

## Summary of the Full Sequence

1. Install PostgreSQL, Python, R
2. Install Python dependencies
3. Create the `<your_database_name>` database
4. Create the four schemas
5. Install the OMOP CDM v5.4 DDL into `omop_temp` and `omop`
6. Download the vocabulary from Athena (and run `cpt4.jar` if CPT4 is needed)
7. Configure `.env`
8. Load the vocabulary into `cdm_vocab`
9. Synchronize `omop_temp` with `cdm_vocab`
10. Verify vocabulary declarations against the real database
11. Place raw source files under `data/raw/<source>/<batch>/`
12. Write `metadata.yaml` for the batch
13. Run `python -m app.main --source <source_name>`
14. Review the Data Quality Dashboard results
15. Inspect provenance and snapshots as needed
