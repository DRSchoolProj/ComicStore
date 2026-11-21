"""
File:        order_management_gui.py
Description: GUI class for order management. Responsible for window rendering
             logic, passing user input to OrderManagementControl, and displaying
             data received from OrderManagementControl.
Authors:     [Hamza]
Date:        [2026-11-20]
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from order_management_control import OrderManagementControl


class OrderManagementGUI:
    """Manage Orders window."""

    COLUMNS = ("order_id", "supplier_name", "order_date", "items_text", "total_cost", "status")

    def __init__(self, parent):
        """Create and display the window.
        parent: The main menu window. This window closes if the main menu (root) closes.
        """
        self.control = OrderManagementControl()     # The GUI never touches the data directly
        self.window = tk.Toplevel(parent)
        self.window.title("Manage Orders")
        self.window.geometry("900x420")

        buttons = tk.Frame(self.window)
        buttons.pack(pady=10)
        for text, command in (("Generate New Order", lambda: self.run(self.control.generate_orders)),
                              ("Modify Order", self.modify_order),
                              ("Approve Order", self.approve_order),
                              ("Mark as Received", lambda: self.run(self.control.receive_order, self.selected()))):
            tk.Button(buttons, text=text, width=18, command=command).pack(side="left", padx=3)

        self.table = ttk.Treeview(self.window, columns=self.COLUMNS, show="headings", height=10)
        for c in self.COLUMNS:
            self.table.heading(c, text=c.replace("_", " ").title())
            self.table.column(c, width=260 if c == "items_text" else 100)
        self.table.pack(padx=10, pady=5, fill="both", expand=True)

        bottom = tk.Frame(self.window)
        bottom.pack(fill="x", padx=10, pady=10)
        self.budget_label = tk.Label(bottom)
        self.budget_label.pack(side="left")
        tk.Button(bottom, text="Close", width=10, command=self.window.destroy).pack(side="right")

        self.refresh_table()

    def run(self, action, *args):
        """Run a control method, show its error message if there is one, then redraw the table."""
        try:
            action(*args)
        except ValueError as error:
            messagebox.showwarning("Cannot do that", str(error), parent=self.window)
        self.refresh_table()

    def selected(self):
        """The selected order's id (row iid = order id), or 0 if nothing is selected."""
        return int(self.table.selection()[0]) if self.table.selection() else 0

    def modify_order(self):
        order_id = self.selected()
        if not order_id:
            messagebox.showinfo("Nothing selected", "Select an order first.", parent=self.window)
            return
        sku = simpledialog.askstring("Modify Order", "SKU of the item to change:", parent=self.window)
        if sku is None:
            return
        quantity = simpledialog.askstring("Modify Order", "New quantity (0 removes the item):", parent=self.window)
        if quantity is None:
            return
        if not sku.strip().isdigit():
            messagebox.showwarning("Cannot do that", "SKU must be a whole number.", parent=self.window)
            return
        self.run(self.control.modify_order, order_id, int(sku), quantity)

    def approve_order(self):
        """Ask twice before approving: first whether the manager approved it, then to confirm."""
        order_id = self.selected()
        if not order_id:
            messagebox.showinfo("Nothing selected", "Select an order first.", parent=self.window)
            return
        if not messagebox.askyesno("Manager approval", "Has the store manager approved this order?",
                                   parent=self.window):
            return
        if not messagebox.askyesno("Confirm approval", f"Please confirm: approve order #{order_id}?\n"
                                   "This cannot be undone.", parent=self.window):
            return
        self.run(self.control.approve_order, order_id)

    def refresh_table(self):
        """Clear the table and redraw it from the control class's data."""
        self.table.delete(*self.table.get_children())
        for o in self.control.get_orders():
            self.table.insert("", tk.END, iid=str(o["order_id"]), values=[o[c] for c in self.COLUMNS])
        self.budget_label.config(text=f"Available Budget: ${self.control.display_available_budget():.2f}")
