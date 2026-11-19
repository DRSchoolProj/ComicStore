"""
File:        main_menu_gui.py
Description: Main menu window for the inventory management application.
             Buttons lead to the Supplier Management, Item, Management, Order Management,
             Expense Management, and Report Generation screens. Buttons currently
             print a placeholder message, but will later open their own windows.
Authors:     [DR]
Date:        [2026-11-18]
"""

import tkinter as tk


# -Button handlers-
# Handler will open their respective window when clicked.
# Currently placeholders.

def ManageSupplierClicked():
    print("ManageSupplierClicked")


def ManageItemsClicked():
    print("ManageItemsClicked")


def ManageOrdersClicked():
    print("ManageOrdersClicked")


def ManageExpensesClicked():
    print("ManageExpensesClicked")


def GenerateReportClicked():
    print("GenerateReportClicked")


# -Main window setup-
root = tk.Tk()
root.title("Main Menu")
root.geometry("300x300")

# Pass handlers to command= WITHOUT parentheses, or else the function is called immediately at startup:
tk.Button(root, text="Manage Suppliers", width=20, command=ManageSupplierClicked).pack(pady=10)
tk.Button(root, text="Manage Items", width=20, command=ManageItemsClicked).pack(pady=10)
tk.Button(root, text="Manage Orders", width=20, command=ManageOrdersClicked).pack(pady=10)
tk.Button(root, text="Manage Expenses", width=20, command=ManageExpensesClicked).pack(pady=10)
tk.Button(root, text="Generate Report", width=20, command=GenerateReportClicked).pack(pady=10)

# Start event loop; Program stays open until this window is closed:
root.mainloop()