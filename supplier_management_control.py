"""
File:        supplier_management_control.py
Description: Control class for supplier management. Sits between the GUI and
             SupplierEntity: validates user input, applies the business rules,
             and tells the entity what to add or remove.
Authors:     [DR]
Date:        [2026-11-19]
"""

from supplier_entity import SupplierEntity


class SupplierManagementControl:
    """Handles supplier management requests from the GUI."""

    def __init__(self, entity=None):
        # Accepting an entity lets tests pass in one that uses a temporary file
        self.entity = entity if entity is not None else SupplierEntity()

    def get_suppliers(self):
        """Return all suppliers as a list of dicts."""
        return self.entity.get_all()    # calls the entity's corresponding function on itself

    def add_supplier(self, name):
        """Validate the name and add a supplier. Returns the new dict.
        Raises ValueError with a user-readable message if the input is invalid.
        """
        name = name.strip()
        if not name:
            raise ValueError("Please enter a supplier name.")
        return self.entity.add(name)

    def remove_suppliers(self, supplier_ids):
        """Remove each supplier whose id is in supplier_ids.
        Raises ValueError if nothing was given to remove.
        """
        if not supplier_ids:
            raise ValueError("Select a supplier to remove.")
        for supplier_id in supplier_ids:
            self.entity.remove(supplier_id)