"""
File:        order_entity.py
Description: Entity class for orders. Holds the list of order dicts and reads/writes
             that list to orders.json. Contains no GUI or validation logic.
             Each order: {"order_id": int, "supplier_id": int, "order_date": "YYYY-MM-DD",
             "status": "Generated" | "Approved" | "Received",
             "line_items": [{"sku": int, "name": str, "quantity": int, "unit_cost": float}],
             "total_cost": float}
Authors:     [Hamza]
Date:        [2026-11-20]
"""

import copy
import json
import os
from datetime import date

# Save next to this source file so the path is the same no matter where the program is launched from
DEFAULT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orders.json")


class OrderEntity:
    """List of order dicts, saveable to disk."""

    def __init__(self, filepath=DEFAULT_FILE):
        self.filepath = filepath
        self.orders = []
        self.load()

    def load(self):
        """Read orders from disk. A missing file just means no orders yet."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                self.orders = json.load(f)
        except FileNotFoundError:
            self.orders = []

    def save(self):
        """Write the current list of orders to disk."""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.orders, f, indent=4)

    def get_all(self):
        """Return a deep copy (each order has a list inside it) so callers can't change it
        without going through this class."""
        return copy.deepcopy(self.orders)

    def get(self, order_id):
        """Return a copy of the order with this id, or None."""
        return next((copy.deepcopy(o) for o in self.orders if o["order_id"] == order_id), None)

    def add(self, supplier_id, line_items):
        """Create a "Generated" order with the next sequential id, save, and return it."""
        order_id = max((o["order_id"] for o in self.orders), default=0) + 1     # highest id + 1
        order = {"order_id": order_id, "supplier_id": supplier_id, "order_date": str(date.today()),
                 "status": "Generated", "line_items": line_items, "total_cost": 0}
        self.update(order)
        return self.get(order_id)

    def update(self, order):
        """Save an order, replacing the one with the same order_id (or adding it if it is new).
        total_cost is recalculated from the line items every time.
        """
        order["total_cost"] = round(sum(l["quantity"] * l["unit_cost"] for l in order["line_items"]), 2)
        self.orders = [o for o in self.orders if o["order_id"] != order["order_id"]] + [order]
        self.orders.sort(key=lambda o: o["order_id"])
        self.save()