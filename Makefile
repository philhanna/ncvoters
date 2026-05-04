ZIP  := /tmp/voter_data.zip
TXT  := /tmp/ncvoter_Statewide.txt
INDEX_SQL := $(wildcard $(HOME)/.config/ncvoters/indexes/*.sql)
VIEW_SQL  := $(wildcard $(HOME)/.config/ncvoters/views/*.sql)

.PHONY: help all download unzip load metadata indexes views clean

# ── help ─────────────────────────────────────────────────────────────────────

help:
	@printf '%s\n' \
		'get-voter-data' \
		'' \
		'Builds an SQLite database from North Carolina voter registration data.' \
		'Default target: help' \
		'' \
		'Usage:' \
		'  get-voter-data [target]' \
		'' \
		'Available targets:' \
		'  help      Show this help text.' \
		'  all       Run the full pipeline: download, unzip, load, metadata, indexes, views.' \
		'  download  Download the statewide zip file to /tmp.' \
		'  unzip     Extract the voter data text file from the zip.' \
		'  load      Load selected columns into the SQLite database.' \
		'  metadata  Refresh built-in metadata lookup tables after load.' \
		'  indexes   Apply user-defined indexes to the existing database.' \
		'  views     Apply user-defined views to the existing database.' \
		'  clean     Remove downloaded files and local build stamps.' \
		'' \
		'Examples:' \
		'  get-voter-data help' \
		'  get-voter-data all' \
		'  get-voter-data clean' \
		'  get-voter-data indexes' \
		'  get-voter-data views'

all: .views.stamp

# ── download ─────────────────────────────────────────────────────────────────

$(ZIP):
	python scripts/download.py $(ZIP)

download: $(ZIP)

# ── unzip ────────────────────────────────────────────────────────────────────

$(TXT): $(ZIP)
	python scripts/unzip.py $(ZIP) $(TXT)

unzip: $(TXT)

# ── load ─────────────────────────────────────────────────────────────────────

.load.stamp: $(TXT)
	python scripts/load.py $(TXT)
	touch .load.stamp

load: .load.stamp

# ── metadata ─────────────────────────────────────────────────────────────────

.metadata.stamp: .load.stamp
	python scripts/metadata.py
	touch .metadata.stamp

metadata: .metadata.stamp

# ── indexes ──────────────────────────────────────────────────────────────────

.indexes.stamp: .load.stamp .metadata.stamp $(INDEX_SQL)
	python scripts/indexes.py
	touch .indexes.stamp

indexes:
	python scripts/indexes.py
	touch .indexes.stamp

# ── views ────────────────────────────────────────────────────────────────────

.views.stamp: .indexes.stamp $(VIEW_SQL)
	python scripts/views.py
	touch .views.stamp

views:
	python scripts/views.py
	touch .views.stamp

# ── clean ────────────────────────────────────────────────────────────────────

clean:
	rm -f $(ZIP) $(TXT) .load.stamp .metadata.stamp .indexes.stamp .views.stamp
