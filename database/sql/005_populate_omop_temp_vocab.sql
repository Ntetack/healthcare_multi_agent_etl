-- Synchronizes omop_temp's vocabulary tables (concept, vocabulary,
-- domain, concept_class, relationship, concept_relationship,
-- concept_synonym, concept_ancestor, drug_strength) with cdm_vocab -
-- the real source of truth used by the Mapping Agent's own vocabulary
-- searches. DQD's isForeignKey checks (and any downstream tool
-- expecting a self-contained CDM instance) need this data ALSO present
-- in omop_temp itself, not just in cdm_vocab.
--
-- SELF-HEALING BY ROW COUNT, not just "only if empty": comparing counts
-- (rather than checking omop_temp for emptiness) means this script
-- correctly refreshes omop_temp whenever cdm_vocab grows - e.g. after
-- adding a new vocabulary (NDC, CPT4, CVX, ...) to an existing
-- installation - not just on a brand-new setup. A prior version of
-- this script only checked "is omop_temp currently empty", which
-- worked for a first install but left omop_temp silently STALE forever
-- after any later vocabulary addition to cdm_vocab.
--
-- Columns are named EXPLICITLY on both sides (never "SELECT *") -
-- cdm_vocab's tables were populated via a Python/pandas loader whose
-- physical column order does not necessarily match the official CDM
-- DDL's order used for omop_temp's tables.
--
-- ONE-TIME-ISH operation (millions of rows) - run this after any
-- cdm_vocab reload/expansion, not per ETL batch. These tables are NOT
-- in OMOP_TABLES (app/tools/database/db.py) and are therefore never
-- touched by truncate_omop_temp() - safe to run independently of the
-- pipeline's own per-batch resets.

DO $$
DECLARE
    cdm_count BIGINT;
    temp_count BIGINT;
