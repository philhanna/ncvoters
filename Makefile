ZIP  := /tmp/voter_data.zip
TXT  := /tmp/ncvoter_Statewide.txt
DB   := $(shell python3 scripts/db_path.py)

.PHONY: all download unzip load indexes views clean

all: views

# ── download ─────────────────────────────────────────────────────────────────

$(ZIP):
	python3 scripts/download.py $(ZIP)

download: $(ZIP)

# ── unzip ────────────────────────────────────────────────────────────────────

$(TXT): $(ZIP)
	python3 scripts/unzip.py $(ZIP) $(TXT)

unzip: $(TXT)

# ── load ─────────────────────────────────────────────────────────────────────

$(DB): $(TXT)
	python3 scripts/load.py $(TXT) "$(DB)"

load: $(DB)

# ── indexes ──────────────────────────────────────────────────────────────────

.indexes.stamp: $(DB)
	python3 scripts/indexes.py "$(DB)"
	touch .indexes.stamp

indexes: .indexes.stamp

# ── views ────────────────────────────────────────────────────────────────────

.views.stamp: .indexes.stamp
	python3 scripts/views.py "$(DB)"
	touch .views.stamp

views: .views.stamp

# ── clean ────────────────────────────────────────────────────────────────────

clean:
	rm -f $(ZIP) $(TXT) "$(DB)" .indexes.stamp .views.stamp
