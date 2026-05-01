ZIP  := /tmp/voter_data.zip
TXT  := /tmp/ncvoter_Statewide.txt
DB   := $(shell python scripts/db_path.py)
INDEX_SQL := $(wildcard $(HOME)/.config/ncvoters/indexes/*.sql)
VIEW_SQL  := $(wildcard $(HOME)/.config/ncvoters/views/*.sql)

.PHONY: all download unzip load indexes views clean

all: views

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
	python scripts/load.py $(TXT) "$(DB)"
	touch .load.stamp

load: .load.stamp

# ── indexes ──────────────────────────────────────────────────────────────────

.indexes.stamp: .load.stamp $(INDEX_SQL) | $(DB)
	python scripts/indexes.py "$(DB)"
	touch .indexes.stamp

indexes: .indexes.stamp

# ── views ────────────────────────────────────────────────────────────────────

.views.stamp: .indexes.stamp $(VIEW_SQL) | $(DB)
	python scripts/views.py "$(DB)"
	touch .views.stamp

views: .views.stamp

# ── clean ────────────────────────────────────────────────────────────────────

clean:
	rm -f $(ZIP) $(TXT) .load.stamp .indexes.stamp .views.stamp
