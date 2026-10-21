"""
Fixed load order for the 9 in-scope OMOP tables, derived from OMOP CDM's
official foreign key constraints (OHDSI/CommonDataModel's "constraints"
DDL file - see database/scripts/install_cdm.R) - not inferred or guessed
at runtime. A table must be loaded after every other in-scope table it
references:
  - PERSON has no dependency among the 9.
  - OBSERVATION_PERIOD, VISIT_OCCURRENCE, DEATH reference PERSON.
  - The 5 clinical event tables reference PERSON and VISIT_OCCURRENCE.
"""
from __future__ import annotations

LOAD_ORDER = [
    "person",
    "observation_period",
    "visit_occurrence",
    "death",
    "condition_occurrence",
    "drug_exposure",
    "measurement",
    "procedure_occurrence",
    "observation",
]

# OBSERVATION_PERIOD is NOT filled by mapping a source field - its
# start/end dates are DERIVED (min/max of a person's clinical event
# dates across the other tables). Out of scope for this Loading pass;
# tracked explicitly rather than silently skipped.
DERIVED_TABLES = {"observation_period"}
