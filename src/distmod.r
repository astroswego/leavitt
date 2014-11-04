#!/usr/bin/env Rscript

main <- function() {
    modulii <- scan(file("stdin"), quiet=TRUE)
    distances <- distance.modulus(modulii)
    write(distances, file="", sep="\n")
}

distance.modulus <- function(modulus) {
    10^(modulus/5 + 1)
}

main()
