# OTIF Blind Spot — Failure Log

What was attempted that didn't work, why it didn't work, and what was
tried next.

Lower bar than DECISIONS.md — capture failures even when they didn't
produce a durable rule. The whole point: future-you (or future-Claude)
shouldn't re-attempt dead ends because the lesson got lost.

---

## Format

### YYYY-MM-DD — [One-line failure description]

**Attempted:** [What was tried]

**Why it didn't work:** [Concrete reason, not "it broke."]

**What we tried instead:** [The next attempt]

**Status:** Resolved / open / abandoned

**Tags:** [keywords for future text-search]

---

## Entries

### 2026-05-31 — Synthesis shipped against po_qty instead of acknowledged_qty, giving fill_vs_855 > 100%

**Attempted:** Set `synthetic_shipped_qty = po_qty` for non-short-ship orders, then computed `fill_vs_855 = total_shipped / total_ack`. For trimmed orders where acknowledged < po_qty, this produced ratios above 1.0.

**Why it didn't work:** Cinderhaven ships against the acknowledged (855) quantity, not the original PO (850). Shipping the full PO when Walmart trimmed the order inflates fill_vs_855 above 100%, which is nonsensical.

**What we tried instead:** Changed base for non-short-ship orders to `synthetic_shipped_qty = acknowledged_qty`. Short-ship orders use `acknowledged_qty × fill_ratio`. This gives fill_vs_855 ≤ 100% and fill_vs_855 > fill_vs_850 as expected.

**Status:** Resolved

**Tags:** synthesis, fill-rate, acknowledged-qty, 855, otif

---

### 2026-05-31 — Cinderhaven seed has 100% fill rate; internal 95% figure is fully synthetic

**Attempted:** Assumed internal fill rate could be derived from `fct_retailer_shipments.units_shipped / fct_retailer_orders.total_units`.

**Why it didn't work:** `seed_retailer.py` seeds `units_shipped = total_units` for every order — 100% fill across the board. There are no natural short-ships in the platform data.

**What we tried instead:** Hardcoded `internal_fill_rate = TARGET_INTERNAL_FILL (0.95)` in `build_summary()`. The 95% is a portfolio claim representing what Cinderhaven would report; it is not derived from the raw data. Added comment in `02_export_json.py`.

**Status:** Resolved — by design

**Tags:** cinderhaven, seed, fill-rate, synthetic, 100-percent

---

### 2026-05-31 — Wrangler OAuth token revoked; account auto-detection returning 403

**Attempted:** `npx wrangler deploy` after prior `wrangler login` session.

**Why it didn't work:** The stored OAuth token (`cfoat_...`) had been revoked or expired between sessions. `GET /v4/accounts` returned 403 Forbidden. Adding account_id to wrangler.jsonc was not sufficient on its own — the token needed to be valid.

**What we tried instead:** User ran `wrangler login` in VS Code terminal (browser auth), obtaining a fresh token. Deploy succeeded immediately after.

**Status:** Resolved

**Tags:** wrangler, cloudflare, oauth, deploy, authentication

---

### 2026-05-31 — run_pipeline.py crashed on Windows with UnicodeEncodeError on box-drawing character

**Attempted:** Used `'─' * 60` (U+2500 BOX DRAWINGS LIGHT HORIZONTAL) in print statements in `run_pipeline.py`.

**Why it didn't work:** Windows console uses cp1252 encoding by default; U+2500 is not in cp1252 and raises `UnicodeEncodeError`.

**What we tried instead:** Replaced `'─'` with ASCII `'-'`.

**Status:** Resolved

**Tags:** windows, encoding, unicode, cp1252, print, pipeline
