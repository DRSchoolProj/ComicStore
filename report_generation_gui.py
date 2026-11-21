"""
File:        report_generation_gui.py
Description: GUI class for report generation. Responsible for window rendering
             logic, passing the chosen report type to ReportControl, and displaying
             the report text received from ReportControl.
Authors:     [Hamza]
Date:        [2026-11-20]
"""

import tkinter as tk
from tkinter import ttk, messagebox
from report_generation_control import ReportControl, REPORT_TYPES


class ReportGUI:
    """Reports window."""

    def __init__(self, parent):
        """Create and display the window.
        parent: The main menu window. This window closes if the main menu (root) closes.
        """
        self.control = ReportControl()      # The GUI never touches the data directly
        self.window = tk.Toplevel(parent)
        self.window.title("Reports")
        self.window.geometry("700x500")

        top = tk.Frame(self.window)
        top.pack(pady=10)
        tk.Label(top, text="Select Report Type:").pack(side="left", padx=5)
        self.type_box = ttk.Combobox(top, values=REPORT_TYPES, state="readonly", width=22)
        self.type_box.current(0)
        self.type_box.pack(side="left", padx=5)
        tk.Button(top, text="Generate Report", command=self.generate_report).pack(side="left", padx=5)

        # Fixed-width font keeps the report lines tidy; the box is read-only (see generate_report)
        self.output = tk.Text(self.window, width=80, height=18, font="TkFixedFont", state="disabled")
        self.output.pack(padx=10, pady=5, fill="both", expand=True)
        tk.Button(self.window, text="Close", width=10, command=self.window.destroy).pack(pady=10)

    def generate_report(self):
        """Ask the control class for the chosen report and show it, or show its error."""
        try:
            report = self.control.generate_report(self.type_box.get())
        except ValueError as error:
            messagebox.showwarning("Cannot generate report", str(error), parent=self.window)
            return
        self.output.config(state="normal")      # Text can only be changed while it is not disabled
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, report)
        self.output.config(state="disabled")
