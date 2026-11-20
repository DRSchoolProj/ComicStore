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
from supplier_management_control import SupplierManagementControl   #

class SupplierManagementGUI:
    """Manage Suppliers window."""

    FIELDS = ("id", "name")   # table columns, matching the keys in each supplier dict

    def __init__(self, parent):
        """Create and display the window.
        parent: The main menu window. Supplier Management window closes if the main menu (root) closes.
        """
        self.control = SupplierManagementControl()   # To be implemented. The GUI never touches the data directly

        self.window = tk.Toplevel(parent)   # Toplevel, not Tk(): only 1 root per program
        self.window.title("Manage Suppliers")
        self.window.geometry("500x400")

        # Creates Table with Headers:
        self.table = ttk.Treeview(self.window, columns=self.FIELDS, show="headings", height=8)
        for field in self.FIELDS:
            self.table.heading(field, text=field.upper() if field == "id" else field.capitalize())
            self.table.column(field, width=50 if field == "id" else 250)
        self.table.pack(padx=10, pady=10, fill="both", expand=True)

        # Creates Entry widgets for each field:
        form = tk.Frame(self.window)
        form.pack(pady=5)
        tk.Label(form, text="Name").grid(row=0, column=0, padx=5)
        self.name_entry = tk.Entry(form, width=30)
        self.name_entry.grid(row=1, column=0, padx=5)
        self.name_entry.bind("<Return>", lambda event: self.add_supplier())   # Enter key adds
        self.name_entry.focus()

        # Buttons
        buttons = tk.Frame(self.window)
        buttons.pack(pady=10)
        tk.Button(buttons, text="Add", width=12, command=self.add_supplier).grid(row=0, column=0, padx=5)
        tk.Button(buttons, text="Remove Selected", width=15, command=self.remove_supplier).grid(row=0, column=1, padx=5)
        tk.Button(buttons, text="Close", width=12, command=self.window.destroy).grid(row=0, column=2, padx=5)

        self.refresh_table()   # show any suppliers already saved on disk

    def add_supplier(self):
        """Pass the typed name to the control class and show any validation error."""
        try:
            self.control.add_supplier(self.name_entry.get())
        except ValueError as error:
            messagebox.showwarning("Cannot add supplier", str(error), parent=self.window)
            return
        self.name_entry.delete(0, tk.END)
        self.refresh_table()

    def remove_supplier(self):
        """Ask the control class to remove the selected rows."""
        # Each row's iid is its supplier id (set in refresh_table), so selection gives ids directly
        selected_ids = [int(iid) for iid in self.table.selection()]
        try:
            self.control.remove_suppliers(selected_ids)
        except ValueError as error:
            messagebox.showinfo("Nothing selected", str(error), parent=self.window)
            return
        self.refresh_table()

    def refresh_table(self):
        """Clear the table and redraw it from the control class's data."""
        self.table.delete(*self.table.get_children())
        for supplier in self.control.get_suppliers():
            self.table.insert("", tk.END, iid=str(supplier["id"]),
                              values=[supplier[f] for f in self.FIELDS])