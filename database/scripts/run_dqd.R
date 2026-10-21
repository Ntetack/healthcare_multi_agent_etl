#!/usr/bin/env Rscript
# Thin CLI wrapper around DataQualityDashboard::executeDqChecks(),
# called from app/tools/validation/dqd_check.py via subprocess.
#
# Requires: install.packages("DataQualityDashboard")
#
# Usage (works from ANY directory - see get_script_dir() below):
#   Rscript database/scripts/run_dqd.R --cdmSchema omop_temp --outputFolder runs/<id>/validation --cdmSourceName <id>
#
# Optional settings, read from .env (all have a default, so nothing changes
# until you define them):
#   DQD_CHECK_LEVELS       comma list among TABLE,FIELD,CONCEPT
#                          (default: TABLE,FIELD,CONCEPT)
#   DQD_TABLES_TO_EXCLUDE  comma list of CDM tables not evaluated
#                          (default: the DQD default list of vocabulary tables)
#   DQD_CHECK_NAMES        comma list of check names to run, e.g.
#                          isStandardValidConcept,fkDomain
#                          (default: empty = all checks)
#   DQD_THRESHOLDS_DIR     folder holding customised copies of the three
#                          threshold CSV files of DataQualityDashboard,
#                          absolute or relative to the project root
#                          (default: empty = package defaults)
#   DQD_NUM_THREADS        number of parallel queries (default: 1)

suppressMessages(library(DataQualityDashboard))
suppressMessages(library(optparse))
suppressMessages(library(DatabaseConnector))

# Locate the PROJECT ROOT from this script's OWN file path on disk -
# never from the current working directory, so this script behaves
# identically regardless of where the user happens to `cd` before
# running it (from the project root, from inside database/scripts/, or
# anywhere else). This script lives at
# <project_root>/database/scripts/run_dqd.R, so the project root is two
# directory levels up from wherever this file actually is.
get_script_dir <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", args, value = TRUE)
  if (length(file_arg) == 0) {
    return(getwd())  # interactive session / unusual invocation - best-effort fallback
  }
  dirname(normalizePath(sub("^--file=", "", file_arg[1])))
}
project_root <- dirname(dirname(get_script_dir()))

# Load the SAME .env file our Python pipeline reads, so this script
# works identically whether it's invoked by that pipeline (which
# already has these variables in its own environment, inherited by
# this script as a subprocess) OR run directly from a raw shell (which
# never sourced .env on its own).
env_file <- file.path(project_root, ".env")
if (file.exists(env_file)) {
  readRenviron(env_file)
}

option_list <- list(
  make_option("--cdmSchema", type = "character"),
  make_option("--outputFolder", type = "character"),
  make_option("--cdmSourceName", type = "character")
)
opt <- parse_args(OptionParser(option_list = option_list))

# Read a comma separated environment variable as a character vector.
# An unset or empty variable gives the default; an empty default gives
# character(0), which DataQualityDashboard treats as "no restriction".
split_env <- function(name, default = "") {
  value <- Sys.getenv(name, default)
  if (identical(trimws(value), "")) {
    return(character(0))
  }
  trimws(strsplit(value, ",")[[1]])
}

# Resolve a path against the project root unless it is already absolute.
resolve_path <- function(path) {
  is_absolute <- grepl("^(/|[A-Za-z]:[/\\\\])", path)
  if (is_absolute) path else file.path(project_root, path)
}

# The PostgreSQL JDBC driver is downloaded ONCE into a fixed,
# project-local folder rather than relying on DATABASECONNECTOR_JAR_FOLDER
# being set (undocumented environment state that varies machine to
# machine, and silently breaks this script - see checkPathToDriver()
# error - the moment it isn't). Checked explicitly before downloading -
# downloadJdbcDrivers() does NOT skip re-downloading on its own when the
# file is already present, so without this check, a network hiccup on a
# SUBSEQUENT run would fail even though a working driver already exists
# from a previous successful run.
jdbc_driver_folder <- file.path(project_root, "database", "jdbc_drivers")
if (!dir.exists(jdbc_driver_folder)) {
  dir.create(jdbc_driver_folder, recursive = TRUE)
}
driver_already_present <- length(list.files(jdbc_driver_folder, pattern = "\\.jar$")) > 0
if (!driver_already_present) {
  downloadJdbcDrivers("postgresql", pathToDriver = jdbc_driver_folder)
}

