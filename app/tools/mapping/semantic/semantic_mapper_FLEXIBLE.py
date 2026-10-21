"""
Semantic mapping tools: search/match source codes against the OMOP
standard vocabulary (CONCEPT / CONCEPT_RELATIONSHIP tables), constrained
by the `standard` declared for the field in this batch's metadata.yaml
(ICD10, LOINC, SNOMED, RxNorm, ...) or by a fixed OMOP vocabulary domain
(Gender, Race, ...). The Mapping Agent calls these tools and records
confidence/reason - it does not guess the vocabulary itself.
"""
from __future__ import annotations

import re

from sqlalchemy import text

from app.tools.database.db import session_scope

# Maps a human-facing standard name to the vocabulary_id values used in
# the OMOP CONCEPT table.
STANDARD_TO_VOCABULARY = {
    "ICD10": ["ICD10", "ICD10CM"],
    "ICD9CM": ["ICD9CM"],       # diagnoses - distinct from ICD9Proc below
    "ICD9Proc": ["ICD9Proc"],   # procedures - a DIFFERENT OMOP vocabulary than ICD9CM
    "CPT4": ["CPT4"],
    "NDC": ["NDC"],
    "LOINC": ["LOINC"],
    "SNOMED": ["SNOMED"],
    "RxNorm": ["RxNorm"],
    "CVX": ["CVX"],
    # OMOP-side, fixed vocabularies (see app/tools/mapping/omop_target_schema.py) -
    # not declared per batch like the others above, since they describe
    # the OMOP target, not the source.
    "Gender": ["Gender"],
    "Race": ["Race"],
    "Ethnicity": ["Ethnicity"],
    "Type Concept": ["Type Concept"],
    "Condition Status": ["Condition Status"],
    "Route": ["SNOMED"],  # "Route" is an OMOP DOMAIN, not a vocabulary_id - confirmed: SNOMED supplies real route concepts
    "Operator": ["Operator"],
    "Unit": ["UCUM"],  # "Unit" is an OMOP DOMAIN, not a vocabulary_id - UCUM is the real vocabulary
    "Meas Value": ["LOINC", "SNOMED"],  # "Meas Value" is a DOMAIN - confirmed: LOINC (dominant) and SNOMED both supply real value concepts
    "Visit": ["Visit"],
    "Concept": [],
}

# Minimum trigram similarity (0-1) for the fuzzy fallback to accept a
# candidate - below this, "no match" is more honest than a bad guess.
FUZZY_SIMILARITY_THRESHOLD = 0.3


def normalize_text(value: str) -> str:
    """Trims leading/trailing whitespace and collapses internal repeated
    whitespace - e.g. " Hispanic  " -> "Hispanic". Does NOT change case
    (ILIKE/casefold comparisons already handle that) and does NOT fix
    spelling - that's the fuzzy fallback's job."""
    return re.sub(r"\s+", " ", value.strip())


def negation_variant(value: str) -> str | None:
    """Common data convention: a concatenated 'non' prefix meaning
    'not X' (e.g. 'nonhispanic' -> 'not hispanic', 'nonsmoker' -> 'not
    smoker'). OMOP vocabularies often spell the concept with a space
    ("Not Hispanic or Latino"), which a source's concatenated form never
    matches via substring search, and which can also fall below the
    fuzzy-similarity threshold due to the length difference. Returns
    None if the value doesn't start with this pattern - this is a
    general English negation-form rule, not specific to any one
    vocabulary or value."""
    lowered = value.lower()
    if lowered.startswith("non") and len(lowered) > 3 and lowered[3].isalpha():
        return "not " + value[3:]
    return None


