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
        choices=c("summary", "fitted.values"), default="fitted.values",
        help="output format")
    parser$add_argument(
        "--header",
        action="store_true", default=TRUE,
        help="input table contains header line")
    parser$add_argument(
        "--no-header", dest="header",
        action="store_false",
        help="input table contains no header line")

    args <- parser$parse_args()

    if (args$input.table == "-") args$input.table = file("stdin")

    args
}

main <- function() {
    args <- get.args()

    data <- read.table(args$input.table, header=args$header)

    model <- lm(data)

    if (args$output == "summary") {
        print(summary(model))
    } else if (args$output == "fitted.values") {
        cat(model$fitted.values, sep="\n")
    } else {
        cat("invalid option", end="\n")
    }
}

main()
