"""Revenue reports for the admin dashboard."""
from collections import defaultdict


def format_currency(cents):
    return f"${cents // 100}.{cents % 100:02d}"


def monthly_totals(orders):
    totals = defaultdict(int)
    for order in orders:
        if order["status"] == "cancelled":
            continue
        key = order["created_at"].strftime("%Y-%m")
        totals[key] += order["amount_cents"] - order.get("refund_cents", 0)
    return {key: format_currency(value) for key, value in sorted(totals.items())}


def weekly_totals(orders):
    totals = defaultdict(int)
    for order in orders:
        if order["status"] == "cancelled":
            continue
        key = order["created_at"].strftime("%G-W%V")
        totals[key] += order["amount_cents"] - order.get("refund_cents", 0)
    return {key: format_currency(value) for key, value in sorted(totals.items())}
