"""Import customers and invoices from the old billing system's CSV exports."""

import csv


def import_customers(path):
    with open(path, newline="") as f:
        return [row for row in csv.DictReader(f) if row.get("status") != "deleted"]


def import_invoices(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))
