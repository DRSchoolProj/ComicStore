"""
File:        supplier_management_gui.py
Description: GUI class for supplier management. Responsible for window rendering
             logic, passing user input to SupplierManagementControl, and displaying
             data received from SupplierManagementControl.
             Currently placeholder data.
Authors:     [DR]
Date:        [2026-11-19]
"""

import tkinter as tk
from tkinter import ttk, messagebox   # ttk has Treeview table; messagebox shows warnings


class SupplierManagementGUI:
    """Manage Suppliers window."""

    FIELDS = ("id", "name")   # dict keys, used as columns in Table
    INPUT_FIELDS = ("name",)  # user-input field. id excluded because it's assigned automatically.
    # trailing  " , " required for proper and extendable field traversal logic

    def __init__(self, parent):
        """Create and display the window.
        parent: The main menu window. Supplier Management window closes if the main menu (root) closes.
        """
        self.window = tk.Toplevel(parent)   # Toplevel, not Tk(): only 1 root per program
        self.window.title("Manage Suppliers")
        self.window.geometry("400x400")

        self.suppliers = []   # list of dicts for demonstration. This will later come from the supplier entity control class
        self.next_id = 1      # id value, auto assigned to new suppliers. Only increases, removing a supplier does not change existing ids

        # Creates Table with Headers:
        self.table = ttk.Treeview(self.window, columns=self.FIELDS, show="headings", height=8)
        for field in self.FIELDS:
            self.table.heading(field, text=field.capitalize())
            self.table.column(field, width=50 if field == "id" else 250)
        self.table.pack(padx=10, pady=10, fill="both", expand=True)

        # Creates Entry widgets for each field:
        form = tk.Frame(self.window)
        form.pack(pady=5)
        self.entries = {}   # maps each field name to its Entry widget:
        for col, field in enumerate(self.INPUT_FIELDS):
            tk.Label(form, text=field.capitalize()).grid(row=0, column=col, padx=5)
            entry = tk.Entry(form, width=30)
            entry.grid(row=1, column=col, padx=5)
            self.entries[field] = entry

        # Buttons
        buttons = tk.Frame(self.window)
        buttons.pack(pady=10)
        tk.Button(buttons, text="Add", width=12, command=self.add_supplier).grid(row=0, column=0, padx=5)
        tk.Button(buttons, text="Remove Selected", width=15, command=self.remove_supplier).grid(row=0, column=1, padx=5)
        tk.Button(buttons, text="Close", width=12, command=self.window.destroy).grid(row=0, column=2, padx=5)

    def add_supplier(self):
        """Read entry fields, assign id, add new dict to the list, refresh table."""
        supplier = {field: self.entries[field].get().strip() for field in self.INPUT_FIELDS}
        if not supplier["name"]:   # if "name" is empty
            messagebox.showwarning("Missing name", "Enter a supplier name.", parent=self.window)
            return

        supplier["id"] = self.next_id   # assign id AFTER validation so failed adds don't waste one
        self.next_id += 1

        self.suppliers.append(supplier)       # add new supplier dict to list
        for entry in self.entries.values():   # clear the boxes for the next entry
            entry.delete(0, tk.END)
        self.refresh_table()

    def remove_supplier(self):
        """Remove the row(s) selected in the table from the list."""
        selected = self.table.selection()   # tuple of selected row IDs
        if not selected:
            messagebox.showinfo("Nothing selected", "Select a supplier to remove.", parent=self.window)
            return
        # Row positions in the table match positions in the list, so delete by index.
        # Delete from the highest index down so earlier deletions don't shift later ones.
        indexes = sorted((self.table.index(item) for item in selected), reverse=True)
        for i in indexes:
            del self.suppliers[i]
        self.refresh_table()

    def refresh_table(self):
        """Clear the table and redraw it from self.suppliers."""
        self.table.delete(*self.table.get_children())
        for supplier in self.suppliers:
            self.table.insert("", tk.END, values=[supplier[f] for f in self.FIELDS])