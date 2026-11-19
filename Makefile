PYTHON ?= python

.PHONY: all data list paper

# Reproduce all figures and tables from the committed data
all:
	$(PYTHON) run.py all

# Re-download / re-derive raw inputs (network; ERA5 needs a CDS account)
data:
	$(PYTHON) run.py data

list:
	$(PYTHON) run.py list

# Build the manuscript PDF (needs pandoc and a Chrome/Chromium binary)
paper:
	bash paper/build_pdf.sh
