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
        action="store_true", default=FALSE,
        help="input table contains header line")
    parser$add_argument(
        "--row-names", dest="row.names",
        action="store_true", default=FALSE,
        help="use row names from first column to name new columns")
    parser$add_argument(
        "--col-prefix", dest="col.prefix",
        default=FALSE,
        help=paste(
            "prefix to use in new column names.",
            "if none given uses row names or 'V'"))
    parser$add_argument(
        "-n", "--n-groups", dest="n.groups",
        default=1, type="integer",
        help=paste(
            "number of groups in input data.",
            "must divide the number of columns in the file.",
            "uses 1 group by default"))
    parser$add_argument(
        "--quote",
        default=FALSE, type="character",
        help="quoting character used on strings, or none if not given")
    parser$add_argument(
        "--sep",
        default="",
        help="input table separator string. if none given uses all whitespace")
    parser$add_argument(
        "--output-sep", dest="output.sep",
        default="\t",
        help="output table separator string. if none given uses tabs")

    args <- parser$parse_args()

    args$input.table <- file(
        if (args$input.table == "-")
            "stdin"
        else
            args$input.table)

    stopifnot(args$n.groups > 0)

    args
}

main <- function() {
    args <- get.args()

    data <- read.table(args$input.table,
                       header=args$header,
                       sep=args$sep,
                       row.names=NULL, as.is=TRUE,
                       check.names=FALSE)

    data.rows <- nrow(data)
    stopifnot((data.rows %% args$n.groups) == 0)
    group.rows <- data.rows %/% args$n.groups

    # determine prefix for the new columns
    col.prefix <-
        # use user-provided prefix if one exists
        if (is.character(args$col.prefix)) {
            args$col.prefix
        # use row names if they exist
        } else if (args$row.names) {
            d <- data[[1]]
            d[1:group.rows]
        # use the string "V" as a last resort
        } else {
            "V"
        }

    
    identity.dimn <- data.rows %/% args$n.groups

    identity.matrix <- diag(identity.dimn)
    repeated.identity.matrices <- rep(list(identity.matrix), args$n.groups)
    stacked.identity.matrices <- do.call(rbind, repeated.identity.matrices)

    print(stacked.identity.matrices)
    data[col.prefix] <- stacked.identity.matrices

    write.table(data, quote=args$quote, sep=args$output.sep, row.names=FALSE)
}

main()
