# Utility function to create a unified table from a papercheck::read() paper object
# Includes: title, keywords, doi, description, authors (JSON), references (JSON), cross_references (JSON)
#
#' Create a summary table for a papercheck paper object
#'
#' @param paper A paper object returned by papercheck::read()
#' @param collapse_keywords Logical, collapse keyword vector into single semicolon-separated string (default TRUE)
#' @param authors_format One of "rows" (each author is a JSON object) or "columns" (jsonlite's default dataframe serialization)
#' @param pretty_json Logical, pretty-print JSON (default FALSE)
#'
#' @return A tibble/data.frame with one row containing metadata + JSON columns
#' @examples
#' # paper <- papercheck::read("path/to/xml")
#' # create_paper_table(paper)
#'
create_paper_table <- function(paper,
                               collapse_keywords = TRUE,
                               authors_format = c("rows", "columns"),
                               pretty_json = FALSE) {
  stopifnot(!missing(paper))
  authors_format <- match.arg(authors_format)
  if (!requireNamespace("jsonlite", quietly = TRUE)) {
    stop("Package 'jsonlite' is required for JSON serialization. Please install it.")
  }
  if (!requireNamespace("tibble", quietly = TRUE)) {
    stop("Package 'tibble' is required. Please install it (install.packages('tibble')).")
  }

  # Helper to safely extract from info_table
  info_tbl <- try(papercheck::info_table(paper, c("title", "keywords", "doi", "description")), silent = TRUE)

  get_info_value <- function(name) {
    # Attempt multiple access strategies
    if (!inherits(info_tbl, "try-error")) {
      # Possible structures: (a) wide with columns, (b) long with name/value
      if (name %in% names(info_tbl)) {
        return(info_tbl[[name]])
      }
      # long form guess
      long_name_col <- intersect(c("name", "field", "key"), names(info_tbl))
      long_value_col <- intersect(c("value", "val"), names(info_tbl))
      if (length(long_name_col) == 1 && length(long_value_col) == 1) {
        row <- info_tbl[info_tbl[[long_name_col]] == name, , drop = FALSE]
        if (nrow(row) == 1) return(row[[long_value_col]])
      }
    }
    # fallback: attempt direct element access on paper object
    if (!is.null(paper[[name]])) return(paper[[name]])
    if (!is.null(paper$info) && !is.null(paper$info[[name]])) return(paper$info[[name]])
    return(NA_character_)
  }

  title <- get_info_value("title")
  keywords <- get_info_value("keywords")
  doi <- get_info_value("doi")
  description <- get_info_value("description")

  # Normalize keywords
  if (is.list(keywords) && length(keywords) == 1) keywords <- keywords[[1]]
  if (is.character(keywords) && length(keywords) > 1 && collapse_keywords) {
    keywords_collapsed <- paste(unique(keywords[nzchar(keywords)]), collapse = "; ")
  } else if (is.character(keywords)) {
    keywords_collapsed <- paste(keywords, collapse = "; ")
  } else {
    keywords_collapsed <- ifelse(length(keywords) == 0 || all(is.na(keywords)), NA_character_, as.character(keywords))
  }

  # Authors
  authors_df <- try(papercheck::author_table(paper), silent = TRUE)
  if (inherits(authors_df, "try-error")) {
    authors_df <- data.frame()
  }

  authors_json <- jsonlite::toJSON(authors_df, dataframe = authors_format, auto_unbox = TRUE, na = "null", pretty = pretty_json)

  # References (bib) & cross-references (xrefs)
  bib_obj <- paper$bib %||% list()
  xrefs_obj <- paper$xrefs %||% list()

  references_json <- jsonlite::toJSON(bib_obj, auto_unbox = TRUE, na = "null", pretty = pretty_json)
  cross_references_json <- jsonlite::toJSON(xrefs_obj, auto_unbox = TRUE, na = "null", pretty = pretty_json)

  # Build tibble
  tibble::tibble(
    title = as.character(title %||% NA_character_),
    keywords = keywords_collapsed,
    doi = as.character(doi %||% NA_character_),
    description = as.character(description %||% NA_character_),
    authors_json = as.character(authors_json),
    references = as.character(references_json),
    cross_references = as.character(cross_references_json)
  )
}

# Define infix %||% if not already available
`%||%` <- function(a, b) {
  if (is.null(a) || (is.atomic(a) && length(a) == 0)) b else a
}
