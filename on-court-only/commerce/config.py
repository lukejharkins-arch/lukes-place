"""Business constants. Every number here is an ASSUMPTION unless a source is cited.

Values flagged `ESTIMATE` must be re-checked before any founder decision.
See docs/ASSUMPTIONS.md for the full register.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "oco.db"
SCHEMA_PATH = ROOT / "data" / "schema.sql"

# ---- founder budget (FOUNDER DECISION, not an estimate)
ACQUISITION_CEILING_AUD_CENTS = 200_000          # strictly UNDER A$2,000
PLANNING_ENVELOPE_AUD_CENTS = {                  # founder planning allocation (A$1,950)
    "TEARAWAYS": 85_000,
    "OTHER_ITEMS": 45_000,
    "FREIGHT_IMPORT": 35_000,
    "AUTH_PREP": 15_000,
    "RESERVE": 15_000,
}

# ---- launch mix (FOUNDER TARGET)
LAUNCH_MIX = {"OWNED": 8, "CONSIGNMENT": 17, "PARTNER": 5}

# ---- FX (ESTIMATE: replace with a dated rate at decision time)
FX_TO_AUD = {"AUD": 1.0, "USD": 1.53, "GBP": 1.98, "EUR": 1.70, "CAD": 1.10, "JPY": 0.0101, "NZD": 0.91}
FX_AS_OF = "2026-11-05 (ESTIMATE, not a live quote)"
FX_CONVERSION_FEE_PCT = 3.0       # ESTIMATE: card/PayPal currency conversion margin

# ---- import (see docs/LEGAL_RESEARCH.md; ESTIMATES until confirmed with a broker)
LOW_VALUE_THRESHOLD_AUD = 1000.0  # GST on low value imports collected at point of sale at/under this
GST_RATE = 0.10
APPAREL_DUTY_RATE = 0.05          # ESTIMATE: 0-5% depending on tariff line and origin (some clothing tariffs removed 1 Jul 2026, unconfirmed)
FORMAL_ENTRY_CHARGES_AUD = 150.0  # ESTIMATE: broker + import processing charge above threshold
DEFAULT_INTL_SHIPPING_AUD = 55.0  # ESTIMATE: US->AU tracked ~1kg parcel when listing shows none
DEFAULT_AUTH_PREP_AUD = 15.0      # ESTIMATE: cleaning, inspection, photography materials per item

# ---- selling (ESTIMATES pending platform choice, see docs/PLATFORM_EVALUATION.md)
PAYMENT_FEE_PCT = 1.7             # Shopify Payments AU domestic 1.7% + 30c (docs/PLATFORM_EVALUATION.md, checked 2026-11-05)
PAYMENT_FEE_FIXED_AUD = 0.30
OUTBOUND_SHIPPING_AUD = 12.05     # Australia Post small satchel ~A$11.70-12.05 (search extract 2026-11-05); Sendle exited AU Jan 2026
RETURNS_ALLOWANCE_PCT = 3.0       # ESTIMATE
GST_REGISTERED = False            # below A$75k turnover registration is optional (FLAG for accountant)

# ---- consignment (PROPOSED commercial terms, not agreed with anyone)
CONSIGNMENT_COMMISSION_PCT = {"STANDARD": 25.0, "PREMIUM_OVER_1000": 20.0}

# ---- deal engine thresholds (business rules)
MIN_GROSS_MARGIN_PCT = 35.0
MIN_VERIFIED_COMPS_FOR_BUY = 2
A_GRADE_SCORE = 80
B_GRADE_SCORE = 60
DAILY_TARGET = 20

# ---- era split
OG_LAST_SEASON_START = 2009       # seasons starting 2009 or earlier render as ON COURT OG
