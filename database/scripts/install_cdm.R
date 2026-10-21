#!/usr/bin/env Rscript
# Generates the OMOP CDM DDL/constraints/indexes SQL files for PostgreSQL
# using buildRelease(), as three SEPARATE files - matching OHDSI's
# recommended order (DDL -> load data -> constraints -> indexes).
#
# We deliberately do NOT use executeDdl() here: in some CommonDataModel
# versions it bundles table creation and constraints together, which can
# fail with "no unique constraint matching given keys for referenced
# table" when statements run out of dependency order (see OHDSI/
# CommonDataModel GitHub issue #439 for the same failure mode).
# Generating the files and running only the DDL file ourselves avoids
# that entirely; constraints/indexes are applied later, after data load.
#
# Install once:
#   install.packages("devtools")
#   devtools::install_github("OHDSI/CommonDataModel")
#
# Usage:
#   Rscript install_cdm.R --outputFolder database/ddl

suppressMessages(library(CommonDataModel))
suppressMessages(library(optparse))

option_list <- list(
  make_option("--outputFolder", type = "character", default = "database/ddl")
)
opt <- parse_args(OptionParser(option_list = option_list))

CommonDataModel::buildRelease(
  cdmVersions = Sys.getenv("CDM_VERSION", "5.4"),
  targetDialects = "postgresql",
  outputfolder = opt$outputFolder
)

cat(sprintf("DDL/constraints/indexes SQL files generated in '%s'.\n", opt$outputFolder))
cat("Next: run only the *ddl* file against each schema (omop_temp, omop) via psql.\n")
cat("Apply *constraints* and *indexes* files LATER, after the first data load.\n")
