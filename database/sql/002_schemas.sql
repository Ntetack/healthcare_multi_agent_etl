-- OMOP_TEMP: persistent structure, TRUNCATEd at the start of every run
-- (see app/tools/database/db.py::truncate_omop_temp). Its sole purpose
-- is to give the DQD a clean, isolated view of the current batch.
CREATE SCHEMA IF NOT EXISTS omop_temp;

-- OMOP_FINAL: the actual OMOP CDM destination.
CREATE SCHEMA IF NOT EXISTS omop;

-- Standard OMOP vocabulary tables (CONCEPT, CONCEPT_RELATIONSHIP, ...),
-- loaded once from the OHDSI Athena vocabulary download.
CREATE SCHEMA IF NOT EXISTS cdm_vocab;

-- Staging area: one table per (source, discovered table), created
-- dynamically by app/tools/staging/staging_writer.py - this migration
-- only needs to create the schema itself, tables are created on the fly.
CREATE SCHEMA IF NOT EXISTS staging;

-- NOTE: this project does not redefine the OMOP CDM DDL itself. Use the
-- official DDL generator (OHDSI/CommonDataModel) for omop_temp/omop
-- table definitions, matching CDM_VERSION in .env.
