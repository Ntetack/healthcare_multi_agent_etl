# Healthcare Multi-Agent ETL Framework — MVP Scaffold

Squelette d'implémentation conforme à l'architecture v6 (7 agents, staging
STRING/TEXT, DQD comme validateur unique, RCA transversal, chargement
OMOP_TEMP → OMOP_FINAL en append simple).

## Comment ce squelette gère "n'importe quelle source" (MIMIC, Synthea, ...)

Ajouter une nouvelle source ne demande **aucun nouveau code d'ingestion**, et un batch n'est **jamais un fichier unique** — un vrai export hospitalier contient plusieurs tables distinctes (MIMIC : `PATIENTS.csv`, `ADMISSIONS.csv`, `DIAGNOSES.csv`, `LABEVENTS.csv`, ... ; export OMOP-natif : `person.csv`, `visit_occurrence.csv`, `condition_occurrence.csv`, ... ; FHIR : un type de ressource par fichier). Trois mécanismes rendent ça possible :

1. **Découverte automatique des tables** (`app/tools/data/source_loader.py::load_source_tables()`) : chaque fichier d'un dossier de batch devient sa propre table, identifiée par son nom de fichier (ou le `resourceType` FHIR) — **jamais fusionnées entre elles**. Seuls des fichiers représentant la même table éclatée en plusieurs morceaux (`DIAGNOSES_part1.csv`, `DIAGNOSES_part2.csv`) sont recombinés.
2. **Profiling automatique par table** (`app/agents/profiling.py`) : l'agent liste les tables présentes dans le dossier — il n'a pas besoin que `source_metadata.yaml` les énumère toutes — et profile chacune séparément (schéma, patterns, codes détectés, interprétation LLM).
3. **Métadonnées auto-portées, déclarées par batch, EXACTEMENT deux formes canoniques** : chaque batch apporte son propre `metadata.yaml`, à l'intérieur de son propre dossier (`data/raw/<source>/<batch>/metadata.yaml`) — pas un fichier central, pas même un fichier par source. Le framework ne connaît que deux formes, jamais une variante par fournisseur/hôpital :

   **CSV / Parquet**, indexé par fichier :
   ```yaml
   format: csv
   files:
     conditions.csv:
       CODE:
         standard: SNOMED
   ```

   **FHIR**, indexé par type de ressource :
   ```yaml
   format: fhir
   resources:
     Condition:
       code:
         standard: SNOMED-CT
     MedicationRequest:
       medicationCodeableConcept:
         standard: RxNorm
   ```

   Les deux sont normalisées dès la lecture (`read_batch_metadata()`) vers la même structure interne (`{table: {champ: standard}}`) — le Profiling Agent et le Mapping Agent ne savent jamais laquelle des deux formes a été utilisée. Les tables non listées sont quand même découvertes et profilées, juste sans indice de standard. Les standards non alignés sur les `vocabulary_id` OMOP (ex: `SNOMED-CT`) sont normalisés automatiquement.

   Onboarder une nouvelle source ou faire évoluer le schéma d'une source existante ne demande **aucune modification de fichier existant** — juste déposer un nouveau dossier de batch avec son propre `metadata.yaml` ; les batches précédents restent inchangés et corrects même si le schéma a changé depuis.

Quatre exemples réels (MIMIC, OMOP-natif, Synthea CSV, Synthea FHIR) sont déjà dans `data/raw/<source>/2026-08-19_batch1/metadata.yaml`.

## Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # renseigner GROQ_API_KEY / MISTRAL_API_KEY / DB_*
```

Base de données (PostgreSQL) :

```bash
psql -d omopdb -f database/sql/002_schemas.sql
psql -d omopdb -f database/sql/003_pipeline_meta.sql
# + charger le DDL OMOP CDM officiel (OHDSI/CommonDataModel) dans omop_temp / omop
# + charger le vocabulaire OHDSI (Athena) dans cdm_vocab
```

DQD (R) :

```r
install.packages(c("DataQualityDashboard", "DatabaseConnector", "optparse"))
```

OMOP CDM (tables uniquement pour l'instant — contraintes/index viennent après le premier chargement) :

```bash
Rscript database/scripts/install_cdm.R --outputFolder database/ddl
# Génère 3 fichiers séparés (ddl, constraints, indexes) sous database/ddl/postgresql/.
# Le fichier ddl contient des placeholders "@cdmDatabaseSchema" (syntaxe SqlRender,
# pas une variable psql) : on les remplace avant exécution, une fois par schéma cible.

