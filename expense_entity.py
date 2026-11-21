"""
File:        expense_entity.py
Description: Entity class for operating expenses. Holds the list of expense dicts
             (each dict is one expense: {"id": int, "name": str, "weekly_amount": float})
             and reads/writes that list to expenses.json. Contains no GUI or validation logic.
Authors:     [Hamza]
Date:        [2026-11-20]
"""

import json
import os

# Save next to this source file so the path is the same no matter where the program is launched from
DEFAULT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.json")


class ExpenseEntity:
    """List of expense dicts, saveable to disk."""

    def __init__(self, filepath=DEFAULT_FILE):
        self.filepath = filepath
        self.expenses = []
        self.load()

    def load(self):
        """Read expenses from disk. A missing file just means no expenses yet."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                self.expenses = json.load(f)
        except FileNotFoundError:
            self.expenses = []

    def save(self):
        """Write the current list of expenses to disk."""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, indent=4)

    def get_all(self):
        """Return a copy of the list so callers can't change it without going through this class."""
        return [dict(e) for e in self.expenses]

    def add(self, name, weekly_amount):
        """Create an expense with the next sequential id, save, and return the new dict."""
        next_id = max((e["id"] for e in self.expenses), default=0) + 1
        expense = {"id": next_id, "name": name, "weekly_amount": weekly_amount}
        self.expenses.append(expense)
        self.save()
        return dict(expense)

    def update(self, expense_id, name, weekly_amount):
        """Overwrite the name and amount of one expense. Returns True if the id was found."""
        for expense in self.expenses:
            if expense["id"] == expense_id:
                expense.update(name=name, weekly_amount=weekly_amount)
                self.save()
                return True
        return False

    def remove(self, expense_id):
        """Delete the expense with this id, save, and return True if one was found."""
        before = len(self.expenses)
        self.expenses = [e for e in self.expenses if e["id"] != expense_id]
        removed = len(self.expenses) < before
        if removed:
            self.save()
        return removed
