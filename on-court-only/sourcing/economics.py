"""Landed cost and resale economics. All outputs carry the assumptions used."""
from __future__ import annotations

from commerce import config as C


def to_aud(amount: float, currency: str) -> float:
    rate = C.FX_TO_AUD.get(currency.upper())
    if rate is None:
        raise ValueError(f"No FX rate configured for {currency}")
    return amount * rate


def landed_cost(price: float, currency: str, shipping: float | None = None,
                auth_prep_aud: float | None = None) -> dict:
    """Estimate Australian landed cost for one overseas (or domestic) purchase.

    price / shipping are in the listing currency. Returns AUD figures and flags.
    """
    flags = []
    cur = currency.upper()
    item_aud = to_aud(price, cur)
    if shipping is None:
        ship_aud = 0.0 if cur == "AUD" else C.DEFAULT_INTL_SHIPPING_AUD
        flags.append(f"Shipping not shown: assumed A${ship_aud:.2f} (ESTIMATE)")
    else:
        ship_aud = to_aud(shipping, cur)
    fx_fee = 0.0 if cur == "AUD" else (item_aud + ship_aud) * C.FX_CONVERSION_FEE_PCT / 100
    gst = duty = entry = 0.0
    if cur != "AUD":
        if item_aud <= C.LOW_VALUE_THRESHOLD_AUD:
            # low value imported goods: GST collected by marketplace / vendor at sale
            gst = (item_aud + ship_aud) * C.GST_RATE
            flags.append("GST on low value import assumed collected at checkout (10%)")
        else:
            duty = item_aud * C.APPAREL_DUTY_RATE
            gst = (item_aud + ship_aud + duty) * C.GST_RATE
            entry = C.FORMAL_ENTRY_CHARGES_AUD
            flags.append("Above A$1,000: formal import entry, duty and broker charges (ESTIMATE)")
    prep = C.DEFAULT_AUTH_PREP_AUD if auth_prep_aud is None else auth_prep_aud
    total = item_aud + ship_aud + fx_fee + gst + duty + entry + prep
    return {
        "item_aud": round(item_aud, 2), "shipping_aud": round(ship_aud, 2), "fx_fee_aud": round(fx_fee, 2),
        "gst_aud": round(gst, 2), "duty_aud": round(duty, 2), "entry_charges_aud": round(entry, 2),
        "auth_prep_aud": round(prep, 2), "total_aud": round(total, 2),
        "fx_as_of": C.FX_AS_OF, "flags": flags,
    }


def resale(sale_price_aud: float, landed_total_aud: float) -> dict:
    """Net proceeds and gross margin for an owned item sold in Australia."""
    gst_out = sale_price_aud / 11 if C.GST_REGISTERED else 0.0
    pay_fee = sale_price_aud * C.PAYMENT_FEE_PCT / 100 + C.PAYMENT_FEE_FIXED_AUD
    returns = sale_price_aud * C.RETURNS_ALLOWANCE_PCT / 100
    net = sale_price_aud - gst_out - pay_fee - C.OUTBOUND_SHIPPING_AUD - returns
    gross_profit = net - landed_total_aud
    margin = (gross_profit / (sale_price_aud - gst_out) * 100) if sale_price_aud else 0.0
    return {
        "sale_price_aud": round(sale_price_aud, 2), "gst_payable_aud": round(gst_out, 2),
        "payment_fees_aud": round(pay_fee, 2), "outbound_shipping_aud": C.OUTBOUND_SHIPPING_AUD,
        "returns_allowance_aud": round(returns, 2), "net_proceeds_aud": round(net, 2),
        "gross_profit_aud": round(gross_profit, 2), "gross_margin_pct": round(margin, 1),
    }


def consignment_payout(sale_price_aud: float) -> dict:
    rate = C.CONSIGNMENT_COMMISSION_PCT["PREMIUM_OVER_1000" if sale_price_aud > 1000 else "STANDARD"]
    commission = sale_price_aud * rate / 100
    pay_fee = sale_price_aud * C.PAYMENT_FEE_PCT / 100 + C.PAYMENT_FEE_FIXED_AUD
    house_net = commission - pay_fee - C.OUTBOUND_SHIPPING_AUD
    return {"commission_pct": rate, "commission_aud": round(commission, 2),
            "consignor_payout_aud": round(sale_price_aud - commission, 2),
            "house_net_aud": round(house_net, 2)}


def comps_estimate(comps: list[dict]) -> dict:
    """Median of VERIFIED sold comparables, converted to AUD. Unverified comps are excluded."""
    verified = [c for c in comps if c.get("verified") and c.get("price") is not None]
    vals = sorted(to_aud(float(c["price"]), c.get("currency", "AUD")) for c in verified)
    if not vals:
        return {"count": 0, "median_aud": None, "excluded": len(comps) - len(verified)}
    mid = len(vals) // 2
    median = vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2
    return {"count": len(vals), "median_aud": round(median, 2), "low_aud": round(vals[0], 2),
            "high_aud": round(vals[-1], 2), "excluded": len(comps) - len(verified)}
