-- ON COURT ONLY | single relational source of truth (SQLite)
-- Every agent, the storefront and the admin read and write this database.
-- Conventions: ids are stable text keys; *_at are ISO-8601 UTC strings;
-- money is stored in integer cents with an explicit currency column.

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------- reference
CREATE TABLE IF NOT EXISTS leagues (
  id TEXT PRIMARY KEY,               -- NBA | NCAA
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS organisations (
  id TEXT PRIMARY KEY,               -- e.g. NBA-LAL, NCAA-SMC, SUP-MEIGRAY
  kind TEXT NOT NULL CHECK (kind IN ('NBA_TEAM','NCAA_PROGRAMME','SUPPLIER','AUTHENTICATOR','AUCTION_HOUSE','MARKETPLACE','UNIVERSITY_SURPLUS','OTHER')),
  name TEXT NOT NULL,
  league_id TEXT REFERENCES leagues(id),
  conference TEXT,
  division TEXT,
  city TEXT,
  website TEXT,
  nickname TEXT,
  iconic_era TEXT,
  recent_success TEXT,
  notes TEXT,
  verification TEXT NOT NULL DEFAULT 'UNVERIFIED' CHECK (verification IN ('VERIFIED','PARTIAL','UNVERIFIED')),
  researched_at TEXT,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

CREATE TABLE IF NOT EXISTS sources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entity_type TEXT NOT NULL,          -- organisation | player | channel | contact | product | opportunity | demand
  entity_id TEXT NOT NULL,
  url TEXT NOT NULL,
  supports TEXT,                      -- what fact this URL supports
  checked_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_sources_entity ON sources(entity_type, entity_id);

CREATE TABLE IF NOT EXISTS players (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  nationality TEXT,
  is_australian INTEGER NOT NULL DEFAULT 0,
  status TEXT CHECK (status IN ('CURRENT_NBA','FORMER_NBA','CURRENT_NCAA','FORMER_NCAA','OTHER')),
  position TEXT,
  college TEXT,
  achievements TEXT,
  verification TEXT NOT NULL DEFAULT 'UNVERIFIED' CHECK (verification IN ('VERIFIED','PARTIAL','UNVERIFIED')),
  notes TEXT
);

-- player <-> organisation stints (team or college), the Australian connection ledger
CREATE TABLE IF NOT EXISTS player_stints (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  player_id TEXT NOT NULL REFERENCES players(id),
  organisation_id TEXT REFERENCES organisations(id),
  organisation_name TEXT NOT NULL,     -- kept even when organisation not yet registered
  seasons TEXT,                        -- e.g. 1994-98
  is_current INTEGER NOT NULL DEFAULT 0,
  champion INTEGER NOT NULL DEFAULT 0,
  verification TEXT NOT NULL DEFAULT 'UNVERIFIED'
);

-- -------------------------------------------------------------- demand model
CREATE TABLE IF NOT EXISTS demand_factors (
  organisation_id TEXT NOT NULL REFERENCES organisations(id),
  factor TEXT NOT NULL,                -- see sourcing/demand.py FACTORS
  score REAL NOT NULL CHECK (score BETWEEN 0 AND 5),
  basis TEXT NOT NULL CHECK (basis IN ('MEASURED','ESTIMATE')),
  evidence TEXT,
  source_url TEXT,
  assessed_at TEXT NOT NULL,
  PRIMARY KEY (organisation_id, factor)
);

-- ---------------------------------------------------------- sourcing / CRM
CREATE TABLE IF NOT EXISTS channels (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  channel_type TEXT NOT NULL,
  sells TEXT,
  classification_typical TEXT,
  ships_to_au TEXT,
  partner_programme TEXT,
  published_contact TEXT,
  contact_url TEXT,
  fit_score INTEGER CHECK (fit_score BETWEEN 1 AND 5),
  fit_reason TEXT,
  verification TEXT NOT NULL DEFAULT 'UNVERIFIED' CHECK (verification IN ('VERIFIED','PARTIAL','UNVERIFIED')),
  checked_at TEXT
);

CREATE TABLE IF NOT EXISTS contacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  organisation_id TEXT NOT NULL REFERENCES organisations(id),
  department TEXT,
  person TEXT,
  role TEXT,
  method TEXT NOT NULL CHECK (method IN ('EMAIL','PHONE','WEB_FORM','POSTAL','CONTACT_PAGE','NONE')),
  value TEXT,                           -- the published email/phone/url, never guessed
  -- VERIFIED_CONTACT: named person or departmental address published on an official page
  -- RESEARCHED_ROUTE: official general route (contact page/form) that reaches the organisation
  -- UNVERIFIED_LEAD: a lead that needs confirmation before any use
  tier TEXT NOT NULL CHECK (tier IN ('VERIFIED_CONTACT','RESEARCHED_ROUTE','UNVERIFIED_LEAD')),
  evidence_url TEXT,
  verified_at TEXT,
  opt_out INTEGER NOT NULL DEFAULT 0,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS relationships (
  organisation_id TEXT PRIMARY KEY REFERENCES organisations(id),
  australian_connection TEXT,
  commercial_opportunity TEXT,
  approved_purchasing_process TEXT,
  status TEXT NOT NULL DEFAULT 'NOT_CONTACTED' CHECK (status IN ('NOT_CONTACTED','DRAFT_READY','APPROVED_TO_SEND','CONTACTED','REPLIED','IN_DISCUSSION','SUPPLY_AGREED','DECLINED','OPTED_OUT','PAUSED')),
  priority INTEGER,                     -- 1 = highest
  follow_up_date TEXT,
  next_action TEXT,
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS outreach_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  organisation_id TEXT NOT NULL REFERENCES organisations(id),
  contact_id INTEGER REFERENCES contacts(id),
  sequence_step INTEGER NOT NULL DEFAULT 0,      -- 0 initial, 1 first follow-up, 2 final
  subject TEXT NOT NULL,
  body TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT','APPROVED','SENT','CANCELLED')),
  personalisation_facts TEXT,                     -- JSON list of {fact, source_url}
  approved_by TEXT,
  approved_at TEXT,
  sent_at TEXT,                                   -- only set when a real send is recorded
  sent_via TEXT,
  reply_summary TEXT,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

-- --------------------------------------------------- opportunities (deals)
CREATE TABLE IF NOT EXISTS opportunities (
  id TEXT PRIMARY KEY,
  found_at TEXT NOT NULL,
  title TEXT NOT NULL,
  organisation_id TEXT REFERENCES organisations(id),
  team_or_school TEXT,
  player TEXT,
  era TEXT,
  season TEXT,
  item_type TEXT,
  seller TEXT,
  platform TEXT,
  listing_url TEXT NOT NULL,
  listed_price_cents INTEGER NOT NULL,
  currency TEXT NOT NULL,
  shipping_cents INTEGER,               -- in listing currency, null = unknown
  claimed_classification TEXT,
  condition TEXT,
  size TEXT,
  evidence TEXT,                        -- JSON list of evidence codes, see authentication/rules.py
  red_flags TEXT,                       -- JSON list
  comps TEXT,                           -- JSON list of {url, price, currency, date, verified}
  live_verified INTEGER NOT NULL DEFAULT 0, -- 1 only when a person/agent loaded the listing directly
  is_demo INTEGER NOT NULL DEFAULT 0,
  -- computed by sourcing/engine.py
  supported_classification TEXT,
  landed_cost_aud_cents INTEGER,
  est_resale_aud_cents INTEGER,
  gross_margin_pct REAL,
  demand_score REAL,
  deal_score REAL,
  risk_grade TEXT,
  recommendation TEXT,
  rejection_reasons TEXT,               -- JSON list
  evaluated_at TEXT
);

-- ---------------------------------------------------- products & inventory
CREATE TABLE IF NOT EXISTS products (
  id TEXT PRIMARY KEY,                  -- SKU, e.g. OCO-TW-0001
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,                  -- "Orlando Magic | Penny Hardaway Era | Original Nike Team-Issued Warmup"
  department TEXT NOT NULL,             -- see commerce/catalogue.py DEPARTMENTS
  era TEXT NOT NULL CHECK (era IN ('OG','CURRENT')),
  league_id TEXT REFERENCES leagues(id),
  organisation_id TEXT REFERENCES organisations(id),
  team_or_school TEXT,
  player_id TEXT REFERENCES players(id),
  player_connection TEXT,               -- free text, must be consistent with classification
  season TEXT,
  manufacturer TEXT,
  item_type TEXT NOT NULL,              -- TEARAWAY_PANTS | WARMUP_JACKET | SHOOTING_SHIRT | JERSEY | SHOES | PRACTICE | BAG | OTHER
  size TEXT,
  condition_grade TEXT,                 -- DEADSTOCK | EXCELLENT | VERY_GOOD | GOOD | FAIR
  condition_notes TEXT,
  claimed_classification TEXT NOT NULL, -- what the listing says
  supported_classification TEXT,        -- what the evidence supports (authentication engine)
  story_team TEXT,
  story_era TEXT,
  story_design TEXT,
  story_rarity TEXT,
  story_why_collect TEXT,
  story_vs_retail TEXT,
  description TEXT,
  price_cents INTEGER,
  currency TEXT NOT NULL DEFAULT 'AUD',
  ownership TEXT NOT NULL CHECK (ownership IN ('OWNED','CONSIGNMENT','PARTNER','MARKETPLACE','DEMO')),
  status TEXT NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DEMO','DRAFT','IN_REVIEW','LISTED','RESERVED','SOLD','WITHDRAWN')),
  stock_qty INTEGER NOT NULL DEFAULT 0,
  stock_confirmed INTEGER NOT NULL DEFAULT 0,      -- physical custody or written listing authority confirmed
  listing_authority_ref TEXT,                      -- agreement id / purchase id
  is_demo INTEGER NOT NULL DEFAULT 0,
  landed_cost_cents INTEGER,
  fulfilment_plan TEXT,
  returns_terms TEXT,
  collections TEXT,                     -- JSON list of department codes the product appears in
  art TEXT,                             -- JSON illustration spec for demo placeholders (no third-party images)
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS product_media (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  side TEXT NOT NULL CHECK (side IN ('ITEM','REFERENCE')),
  -- ITEM:      EXACT_ITEM_PHOTO | ILLUSTRATION_PLACEHOLDER
  -- REFERENCE: EXACT_PHOTO_MATCH | SAME_DESIGN_REFERENCE | ERA_REFERENCE | REFERENCE_PENDING
  match_level TEXT NOT NULL,
  url TEXT,
  caption TEXT,
  rights_status TEXT NOT NULL CHECK (rights_status IN ('OWNED','LICENSED','PUBLIC_DOMAIN','CC_LICENCE','LINK_ONLY','PENDING','NONE')),
  rights_ref TEXT,
  credit TEXT
);

-- evidence attached to a product (authentication record)
CREATE TABLE IF NOT EXISTS evidence (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  code TEXT NOT NULL,                   -- see authentication/rules.py EVIDENCE
  detail TEXT,
  reference_id TEXT,                    -- certificate / LOA / lot number
  url TEXT,
  verified_by TEXT,
  verified_at TEXT
);

CREATE TABLE IF NOT EXISTS custody_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  happened_on TEXT,                     -- may be approximate e.g. 1996
  holder TEXT NOT NULL,
  event TEXT NOT NULL,                  -- ISSUED | RETAINED | RELEASED | SOLD | CONSIGNED | RECEIVED | AUTHENTICATED
  documented INTEGER NOT NULL DEFAULT 0,
  note TEXT
);

CREATE TABLE IF NOT EXISTS auth_reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  reviewed_at TEXT NOT NULL,
  reviewer TEXT NOT NULL,
  supported_classification TEXT NOT NULL,
  claim_ok INTEGER NOT NULL,
  findings TEXT NOT NULL                -- JSON
);

-- ---------------------------------------------- consignment & sellers
CREATE TABLE IF NOT EXISTS sellers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER REFERENCES users(id),
  display_name TEXT NOT NULL,
  email TEXT NOT NULL,
  country TEXT,
  tier TEXT NOT NULL DEFAULT 'APPLICANT' CHECK (tier IN ('APPLICANT','ID_VERIFIED','VERIFIED_COLLECTOR','APPROVED_PARTNER','SUSPENDED')),
  checks TEXT,                          -- JSON of onboarding checklist booleans
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

CREATE TABLE IF NOT EXISTS consignments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  seller_id INTEGER REFERENCES sellers(id),
  applicant_name TEXT NOT NULL,
  applicant_email TEXT NOT NULL,
  item_description TEXT NOT NULL,
  team_or_school TEXT,
  era TEXT,
  claimed_classification TEXT,
  provenance_story TEXT,
  evidence_offered TEXT,               -- JSON list of evidence codes the applicant says they hold
  asking_price_cents INTEGER,
  status TEXT NOT NULL DEFAULT 'SUBMITTED' CHECK (status IN ('SUBMITTED','EVIDENCE_REVIEW','ACCEPTED','DECLINED','AGREEMENT_SENT','AGREEMENT_SIGNED','RECEIVED','AUTHENTICATED','LISTED','SOLD','PAID_OUT','RETURNED')),
  commission_pct REAL,
  agreement_ref TEXT,
  product_id TEXT REFERENCES products(id),
  decision_notes TEXT,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  updated_at TEXT
);

-- ------------------------------------------------- finance and launch
CREATE TABLE IF NOT EXISTS acquisitions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  opportunity_id TEXT REFERENCES opportunities(id),
  product_id TEXT REFERENCES products(id),
  description TEXT NOT NULL,
  category TEXT NOT NULL CHECK (category IN ('TEARAWAYS','OTHER_ITEMS','FREIGHT_IMPORT','AUTH_PREP','RESERVE')),
  amount_aud_cents INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'PROPOSED' CHECK (status IN ('PROPOSED','APPROVED','COMMITTED','PAID','CANCELLED')),
  approved_by TEXT,
  approved_at TEXT,
  is_estimate INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

CREATE TABLE IF NOT EXISTS launch_slots (
  slot INTEGER PRIMARY KEY,             -- 1..30
  lane TEXT NOT NULL CHECK (lane IN ('OWNED','CONSIGNMENT','PARTNER')),
  target_description TEXT,
  product_id TEXT REFERENCES products(id),
  opportunity_id TEXT REFERENCES opportunities(id),
  consignment_id INTEGER REFERENCES consignments(id),
  notes TEXT
);

-- --------------------------------------------------- customers/community
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  display_name TEXT,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'CUSTOMER' CHECK (role IN ('CUSTOMER','SELLER','ADMIN')),
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

CREATE TABLE IF NOT EXISTS sessions (
  token TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS wishlist (
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  product_id TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  added_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  PRIMARY KEY (user_id, product_id)
);

CREATE TABLE IF NOT EXISTS wanted_posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER REFERENCES users(id),
  display_name TEXT NOT NULL,
  team_or_school TEXT,
  era TEXT,
  item_type TEXT,
  description TEXT NOT NULL,
  budget_aud_cents INTEGER,
  status TEXT NOT NULL DEFAULT 'PENDING_MODERATION' CHECK (status IN ('PENDING_MODERATION','OPEN','MATCHED','CLOSED','REJECTED')),
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

CREATE TABLE IF NOT EXISTS waitlist (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  era_preference TEXT,
  teams TEXT,
  consent_marketing INTEGER NOT NULL,
  consent_text TEXT NOT NULL,
  source TEXT,
  unsubscribed INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER REFERENCES users(id),
  status TEXT NOT NULL CHECK (status IN ('PENDING_PAYMENT','PAID','FULFILLED','CANCELLED','REFUNDED')),
  provider TEXT,
  provider_ref TEXT,
  total_cents INTEGER NOT NULL,
  currency TEXT NOT NULL DEFAULT 'AUD',
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

CREATE TABLE IF NOT EXISTS order_lines (
  order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  product_id TEXT NOT NULL REFERENCES products(id),
  price_cents INTEGER NOT NULL
);

-- --------------------------------------------------------------- audit
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  actor TEXT NOT NULL,                 -- agent name, user email, or system
  action TEXT NOT NULL,
  entity_type TEXT,
  entity_id TEXT,
  detail TEXT
);

CREATE TABLE IF NOT EXISTS agent_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  agent TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  ok INTEGER,
  summary TEXT,
  metrics TEXT                          -- JSON of measurable objective results
);
