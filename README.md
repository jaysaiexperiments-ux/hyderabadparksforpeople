# Hyderabad Parks For People

An open-source civic accountability site for Hyderabad's parks. A single static page that reads JSON files and renders a legal summary, a chain of accountability, a curated timeline, a violations table, take-action helpers, and an auto-refreshed news feed. No frameworks. No build step. No trackers.

**Live:** https://jaysaiexperiments-ux.github.io/hyderabadparksforpeople

**Currently tracking:** [KBR National Park](data/parks/kbr.json) — 390-acre National Park in Jubilee Hills, notified under WPA 1972 (GO Ms. No. 187 EFS&T, 5 Dec 1998). Subject of the H-CITI infrastructure project: 7 flyovers + 7 underpasses encircling the park, ₹2,654 crore budget. As of the most recent verified update, **1,532 trees have been felled**. A legal challenge is pending in the Telangana High Court; stay was refused 30 March 2026 and the case was adjourned to 5 May 2026.

---

## How the auto fact-check works

A scheduled GitHub Actions workflow (`.github/workflows/fact-check.yml`) runs at **07:00 IST** and **19:00 IST** every day. It executes `scripts/fetch-updates.py`, which:

1. Reads `data/parks-index.json` to find each tracked park.
2. Runs a set of Google News RSS queries for that park.
3. Deduplicates by URL, sorts newest-first, keeps the top 10.
4. Flags any item whose headline matches a "signal pattern" (tree counts, court orders, NGT directives, new GO numbers, officer appointments) and copies it to `data/review-queue/<id>.json`.
5. Writes the result to `data/updates/<id>.json` and commits if there's a diff.

The page fetches `data/updates/<id>.json` at load and shows the items under **Latest updates**, labeling flagged items "Pending verification". **The automation never touches the curated park JSON** — it only writes to `data/updates/` and `data/review-queue/`. Maintainers manually promote verified items into the timeline.

---

## How to contribute (non-developer)

Two ways, both via email — no GitHub account needed:

- **Report an issue / suggest a fix** → use the "Report an issue" button on the site. It opens a pre-filled email with prompts for the page section, what you noticed, and a suggested fix. Send to `notforprofuse123@gmail.com`.
- **Submit a verified update** → use the "Submit verified update" button. It opens a pre-filled email asking for the date, what happened, and a source URL (news outlet, court order, or official document). A secondary source is appreciated but not required.

We respond within 48 hours and credit contributors by name on request, or leave you anonymous.

---

## How to contribute (developer)

1. Fork the repo.
2. Edit `data/parks/<id>.json` (or `data/parks-index.json`) — the schema is the contract; everything else renders from it.
3. Run the page locally with any static server, e.g.:
   ```bash
   python3 -m http.server 8000
   # then open http://localhost:8000
   ```
4. Open a PR. Maintainers verify changes against the cited source before merging.

To dry-run the news fetcher locally:

```bash
pip install feedparser==6.0.11
python scripts/fetch-updates.py
# writes data/updates/<id>.json
```

---

## How to add a new park

The data schema is the contract — `index.html` and the workflow do not need code changes to support a second park.

1. **Create `data/parks/<new-id>.json`** with the same schema as `kbr.json`: `id`, `name`, `shortName`, `area`, `location`, contacts[], timeline[], violations[], evidenceLog[], etc.
2. **Append an entry to `data/parks-index.json`** — give it `id`, `name`, `status`, `dataFile`, `updatesFile`.
3. **Add a queries entry in `scripts/fetch-updates.py`** — append to the `PARK_QUERIES` dict so the auto-fetcher knows what to search for.
4. (Optional) Update the header sub-line in `index.html` to mention multiple parks tracked.

That's it. The next scheduled run will populate `data/updates/<new-id>.json`.

---

## File map

```
.
├── index.html                          # Single-page UI (HTML + CSS + vanilla JS)
├── data/
│   ├── parks-index.json                # List of tracked parks
│   ├── parks/
│   │   └── kbr.json                    # Curated park data (legal, contacts, timeline, violations)
│   ├── updates/
│   │   └── kbr.json                    # Auto-fetched news (twice daily)
│   └── review-queue/
│       └── kbr.json                    # Flagged items awaiting maintainer review
├── scripts/
│   └── fetch-updates.py                # News fetcher
├── .github/workflows/
│   └── fact-check.yml                  # Scheduled refresh: 07:00 + 19:00 IST
└── README.md
```

---

## Trust guarantees

- Auto-fetched updates are always labeled "Pending verification" on the page.
- Only maintainer-curated park JSON drives the main legal claims, timeline, and contacts.
- The twice-daily automation modifies **only** `data/updates/<id>.json` and `data/review-queue/<id>.json`.
- Human review is required before any flagged item is promoted into the main record.
- All contact details are from public sources only — never invented.
- No external trackers, analytics, or cookies. The page works offline once loaded.

---

## License

- **Code** (`index.html`, `scripts/`, `.github/`): MIT
- **Data** (`data/`): CC-BY-SA 4.0

---

## Disclaimer

This project is not affiliated with any political party. It is a citizen-maintained record assembled from public documents and reporting. It is **not a substitute for legal advice** — if you need to act on this information in a legal capacity, please consult a qualified advocate.

Contact: `notforprofuse123@gmail.com`
