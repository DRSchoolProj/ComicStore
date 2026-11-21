"""
File:        item_management_control.py
Description: Control class for item management. Sits between the GUI and
             ItemEntity: validates user input, applies the business rules,
             and tells the entity what to add, update or remove.
Authors:     [Hamza]
Date:        [2026-11-20]
"""

from item_entity import ItemEntity
from supplier_management_control import SupplierManagementControl


def calculate_sales_rate(sold):
    """Units sold per day (sold is the total for the week)."""
    return round(sold / 7, 2)


class ItemManagementControl:
    """Handles item management requests from the GUI."""

    def __init__(self, entity=None, supplier_control=None):
        # Accepting these lets tests pass in ones that use temporary files
        self.entity = entity if entity is not None else ItemEntity()
        self.supplier_control = (supplier_control if supplier_control is not None
                                 else SupplierManagementControl())

    def get_items(self):
        """Return all items as dicts, each with extra keys:
        "sales_rate" (units/day) and "low_stock" (quantity at or below threshold).
        """
        items = self.entity.get_all()
        for item in items:
            item["sales_rate"] = calculate_sales_rate(item["sold"])
            item["low_stock"] = item["quantity"] <= item["threshold"]
        return items

    def get_suppliers(self):
        """Return all suppliers so the GUI can offer them in a dropdown."""
        return self.supplier_control.get_suppliers()

    def add_item(self, name, category, quantity, supplier_id, unit_cost, price, threshold):
        """Validate the input and add an item. Returns the new dict.
        Raises ValueError with a user-readable message if the input is invalid.
        """
        values = self._validate(name, category, quantity, supplier_id, unit_cost, price, threshold)
        return self.entity.add(*values)

    def update_item(self, sku, name, category, quantity, supplier_id, unit_cost, price, threshold):
        """Validate the input and overwrite the item with this sku.
        Raises ValueError if the input is invalid or the item no longer exists.
        """
        values = self._validate(name, category, quantity, supplier_id, unit_cost, price, threshold)
        if not self.entity.update(sku, *values):
            raise ValueError("That item no longer exists.")

    def remove_items(self, skus):
        """Remove each item whose sku is in skus.
        Raises ValueError if nothing was given to remove.
        """
        if not skus:
            raise ValueError("Select an item to remove.")
        for sku in skus:
            self.entity.remove(sku)

    def adjust_stock(self, sku, amount, sold=0):
        """Add amount to an item's stock (negative to subtract), e.g. for orders or sales.
        Raises ValueError if the item doesn't exist or stock would go below zero.
        """
        item = self.entity.get(sku)
        if item is None:
            raise ValueError("That item no longer exists.")
        if item["quantity"] + amount < 0:
            raise ValueError(f"Not enough stock of {item['name']} (only {item['quantity']} left).")
        self.entity.change_stock(sku, amount, sold)

    def reset_weekly_sales(self):
        """Start a new sales week."""
        self.entity.reset_sales()

    # ---- helpers ----

    def _validate(self, name, category, quantity, supplier_id, unit_cost, price, threshold):
        """Clean and check the form values. Returns them as a tuple in ItemEntity's FIELDS order."""
        name = name.strip()
        category = category.strip()
        if not name:
            raise ValueError("Please enter an item name.")
        if not category:
            raise ValueError("Please enter a category.")
        quantity = self._number(quantity, int, "Quantity")
        unit_cost = self._number(unit_cost, float, "Unit cost")
        price = self._number(price, float, "Price")

        # Order threshold: if the projected sales rate shows that the item's quantity will fall
        # below this threshold soon, the item is included in the next generated order.
        # Optional: left blank, it defaults to 0.
        if threshold is None or not str(threshold).strip():
            threshold = 0
        threshold = self._number(threshold, int, "Order threshold")

        if supplier_id in ("", None):
            raise ValueError("Please select a supplier (add one under Manage Suppliers first).")
        supplier_id = self._number(supplier_id, int, "Supplier")
        if supplier_id not in {s["id"] for s in self.get_suppliers()}:
            raise ValueError("That supplier does not exist.")

        return (name, category, quantity, supplier_id, unit_cost, price, threshold)

    @staticmethod
    def _number(value, kind, label):
        """Convert text to int/float; raise a readable ValueError if it isn't a non-negative number."""
        try:
            number = kind(str(value).strip())
        except ValueError:
            raise ValueError(f"{label} must be a {'whole number' if kind is int else 'number'}.")
        if number < 0:
            raise ValueError(f"{label} cannot be negative.")
        return number
