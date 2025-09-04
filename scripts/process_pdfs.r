# --- Configuration ---
# --- Configuration ---
PDF_SOURCE_DIR <- '/home/jakub/Projects/paper_testing/documents_to_test/psych_science_pdf_oa'
OUTPUT_DIR <- '/home/jakub/Projects/paper_testing/output'
CONFIG_PATH <- '/home/jakub/Projects/paper_testing/config.json'
MAX_RETRIES <- 3
TIMEOUT_SECONDS <- 300  # 5 minutes
NTFY_URL <- 'https://ntfy.jakubwerner.com/papercheck'
CORRIGENDUM_PAPERS_START_DICT <- list( # maps for which papers we have to specify start=X
    "0956797617710785.pdf" = 6,
    "0956797618795679.pdf" = 2,
    "0956797618815482.pdf" = 2,
    "0956797619830329.pdf" = 2,
    "0956797620959594.pdf" = 4,
)

library(papercheck)