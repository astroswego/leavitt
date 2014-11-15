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
        "-o", "--output",
        choices=c("summary", "coefficients", "fitted.values"),
        default="fitted.values",
        help="output format")
    parser$add_argument(
        "-m", "--method",
        choices=c("lm", "svd"),
        default="lm",
        help="fitting method")
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

    args <- parser$parse_args()

    if (args$input.table == "-") args$input.table <- file("stdin")

    args$row.names <- if (args$row.names) 1 else NULL

    args
}

print.coefficients <- function(model) {
    output <- capture.output(write.table(model$coefficients, quote=FALSE))
    # remove backticks from output
    cat(gsub("`", "", output), sep="\n")
}

fit.lm <- function(data, output) {
    model <- lm(data[[1]] ~ . + 0, data=data[-1])

    if (output == "summary") {
        print(summary(model))
    } else if (output == "coefficients") {
        print.coefficients(model)
    } else if (output == "fitted.values") {
        cat(model$fitted.values, sep="\n")
    } else {
        cat("invalid option", end="\n")
    }
}

fit.svd <- function(data, output) {
    A <- data[-1]
    b <- data[[1]]

    svd.result <- svd(A)
    D <- diag(svd.result$d)
    D[D >  1e-10] <- 1/D[D > 1e-10]
    D[D <= 1e-10] <- 0
    U <- svd.result$u
    V <- svd.result$v
    
    x <- V %*% D %*% t(U) %*% b

    write.table(x)
}


main <- function() {
    args <- get.args()

    data <- read.table(args$input.table,
                       header=args$header,
                       row.names=args$row.names,
                       check.names=FALSE)

    if (args$method == "lm") {
        fit.lm(data, args$output)
    } else if (args$method == "svd") {
        fit.svd(data, args$output)
    } else {
        cat("invalid method", end="\n")
    }
}

main()
