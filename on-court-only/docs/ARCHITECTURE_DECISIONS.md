# Architecture decision record

**ADR-1 Zero-dependency Python + SQLite as the system of record.** Python 3.11+ standard library only (http.server, sqlite3, hashlib). *Why:* a founder can run it anywhere with no install step; nothing to patch; the evidence and claim rules are plain, testable Python. *Trade-off:* not a high-traffic web server. Production traffic goes through Shopify for checkout, and this app can sit behind a reverse proxy or move to a WSGI framework later without changing the domain modules.

**ADR-2 Rules engine, not free-text judgement.** Classification is derived from coded evidence. Copy is linted against the derived class. *Why:* the brand's whole promise is that claims match evidence, so it has to be enforced mechanically.

**ADR-3 Separate checkout (Shopify) from provenance (ours).** See `commerce/ECOMMERCE_ARCHITECTURE.md`.

**ADR-4 No third-party images.** Demo products use original code-drawn illustrations; reference panels stay empty until rights are cleared. *Why:* copyright and false-association risk; it is also honest.

**ADR-5 Contact tiers.** VERIFIED_CONTACT only after a person confirms the contact on the live page; RESEARCHED_ROUTE for official pages; UNVERIFIED_LEAD for anything else, including emails seen only in search extracts. Outreach to unverified leads cannot be approved.

**ADR-6 Recommendations stop at PROPOSE_TO_FOUNDER.** No status means "buy".

**ADR-7 Era cutoff.** Seasons starting 2009 or earlier are ON COURT OG / Vintage Team Issue; 2010 onward is Current Court. Configurable (`OG_LAST_SEASON_START`).

**ADR-8 Agents as code plus Claude Code subagents.** Deterministic workflows (`agents/run.py`) do the repeatable work and log metrics; Claude Code subagents (`.claude/agents/`) do the research and judgement, writing JSON that the code ingests.

**ADR-9 Vanilla JS front end.** No build step; CSP `script-src 'self'`; all API text escaped. Adequate for a catalogue of tens to hundreds of items.

**ADR-10 Independent of the Codex pack's technology.** The pack's prototype is a single static HTML page; we kept only its business rules.