connectionDetails <- DatabaseConnector::createConnectionDetails(
  dbms = "postgresql",
  server = paste0(Sys.getenv("DB_HOST"), "/", Sys.getenv("DB_NAME")),
  user = Sys.getenv("DB_USER"),
  password = Sys.getenv("DB_PASSWORD"),
  port = Sys.getenv("DB_PORT"),
  pathToDriver = jdbc_driver_folder
)

# ---- Configurable part -------------------------------------------------

check_levels <- split_env("DQD_CHECK_LEVELS", "TABLE,FIELD,CONCEPT")
tables_to_exclude <- split_env(
  "DQD_TABLES_TO_EXCLUDE",
  paste(
    "CONCEPT", "VOCABULARY", "CONCEPT_ANCESTOR", "CONCEPT_RELATIONSHIP",
    "CONCEPT_CLASS", "CONCEPT_SYNONYM", "RELATIONSHIP", "DOMAIN",
    sep = ","
  )
)
check_names <- split_env("DQD_CHECK_NAMES")
num_threads <- as.integer(Sys.getenv("DQD_NUM_THREADS", "1"))

dqd_args <- list(
  connectionDetails = connectionDetails,
  cdmDatabaseSchema = opt$cdmSchema,
  resultsDatabaseSchema = opt$cdmSchema,
  cdmSourceName = opt$cdmSourceName,
  outputFolder = opt$outputFolder,
  cdmVersion = Sys.getenv("CDM_VERSION", "5.4"),
  checkLevels = check_levels,
  tablesToExclude = tables_to_exclude,
  numThreads = num_threads,
  writeToTable = FALSE
)

# Only passed when set, so that an empty value keeps the package default.
if (length(check_names) > 0) {
  dqd_args$checkNames <- check_names
}

# Customised thresholds: the folder must hold the three CSV files below,
# copied from system.file("csv", package = "DataQualityDashboard") and edited.
thresholds_dir <- Sys.getenv("DQD_THRESHOLDS_DIR", "")
if (!identical(trimws(thresholds_dir), "")) {
  thresholds_dir <- resolve_path(thresholds_dir)
  cdm_version <- Sys.getenv("CDM_VERSION", "5.4")
  table_csv   <- file.path(thresholds_dir, sprintf("OMOP_CDMv%s_Table_Level.csv", cdm_version))
  field_csv   <- file.path(thresholds_dir, sprintf("OMOP_CDMv%s_Field_Level.csv", cdm_version))
  concept_csv <- file.path(thresholds_dir, sprintf("OMOP_CDMv%s_Concept_Level.csv", cdm_version))
  missing_csv <- c(table_csv, field_csv, concept_csv)[!file.exists(c(table_csv, field_csv, concept_csv))]
  if (length(missing_csv) > 0) {
    stop("DQD_THRESHOLDS_DIR is set but these files are missing: ",
         paste(missing_csv, collapse = ", "))
  }
  dqd_args$tableCheckThresholdLoc <- table_csv
  dqd_args$fieldCheckThresholdLoc <- field_csv
  dqd_args$conceptCheckThresholdLoc <- concept_csv
}

# Written on stderr, so it ends up in the error text that the Validation
# Agent forwards to the Root Cause Analyzer if the run fails.
message(
  "DQD settings: levels=", paste(check_levels, collapse = ","),
  " | excluded tables=", if (length(tables_to_exclude)) paste(tables_to_exclude, collapse = ",") else "none",
  " | check names=", if (length(check_names)) paste(check_names, collapse = ",") else "all",
  " | thresholds=", if (identical(trimws(thresholds_dir), "")) "package defaults" else thresholds_dir
)

do.call(executeDqChecks, dqd_args)
