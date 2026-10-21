-- Enables trigram-based fuzzy text matching (pg_trgm), used as a
-- last-resort fallback in search_concept() when neither an exact code
-- match nor a substring match finds anything - e.g. "Hyspanic" (typo)
-- matching "Hispanic" in the vocabulary. Only triggers when exact/
-- substring matching returns nothing, so it never overrides a reliable
-- match with a fuzzy guess.
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Speeds up the fuzzy fallback query (similarity() against concept_name
-- AND concept_code) on the vocabulary table, which is large (millions
-- of rows).
CREATE INDEX IF NOT EXISTS idx_concept_name_trgm
    ON cdm_vocab.concept USING gin (concept_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_concept_code_trgm
    ON cdm_vocab.concept USING gin (concept_code gin_trgm_ops);
