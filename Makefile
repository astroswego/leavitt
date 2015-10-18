# directories
INPUT = input
TMP = temp
OUTPUT = output
DIRECTORIES = $(INPUT) $(TMP) $(OUTPUT)

# image extension to use
EXT = eps

# band names
BANDS = I V J H K

# mean distance modulus
MEAN_MODULUS = 18.493

# links to data table files
MACRI_URL_3 = http://people.physics.tamu.edu/lmacri/LMCNISS/Macri14_Table_3.txt
MACRI_URL_5 = http://people.physics.tamu.edu/lmacri/LMCNISS/Macri14_Table_5.txt
OGLE_URL = http://cs.oswego.edu/~dwysocki/public_downloads/data/OGLE-LMC-CEP-F.dat

# data table files downloaded from the Internet
MACRI_TABLE_3 = $(INPUT)/$(notdir $(MACRI_URL_3))
MACRI_TABLE_5 = $(INPUT)/$(notdir $(MACRI_URL_5))
OGLE_TABLE    = $(INPUT)/$(notdir $(OGLE_URL))

# data table files produced by this script
RADEC_TABLE = $(TMP)/RA_DEC_Table.txt
MACRI_TABLE = $(TMP)/Macri14_Table_Combined.txt
DATA_TABLE_RAW = $(TMP)/Data_Table_Raw.txt
DATA_TABLE_COR = $(TMP)/Data_Table_Corrected.txt

# output
PL_COEFFS = $(OUTPUT)/Period_Luminosity_Coefficients.txt

# single quantity files
RA = $(TMP)/Right_Ascention.txt
DEC = $(TMP)/Declination.txt
LOGP = $(TMP)/logP.txt
MAGS = $(TMP)/Magnitudes.txt
FITTED_MAGS = $(TMP)/Fitted_Magnitudes.txt
RESIDUALS = $(TMP)/Residuals.txt
RESIDUALS_MEAN = $(TMP)/Residuals_Mean.txt
DISTANCE_MODULII = $(TMP)/Distance_Modulii.txt
DISTANCES_KPC = $(TMP)/Distances_Kiloparsecs.txt

# plot files
POSITION_MAG_SCATTER_PLOT_PREFIX = \
    $(OUTPUT)/OGLE-LMC-CEP-F-Position_Mag_Scatter-
POSITION_DENSITY_CONTOUR_PLOT_PREFIX = \
    $(OUTPUT)/OGLE-LMC-CEP-F-Position_Density-
LEAVITT_PLOT_PREFIX = \
    $(OUTPUT)/OGLE-LMC-CEP-F-Leavitt_Law-
DEPTH_PLOT_PREFIX = \
    $(OUTPUT)/OGLE-LMC-CEP-F-Depth_Effect-

#############
## Scripts ##
#############

# formats Macri data
MACRI_TABLE_FORMATTER = scripts/macri_table_format.sh
# formats RA/DEC data
RADEC_TABLE_FORMATTER = scripts/radec_table_format.sh
# creates scatter plots of star magnitudes at each RA/DEC position
PY_POSITION_MAG_SCATTER_PLOTS = scripts/position_mag_scatter_plots.py
# creates contour plots of star density as a function of RA/DEC position
PY_POSITION_DENSITY_CONTOUR_PLOTS = scripts/position_density_contour_plots.py
# plots Leavitt's law in multiple bands
PY_LEAVITT_PLOT = scripts/leavitt_plot.py
# plots the depth effect
PY_DEPTH_PLOT = scripts/depth_plot.py
# plots the 3d structure in cartesian coordinates at 360 different angles
## TODO ##
PY_CARTESIAN_3D_PLOT = scripts/cartesian_3d_plot.py
# fits Leavitt's law in multiple bands
PY_LEAVITT_FIT = scripts/leavitt_fit.py
# predicts magnitudes based on Leavitt's law
PY_LEAVITT_PREDICT = scripts/leavitt_predict.py
# converts equatorial coordinates to cartesian
## TODO ##
PY_EQUATORIAL_TO_CARTESIAN = scripts/equatorial2cartesian.py
# performs an arithmetic operation on two table files
PY_TABLE_ARITH = scripts/table_arith.py
# averages the rows in the input file
AWK_ROW_AVERAGER = scripts/row_averager.awk
# converts distance modulii to kiloparsecs
AWK_MODULII_TO_KPC = scripts/modulii2kpc.awk


.PHONY: all clean clobber help \
        results \
        plots \
            INITIAL_PLOTS LEAVITT_PLOTS DEPTH_PLOTS


all: results plots
results: $(PL_COEFFS)
plots: INITIAL_PLOTS LEAVITT_PLOTS DEPTH_PLOTS


#############
## Results ##
#############

# table containing period-luminosity coefficients
$(PL_COEFFS): $(PY_LEAVITT_FIT) $(LOGP) $(MAGS)
	python3 $(PY_LEAVITT_FIT) $(LOGP) $(MAGS) > $(PL_COEFFS)





###########
## Plots ##
###########

