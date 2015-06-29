# directories
INPUT = input
TMP = temp
OUTPUT = output
DIRECTORIES = $(INPUT) $(TMP) $(OUTPUT)

# image extension to use
EXT = eps

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


# band names
BANDS = I V J H K

# plot files
POSITION_MAG_SCATTER_PLOT_PREFIX = \
    $(OUTPUT)/OGLE-LMC-CEP-F-Position_Mag_Scatter-
POSITION_MAG_COUNT_CONTOUR_PLOT_PREFIX = \
    $(OUTPUT)/OGLE-LMC-CEP-F-Position_Mag_Count-

# scripts
MACRI_TABLE_FORMATTER = macri_table_format.sh
RADEC_TABLE_FORMATTER = radec_table_format.sh
PY_POSITION_MAG_SCATTER_PLOTS = position_mag_scatter_plots.py
PY_POSITION_MAG_COUNT_CONTOUR_PLOTS = position_mag_count_contour_plots.py

.PHONY: clean clobber help

###########
## Plots ##
###########

# OGLE LMC MAG contour plot
$(POSITION_MAG_SCATTER_PLOTS): POSITION_MAG_SCATTER_PLOTS_INTERMEDIATE

.INTERMEDIATE: POSITION_MAG_SCATTER_PLOTS_INTERMEDIATE

INITIAL_PLOTS: $(PY_POSITION_MAG_SCATTER_PLOTS) \
               $(PY_POSITION_MAG_COUNT_CONTOUR_PLOTS) \
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
	python3 $(PY_POSITION_MAG_COUNT_CONTOUR_PLOTS) \
	        $(POSITION_MAG_COUNT_CONTOUR_PLOT_PREFIX) $(EXT) $(BANDS) \
	  < $($@_tempfile)

########################
## Intermediate files ##
########################

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
	join -t '	' $(MACRI_TABLE) $(RADEC_TABLE) > $(DATA_TABLE_RAW)

# full table for reddening corrected data
##
## this is currently a placeholder,
## and does not apply reddening corrections
##
$(DATA_TABLE_COR): $(DATA_TABLE_RAW)
	cat $(DATA_TABLE_RAW) > $(DATA_TABLE_COR)


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

clobber:
	rm -rf $(INPUT) $(TMP) $(OUTPUT)

help:
	@echo "Makes things"
	@echo "(real description coming soon)"