def _normalize_icd9_code(code: str, is_procedure: bool) -> str:
    """ICD9 codes are conventionally written WITH a decimal point in
    OMOP's vocabulary (e.g. '307.50', confirmed by OHDSI's own ICD9CM
    documentation: 'All ICD9CM codes are represented in the format
    containing the dot') - but many raw EHR exports (MIMIC-III among
    them) store the digits without it (e.g. '30750'). This is a
    property of the ICD9 coding system itself, not specific to any one
    hospital, so it's normalized here for ANY source declaring
    ICD9CM/ICD9Proc, not special-cased to MIMIC.

    Diagnosis codes: 3 digits before the decimal (4 for E-codes, 2 for
    V-codes is naturally covered since 'V' occupies one of the 3
    positions). Procedure codes: 2 digits before the decimal."""
    code = code.strip().upper()
    if "." in code:
        return code  # already in the expected format
    decimal_position = 2 if is_procedure else (4 if code.startswith("E") else 3)
    if len(code) <= decimal_position:
        return code  # a bare category code with no subcategory digit - no dot needed
    return code[:decimal_position] + "." + code[decimal_position:]


def search_concept(source_value: str, standard: str, limit: int = 5, require_standard: bool = True) -> list[dict]:
    """Searches the OMOP CONCEPT table for candidates matching
    source_value, constrained to the vocabularies implied by `standard`.
    Candidates are RANKED by match quality:
      0. exact code match
      1. exact name match (case-insensitive, whitespace-normalized)
      2. substring match (fuzzy in the loose sense, but still literal)
      3. trigram similarity match (typo-tolerant, e.g. "Hyspanic" ->
         "Hispanic") - ONLY attempted if tiers 0-2 find nothing, so a
         reliable match is never overridden by a fuzzy guess.

    `require_standard=True` (the default) only returns Standard
    concepts (standard_concept = 'S') - correct for OUR OWN fixed
    target vocabularies (Gender, Race, Ethnicity, Type Concept, ...),
    which genuinely only ever contain standard concepts. Set to False
    when searching a SOURCE classification vocabulary that may be
    entirely non-standard (ICD9CM, ICD9Proc, ICD10CM, CPT4, ...) - see
    resolve_concept_pair(), which is the correct entry point for that
    case: it finds the source concept AS-IS (standard or not), then
    separately follows 'Maps to' to the real standard concept.

    Returns [] immediately for an empty/blank source_value - without
    this guard, the ILIKE '%' || value || '%' clause would degrade to
    ILIKE '%%', matching every concept in the vocabulary.
    """
    if not source_value or not source_value.strip():
        return []
    vocab_ids = STANDARD_TO_VOCABULARY.get(standard, [])
    if not vocab_ids:
        return []

    if standard in ("ICD9CM", "ICD9Proc"):
        source_value = _normalize_icd9_code(source_value, is_procedure=(standard == "ICD9Proc"))

    normalized = normalize_text(source_value)
    candidates_to_try = [normalized]
    variant = negation_variant(normalized)
    if variant:
        candidates_to_try.append(variant)

    standard_clause = "AND standard_concept = 'S'" if require_standard else ""

    with session_scope() as session:
        for candidate_value in candidates_to_try:
            rows = session.execute(
                text(
                    f"""
                    SELECT concept_id, concept_name, concept_code, vocabulary_id, domain_id, standard_concept
                    FROM cdm_vocab.concept
                    WHERE vocabulary_id = ANY(:vocab_ids)
                      AND (concept_code = :code OR concept_name ILIKE :like_code)
                      {standard_clause}
                    LIMIT 50
                    """
                ),
                {"vocab_ids": vocab_ids, "code": candidate_value, "like_code": f"%{candidate_value}%"},
            ).mappings().all()
            candidates = [dict(r) for r in rows]
            if candidates:
                ranked = sorted(candidates, key=lambda c: _match_rank(c, candidate_value))
                return ranked[:limit]

        # No exact/substring match for the value or its negation variant
        # - try typo-tolerant trigram similarity as a last resort
        # (requires pg_trgm, see database/sql/004_pg_trgm.sql). Checks
        # BOTH concept_name (descriptive text) AND concept_code (typo'd
        # codes) against every candidate string tried above.
        for candidate_value in candidates_to_try:
            fuzzy_rows = session.execute(
                text(
                    f"""
                    SELECT concept_id, concept_name, concept_code, vocabulary_id, domain_id, standard_concept,
                           GREATEST(similarity(concept_name, :value), similarity(concept_code, :value)) AS sim
                    FROM cdm_vocab.concept
                    WHERE vocabulary_id = ANY(:vocab_ids)
                      {standard_clause}
                      AND (similarity(concept_name, :value) > :threshold
                           OR similarity(concept_code, :value) > :threshold)
                    ORDER BY sim DESC
                    LIMIT :limit
                    """
                ),
                {"vocab_ids": vocab_ids, "value": candidate_value,
                 "threshold": FUZZY_SIMILARITY_THRESHOLD, "limit": limit},
            ).mappings().all()
            if fuzzy_rows:
                return [dict(r) for r in fuzzy_rows]

    return []


