#!/usr/bin/env Rscript

library(optparse)

get_options <- function() {
    option_list <- list(
        make_option(
            c("-i", "--input"),
            action="store", type="character", default="stdin",
            help="Location of input table. Defaults to stdin."),
        make_option(
            c("-o", "--output"),
            action="store", type="character", default=NULL,
            help=paste(
                "Location to output plots.",
                "No plots generated if not provided.")),
        make_option(
            "--header",
            action="store_true", default=TRUE, dest="header",
            help="Input file contains header. True by default."),
        make_option(
            "--no-header", dest="header",
            action="store_false",
            help="Input file does not contain header, use column numbers."),
        make_option(
            "--period-min", dest="period.min",
            action="store", type="double", default=NULL,
            help="Minimum allowed period. Leave blank for no minimum."),
        make_option(
            "--period-max", dest="period.max",
            action="store", type="double", default=NULL,
            help="Maximum allowed period. Leave blank for no maximum."),
        make_option(
            "--name-col", dest="row.names",
            action="store", type="integer", default=1,
            help=paste(
                "Column in input file to read names from.",
                "Provide a number less than 1 to ignore names.",
                "Default is 1.")),
        make_option(
            "--period-col", dest="period.col",
            action="store", type="integer", default=2,
            help=paste(
                "Column in input file to read periods from.",
                "Default is 2.")),
        make_option(
            "--luminosity-col", dest="luminosity.col",
            action="store", type="integer", default=3,
            help=paste(
                "Column in input file to read luminosities from.",
                "Default is 3.")))

    opts <- parse_args(OptionParser(prog = "leavitt",
                                    option_list=option_list))

    opts$period.col <- opts$period.col -
        if((opts$row.names > 0) & (opts$row.names < opts$period.col))
            1 else 0
    opts$luminosity.col <- opts$luminosity.col -
        if((opts$row.names > 0) & (opts$row.names < opts$luminosity.col))
            1 else 0
    opts
}

process_relation <- function(period_name, luminosity_name, data, var_name=NULL) {
    periods <- data[, period_name]
    luminosities <- data[, luminosity_name]
    var <- data[, var_name]

    cat(
        paste(
            "Processing",
            paste(
                c(
                    period_name,
                    luminosity_name,
                    var_name),
                collapse="-"),
            "relation"))
    cat("\n")
}

display_relation <- function(relation) {
    NULL
}

plot_relation <- function(relation) {
    NULL
}



main <- function() {
    opts <- get_options()

    data <- read.table(
        opts$input, header=opts$header,
        row.names=opts$row.names)

    data <- data[(data[, opts$period.col] > opts$period.min) &
                 (data[, opts$period.col] < opts$period.max), ]

    period_name <- colnames(data)[opts$period.col]
    luminosity_name <- colnames(data)[opts$luminosity.col]

    process_relation(period_name, luminosity_name, data)
    for(var_name in colnames(data)) {
        if(var_name != period_name & var_name != luminosity_name) {
            r <- process_relation(period_name, luminosity_name, data, var_name)
            display_relation(r)
            if(is.character(opts$output)) {
                plot_relation(r)
            }
        }
    }
}

main()
