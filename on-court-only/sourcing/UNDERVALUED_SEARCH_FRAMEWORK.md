# Undervalued resale search framework

Code: `sourcing/search_framework.py`. Output each day: `sourcing/search_plan_<date>.md`.

## How it works
1. **Prioritise:** the top 8 teams and programmes from the demand model, alternating OG and Current manufacturer vocabularies.
2. **Generate queries:** precise ("team issued warm up pants", "pro cut warm up", "player issued"), manufacturer-era ("champion orlando magic warm up", "starter …", "reebok …"), deliberate misspellings ("orlando majic", "tear-a-way", "wram up", "st marys"), vague seller phrasing ("big and tall nike pants", "90s basketball pants", "sports clothing lot", "mens 4xl track pants") and lots.
3. **Link out, don't scrape:** public search URLs for eBay (US live and sold, AU), Grailed, Depop, Vinted, Mercari, Poshmark, Etsy, Gumtree AU, Facebook Marketplace, GovDeals and Public Surplus. A person reviews the results within each site's terms.
4. **Score misclassification:** `misclassification_signal(title, price)` rises with pro-sizing or construction hints (XL+2, 3XLT, "made in USA", "sewn"), era cues and vague wording at low prices, and falls when the seller already uses collector vocabulary (priced accordingly).
5. **Record real finds only:** `sourcing/inbox/<date>.json` needs url, title, listed_price and currency. The hunter ingests it and the engine evaluates it.

## Seller vocabulary (evidence in `research/raw/supply_channels.json`)
Team issued / TI · game issued · player issued · pro cut · warmup-worn · photo-matched · LOA · MeiGray registration tag · tall sizing (LT, 2XL-T, XL+2) · tearaway, breakaway, rip-away, snap pants, popper pants (UK/AU) · Nike Team, Elite, "Authentics" (often retail).

## Hard rules
A low price or a poor description is never evidence. No deception, no impersonation, no pressure. Ask sellers for tag, label and size-tag photos and how they acquired the item; walk away from anything with unclear title, possible equipment-room theft or restricted college athlete gear.
