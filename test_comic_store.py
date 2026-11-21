"""
File:        test_comic_store.py
Description: Automated tests for the ComicStore project (unittest, standard library only).
             Every test copies the JSON files in tests/test_data into a temporary folder and
             builds the entity/control classes on those copies, so real data is never touched.
             Run from the project root:  python -m unittest tests.test_comic_store -v
Authors:     [Daphne]
Date:        [2026-11-20]
"""

import os
import shutil
import sys
import tempfile
import unittest

# Make the project's modules importable no matter where the tests are launched from
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from expense_entity import ExpenseEntity
from expense_management_control import ExpenseManagementControl
from item_entity import ItemEntity
from item_management_control import ItemManagementControl
from order_entity import OrderEntity
from order_management_control import OrderManagementControl
from report_generation_control import ReportControl
from supplier_entity import SupplierEntity
from supplier_management_control import SupplierManagementControl

TEST_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data")


class ComicStoreTestCase(unittest.TestCase):
    """Builds the full entity/control stack on temporary copies of the test JSON files."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        for name in ("items", "suppliers", "expenses", "orders"):
            shutil.copy(os.path.join(TEST_DATA, name + ".json"), self.tmp)
        path = lambda name: os.path.join(self.tmp, name + ".json")

        self.suppliers = SupplierManagementControl(SupplierEntity(path("suppliers")))
        self.expenses = ExpenseManagementControl(ExpenseEntity(path("expenses")))
        self.items = ItemManagementControl(ItemEntity(path("items")), self.suppliers)
        self.order_entity = OrderEntity(path("orders"))
        self.orders = OrderManagementControl(self.order_entity, self.items, self.suppliers, self.expenses)


class TestItemInputValidation(ComicStoreTestCase):
    """TEST 1 - Unit test, black-box (equivalence classes + boundary values)."""

    def test_add_item_validation(self):
        # Valid class: whitespace is trimmed, blank threshold defaults to 0, next sku is 5
        item = self.items.add_item("  Spider-Man #1 ", "comic", "5", "1", "3.50", "9.99", "")
        self.assertEqual((item["name"], item["sku"], item["threshold"]), ("Spider-Man #1", 5, 0))

        # Boundary: 0 is the lowest legal quantity, so it is accepted
        self.items.add_item("Free Sticker", "misc", "0", "2", "0", "0", "0")

        # Invalid classes: each must raise ValueError and must not add anything
        count = len(self.items.get_items())
        bad_inputs = {
            "blank name":         ("", "comic", "5", "1", "1", "2", "0"),
            "negative quantity":  ("X", "comic", "-1", "1", "1", "2", "0"),   # just below boundary
            "non-numeric cost":   ("X", "comic", "5", "1", "abc", "2", "0"),
            "decimal quantity":   ("X", "comic", "2.5", "1", "1", "2", "0"),
            "unknown supplier":   ("X", "comic", "5", "99", "1", "2", "0"),
            "no supplier chosen": ("X", "comic", "5", "", "1", "2", "0"),
        }
        for label, args in bad_inputs.items():
            with self.subTest(label):
                with self.assertRaises(ValueError):
                    self.items.add_item(*args)
        self.assertEqual(len(self.items.get_items()), count)


class TestOrderGenerationAndBudget(ComicStoreTestCase):
    """TEST 2 - Integration test (item + supplier + expense + order + budget), glass-box branches."""

    def test_generate_orders_restock_rules_and_funds(self):
        # Income 98+105+700 = 903, expenses 250, no approved orders -> 653 available
        self.assertEqual(self.orders.display_available_budget(), 653.0)

        new_orders = self.orders.generate_orders()
        lines = {l["sku"]: l["quantity"] for o in new_orders for l in o["line_items"]}

        # sku 1: quantity 2 <= threshold 5                       -> low-stock branch, 26 ordered
        # sku 3: quantity 20 > threshold 10, but 20 - 10*7 < 10  -> projected-sales branch, 120 ordered
        # sku 4: quantity 20 == threshold 20 (boundary)          -> reordered, 20 ordered
        # sku 2: quantity 40, projected 33 >= threshold 8        -> NOT reordered
        self.assertEqual(lines, {1: 26, 3: 120, 4: 20})

        # One order per supplier, ids continue after the existing order 1, all start as "Generated"
        self.assertEqual({o["supplier_id"]: o["total_cost"] for o in new_orders}, {1: 292.0, 2: 40.0})
        self.assertEqual([o["order_id"] for o in new_orders], [2, 3])
        self.assertTrue(all(o["status"] == "Generated" for o in new_orders))

        # Running it again must not re-order items that are already on an unreceived order
        with self.assertRaises(ValueError):
            self.orders.generate_orders()


class TestOrderLifecycleAndReport(ComicStoreTestCase):
    """TEST 3 - Product (system-level) test of the whole workflow, functional testing."""

    def test_generate_modify_approve_receive_and_report(self):
        order = next(o for o in self.orders.generate_orders() if o["supplier_id"] == 1)   # order id 2

        # Modify: Batman 26 -> 30 recalculates the total (30*2 + 120*2 = 300); bad input is refused
        self.orders.modify_order(order["order_id"], 1, "30")
        self.assertEqual(self.order_entity.get(order["order_id"])["total_cost"], 300.0)
        with self.assertRaises(ValueError):
            self.orders.modify_order(order["order_id"], 1, "abc")

        # Approve: status changes and the order's cost is held against the budget (653 - 300)
        self.orders.approve_order(order["order_id"])
        self.assertEqual(self.orders.display_available_budget(), 353.0)
        with self.assertRaises(ValueError):        # approved orders cannot be approved or modified again
            self.orders.approve_order(order["order_id"])
        with self.assertRaises(ValueError):
            self.orders.modify_order(order["order_id"], 1, "5")

        # Receive: stock goes up (Batman 2 + 30), status becomes Received, budget hold is released
        self.orders.receive_order(order["order_id"])
        self.assertEqual(self.items.entity.get(1)["quantity"], 32)
        self.assertEqual(self.order_entity.get(order["order_id"])["status"], "Received")
        self.assertEqual(self.orders.display_available_budget(), 653.0)
        with self.assertRaises(ValueError):        # cannot be received twice
            self.orders.receive_order(order["order_id"])

        # Reports read the same data: the budget summary matches and Batman is no longer LOW
        reports = ReportControl(self.items, self.expenses, self.order_entity)
        self.assertIn("Funds available: $653.00", reports.generate_report("Budget Summary"))
        batman_line = next(l for l in reports.generate_report("Current Inventory").splitlines()
                           if "Batman" in l)
        self.assertNotIn("LOW", batman_line)
        with self.assertRaises(ValueError):
            reports.generate_report("")


if __name__ == "__main__":
    unittest.main()
