import unittest
import pandas as pd


def calculate_otif(quantity_ordered, quantity_shipped, promised_date, ship_date):
    on_time = ship_date <= promised_date
    in_full = quantity_shipped >= quantity_ordered
    return on_time and in_full


class TestOTIF(unittest.TestCase):

    def test_on_time_and_in_full_is_true(self):
        result = calculate_otif(100, 100, pd.Timestamp("2026-09-05"), pd.Timestamp("2026-09-05"))
        self.assertTrue(result)

    def test_late_shipment_fails_otif(self):
        result = calculate_otif(100, 100, pd.Timestamp("2026-09-05"), pd.Timestamp("2026-09-07"))
        self.assertFalse(result)

    def test_short_shipment_fails_otif(self):
        result = calculate_otif(100, 80, pd.Timestamp("2026-09-05"), pd.Timestamp("2026-09-05"))
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()