def _match_rank(candidate: dict, normalized_value: str) -> int:
    """Lower is better. 0 = exact code match, 1 = exact name match
    (case-insensitive), 2 = substring match only."""
    if candidate["concept_code"] == normalized_value:
        return 0
    if candidate["concept_name"].casefold() == normalized_value.casefold():
        return 1
    return 2


# Confidence assigned per match tier - lets a future human-review
# threshold distinguish a certain match from a typo-tolerant guess,
# rather than the old binary 1.0/0.0. Fuzzy matches do NOT get a flat
# constant here - see map_concept()/resolve_concept_pair(), which use
# the ACTUAL computed similarity score instead. A fuzzy match that
# barely cleared FUZZY_SIMILARITY_THRESHOLD (likely coincidental
# character overlap, e.g. a Race value like "ASIAN" accidentally
# resembling some unrelated Ethnicity concept) and one that scored very
# high (e.g. "BLACK/AFRICAN AMERICAN" against "Black or African
# American" - genuinely the right concept, just reached via fuzzy
# matching because of the "/" punctuation) are NOT equally trustworthy,
# and treating them identically was a real bug: it either let both
# through blindly, or excluded both including the genuinely correct one.
_CONFIDENCE_BY_RANK = {0: 1.0, 1: 0.95, 2: 0.7}


# Rigid, deterministic mapping for Ethnicity specifically - the
# flexible substring/fuzzy search in map_concept() has a real bug for
# this vocabulary: "hispanic" is a literal SUBSTRING of BOTH "Hispanic
# or Latino" AND "Not Hispanic or Latino", so the substring tier
# matches both concepts, and since search_concept() is called with
# limit=1 (truncating at the SQL level, before Python's own ranking
# logic ever runs), the database can arbitrarily return the WRONG one
# with no way to tell them apart - confirmed as the actual cause of
# hispanic/nonhispanic both resolving to the same wrong concept.
# Deliberately rigid rather than fixed here: only recognizes Synthea's
# own two known raw values, never guesses on anything else (unlike
# MIMIC's spelled-out "HISPANIC OR LATINO" style values, which the
# general search still handles - this override only applies to these
# two exact short forms).
_ETHNICITY_EXACT_NAME_LOOKUP = {
    "hispanic": "Hispanic or Latino",
    "nonhispanic": "Not Hispanic or Latino",
}


def resolve_ethnicity_rigid(value: str) -> dict | None:
    """Rigid override for Ethnicity: maps a known raw value to its
    EXACT concept name, then looks up that concept's real id in the
    live vocabulary (never a hardcoded number, so it stays correct
    across installations) - no substring or fuzzy matching involved at
    all. Returns None for any value other than the two known forms,
    falling through to the normal map_concept() path (e.g. for a
    source that spells out "HISPANIC OR LATINO" in full already)."""
    concept_name = _ETHNICITY_EXACT_NAME_LOOKUP.get(value.strip().lower())
    if concept_name is None:
        return None
    with session_scope() as session:
        row = session.execute(
            text(
                """
                SELECT concept_id, concept_name, concept_code, vocabulary_id, domain_id, standard_concept
                FROM cdm_vocab.concept
                WHERE vocabulary_id = 'Ethnicity' AND lower(concept_name) = lower(:name)
                  AND standard_concept = 'S'
                LIMIT 1
                """
            ),
            {"name": concept_name},
        ).mappings().first()
        if row is None:
            return None
        result = dict(row)
        result["_match_confidence"] = 1.0
        return result


