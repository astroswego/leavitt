#!/usr/bin/env Rscript

library(optparse)

get.options <- function() {
    f <- file("stdin")
    open(f)
    option.list <- list(
        make_option(
            c("-i", "--input"),
            action="store", type="character", default=f,#"stdin",
            help="Location of input table. Defaults to stdin."),
        make_option(
            c("-o", "--output"),
            action="store", type="character", default=NULL,
            help=paste(
                "Location to output plots.",
                "No plots generated if not provided.")),
        make_option(
            "--mode",
            action="store", type="character", default="summary",
            help="Output mode (summary or table). Defaults to summary."),
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
                "Default is 3.")),
        make_option(
            "--distance-modulus", dest="distance.modulus",
            action="store", type="double", default=0.0,
            help="Distance modulus to apply to magnitudes"))

    opts <- parse_args(OptionParser(prog="leavitt",
                                    option_list=option.list))

    opts$period.col <- opts$period.col -
        if((opts$row.names > 0) & (opts$row.names < opts$period.col))
            1 else 0
    opts$luminosity.col <- opts$luminosity.col -
        if((opts$row.names > 0) & (opts$row.names < opts$luminosity.col))
            1 else 0

    if(is.character(opts$output)) {
        opts$output.plots <- file.path(opts$output, "plots")
        opts$output.data <- file.path(opts$output, "data")

        dir.create(opts$output,       showWarnings=FALSE)
        dir.create(opts$output.plots, showWarnings=FALSE)
        dir.create(opts$output.data,  showWarnings=FALSE)
    }
    
    opts
}

model.name <- function(...) {
    paste(list(...), collapse="-")
}

get.model <- function(data, period.name, luminosity.name,
                      var.name=NULL, distance.modulus=0.0) {
    P <- data[[period.name]]
    L <- data[[luminosity.name]]-distance.modulus
    V <- if(is.character(var.name)) data[[var.name]] else NULL
    # make the model
    if(is.numeric(V)) lm(L ~ P + V) else lm(L ~ P)
}

display.summary <- function(model, period.name, luminosity.name,
                            var.name=NULL) {
    cat(
        paste(
            "#",
            model.name(period.name, luminosity.name, var.name),
            "relation"))
    cat("\n\n")
    cat("```")
    print(summary(model))
    cat("```\n")
}

display.header <- function(period.name) {
    cat("Variable",
        paste(c("Intercept", period.name, "Variable"),
              c("d_Intercept", paste("d", period.name, sep="_"), "d_Variable"),
              c("t_Intercept", paste("t", period.name, sep="_"), "t_Variable"),
              c("Pr_Intercept", paste("Pr", period.name, sep="_"),
                "Pr_Variable"),
              sep="\t"),
        sep="\t")
    cat("\n")
}

display.table <- function(model, var.name=NULL, ...) {
    if (is.null(var.name)) var.name <- "NA"

    summary   <- summary(model)
    coefs     <- summary$coefficients
    ncoefs    <- nrow(coefs)

    estimates <- coefs[, 1]
    stderrs   <- coefs[, 2]
    tvalues   <- coefs[, 3]
    probs     <- coefs[, 4]

    if (ncoefs == 2) {
        estimates <- c(estimates, "NA")
        stderrs   <- c(stderrs,   "NA")
        tvalues   <- c(tvalues,   "NA")
        probs     <- c(probs,     "NA")
    }

    cat(var.name, end="\t")
    cat(paste(estimates, stderrs, tvalues, probs, collapse="\t"))
    cat("\n")
}

display.model <- function(model, mode="summary", ...) {
    if (mode == "summary") {
        display.summary(model, ...)
    } else if (mode == "table") {
        display.table(model, ...)
    } else {
        print("Undefined mode.")
    }
}

plot.model <- function(model, output,
                       period.name, luminosity.name, var.name=NULL,
                       distance.modulus=0.0,
                       data.color="black", fit.color="red") {
    dir <- file.path(output,
                     paste(
                         paste(
                             c(period.name,
                               luminosity.name,
                               var.name),
                             collapse="_"),
                         ".eps",
                         sep=""))
    setEPS()
    postscript(dir)
    plot(model$model[[2]], model$model[[1]]-distance.modulus,
         xlab=period.name, ylab=luminosity.name, col=data.color)
    points(model$model[[2]], model$fitted.values,
           col=fit.color)
    dev.off()
}

output.fitted.data <- function(model, data, output) {
    data$fit <- model$fitted.values

    unlink(output)
    cat(file=output, "ID\t")
    suppressWarnings(
        write.table(data, output, sep="\t", quote=FALSE, append=TRUE))
}



main <- function() {
    opts <- get.options()

    data_ <- read.table(
        opts$input, header=opts$header,
        row.names=opts$row.names)

    low.periods <- if(is.numeric(opts$period.max)) {
        data_[, opts$period.col] < opts$period.max
    } else TRUE
    high.periods <- if(is.numeric(opts$period.min)) {
        data_[, opts$period.col] > opts$period.min
    } else TRUE

    data <- data_[low.periods & high.periods]

    col.names <- colnames(data)
    period.name <- col.names[opts$period.col]
    luminosity.name <- col.names[opts$luminosity.col]

    if (opts$mode == "table") {
        display.header(period.name)
    }
    # process and display L ~ P relation
    model <- get.model(data, period.name, luminosity.name,
                       distance.modulus=opts$distance.modulus)
    display.model(model, period.name, luminosity.name, var.name=NULL,
                  mode=opts$mode)
    if(is.character(opts$output.plots)) {
        plot.model(model, opts$output.plots, period.name, luminosity.name,
                   distance.modulus=opts$distance.modulus)
    }
    if(is.character(opts$output.data)) {
        file <- file.path(opts$output.data,
                          paste(
                              paste(
                                  c(period.name,
                                    luminosity.name),
                                  collapse="_"),
                              ".dat",
                              sep=""))
        output.fitted.data(model, data, file)
    }
    # process and display L ~ P + V relations
    for(var.name in colnames(data)) {
        if(var.name != period.name & var.name != luminosity.name) {
            model <- get.model(data, period.name, luminosity.name, var.name,
                               distance.modulus=opts$distance.modulus)
            display.model(model,
                          period.name, luminosity.name, var.name=var.name,
                          mode=opts$mode)
            if(is.character(opts$output.plots)) {
                plot.model(model, opts$output.plots,
                           period.name, luminosity.name, var.name,
                           distance.modulus=opts$distance.modulus)
            }
            if(is.character(opts$output.data)) {
                file <- file.path(opts$output.data,
                                  paste(
                                      paste(
                                          c(period.name,
                                            luminosity.name,
                                            var.name),
                                          collapse="_"),
                                      ".dat",
                                      sep=""))
                output.fitted.data(model, data, file)
            }
        }
    }
}

main()