DDL_FILE="database/ddl/postgresql/OMOP CDM ddl - PostgreSQL.sql"

sed 's/@cdmDatabaseSchema/omop_temp/g' "$DDL_FILE" | psql -d omopdb
sed 's/@cdmDatabaseSchema/omop/g'      "$DDL_FILE" | psql -d omopdb
```

## Lancer un run

```bash
python -m app.main --source hospital_a
```

Au premier run d'une source, `--save-mapping NOM` conserve le mapping ; pour les batches suivants, `--replay-mapping NOM` le rejoue (voir « Conserver et rejouer un mapping »).

## État de complétude de ce scaffold

| Composant | État |
|---|---|
| Structure du repo, 7 agents, schémas, graphe LangGraph | ✅ fonctionnel |
| Découverte + lecture multi-tables par batch (CSV/Parquet/FHIR NDJSON) | ✅ fonctionnel, testé |
| Profiling tools (schema/profile/patterns/codings), par table | ✅ fonctionnel, testé |
| **Détection de nouvelles données** (nouveaux sous-dossiers par batch) | ✅ fonctionnel, testé (`app/tools/data/folder_watcher.py`) |
| Appel LLM réel dans le Profiling Agent (par table) | ✅ câblé (`_interpret_with_llm`, JSON structuré) |
| Mapping structurel + sémantique, par table | ✅ câblé (`app/agents/mapping.py`) — toutes les valeurs distinctes mappées, `concept_id` écrit dans staging |
| Résolution structurelle LLM (PERSON/VISIT_OCCURRENCE/OBSERVATION_PERIOD/DEATH) | ✅ câblé (`_resolve_structural_targets`) |
| Écriture réelle en staging (enrichi, une seule écriture) | ✅ fonctionnel, testé |
| Transformation (cast dates/types), pilotée par le Mapping | ✅ câblé — ne transforme que les champs identifiés par `structural_target_mappings`, pas de pattern-matching aveugle |
| Mapping sémantique (`search_concept`) | ✅ validé sur données réelles (93-100% selon standard) |
| DQD (`dqd_check.py` + `run_dqd.R`) | ⏳ nécessite R + DataQualityDashboard installés |
| Loading OMOP_TEMP → OMOP_FINAL (append simple, pas d'upsert) | ✅ fonctionnel pour les sources déjà nommées comme des tables OMOP |
| **Routage table source → table/domaine OMOP cible** (MIMIC, FHIR) | ⏳ TODO — actuellement seules les tables déjà nommées comme OMOP (`condition_occurrence`, ...) sont chargées ; `DIAGNOSES`, `Condition`, etc. sont profilées/mappées mais pas encore routées vers la bonne table OMOP au chargement |

## Détection de nouvelles données

Chaque source a un **dossier racine** (`data/raw/<source_name>/`) — purement un espace de noms, sans métadonnées propres. Chaque nouveau batch arrive dans un sous-dossier neuf et daté, **avec son propre `metadata.yaml`** (voir section ci-dessus).

Le Profiling Agent détecte automatiquement les nouveaux sous-dossiers en les comparant à `pipeline_meta.processed_folders` (créée par `database/sql/003_pipeline_meta.sql`) — la détection elle-même ne lit aucune métadonnée, c'est une opération purement filesystem/DB :
- Aucun nouveau dossier → le run s'arrête proprement (`status: NOTHING_TO_PROCESS`), sans erreur.
- Un nouveau dossier → il est marqué `IN_PROGRESS`, son `metadata.yaml` est lu (obligatoire — un batch sans `metadata.yaml` échoue explicitement plutôt que de réutiliser silencieusement le schéma d'un batch précédent), puis il devient la source du run.
- Le Loading Agent le marque `SUCCESS` une fois le chargement confirmé — jamais le Profiling Agent lui-même, qui ne sait pas si le reste du pipeline aboutira.
- Le Root Cause Analyzer le marque `FAILED` en cas d'échec non récupérable ailleurs dans le pipeline, ce qui le rend à nouveau éligible à un run futur.

## Tests

```bash
pytest tests/ -v -m "not integration"   # tests unitaires, sans DB/R
pytest tests/ -v                          # tout, nécessite Postgres + R configurés
```

## Hypothèses documentées

- **Exécution séquentielle** : `OMOP_TEMP` est tronqué au début de
  chaque run. Des runs concurrents se marcheraient dessus — si ça devient
  un besoin réel, remplacer par un schéma/suffixe par `execution_id`.
- **Append-only, pas d'upsert** : `promote_to_final()` fait un simple
  `INSERT ... SELECT` de OMOP_TEMP vers OMOP_FINAL. Un même patient
  chargé dans deux runs différents sera dupliqué dans OMOP_FINAL. Choix
  volontaire pour garder le MVP simple ; la déduplication cross-batch
  (crosswalk, upsert) est explicitement hors scope pour l'instant.

## Mapping vers les tables OMOP cibles

Prototype limité à 9 tables : `PERSON`, `OBSERVATION_PERIOD`, `VISIT_OCCURRENCE`, `CONDITION_OCCURRENCE`, `DRUG_EXPOSURE`, `MEASUREMENT`, `PROCEDURE_OCCURRENCE`, `OBSERVATION`, `DEATH`. Deux mécanismes, aucun des deux ne devine ou ne construit sa propre base de connaissance :

**1. Routage par domaine** (5 tables événement clinique) : une fois qu'un concept est trouvé via `search_concept()`, son `domain_id` indique automatiquement la table OMOP cible et les champs à remplir. Piloté par le `standard` déclaré dans `metadata.yaml`.

**2. Résolution par champ cible, exhaustive** (les 9 tables) : pour **chaque champ réel** d'une table cible — introspecté depuis le DDL OMOP déjà installé (`information_schema.columns`, jamais une liste choisie à la main) — le Mapping Agent détermine s'il faut :
   - **un vocabulaire fixe** (`gender_concept_id` → `Gender`, etc.) : déclaré dans `app/config/reference/omop_vocabulary_fields.yaml`, un fichier fourni par l'utilisateur, **jamais généré par un agent**. Le champ source correspondant (`gender_source_value`) est retrouvé automatiquement par une règle de convention de nommage OMOP (`app/tools/mapping/omop_target_schema.py::find_paired_source_value_field`), pas par une correspondance codée en dur.
   - **une résolution LLM structurelle** (`birth_datetime`, `condition_start_date`, ...) : le LLM propose la meilleure correspondance `(table source, champ source)` parmi toutes les tables découvertes dans le batch, sans déclaration manuelle.

   Le **type SQL réel** de chaque champ (introspecté, jamais deviné) détermine directement le cast appliqué par la Transformation — pas de table de correspondance nom-de-champ → type maintenue à la main.

Un champ sans correspondance plausible (ex: `condition_type_concept_id`, qui représente la provenance de l'enregistrement, pas une valeur présente dans les données source) reste explicitement non résolu, avec la raison enregistrée — jamais deviné.

## Conserver et rejouer un mapping

Le premier batch d'une source coûte des appels au modèle (choix des colonnes sources, jointures de dictionnaire). Les batches suivants de la même source n'ont en général pas besoin de refaire ces choix : on peut **sauvegarder le mapping d'un batch validé et le rejouer** sur un autre.

```bash
# 1. Premier batch, mode automatique. Le mapping n'est sauvegardé que si le run va jusqu'à la promotion (DQD passé).
python -m app.main --source hospital_a --save-mapping hospital_a_v1

