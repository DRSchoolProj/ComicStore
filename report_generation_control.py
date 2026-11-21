"""
File:        report_generation_control.py
Description: Control class for report generation. Builds the reports as plain text
             from item, expense and order data. Read-only: it never changes any data.
             Item and expense data are read through their control classes.
Authors:     [Hamza]
Date:        [2026-11-20]
"""

from calculate_budget import CalculateBudget
from expense_management_control import ExpenseManagementControl
from item_management_control import ItemManagementControl
from order_entity import OrderEntity

REPORT_TYPES = ("Budget Summary", "Operating Expenses", "Current Inventory", "Sales Statistics")


class ReportControl:
    """Builds the reports."""

    def __init__(self, item_control=None, expense_control=None, order_entity=None):
        # Passing these in lets tests use ones that use temporary files
        self.items = item_control or ItemManagementControl()
        self.expenses = expense_control or ExpenseManagementControl()
        self.budget = CalculateBudget(self.items, self.expenses, order_entity or OrderEntity())

    def generate_report(self, report_type):
        """Return the report as text. Raises ValueError if no valid type was chosen."""
        builders = {
            "Budget Summary": self.budget_summary,
            "Operating Expenses": self.operating_expenses,
            "Current Inventory": self.current_inventory,
            "Sales Statistics": self.sales_statistics,
        }
        if report_type not in builders:
            raise ValueError("Please select a report type.")
        return "\n".join([report_type.upper()] + builders[report_type]())

    # Each builder below returns the lines that go under the report's title.

    def budget_summary(self):
        b = self.budget
        return [f"Sales income: ${b.calculate_income():.2f}",
                f"Operating expenses: -${b.calculate_expenses():.2f}",
                f"Pending order charges: -${b.calculate_pending():.2f}",
                f"Funds available: ${b.calculate_available_funds():.2f}"]

    def operating_expenses(self):
        lines = [f"{e['name']}: ${e['weekly_amount']:.2f}" for e in self.expenses.get_expenses()]
        if not lines:
            lines = ["No expenses recorded."]
        return lines + [f"Total per week: ${self.budget.calculate_expenses():.2f}"]

    def current_inventory(self):
        lines = [f"SKU {i['sku']}  {i['name']}  qty {i['quantity']}  order threshold {i['threshold']}"
                 + ("  LOW" if i["low_stock"] else "") for i in self.items.get_items()]
        return lines or ["No items in inventory."]

    def sales_statistics(self):
        """Sales so far this week. Profit = (price - unit cost) x units sold, taking unit cost
        as what the store pays the supplier.
        """
        sold = [i for i in self.items.get_items() if i["sold"] > 0]
        if not sold:
            return ["No sales recorded this week."]
        lines = [f"{i['name']}: sold {i['sold']} ({i['sales_rate']}/day)  "
                 f"revenue ${i['sold'] * i['price']:.2f}  "
                 f"profit ${i['sold'] * (i['price'] - i['unit_cost']):.2f}" for i in sold]
        revenue = sum(i["sold"] * i["price"] for i in sold)
        profit = sum(i["sold"] * (i["price"] - i["unit_cost"]) for i in sold)
        return lines + [f"Total revenue ${revenue:.2f}  Total profit ${profit:.2f}"]
