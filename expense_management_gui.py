"""
File:        expense_management_gui.py
Description: GUI class for expense management. Responsible for window rendering
             logic, passing user input to ExpenseManagementControl, and displaying
             data received from ExpenseManagementControl.
Authors:     [Hamza]
Date:        [2026-11-20]
"""

import tkinter as tk
from tkinter import ttk, messagebox
from expense_management_control import ExpenseManagementControl


class ExpenseManagementGUI:
    """Operating Expenses window."""

    # (column key, heading text, column width)
    COLUMNS = (("id", "ID", 50), ("name", "Name", 250), ("weekly_amount", "Weekly Amount", 110))

    def __init__(self, parent):
        """Create and display the window.
        parent: The main menu window. This window closes if the main menu (root) closes.
        """
        self.control = ExpenseManagementControl()   # The GUI never touches the data directly
        self.window = tk.Toplevel(parent)
        self.window.title("Operating Expenses")
        self.window.geometry("500x440")

        self.table = ttk.Treeview(self.window, columns=[k for k, _, _ in self.COLUMNS],
                                  show="headings", height=8)
        for key, heading, width in self.COLUMNS:
            self.table.heading(key, text=heading)
            self.table.column(key, width=width)
        self.table.pack(padx=10, pady=10, fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", lambda event: self.fill_form())   # copy a clicked row into the form
        self.total_label = tk.Label(self.window)
        self.total_label.pack()

        form = tk.Frame(self.window)
        form.pack(pady=5)
        self.name_entry, self.amount_entry = tk.Entry(form, width=28), tk.Entry(form, width=12)
        for n, (text, entry) in enumerate((("Expense Name", self.name_entry), ("Weekly Amount", self.amount_entry))):
            tk.Label(form, text=text).grid(row=0, column=n)
            entry.grid(row=1, column=n, padx=5)
            entry.bind("<Return>", lambda event: self.add_expense())    # Enter key adds
        self.name_entry.focus()

        buttons = tk.Frame(self.window)
        buttons.pack(pady=10)
        for text, command in (("Add", self.add_expense), ("Update Selected", self.update_expense),
                              ("Remove Selected", self.remove_expense), ("Close", self.window.destroy)):
            tk.Button(buttons, text=text, width=14, command=command).pack(side="left", padx=3)
        self.refresh_table()

    def run(self, action, *args):
        """Run a control method and show its error message if there is one, then redraw the table.
        Returns True if it worked.
        """
        try:
            action(*args)
        except ValueError as error:
            messagebox.showwarning("Cannot do that", str(error), parent=self.window)
            return False
        finally:
            self.refresh_table()
        return True

    def selected(self):
        return [int(i) for i in self.table.selection()]     # each row's iid is its id

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)

    def fill_form(self):
        """When exactly one row is selected, copy it into the entry boxes for editing."""
        if len(self.selected()) != 1:
            return
        for e in self.control.get_expenses():
            if e["id"] == self.selected()[0]:
                self.clear_form()
                self.name_entry.insert(0, e["name"])
                self.amount_entry.insert(0, e["weekly_amount"])

    def add_expense(self):
        if self.run(self.control.add_expense, self.name_entry.get(), self.amount_entry.get()):
            self.clear_form()

    def update_expense(self):
        if len(self.selected()) != 1:
            messagebox.showinfo("Nothing selected", "Select one expense to update.", parent=self.window)
            return
        if self.run(self.control.update_expense, self.selected()[0], self.name_entry.get(), self.amount_entry.get()):
            self.clear_form()

    def remove_expense(self):
        if self.run(self.control.remove_expenses, self.selected()):
            self.clear_form()

    def refresh_table(self):
        """Clear the table and redraw it from the control class's data."""
        self.table.delete(*self.table.get_children())
        for e in self.control.get_expenses():
            self.table.insert("", tk.END, iid=str(e["id"]),
                              values=(e["id"], e["name"], f"${e['weekly_amount']:.2f}"))
        self.total_label.config(text=f"Total weekly expenses: ${self.control.total_weekly_expenses():.2f}")
