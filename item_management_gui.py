"""
File:        item_management_gui.py
Description: GUI class for item management. Responsible for window rendering
             logic, passing user input to ItemManagementControl, and displaying
             data received from ItemManagementControl.
Authors:     [Hamza]
Date:        [2026-11-20]
"""

import tkinter as tk
from tkinter import ttk, messagebox
from item_management_control import ItemManagementControl


class ItemManagementGUI:
    """Manage Items window."""

    # (column key, heading text, column width)
    COLUMNS = (
        ("sku", "SKU", 50),
        ("name", "Name", 140),
        ("category", "Category", 100),
        ("quantity", "Qty", 60),
        ("supplier", "Supplier", 120),
        ("unit_cost", "Unit Cost", 70),         # Price we pay supplier
        ("price", "Price", 70),                 # Price customer pays us
        ("threshold", "Order Threshold", 100),  # The quantity below which item is added to newly generated orders
        ("sales_rate", "Sold/Day", 70),
    )

    def __init__(self, parent):
        """Create and display the window.
        parent: The main menu window. This window closes if the main menu (root) closes.
        """
        self.control = ItemManagementControl()   # The GUI never touches the data directly
        self.supplier_names = {}                 # supplier id -> name, refreshed from the control class

        self.window = tk.Toplevel(parent)
        self.window.title("Manage Items")
        self.window.geometry("900x520")

        # Table with headers. Rows with low stock get the "low" tag (see refresh_table)
        keys = [key for key, _, _ in self.COLUMNS]
        self.table = ttk.Treeview(self.window, columns=keys, show="headings", height=10)
        for key, heading, width in self.COLUMNS:
            self.table.heading(key, text=heading)
            self.table.column(key, width=width)
        self.table.tag_configure("low", background="#ffd6d6")
        self.table.pack(padx=10, pady=10, fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.load_selected)   # copy a clicked row into the form

        # Entry widgets for each field
        form = tk.Frame(self.window)
        form.pack(pady=5)
        self.entries = {}
        for col, (key, label) in enumerate((("name", "Name"), ("category", "Category"),
                                            ("quantity", "Quantity"), ("supplier", "Supplier"),
                                            ("unit_cost", "Unit Cost"), ("price", "Price"),
                                            ("threshold", "Order Threshold"))):
            tk.Label(form, text=label).grid(row=0, column=col, padx=3)
            if key == "supplier":
                widget = ttk.Combobox(form, width=14, state="readonly", postcommand=self.refresh_suppliers)
            else:
                widget = tk.Entry(form, width=13 if key == "threshold" else 10 if key != "name" else 16)
            widget.grid(row=1, column=col, padx=3)
            self.entries[key] = widget
        self.entries["name"].bind("<Return>", lambda event: self.add_item())
        self.entries["name"].focus()

        # Buttons
        buttons = tk.Frame(self.window)
        buttons.pack(pady=10)
        tk.Button(buttons, text="Add", width=12, command=self.add_item).grid(row=0, column=0, padx=5)
        tk.Button(buttons, text="Update Selected", width=15, command=self.update_item).grid(row=0, column=1, padx=5)
        tk.Button(buttons, text="Remove Selected", width=15, command=self.remove_item).grid(row=0, column=2, padx=5)
        tk.Button(buttons, text="Close", width=12, command=self.window.destroy).grid(row=0, column=3, padx=5)

        self.refresh_suppliers()
        self.refresh_table()

    # ---- button handlers ----

    def add_item(self):
        """Pass the form values to the control class and show any validation error."""
        try:
            self.control.add_item(*self.form_values())
        except ValueError as error:
            messagebox.showwarning("Cannot add item", str(error), parent=self.window)
            return
        self.clear_form()
        self.refresh_table()

    def update_item(self):
        """Overwrite the selected item with the values currently in the form."""
        selected = self.table.selection()
        if len(selected) != 1:
            messagebox.showinfo("Nothing selected", "Select one item to update.", parent=self.window)
            return
        try:
            self.control.update_item(int(selected[0]), *self.form_values())
        except ValueError as error:
            messagebox.showwarning("Cannot update item", str(error), parent=self.window)
            return
        self.clear_form()
        self.refresh_table()

    def remove_item(self):
        """Ask the control class to remove the selected rows."""
        # Each row's iid is its sku (set in refresh_table), so selection gives skus directly
        selected_skus = [int(iid) for iid in self.table.selection()]
        try:
            self.control.remove_items(selected_skus)
        except ValueError as error:
            messagebox.showinfo("Nothing selected", str(error), parent=self.window)
            return
        self.clear_form()
        self.refresh_table()

    # ---- helpers ----

    def form_values(self):
        """Return the form contents in the order the control class expects.
        The supplier dropdown shows "id - name"; only the id is passed on.
        """
        e = self.entries
        supplier_id = e["supplier"].get().split(" - ")[0]
        return (e["name"].get(), e["category"].get(), e["quantity"].get(), supplier_id,
                e["unit_cost"].get(), e["price"].get(), e["threshold"].get())

    def clear_form(self):
        for key, widget in self.entries.items():
            if key == "supplier":
                widget.set("")
            else:
                widget.delete(0, tk.END)

    def load_selected(self, event=None):
        """When exactly one row is selected, copy its values into the form for editing."""
        selected = self.table.selection()
        if len(selected) != 1:
            return
        item = next((i for i in self.control.get_items() if i["sku"] == int(selected[0])), None)
        if item is None:
            return
        self.clear_form()
        for key in ("name", "category", "quantity", "unit_cost", "price", "threshold"):
            self.entries[key].insert(0, item[key])
        self.entries["supplier"].set(self.supplier_label(item["supplier_id"]))

    def supplier_label(self, supplier_id):
        """Text shown for a supplier in the dropdown and table."""
        name = self.supplier_names.get(supplier_id)
        return f"{supplier_id} - {name}" if name else f"{supplier_id} - (missing)"

    def refresh_suppliers(self):
        """Reload the supplier dropdown, in case suppliers changed in the other window."""
        self.supplier_names = {s["id"]: s["name"] for s in self.control.get_suppliers()}
        self.entries["supplier"]["values"] = [self.supplier_label(i) for i in self.supplier_names]

    def refresh_table(self):
        """Clear the table and redraw it from the control class's data."""
        self.refresh_suppliers()
        self.table.delete(*self.table.get_children())
        for item in self.control.get_items():
            row = [item["sku"], item["name"], item["category"], item["quantity"],
                   self.supplier_names.get(item["supplier_id"], "(missing)"),
                   f"{item['unit_cost']:.2f}", f"{item['price']:.2f}",
                   item["threshold"], item["sales_rate"]]
            self.table.insert("", tk.END, iid=str(item["sku"]), values=row,
                              tags=("low",) if item["low_stock"] else ())