# 2. Batches suivants : le modèle n'est plus appelé pour ce que le snapshot couvre.
python -m app.main --source hospital_a --replay-mapping hospital_a_v1
```

Le snapshot est un fichier JSON versionnable, `mappings/<source>/<nom>.json` (dossier modifiable avec `MAPPING_SNAPSHOT_DIR`). Il ne contient que des codes et libellés distincts, jamais de lignes de patients. `--overwrite-mapping` autorise le remplacement d'un snapshot existant.

**Ce qui est rejoué, ce qui est recalculé.** Sont figées les décisions du modèle : la colonne source de chaque champ cible, la colonne finalement retenue pour chaque champ de vocabulaire, les jointures de dictionnaire locales. Les recherches de concepts restent recalculées à chaque batch, car elles sont déterministes et ne coûtent aucun token : un code absent du premier batch est donc résolu normalement. Les mappings curés (`fixed_value_mappings`) gardent leur priorité absolue.

**Garde-fous.**
- Un snapshot appartient à une source et à une version du CDM : il est refusé pour une autre source ou une autre version.
- Les noms de tables et de colonnes sont retrouvés sans tenir compte de la casse. Un snapshot ne contourne jamais le contrôle de recouvrement réel d'une jointure locale (`MIN_JOIN_OVERLAP`).
- Quand le snapshot ne peut pas fournir une décision (colonne disparue, source qui alimente une table pour la première fois, champ de vocabulaire qui ne correspond plus à rien), `--replay-on-mismatch fallback` (défaut) la résout de la façon habituelle et la liste dans le rapport, tandis que `--replay-on-mismatch fail` arrête le run.
- Le rapport `runs/<id>/mapping/report.md` contient une section « Replayed mapping » : décisions réutilisées, décisions non couvertes, jointures rejetées, avertissements (version des vocabulaires, fichier curé modifié, colonnes nouvelles ou manquantes) et **dérive des valeurs** : nombre de valeurs communes aux deux batches dont le concept a changé, ce qui révèle une mise à jour du vocabulaire.

Ce mécanisme sert la production. Pour mesurer la capacité du framework à découvrir un mapping sur une nouvelle source, gardez le mode automatique : un run rejoué ne mesure plus le modèle, mais la mémoire du snapshot.

## Transformation

Cast les champs identifiés par le Mapping Agent, selon leur type SQL réel :
- **Champs vocabulaire** (`concept_id` déjà résolu par valeur distincte) : regroupés et appliqués à toute la colonne en une fois (`__omop_<table>__<champ>`)
- **Champs simples** : cast selon `data_type` (date/timestamp → `parse_date`, numérique → `cast_decimal`, entier → `cast_integer`, booléen → `normalize_boolean`, sinon copié tel quel)

Rien n'est transformé qui n'a pas été explicitement identifié par le Mapping — pas de détection de motif à l'aveugle sur des colonnes qui "ressemblent" à des dates.

## Loading

Assemble les lignes OMOP finales à partir de ce que Mapping et Transformation ont résolu, suivant un **ordre de chargement fixe** (`app/tools/mapping/omop_load_order.py`, dérivé des contraintes de clés étrangères officielles OMOP) : `PERSON` d'abord, puis `OBSERVATION_PERIOD`/`VISIT_OCCURRENCE`/`DEATH`, puis les 5 tables événement.

Quand les champs d'une même table cible viennent de **tables sources différentes** (ex: `person_source_value` dans `patients`, `visit_start_date` dans `encounters`), le Loading Agent demande au LLM **une seule fois par paire de tables** quelle colonne les relie — la jointure elle-même est ensuite exécutée de façon déterministe (pandas), jamais par le LLM. La réponse est mise en cache pour tout le run.

Conventions appliquées automatiquement :
- `year_of_birth`/`month_of_birth`/`day_of_birth` dérivés de `birth_datetime` quand la source ne les fournit pas séparément (règle fixe du CDM, pas une correspondance à deviner)
- Un champ `concept_id` non résolu vaut `0` ("No matching concept"), jamais `NULL` — convention officielle OMOP

`OBSERVATION_PERIOD` est explicitement **hors scope** : ses dates sont dérivées (min/max des événements cliniques d'un patient), pas mappées depuis un champ source — signalé clairement, jamais silencieusement ignoré.

## Root Cause Analyzer et Coordinator

Toute exception non gérée dans **n'importe quelle étape** (Profiling, Mapping, Transformation, Loading, Validation) est capturée et transformée en `FailureEvent`, plutôt que de faire planter tout le pipeline. Le Root Cause Analyzer (vrai appel LLM, plus un pile-ou-face) évalue la gravité (`tolerable`/`serious`/`fatal`) et recommande une action.

Le **Coordinator** est le seul endroit qui décide réellement de la suite : il traduit la recommandation du RCA en étape concrète à reprendre, applique le budget de tentatives (2 par étape), et arrête proprement (`stop`) si le budget est épuisé ou si le RCA recommande une intervention humaine. Les fonctions de routage (`app/graph/routing.py`) ne font que lire cette décision déjà prise — elles ne décident jamais elles-mêmes.
