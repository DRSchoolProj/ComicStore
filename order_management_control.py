"""
File:        order_management_control.py
Description: Control class for order management. Sits between the GUI and OrderEntity:
             generates, modifies, approves and receives orders, applying the business rules.
             Item and supplier data are read through their control classes.
Authors:     [Daphne]
Date:        [2026-11-20]
"""

import math

from order_entity import OrderEntity
from calculate_budget import CalculateBudget
from expense_management_control import ExpenseManagementControl
from item_management_control import ItemManagementControl
from supplier_management_control import SupplierManagementControl

# How many days ahead to project sales when deciding whether an item needs reordering.
# Set to 0 to only reorder items that are already at or below their order threshold.
LOOKAHEAD_DAYS = 7


def calculate_reorder_quantity(quantity, threshold, sales_rate):
    """How many to order: enough for twice the reorder level or two weeks of sales, whichever is more."""
    return max(max(threshold * 2, math.ceil(sales_rate * 14)) - quantity, 1)


def needs_restock(item):
    """True if the item is at/below its order threshold, or if the projected sales rate shows
    its quantity will fall below the order threshold soon (within LOOKAHEAD_DAYS).
    Such items are included in the next generated order.
    """
    projected = item["quantity"] - item["sales_rate"] * LOOKAHEAD_DAYS
    return item["quantity"] <= item["threshold"] or projected < item["threshold"]


class OrderManagementControl:
    """Handles order management requests from the GUI."""

    def __init__(self, order_entity=None, item_control=None, supplier_control=None, expense_control=None):
        # Passing these in lets tests use ones that use temporary files
        self.orders = order_entity or OrderEntity()
        self.items = item_control or ItemManagementControl()
        self.suppliers = supplier_control or SupplierManagementControl()
        self.expenses = expense_control or ExpenseManagementControl()
        self.budget = CalculateBudget(self.items, self.expenses, self.orders)

    def display_available_budget(self):
        return self.budget.calculate_available_funds()

    def get_orders(self):
        """All orders, each with the supplier name and a short list of items added for the table."""
        names = {s["id"]: s["name"] for s in self.suppliers.get_suppliers()}
        orders = self.orders.get_all()
        for order in orders:
            order["supplier_name"] = names.get(order["supplier_id"], "(removed)")
            order["items_text"] = ", ".join(f"{l['name']} x{l['quantity']}" for l in order["line_items"])
        return orders

    def generate_orders(self):
        """One order per supplier for the items that need restocking, without going over the
        available funds. Returns the new orders. Raises ValueError if none can be made.
        """
        orders = self.orders.get_all()
        # money already used by generated orders can't be used again
        remaining = (self.budget.calculate_available_funds()
                     - sum(o["total_cost"] for o in orders if o["status"] == "Generated"))
        if remaining <= 0:
            raise ValueError("No funds are available for a new order.")
        ordered = [l["sku"] for o in orders if o["status"] != "Received" for l in o["line_items"]]
        supplier_ids = [s["id"] for s in self.suppliers.get_suppliers()]
        low = [i for i in self.items.get_items()
               if i["supplier_id"] in supplier_ids and i["sku"] not in ordered and needs_restock(i)]
        if not low:
            raise ValueError("No items need restocking.")
        low.sort(key=lambda i: i["quantity"] / max(i["threshold"], 1))      # lowest stock first
        lines = {}
        for item in low:
            quantity = calculate_reorder_quantity(item["quantity"], item["threshold"], item["sales_rate"])
            if item["unit_cost"] > 0:
                quantity = min(quantity, int(remaining // item["unit_cost"]))   # only what we can afford
            if quantity >= 1:
                remaining -= quantity * item["unit_cost"]
                lines.setdefault(item["supplier_id"], []).append(
                    {"sku": item["sku"], "name": item["name"], "quantity": quantity, "unit_cost": item["unit_cost"]})
        if not lines:
            raise ValueError("Not enough funds to order any items.")
        return [self.orders.add(supplier_id, items) for supplier_id, items in lines.items()]

    def find_order(self, order_id, status, message):
        """Return the order if it exists and has this status, otherwise raise ValueError."""
        order = self.orders.get(order_id)
        if order is None:
            raise ValueError("Select an order first.")
        if order["status"] != status:
            raise ValueError(message)
        return order

    def modify_order(self, order_id, sku, quantity):
        """Change the quantity of one item on an order that is not approved yet. 0 removes the item."""
        order = self.find_order(order_id, "Generated", "Only orders that are not approved can be modified.")
        try:
            quantity = int(quantity)
        except ValueError:
            raise ValueError("Quantity must be a whole number.")
        line = next((l for l in order["line_items"] if l["sku"] == sku), None)
        if quantity < 0 or line is None:
            raise ValueError("Enter a quantity of 0 or more for an item that is on the order.")
        if quantity == 0:
            order["line_items"].remove(line)
        else:
            line["quantity"] = quantity
        if not order["line_items"]:
            raise ValueError("An order must have at least one item.")
        self.orders.update(order)

    def approve_order(self, order_id):
        """Approve an order that is not approved yet, as long as it fits within the available funds."""
        order = self.find_order(order_id, "Generated", "This order is already approved.")
        if order["total_cost"] > self.budget.calculate_available_funds():
            raise ValueError("This order costs more than the funds available.")
        order["status"] = "Approved"
        self.orders.update(order)

    def receive_order(self, order_id):
        """Mark an approved order as received and add its items to the stock."""
        order = self.find_order(order_id, "Approved", "Only approved orders can be marked as received.")
        existing = {i["sku"] for i in self.items.get_items()}
        for line in order["line_items"]:
            if line["sku"] in existing:         # skip items deleted since the order was made
                self.items.adjust_stock(line["sku"], line["quantity"])
        order["status"] = "Received"
        self.orders.update(order)
