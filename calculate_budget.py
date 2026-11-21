"""
File:        calculate_budget.py
Description: Works out the funds available this week:
             income this week - weekly expenses - pending charges (approved, unreceived orders).
Authors:     [Daphne]
Date:        [2026-11-20]
"""


class CalculateBudget:
    """Funds available = income this week - weekly expenses - pending charges."""

    def __init__(self, item_control, expense_control, order_entity):
        # item_control: ItemManagementControl, expense_control: ExpenseManagementControl
        # (read through them, not through their entities directly)
        self.items, self.expenses, self.orders = item_control, expense_control, order_entity

    def calculate_income(self):
        """Units sold this week x selling price, for every item."""
        return round(sum(i["sold"] * i["price"] for i in self.items.get_items()), 2)

    def calculate_expenses(self):
        """Total of all weekly expenses."""
        return self.expenses.total_weekly_expenses()

    def calculate_pending(self):
        """Estimated cost of the orders that are approved but not received yet."""
        return round(sum(o["total_cost"] for o in self.orders.get_all() if o["status"] == "Approved"), 2)

    def calculate_available_funds(self):
        return round(self.calculate_income() - self.calculate_expenses() - self.calculate_pending(), 2)
