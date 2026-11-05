# Checkout, payment and shipping integration architecture

**Status: designed, not connected.** `/api/checkout` validates every item through `catalogue.can_purchase()` (not demo, LISTED, stock confirmed, listing authority recorded) and then returns 503 because no payment provider is configured. No card data ever touches this system.

## Flow once credentials are approved
1. Launch gate passes for a product (`operations/launch.py`): real stock, right to sell, evidence supports the claim, clean copy, exact item photos, reference rights resolved, condition, price, fulfilment and returns terms.
2. Admin publishes it: the adapter creates or updates a Shopify product (quantity 1, SKU = our product id, metafields: classification, evidence summary, provenance URL back to our exhibit page).
3. Shopper checks out on Shopify Checkout (cards, Apple Pay, Google Pay, PayPal; Afterpay or Zip after quoting merchant fees).
4. Shopify `orders/paid` webhook (HMAC-verified) marks our product SOLD and writes an `orders` row; consignment items move the consignment to SOLD for payout.
5. Fulfilment: Australia Post tracked satchel domestically (about A$11.70-12.05 small satchel, per 2026-11-05 research); international via Australia Post International Standard or an aggregator. Sendle closed in Australia in January 2026.

## Rules already reflected
- Card surcharges are banned in Australia from 1 October 2026, so fees are priced into the product.
- Single-quantity, one-of-one stock: Shopify inventory tracking on, overselling off.
- Consignor payout only after the return window closes.

## Credentials needed (founder action)
Shopify store and Admin API token (`write_products`, `read_orders`), webhook secret, Shopify Payments onboarding (ABN, bank account), Australia Post business account. Store them as environment variables, never in the repository.
