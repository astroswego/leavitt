#!/usr/bin/env Rscript

library(optparse)

get.options <- function() {
    option.list <- list(
        make_option(
            c("-i", "--input"),
            action="store", type="character", #default="stdin",
            help="Location of input table."),
        make_option(
            c("-d", "--digits"),
            action="store", type="integer", default=6,
            help="Number of digits to output."),
        make_option(
            c("-u", "--units"),
            action="store", type="character", default="modulus",
            help=paste(
                "Units to output distance in (kpc or modulus).",
                "Defaults to modulus.")),
        make_option(
            "--header",
            action="store_true", default=TRUE, dest="header",
            help="Input file contains header. True by default."),
        make_option(
            "--no-header", dest="header",
            action="store_false",
            help="Input file does not contain header, use column numbers."),
        make_option(
            "--name-col", dest="row.names",
            action="store", type="integer", default=1,
            help=paste(
                "Column in input file to read names from.",
                "Provide a number less than 1 to ignore names.",
                "Default is 1.")),
        make_option(
            "--apparent-mag-col", dest="apparent.mag.col",
            action="store", type="integer", default=2,
            help=paste(
                "Column in input file to read apparent magnitudes from.",
                "Default is 2.")),
        make_option(
            "--absolute-mag-col", dest="absolute.mag.col",
            action="store", type="integer", default=3,
            help=paste(
                "Column in input file to read absolute magnitudes from.",
                "Default is 3.")))
    opts <- parse_args(OptionParser(prog="modulus",
                                    option_list=option.list))
    opts$apparent.mag.col <- opts$apparent.mag.col -
        if((opts$row.names > 0) & (opts$row.names < opts$apparent.mag.col))
            1 else 0
    opts$absolute.mag.col <- opts$absolute.mag.col -
        if((opts$row.names > 0) & (opts$row.names < opts$absolute.mag.col))
            1 else 0

    opts
}

modulus2pc <- function(modulus) {
    10^(modulus/5 + 1)
}

main <- function() {
    opts <- get.options()

    data <- read.table(
        opts$input, header=opts$header,
        row.names=opts$row.names)

    col.names <- colnames(data)
    app.mag.name <- col.names[opts$apparent.mag.col]
    abs.mag.name <- col.names[opts$absolute.mag.col]

    app.mag <- data[[app.mag.name]]
    abs.mag <- data[[abs.mag.name]]

    modulus <- app.mag - abs.mag

    output <- data.frame(matrix(ncol=3, nrow=length(app.mag)))
    names(output) <- c(app.mag.name, abs.mag.name, opts$units)

    output[[app.mag.name]] <- app.mag
    output[[abs.mag.name]] <- abs.mag

    switch(opts$units,
        modulus={output$modulus <- modulus},
        pc={output$pc <- modulus2pc(modulus)},
        kpc={output$kpc <- modulus2pc(modulus)/1000})

    row.names(output) <- row.names(data)

    cat("ID\t")
    write.table(format(output, digits=opts$digits),
                quote=FALSE, sep="\t")
}

main()
