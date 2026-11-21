"""
File:        main_menu_gui.py
Description: Main menu window for the inventory management application.
             Buttons lead to the Supplier Management, Item, Management, Order Management,
             Expense Management, and Report Generation screens. Buttons currently
             print a placeholder message, but will later open their own windows.
Authors:     [DR]
Date:        [2026-11-18]
"""

import tkinter as tk    #Python's built-in GUI library

# Import GUI classes for each menu function, so they can be called by button handlers
from supplier_management_gui import SupplierManagementGUI

# Button handlers:
# Handler will open their respective window when clicked.
# Some are currently placeholders.

def manage_supplier_clicked():
    SupplierManagementGUI(root)   # Creates and opens Supplier Management window as child of root


def manage_items_clicked():
    print("manage_items_clicked")


def manage_orders_clicked():
    print("manage_orders_clicked")


def manage_expenses_clicked():
    print("manage_expenses_clicked")


def generate_report_clicked():
    print("generate_report_clicked")


# Main window setup
root = tk.Tk()             # There can only be ONE root/Tk() per program
root.title("Main Menu")
root.geometry("300x300")

# Pass handlers to command= WITHOUT parentheses, or else the function is called immediately at startup:
tk.Button(root, text="Manage Suppliers", width=20, command=manage_supplier_clicked).pack(pady=10)
tk.Button(root, text="Manage Items", width=20, command=manage_items_clicked).pack(pady=10)
tk.Button(root, text="Manage Orders", width=20, command=manage_orders_clicked).pack(pady=10)
tk.Button(root, text="Manage Expenses", width=20, command=manage_expenses_clicked).pack(pady=10)
tk.Button(root, text="Generate Report", width=20, command=generate_report_clicked).pack(pady=10)

# Start event loop. Program stays open until this window is closed:
root.mainloop()