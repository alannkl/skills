"""Shopping cart, kept in the user's session between requests."""
from dataclasses import dataclass, field


@dataclass
class Line:
    sku: str
    quantity: int
    unit_cents: int


@dataclass
class Cart:
    lines: list = field(default_factory=list)
    item_count: int = 0

    def add(self, sku, quantity, unit_cents):
        self.item_count += quantity
        for line in self.lines:
            if line.sku == sku:
                line.quantity += quantity
                return
        self.lines.append(Line(sku, quantity, unit_cents))

    def remove(self, sku):
        for line in self.lines:
            if line.sku == sku:
                self.item_count -= line.quantity
        self.lines = [line for line in self.lines if line.sku != sku]

    def set_quantity(self, sku, quantity):
        if quantity <= 0:
            self.remove(sku)
            return
        for line in self.lines:
            if line.sku == sku:
                self.item_count += quantity - line.quantity
                line.quantity = quantity
                return
        raise KeyError(sku)

    def total_cents(self):
        return sum(line.quantity * line.unit_cents for line in self.lines)
