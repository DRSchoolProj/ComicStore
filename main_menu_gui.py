"""
File:        main_menu_gui.py
Description: Main menu window for the inventory management application.
             Buttons lead to the Supplier Management, Item, Management, Order Management,
             Expense Management, and Report Generation screens. 
Authors:     [Daphne, Hamza, Kassy, Sheetal]
Date:        [2026-11-18]
"""

import tkinter as tk    #Python's built-in GUI library

# Import GUI classes for each menu function, so they can be called by button handlers
from supplier_management_gui import SupplierManagementGUI
from item_management_gui import ItemManagementGUI
from order_management_gui import OrderManagementGUI
from expense_management_gui import ExpenseManagementGUI
from report_generation_gui import ReportGUI

# Button handlers:
# Handler will open their respective window when clicked.


def manage_supplier_clicked():
    SupplierManagementGUI(root)   # Creates and opens Supplier Management window as child of root


def manage_items_clicked():
    ItemManagementGUI(root)       # Creates and opens Item Management window as child of root


def manage_orders_clicked():
    OrderManagementGUI(root)      # Creates and opens Order Management window as child of root


def manage_expenses_clicked():
    ExpenseManagementGUI(root)    # Creates and opens Expense Management window as child of root


def generate_report_clicked():
    ReportGUI(root)               # Creates and opens Report Generation window as child of root


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