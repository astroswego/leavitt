leavitt
=======

A set of scripts for computing Leavitt's law and variants for variable stars.

In its current iteration, the scripts are orchestrated by a `Makefile`, which downloads the input data, performs all the calculations, and produces plots. If you would like all results, run `make all`. If you would only like the calculations, run `make results`. If you would like plots, run `make plots`.

After running `make all`, the `output/` folder will contain a number of plots, and a text file. The text file, named `Period_Luminosity_Coefficients.txt`, has two rows and 5 columns. The columns correspond to the _V_- _I_- _J_- _H_- and _K_-bands, respectively. The rows contain the slope and zero-point of the PL relation, respectively. The names and contents of the plots should be self-explanatory.

The `input/` folder will contain all of the files downloaded by the `Makefile`, and the `temp/` folder will contain a number of intermediate files.
