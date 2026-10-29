from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def prorate(lines, days_used, days_in_period):
    ratio = Decimal(days_used) / Decimal(days_in_period)
    return sum(
        (Decimal(line.amount) * ratio).quantize(CENT, rounding=ROUND_HALF_UP)
        for line in lines
    )
