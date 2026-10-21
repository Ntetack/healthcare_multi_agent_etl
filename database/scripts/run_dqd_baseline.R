library(DataQualityDashboard)
library(DatabaseConnector)

cd <- createConnectionDetails(
  dbms = "postgresql",
  server = "localhost/mimic",
  user = "postgres",
  password = Sys.getenv("BASELINE_DB_PASSWORD"),
  port = 5432,
  pathToDriver = "database/jdbc_drivers"
)

executeDqChecks(
  connectionDetails     = cd,
  cdmDatabaseSchema     = "omop",
  vocabDatabaseSchema   = "omop",
  resultsDatabaseSchema = "omop",
  cdmSourceName         = "mimic-baseline",
  outputFolder          = "runs/baseline_dqd",
  cdmVersion            = "5.4",
  checkLevels           = c("TABLE", "FIELD", "CONCEPT"),
  tablesToExclude       = c("VISIT_DETAIL", "CONCEPT", "VOCABULARY", "CONCEPT_ANCESTOR", "CONCEPT_RELATIONSHIP",
                            "CONCEPT_CLASS", "CONCEPT_SYNONYM", "RELATIONSHIP", "DOMAIN"),
  numThreads            = 4,
  writeToTable          = FALSE
)