BEGIN
    -- concept ---------------------------------------------------------
    SELECT COUNT(*) INTO cdm_count FROM cdm_vocab.concept;
    SELECT COUNT(*) INTO temp_count FROM omop_temp.concept;
    IF cdm_count != temp_count THEN
        TRUNCATE omop_temp.concept;
        INSERT INTO omop_temp.concept (
            concept_id, concept_name, domain_id, vocabulary_id, concept_class_id,
            standard_concept, concept_code, valid_start_date, valid_end_date, invalid_reason
        )
        SELECT
            concept_id, concept_name, domain_id, vocabulary_id, concept_class_id,
            standard_concept, concept_code, valid_start_date, valid_end_date, invalid_reason
        FROM cdm_vocab.concept;
    END IF;

    -- vocabulary --------------------------------------------------------
    SELECT COUNT(*) INTO cdm_count FROM cdm_vocab.vocabulary;
    SELECT COUNT(*) INTO temp_count FROM omop_temp.vocabulary;
    IF cdm_count != temp_count THEN
        TRUNCATE omop_temp.vocabulary;
        INSERT INTO omop_temp.vocabulary (
            vocabulary_id, vocabulary_name, vocabulary_reference, vocabulary_version, vocabulary_concept_id
        )
        SELECT
            vocabulary_id, vocabulary_name, vocabulary_reference, vocabulary_version, vocabulary_concept_id
        FROM cdm_vocab.vocabulary;
    END IF;

    -- domain --------------------------------------------------------
    SELECT COUNT(*) INTO cdm_count FROM cdm_vocab.domain;
    SELECT COUNT(*) INTO temp_count FROM omop_temp.domain;
    IF cdm_count != temp_count THEN
        TRUNCATE omop_temp.domain;
        INSERT INTO omop_temp.domain (domain_id, domain_name, domain_concept_id)
        SELECT domain_id, domain_name, domain_concept_id
        FROM cdm_vocab.domain;
    END IF;

    -- concept_class --------------------------------------------------
    SELECT COUNT(*) INTO cdm_count FROM cdm_vocab.concept_class;
    SELECT COUNT(*) INTO temp_count FROM omop_temp.concept_class;
    IF cdm_count != temp_count THEN
        TRUNCATE omop_temp.concept_class;
        INSERT INTO omop_temp.concept_class (concept_class_id, concept_class_name, concept_class_concept_id)
        SELECT concept_class_id, concept_class_name, concept_class_concept_id
        FROM cdm_vocab.concept_class;
    END IF;

    -- relationship --------------------------------------------------
    SELECT COUNT(*) INTO cdm_count FROM cdm_vocab.relationship;
    SELECT COUNT(*) INTO temp_count FROM omop_temp.relationship;
    IF cdm_count != temp_count THEN
        TRUNCATE omop_temp.relationship;
        INSERT INTO omop_temp.relationship (
            relationship_id, relationship_name, is_hierarchical, defines_ancestry,
            reverse_relationship_id, relationship_concept_id
        )
        SELECT
            relationship_id, relationship_name, is_hierarchical, defines_ancestry,
            reverse_relationship_id, relationship_concept_id
        FROM cdm_vocab.relationship;
    END IF;

    -- concept_relationship --------------------------------------------
    SELECT COUNT(*) INTO cdm_count FROM cdm_vocab.concept_relationship;
    SELECT COUNT(*) INTO temp_count FROM omop_temp.concept_relationship;
    IF cdm_count != temp_count THEN
        TRUNCATE omop_temp.concept_relationship;
        INSERT INTO omop_temp.concept_relationship (
            concept_id_1, concept_id_2, relationship_id, valid_start_date, valid_end_date, invalid_reason
        )
        SELECT
            concept_id_1, concept_id_2, relationship_id, valid_start_date, valid_end_date, invalid_reason
        FROM cdm_vocab.concept_relationship;
    END IF;

    -- concept_synonym --------------------------------------------------
    SELECT COUNT(*) INTO cdm_count FROM cdm_vocab.concept_synonym;
    SELECT COUNT(*) INTO temp_count FROM omop_temp.concept_synonym;
    IF cdm_count != temp_count THEN
        TRUNCATE omop_temp.concept_synonym;
        INSERT INTO omop_temp.concept_synonym (concept_id, concept_synonym_name, language_concept_id)
        SELECT concept_id, concept_synonym_name, language_concept_id
        FROM cdm_vocab.concept_synonym;
    END IF;

    -- concept_ancestor --------------------------------------------------
    SELECT COUNT(*) INTO cdm_count FROM cdm_vocab.concept_ancestor;
    SELECT COUNT(*) INTO temp_count FROM omop_temp.concept_ancestor;
    IF cdm_count != temp_count THEN
        TRUNCATE omop_temp.concept_ancestor;
        INSERT INTO omop_temp.concept_ancestor (
            ancestor_concept_id, descendant_concept_id, min_levels_of_separation, max_levels_of_separation
        )
        SELECT
            ancestor_concept_id, descendant_concept_id, min_levels_of_separation, max_levels_of_separation
        FROM cdm_vocab.concept_ancestor;
    END IF;

    -- drug_strength --------------------------------------------------
    SELECT COUNT(*) INTO cdm_count FROM cdm_vocab.drug_strength;
    SELECT COUNT(*) INTO temp_count FROM omop_temp.drug_strength;
    IF cdm_count != temp_count THEN
        TRUNCATE omop_temp.drug_strength;
        INSERT INTO omop_temp.drug_strength (
            drug_concept_id, ingredient_concept_id, amount_value, amount_unit_concept_id,
            numerator_value, numerator_unit_concept_id, denominator_value,
            denominator_unit_concept_id, box_size, valid_start_date, valid_end_date, invalid_reason
        )
        SELECT
            drug_concept_id, ingredient_concept_id, amount_value, amount_unit_concept_id,
            numerator_value, numerator_unit_concept_id, denominator_value,
            denominator_unit_concept_id, box_size, valid_start_date, valid_end_date, invalid_reason
        FROM cdm_vocab.drug_strength;
    END IF;
END $$;
