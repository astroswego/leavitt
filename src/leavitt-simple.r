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
        "--output",
        choices=c("summary", "coefficients", "fitted.values"),
        default="fitted.values",
        help="output format")
    parser$add_argument(
        "--header",
        action="store_true", default=TRUE,
        help="input table contains header line")
    parser$add_argument(
        "--no-header", dest="header",
        action="store_false",
        help="input table contains no header line")
    parser$add_argument(
        "--individual-coef", dest="individual.coef",
        action="store_true", default=FALSE,
        help="add a fit coefficient for each individual entity")

    args <- parser$parse_args()

    if (args$input.table == "-") args$input.table <- file("stdin")

    args
}

print.coefficients <- function(model) {
    # not yet implemented
}

unused.name <- function(name, names) {
    "If string name is not in list names, returns it."
    "Otherwise adds numbers 0, 1, ... to the end of name until"
    "it is not present in names."
    unused.name.iter <- function(num, names) {
        "Iteratively finds an unused name by appending increasing numbers to"
        "desired name"
        current.name <- paste(name, num, sep="")
        if (current.name %in% names) {
            unused.name.iter(num+1, name, names)
        } else {
            current.name
        }
    }

    if (name %in% names) {
        # name is already used, so iteratively find an unused name
        unused.name.iter(0, names)
    } else {
        name
    }
}

main <- function() {
    args <- get.args()

    data <- read.table(args$input.table, header=args$header)

    # adds identity matrix to end of data frame if individual coefficients
    # are requested by --individual-coef command line argument
    if (args$individual.coef) {
        # column name for identity matrix columns must not be an existing name
        new.name <- unused.name("indiv", colnames(data))
        # identity matrix
        id.matrix <- diag(nrow(data))
        # add identity matrix to data frame
        data[[new.name]] <- id.matrix
    }

    model <- lm(data)

    if (args$output == "summary") {
        print(summary(model))
    } else if (args$output == "coefficients") {
        print.coefficients(model)
    } else if (args$output == "fitted.values") {
        cat(model$fitted.values, sep="\n")
    } else {
        cat("invalid option", end="\n")
    }
}

main()
