#!/usr/bin/env Rscript
suppressMessages(
    library(argparse)
)

get.args <- function() {
    parser <- ArgumentParser()

    parser$add_argument(
        "input.table", metavar="input table",
        type="character",
        help="table containing variables to be modeled")
    parser$add_argument(
        "--header",
        action="store_true", default=TRUE,
        help="input table contains header line")
    parser$add_argument(
        "--no-header", dest="header",
        action="store_false",
        help="input table contains no header line")
    parser$add_argument(
        "--row-names", dest="row.names",
        action="store_true", default=FALSE,
        help="input table contains row names")
    parser$add_argument(
        "--col-prefix", dest="col.prefix",
        default=FALSE,
        help=paste(
            "prefix to use in new column names.",
            "if none given uses row names or 'V'"))

    args <- parser$parse_args()

    if (args$input.table == "-") args$input.table <- file("stdin")

    args$row.names <- if (args$row.names) 1 else NULL


    args
}

main <- function() {
    args <- get.args()

    data <- read.table(args$input.table,
                       header=args$header,
                       row.names=args$row.names,
                       check.names=FALSE)
    # determine prefix for the new columns
    col.prefix <-
        # use user-provided prefix if one exists
        if (is.character(args$col.prefix)) {
            args$col.prefix
        # use row names if they exist
        } else if (is.numeric(args$row.names)) {
            row.names(data)
        # use the string "V" as a last resort
        } else {
            "V"
        }

    identity.matrix <- diag(nrow(data))
    
    data[col.prefix] <- identity.matrix

    write.table(data, quote=FALSE)
}

main()
