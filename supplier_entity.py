"""
File:        supplier_entity.py
Description: Entity class for suppliers. Holds the list of supplier dicts
             (each dict is one supplier: {"id": int, "name": str}) and reads/writes
             that list to a JSON file on disk. Contains no GUI or validation logic.
Authors:     [DR]
Date:        [2026-11-19]
"""

import json
import os

# Save next to this source file so the path is the same no matter where the program is launched from
DEFAULT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "suppliers.json")


class SupplierEntity:
    """List of supplier dicts, saveable to disk."""

    def __init__(self, filepath=DEFAULT_FILE):
        self.filepath = filepath
        self.suppliers = []   # list of dicts, one per supplier
        self.load()

    def load(self):
        """Read suppliers from disk. A missing file just means no suppliers yet."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                self.suppliers = json.load(f)
        except FileNotFoundError:
            self.suppliers = []

    def save(self):
        """Write the current list of suppliers to disk."""
        # Creates json file in same directory as program
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.suppliers, f, indent=4)

    def get_all(self):
        """Return a copy of the list so callers can't change it without going through this class."""
        return [dict(s) for s in self.suppliers]

    def add(self, name):
        """Create a supplier with the next sequential id, save, and return the new dict."""
        # Highest existing id + 1; an empty list starts at 1
        next_id = max((s["id"] for s in self.suppliers), default=0) + 1
        supplier = {"id": next_id, "name": name}
        self.suppliers.append(supplier)
        self.save()
        return dict(supplier)

    def remove(self, supplier_id):
        """Delete the supplier with this id, save, and return True if one was found."""
        before = len(self.suppliers)
        self.suppliers = [s for s in self.suppliers if s["id"] != supplier_id]
        removed = len(self.suppliers) < before
        if removed:
            self.save()
        return removed