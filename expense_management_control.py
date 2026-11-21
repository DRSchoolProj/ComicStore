"""
File:        expense_management_control.py
Description: Control class for expense management. Sits between the GUI and
             ExpenseEntity: validates user input, applies the business rules,
             and tells the entity what to add, update or remove.
Authors:     [Hamza]
Date:        [2026-11-20]
"""

import math

from expense_entity import ExpenseEntity


class ExpenseManagementControl:
    """Handles expense management requests from the GUI."""

    def __init__(self, entity=None):
        # Accepting an entity lets tests pass in one that uses a temporary file
        self.entity = entity if entity is not None else ExpenseEntity()

    def get_expenses(self):
        """Return all expenses as a list of dicts."""
        return self.entity.get_all()

    def total_weekly_expenses(self):
        return round(sum(e["weekly_amount"] for e in self.entity.get_all()), 2)

    def check_expense(self, name, weekly_amount):
        """Return the cleaned (name, weekly_amount) or raise ValueError with a message for the user."""
        name = name.strip()
        if not name:
            raise ValueError("Please enter an expense name.")
        try:
            weekly_amount = float(str(weekly_amount).strip())
        except ValueError:
            raise ValueError("Weekly amount must be a number.")
        if not math.isfinite(weekly_amount):        # float() also accepts "nan" and "inf"
            raise ValueError("Weekly amount must be a number.")
        if weekly_amount < 0:
            raise ValueError("Weekly amount cannot be negative.")
        return name, weekly_amount

    def add_expense(self, name, weekly_amount):
        """Validate the input and add an expense. Returns the new dict."""
        return self.entity.add(*self.check_expense(name, weekly_amount))

    def update_expense(self, expense_id, name, weekly_amount):
        """Validate the input and overwrite the expense with this id.
        Raises ValueError if the input is invalid or the expense no longer exists.
        """
        if not self.entity.update(expense_id, *self.check_expense(name, weekly_amount)):
            raise ValueError("That expense no longer exists.")

    def remove_expenses(self, expense_ids):
        """Remove each expense whose id is in expense_ids.
        Raises ValueError if nothing was given to remove.
        """
        if not expense_ids:
            raise ValueError("Select an expense to remove.")
        for expense_id in expense_ids:
            self.entity.remove(expense_id)
