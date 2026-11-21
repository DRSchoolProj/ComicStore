"""
File:        item_entity.py
Description: Entity class for items. Holds the list of item dicts and reads/writes
             that list to a JSON file on disk. Contains no GUI or validation logic.
             Each item dict: {"sku": int, "name": str, "category": str, "quantity": int,
             "supplier_id": int, "unit_cost": float, "price": float, "threshold": int,
             "sold": int}   (sold = units sold this week)
Authors:     [Hamza]
Date:        [2026-11-20]
"""

import json
import os

# Save next to this source file so the path is the same no matter where the program is launched from
DEFAULT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "items.json")

# Order of the values passed to add() and update() (sku and sold are managed by the entity itself)
# "threshold" is the item's order threshold: if the projected sales rate shows that the item's
# quantity will fall below it soon, the item is included in the next generated order.
FIELDS = ("name", "category", "quantity", "supplier_id", "unit_cost", "price", "threshold")


class ItemEntity:
    """List of item dicts, saveable to disk."""

    def __init__(self, filepath=DEFAULT_FILE):
        self.filepath = filepath
        self.items = []   # list of dicts, one per item
        self.load()

    def load(self):
        """Read items from disk. A missing file just means no items yet."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                self.items = json.load(f)
        except FileNotFoundError:
            self.items = []

    def save(self):
        """Write the current list of items to disk."""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.items, f, indent=4)

    def get_all(self):
        """Return a copy of the list so callers can't change it without going through this class."""
        return [dict(i) for i in self.items]

    def get(self, sku):
        """Return a copy of the item with this sku, or None."""
        return next((i for i in self.get_all() if i["sku"] == sku), None)

    def add(self, *values):
        """Create an item with the next sequential sku, save, and return the new dict.
        values are in the order of FIELDS.
        """
        next_sku = max((i["sku"] for i in self.items), default=0) + 1
        item = dict(zip(FIELDS, values), sku=next_sku, sold=0)
        self.items.append(item)
        self.save()
        return dict(item)

    def update(self, sku, *values):
        """Overwrite the FIELDS of the item with this sku. Returns True if one was found."""
        for item in self.items:
            if item["sku"] == sku:
                item.update(zip(FIELDS, values))
                self.save()
                return True
        return False

    def remove(self, sku):
        """Delete the item with this sku, save, and return True if one was found."""
        before = len(self.items)
        self.items = [i for i in self.items if i["sku"] != sku]
        removed = len(self.items) < before
        if removed:
            self.save()
        return removed

    def change_stock(self, sku, amount, sold=0):
        """Add amount to the item's quantity (negative to subtract) and sold to its weekly sales."""
        for item in self.items:
            if item["sku"] == sku:
                item["quantity"] += amount
                item["sold"] += sold
        self.save()

    def reset_sales(self):
        """Set every item's weekly sales back to 0."""
        for item in self.items:
            item["sold"] = 0
        self.save()
