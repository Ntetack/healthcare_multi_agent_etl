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

# Raw values that mean "no value" in an export rather than a code or a
# label (a numeric zero filling an empty NDC column, a stringified
# missing value, a lone dash). They are never searched: a short token
# like "0" has no business being compared to a vocabulary, and comparing
# it anyway is how an unrelated concept got attached to every row that
# carried it. The list is deliberately limited to tokens that cannot be
# a real code or label in any vocabulary this project searches; words
# that can be a legitimate answer ("unknown", "other") are NOT here.
PLACEHOLDER_VALUES = frozenset({"0", "nan", "none", "null", "nat", "<na>", "n/a", "na", "-", "--", "?", "."})


def is_placeholder(value) -> bool:
    """True for an empty value or one of PLACEHOLDER_VALUES."""
    if value is None:
        return True
    normalized = normalize_text(str(value)).casefold()
    return normalized == "" or normalized in PLACEHOLDER_VALUES


def normalize_text(value: str) -> str:
    """Trims leading/trailing whitespace and collapses internal repeated
    whitespace - e.g. " Hispanic  " -> "Hispanic". Does NOT change case
    (the comparisons below are case-insensitive on names) and does NOT
    fix spelling: matching is exact."""
    return re.sub(r"\s+", " ", value.strip())


def negation_variant(value: str) -> str | None:
    """Common data convention: a concatenated 'non' prefix meaning
    'not X' (e.g. 'nonhispanic' -> 'not hispanic', 'nonsmoker' -> 'not
    smoker'). OMOP vocabularies often spell the concept with a space,
    which a source's concatenated form does not match as written; the
    variant is searched (exactly) as a second candidate. Returns
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


def search_concept(
    source_value: str, standard: str, limit: int = 5, require_standard: bool = True
) -> list[dict]:
    """Searches the OMOP CONCEPT table for candidates matching
    source_value, constrained to the vocabularies implied by `standard`.
    Matching is EXACT, for every vocabulary:
      0. exact code match
      1. exact name match (case-insensitive, whitespace-normalized)
    There is no substring tier and no trigram-similarity fallback. Both
    were removed after they were seen attaching unrelated concepts to
    short or generic values (the NDC placeholder "0" matched every
    concept whose name contains a zero, and landed on a rectal cream;
    "Solution" and "Lactic acid" came from the same mechanism). Not
    finding a concept is a correct outcome here; a confident-looking
    wrong one is not.

    `require_standard=True` (the default) only returns Standard
    concepts (standard_concept = 'S') - correct for OUR OWN fixed
    target vocabularies (Gender, Race, Ethnicity, Type Concept, ...),
    which genuinely only ever contain standard concepts. Set to False
    when searching a SOURCE classification vocabulary that may be
    entirely non-standard (ICD9CM, ICD9Proc, ICD10CM, CPT4, ...) - see
    resolve_concept_pair(), which is the correct entry point for that
    case: it finds the source concept AS-IS (standard or not), then
    separately follows 'Maps to' to the real standard concept.

    Returns [] immediately, without querying, for an empty value or a
    placeholder (see PLACEHOLDER_VALUES).
    """
    if is_placeholder(source_value):
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
                    SELECT concept_id, concept_name, concept_code, vocabulary_id, domain_id, standard_concept, invalid_reason
                    FROM cdm_vocab.concept
                    WHERE vocabulary_id = ANY(:vocab_ids)
                      AND (concept_code = :code OR lower(concept_name) = lower(:code))
                      {standard_clause}
                    ORDER BY (concept_code = :code) DESC,
                             (standard_concept = 'S') DESC NULLS LAST,
                             (invalid_reason IS NULL) DESC,
                             concept_id
                    LIMIT 50
                    """
                ),
                {"vocab_ids": vocab_ids, "code": candidate_value},
            ).mappings().all()
            candidates = [dict(r) for r in rows]
            if candidates:
                ranked = sorted(candidates, key=lambda c: _match_rank(c, candidate_value))
                return ranked[:limit]

    return []


def _match_rank(candidate: dict, normalized_value: str) -> int:
    """Lower is better. 0 = exact code match, 1 = exact name match
    (case-insensitive). 2 is what any other candidate would get; the
    search no longer returns such candidates, the value is kept so the
    confidence table keeps its three tiers."""
    if candidate["concept_code"] == normalized_value:
        return 0
    if candidate["concept_name"].casefold() == normalized_value.casefold():
        return 1
    return 2


# Confidence assigned per match tier. Only the first two tiers can come
# out of search_concept() now (exact code, exact name); the third entry
# is kept for the rank scale used by _match_rank().
_CONFIDENCE_BY_RANK = {0: 1.0, 1: 0.95, 2: 0.7}


def map_concept(source_value: str, standard: str) -> dict | None:
    """Returns the single best candidate for source_value, or None if
    none was found. Attaches a `_match_confidence` key reflecting which
    exact tier matched (code or name).

    Only ever returns a Standard concept (require_standard=True) -
    correct for OUR OWN fixed target vocabularies (Gender, Race,
    Ethnicity, Type Concept, ...). For a SOURCE classification
    vocabulary that may be non-standard (ICD9CM, CPT4, ...), use
    resolve_concept_pair() instead - see its docstring for why."""
    candidates = search_concept(source_value, standard, limit=1)
    if not candidates:
        return None

    candidate = candidates[0]
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
                  AND c2.invalid_reason IS NULL
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
        source_concept["_match_confidence"] = _CONFIDENCE_BY_RANK[
            _match_rank(source_concept, normalize_text(source_value))
        ]

    if source_concept is None:
        return {"source_concept": None, "standard_concept": None}

    if source_concept.get("standard_concept") == "S":
        return {"source_concept": source_concept, "standard_concept": source_concept}

    standard_concept = find_standard_concept_via_maps_to(source_concept["concept_id"])
    return {"source_concept": source_concept, "standard_concept": standard_concept}
