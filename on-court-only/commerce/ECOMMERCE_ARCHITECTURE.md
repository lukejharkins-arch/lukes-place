# Ecommerce architecture

Independent decision. Platform pricing and capabilities are in `docs/PLATFORM_EVALUATION.md` (researched 2026-11-05, sources cited there).

## Decision
**Split the system of record from the checkout.**

1. **System of record: this repository** (Python standard library + SQLite). Sourcing, authentication, provenance, consignment, CRM, launch gate and the two-era storefront. This is the part no off-the-shelf platform does, and it is the competitive moat: every product's evidence, custody and classification lives here and is enforced in code.
2. **Launch checkout: Shopify Basic + Shopify Payments** (A$42/month on annual billing; cards 1.7% + 30c domestic, 3.5% + 30c international; a 2% surcharge applies on Basic if a third-party gateway is used). Products that pass the launch gate are pushed to Shopify as single-quantity listings; Shopify handles payment, GST-ready invoicing, fraud screening and order notifications. A consignment app (Consignbook free tier or SplitMere at about US$19/month) tracks consignor payouts.
3. **Marketplace phase (after launch): Sharetribe Live or a custom Stripe Connect build.** Sharetribe (about US$199-259/month) gives seller onboarding and split payouts quickly; a custom Medusa or Stripe Connect build on our own database scored slightly higher for long-term fit but needs a developer. Decide once there are 50+ approved consignors.

## Why not the alternatives (summary)
| Option | Verdict |
|---|---|
| Shopify only | Great checkout, but it can't enforce the evidence-to-claim rules or model provenance and custody without heavy custom apps |
| Shopify + multi-vendor app at launch | Premature: an open marketplace before seller verification and buyer protection is the biggest trust risk |
| WooCommerce | Cheap licences but hosting, security patching and plugin conflicts fall on a one-person business (scored 3.1/5 vs Shopify 4.3) |
| Sharetribe now | Built for many sellers; we start as one controlled retailer |
| Fully custom checkout | PCI scope, fraud and tax logic for no benefit at 30 items |

## Component map
```
storefront/ (vanilla JS SPA, two era themes) ──HTTP──> server.py (JSON API, sessions, CSRF header, CSP)
                                                          │
                          ┌───────────────────────────────┼─────────────────────────────┐
                 authentication/rules.py        sourcing/engine.py, economics.py   outreach/crm.py
                 (classify, lint, media)        demand.py, search_framework.py     operations/*.py
                          └───────────────────────────────┼─────────────────────────────┘
                                                  data/oco.db (SQLite, schema.sql)
                                                          │
                                   agents/run.py (12 agents) · reports/generate.py
                                                          │  (future adapter)
                                         commerce/shopify_adapter (not built: needs credentials)
```

## What is built and working
Responsive storefront with OG and Current modes; homepage; departments; search and filters; product exhibit pages with left/right comparison; team pages; player references; Tearaway Vault; wishlists; wanted board (moderated); consignment application; seller onboarding tiers; accounts; email waitlist with recorded consent; admin dashboard (sourcing, search plan, CRM, outreach, launch tracker, budget, products with gate results, consignments, moderation, demand, channels). Checkout endpoint validates items and refuses: no provider is configured.

## Checkout and shipping integration
See `CHECKOUT_ARCHITECTURE.md`.

## User accounts and security
PBKDF2-SHA256 (240k iterations) password hashes; random 256-bit session tokens in HttpOnly, SameSite=Strict cookies; state-changing requests need a custom `X-Requested-With` header (CSRF defence with SameSite); 64 KB request cap; CSP `default-src 'self'`; static path traversal guarded; all user text escaped on render; admin routes require the ADMIN role. Not yet: rate limiting, email verification, password reset, 2FA for admin. These are listed in `docs/KNOWN_GAPS.md`.