def map_concept(source_value: str, standard: str) -> dict | None:
    """Returns the single best candidate for source_value, or None if
    none was found (including the fuzzy fallback). Attaches a
    `_match_confidence` key reflecting how the match was found, so
    callers can distinguish a certain match from a typo-tolerant guess.

    Only ever returns a Standard concept (require_standard=True) -
    correct for OUR OWN fixed target vocabularies (Gender, Race,
    Ethnicity, Type Concept, ...). For a SOURCE classification
    vocabulary that may be non-standard (ICD9CM, CPT4, ...), use
    resolve_concept_pair() instead - see its docstring for why."""
    candidates = search_concept(source_value, standard, limit=1)
    if not candidates:
        return None

    candidate = candidates[0]
    if "sim" in candidate:
        # The real similarity score IS the confidence - see the module-
        # level note above _CONFIDENCE_BY_RANK for why a flat constant
        # was wrong here.
        candidate["_match_confidence"] = candidate["sim"]
        return candidate

    normalized = normalize_text(source_value)
    variant = negation_variant(normalized)
    rank = min(
        _match_rank(candidate, normalized),
        _match_rank(candidate, variant) if variant else 2,
    )
    candidate["_match_confidence"] = _CONFIDENCE_BY_RANK[rank]
    return candidate


def find_standard_concept_via_maps_to(source_concept_id: int) -> dict | None:
    """Follows the 'Maps to' relationship from source_concept_id to its
    STANDARD equivalent - the correct, universal OMOP ETL convention for
    turning a source/classification code (e.g. an ICD9CM diagnosis code,
    which is itself non-standard) into the Standard concept that
    actually belongs in a *_concept_id field. Returns None if
    source_concept_id has no valid 'Maps to' target (a real, honest
    possibility - not every source code has a standard equivalent)."""
    with session_scope() as session:
        row = session.execute(
            text(
                """
                SELECT c2.concept_id, c2.concept_name, c2.concept_code, c2.vocabulary_id, c2.domain_id
                FROM cdm_vocab.concept_relationship cr
                JOIN cdm_vocab.concept c2 ON cr.concept_id_2 = c2.concept_id
                WHERE cr.concept_id_1 = :source_concept_id
                  AND cr.relationship_id = 'Maps to'
                  AND cr.invalid_reason IS NULL
                  AND c2.standard_concept = 'S'
                LIMIT 1
                """
            ),
            {"source_concept_id": source_concept_id},
        ).mappings().first()
        return dict(row) if row else None


def resolve_concept_pair(source_value: str, standard: str) -> dict:
    """The correct, two-step OMOP resolution for a SOURCE-vocabulary
    code (as opposed to map_concept(), which is for OUR OWN already-
    standard target vocabularies):

      1. source_concept: the concept representing source_value AS-IS in
         its own declared vocabulary - found WITHOUT requiring
         standard_concept='S', since many source vocabularies (ICD9CM,
         ICD9Proc, ICD10CM, CPT4, ...) are themselves entirely
         non-standard classification systems in OMOP. Searching them
         with a standard-only filter (the old, incorrect behavior)
         would find literally nothing, regardless of how correctly the
         vocabulary name/code format were otherwise handled.
      2. standard_concept: the Standard concept the source concept maps
         to, via 'Maps to' (see find_standard_concept_via_maps_to). If
         the source concept IS ALREADY standard (true for SNOMED,
         LOINC, RxNorm, CVX - vocabularies that are themselves
         Standard), it IS the standard concept - no separate lookup
         needed, and often no 'Maps to' row would even exist for it.

    Returns {"source_concept": dict | None, "standard_concept": dict | None}.
    Both are None if source_value couldn't be found in its own
    vocabulary at all."""
    source_concept = None
    candidates = search_concept(source_value, standard, limit=1, require_standard=False)
    if candidates:
        source_concept = candidates[0]
        source_concept["_match_confidence"] = (
            source_concept["sim"] if "sim" in source_concept
            else _CONFIDENCE_BY_RANK[_match_rank(source_concept, normalize_text(source_value))]
        )

    if source_concept is None:
        return {"source_concept": None, "standard_concept": None}

    if source_concept.get("standard_concept") == "S":
        return {"source_concept": source_concept, "standard_concept": source_concept}

    standard_concept = find_standard_concept_via_maps_to(source_concept["concept_id"])
    return {"source_concept": source_concept, "standard_concept": standard_concept}