# OGLE LMC MAG contour plot
INITIAL_PLOTS: $(PY_POSITION_MAG_SCATTER_PLOTS) \
               $(PY_POSITION_DENSITY_CONTOUR_PLOTS) \
               $(DATA_TABLE_COR) \
               $(OUTPUT)
	# make temporary file to store input data for multiple scripts
	$(eval $@_tempfile := $(shell mktemp))
	awk '$$3=="FU" && $$13=="Y" { print $$14,$$15,$$4,$$5,$$6,$$7,$$8 }' \
	    $(DATA_TABLE_COR) \
	  > $($@_tempfile)
	# create scatter plots of RA vs DEC, with colors scaled by MAG
	python3 $(PY_POSITION_MAG_SCATTER_PLOTS) \
	        $(POSITION_MAG_SCATTER_PLOT_PREFIX) $(EXT) $(BANDS) \
	  < $($@_tempfile)
	# create contour plots of magnitude stdev at each position in the sky
	python3 $(PY_POSITION_DENSITY_CONTOUR_PLOTS) \
	        $(POSITION_DENSITY_CONTOUR_PLOT_PREFIX) $(EXT) $(BANDS) \
	  < $($@_tempfile)

LEAVITT_PLOTS: $(PY_LEAVITT_PLOT) \
               $(LOGP) $(MAGS) $(PL_COEFFS)
	python3 $(PY_LEAVITT_PLOT) $(LOGP) $(MAGS) $(PL_COEFFS) \
	        $(LEAVITT_PLOT_PREFIX) $(EXT) $(BANDS)

DEPTH_PLOTS: $(PY_DEPTH_PLOT) \
             $(RA) $(DEC) $(RESIDUALS)
	python3 $(PY_DEPTH_PLOT) $(RA) $(DEC) $(RESIDUALS) \
	        $(DEPTH_PLOT_PREFIX) $(EXT) $(BANDS)

##############################
## Intermediate table files ##
##############################

# combined Macri et al (2014) data tables
$(MACRI_TABLE): $(MACRI_TABLE_FORMATTER) \
                $(MACRI_TABLE_3) $(MACRI_TABLE_5) \
                $(TMP)
	bash $(MACRI_TABLE_FORMATTER) \
	     $(MACRI_TABLE_3) $(MACRI_TABLE_5) \
	  | sort \
	  > $(MACRI_TABLE)

# table containing only ID/RA/DEC
$(RADEC_TABLE): $(RADEC_TABLE_FORMATTER) $(OGLE_TABLE)
                # Persson (2004) table when available
	bash $(RADEC_TABLE_FORMATTER) $(OGLE_TABLE) \
	  | sort \
	  > $(RADEC_TABLE)

# full table for pre-reddening corrected data
$(DATA_TABLE_RAW): $(MACRI_TABLE) $(RADEC_TABLE)
	join -t '	' $(MACRI_TABLE) $(RADEC_TABLE) \
	  | grep -v '99\.999' \
	  > $(DATA_TABLE_RAW)

# full table for reddening corrected data
##
## this is currently a placeholder,
## and does not apply reddening corrections
##
$(DATA_TABLE_COR): $(DATA_TABLE_RAW)
	cp $(DATA_TABLE_RAW) $(DATA_TABLE_COR)


###########################
## Single Quantity Files ##
###########################

# table containing only RA
$(RA): $(DATA_TABLE_COR)
	cut -f 14 $(DATA_TABLE_COR) > $(RA)

# table containing only DEC
$(DEC): $(DATA_TABLE_COR)
	cut -f 15 $(DATA_TABLE_COR) > $(DEC)

# table containing only logP
$(LOGP): $(DATA_TABLE_COR)
	awk '{print log($$2)/log(10)}' $(DATA_TABLE_COR) > $(LOGP)

# table containing only magnitudes
$(MAGS): $(DATA_TABLE_COR)
	cut -f 4-8 $(DATA_TABLE_COR) > $(MAGS)

# table containing fitted magnitudes from PL-relations
$(FITTED_MAGS): $(PY_LEAVITT_PREDICT) $(LOGP) $(PL_COEFFS)
	python3 $(PY_LEAVITT_PREDICT) $(LOGP) $(PL_COEFFS) > $(FITTED_MAGS)

# compute the residuals of the fitted magnitudes
$(RESIDUALS): $(PY_TABLE_ARITH) $(MAGS) $(FITTED_MAGS)
	python3 $(PY_TABLE_ARITH) $(MAGS) - $(FITTED_MAGS) > $(RESIDUALS)

# average the fitted magnitudes for each band
#
## TODO: do a weighted average, using the relative errors
#
$(RESIDUALS_MEAN): $(AWK_ROW_AVERAGER) $(RESIDUALS)
	awk -f $(AWK_ROW_AVERAGER) $(RESIDUALS) > $(RESIDUALS_MEAN)

# compute the distance modulus of each star as the mean modulus of the LMC
# offset by the average magnitude residual across all bands
$(DISTANCE_MODULII): $(RESIDUALS_MEAN)
	awk '$$1 = ($$1 + $(MEAN_MODULUS))' $(RESIDUALS_MEAN) > $(DISTANCE_MODULII)

# convert distance modulii to kiloparsecs
$(DISTANCES_KPC): $(AWK_MODULII_TO_KPC) $(DISTANCE_MODULII)
	awk -f $(AWK_MODULII_TO_KPC) $(DISTANCE_MODULII) > $(DISTANCES_KPC)



###########################
## Download remote files ##
###########################

# photometry from Macri et al (2014)
$(MACRI_TABLE_3): $(INPUT)
	curl $(MACRI_URL_3) -o $@
$(MACRI_TABLE_5): $(INPUT)
	curl $(MACRI_URL_5) -o $@

# photometry from OGLE-III
$(OGLE_TABLE): $(INPUT)
	curl $(OGLE_URL) -o $@

$(DIRECTORIES):
	mkdir -p $@


clean:
	rm -rf $(TMP)

clobber: clean
	rm -rf $(INPUT) $(OUTPUT)

help:
	@echo "Makes things"
	@echo "(real description coming soon)"
