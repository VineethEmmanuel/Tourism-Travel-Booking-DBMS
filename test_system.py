import unittest
import db
import sqlite3

class TestTourismDBMS(unittest.TestCase):
    def setUp(self):
        # Reset database to a pristine seed state before tests
        db.init_db(force_reset=True)

    def test_01_thirteen_core_entities_exist(self):
        """Verifies that all 13 tables specified in the ER schema exist in 3NF."""
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
        tables = [r[0] for r in cursor.fetchall()]
        conn.close()

        expected_tables = sorted([
            "Destination", "Package", "Itinerary_Day", "Guide", "Hotel",
            "Transport", "Departure", "Customer", "Booking", "Traveller",
            "Payment", "Cancellation", "Refund"
        ])
        self.assertEqual(sorted(tables), expected_tables, f"Mismatch in 13 core entities. Found: {tables}")

    def test_02_capacity_control_prevents_overbooking(self):
        """Verifies that total registered Travellers cannot exceed Departure Max_Capacity."""
        # Departure 6 is Swiss Alps with Max_Capacity = 6. Seed has 2 booked travellers.
        booked, max_cap, available = db.get_departure_occupancy(6)
        self.assertEqual(booked, 2)
        self.assertEqual(max_cap, 6)
        self.assertEqual(available, 4)

        # Attempt to book 5 travellers (2 + 5 = 7 > 6)
        party = [{"name": f"Guest {i}", "age": 25} for i in range(5)]
        success, msg, booking_id = db.create_booking_with_travellers(
            cust_id=1, depart_id=6, booking_date="2026-10-14", travellers_data=party
        )
        self.assertFalse(success)
        self.assertIn("Capacity limit exceeded", msg)
        self.assertIsNone(booking_id)

        # Now attempt to book exactly 4 travellers (2 + 4 = 6 <= 6) -> Should succeed
        valid_party = [{"name": f"Valid Guest {i}", "age": 28} for i in range(4)]
        success, msg, booking_id = db.create_booking_with_travellers(
            cust_id=1, depart_id=6, booking_date="2026-10-14", travellers_data=valid_party
        )
        self.assertTrue(success)
        self.assertIsNotNone(booking_id)

        # Now departure is full (available = 0)
        booked_after, _, available_after = db.get_departure_occupancy(6)
        self.assertEqual(booked_after, 6)
        self.assertEqual(available_after, 0)

        # Any further booking should be rejected
        fail_party = [{"name": "Extra Guest", "age": 30}]
        success, msg, _ = db.create_booking_with_travellers(
            cust_id=2, depart_id=6, booking_date="2026-10-14", travellers_data=fail_party
        )
        self.assertFalse(success)
        self.assertIn("Capacity limit exceeded", msg)

    def test_03_guide_conflict_prevention(self):
        """Verifies that a Guide cannot be double-booked for overlapping date ranges."""
        # Guide 1 (Jean-Luc) is booked on Departure 1: 2026-11-01 to 2026-11-05
        # Attempt to schedule Guide 1 from 2026-11-03 to 2026-11-07
        has_conflict, conflicts = db.check_guide_conflict(1, "2026-11-03", "2026-11-07")
        self.assertTrue(has_conflict)
        self.assertEqual(conflicts[0]["Depart_ID"], 1)

        # Attempting to schedule via db.schedule_departure should fail
        ok, msg = db.schedule_departure(
            package_id=1, guide_id=1, transport_id=1,
            start_date="2026-11-03", end_date="2026-11-07", max_capacity=10
        )
        self.assertFalse(ok)
        self.assertIn("Guide Conflict", msg)

        # Non-overlapping range (2026-11-08 to 2026-11-12) should have NO conflict
        has_conflict_free, _ = db.check_guide_conflict(1, "2026-11-08", "2026-11-12")
        self.assertFalse(has_conflict_free)

    def test_04_transport_conflict_prevention(self):
        """Verifies that a Transport asset cannot be double-booked for overlapping dates."""
        # Transport 3 (Sprinter Van) is assigned to Departure 1: 2026-11-01 to 2026-11-05
        has_conflict, conflicts = db.check_transport_conflict(3, "2026-10-31", "2026-11-02")
        self.assertTrue(has_conflict)
        self.assertEqual(conflicts[0]["Depart_ID"], 1)

        ok, msg = db.schedule_departure(
            package_id=2, guide_id=2, transport_id=3,
            start_date="2026-10-31", end_date="2026-11-02", max_capacity=10
        )
        self.assertFalse(ok)
        self.assertIn("Transport Conflict", msg)

    def test_05_transport_capacity_limit(self):
        """Verifies departure max capacity cannot exceed vehicle physical seating capacity."""
        # Transport 5 has capacity 6
        ok, msg = db.schedule_departure(
            package_id=6, guide_id=6, transport_id=5,
            start_date="2027-01-01", end_date="2027-01-07", max_capacity=12
        )
        self.assertFalse(ok)
        self.assertIn("exceeds vehicle", msg)

    def test_06_financial_integrity_refunds(self):
        """Verifies total Refund amounts cannot exceed corresponding Payment amounts."""
        # Booking 1 has total payment $2,900.00 and no prior refunds
        valid, paid, ref, max_ref, err = db.check_refund_integrity(1, 2900.00)
        self.assertTrue(valid)
        self.assertEqual(paid, 2900.0)
        self.assertEqual(ref, 0.0)
        self.assertEqual(max_ref, 2900.0)

        # Requesting $3,000 should violate financial integrity
        invalid, _, _, _, err_msg = db.check_refund_integrity(1, 3000.00)
        self.assertFalse(invalid)
        self.assertIn("Financial Integrity Violation", err_msg)

        # Booking 5 (cancelled in seed) has $1,450 paid and $1,200 already refunded
        valid5, paid5, ref5, max_ref5, err5 = db.check_refund_integrity(5, 250.00)
        self.assertTrue(valid5)
        self.assertEqual(max_ref5, 250.00)

        invalid5, _, _, _, err_msg5 = db.check_refund_integrity(5, 251.00)
        self.assertFalse(invalid5)

    def test_07_customer_booking_and_payment_flow(self):
        """Verifies full customer lifecycle: booking, payment, cancellation, and refund."""
        # 1. Book Departure 4 (Bali) for 2 travellers
        party = [{"name": "Alice Walker", "age": 31}, {"name": "Bob Walker", "age": 35}]
        ok, msg, b_id = db.create_booking_with_travellers(1, 4, "2026-10-15", party)
        self.assertTrue(ok)
        self.assertIsNotNone(b_id)

        # 2. Make payment
        pay_ok, pay_msg = db.record_payment(b_id, 2400.0, "2026-10-15")
        self.assertTrue(pay_ok)

        # 3. Cancel booking and request refund
        cancel_ok, cancel_msg = db.cancel_booking_and_request_refund(
            b_id, "2026-10-16", "Family commitment change", refund_amount=2000.0
        )
        self.assertTrue(cancel_ok)

        # 4. Seat should now be released (cancelled bookings do not occupy capacity)
        booked, max_c, avail = db.get_departure_occupancy(4)
        # Bali was booked with 2 in seed (James Wilson) + 2 from Alice Walker (now cancelled)
        self.assertEqual(booked, 2)

    def test_08_guide_portal_manifest(self):
        """Verifies tour guide receives conflict-free roster and correct passenger manifest."""
        roster = db.get_guide_roster(1)  # Jean-Luc Moreau
        self.assertGreater(len(roster), 0)
        dep1 = roster[0]
        self.assertEqual(dep1["Depart_ID"], 1)
        self.assertGreater(len(dep1["manifest"]), 0)
        self.assertGreater(len(dep1["itinerary"]), 0)

    def test_09_sql_console_execution(self):
        """Verifies raw SQL query execution works safely."""
        ok, cols, rows, msg = db.run_raw_sql("SELECT COUNT(*) as TableCount FROM sqlite_master WHERE type='table';")
        self.assertTrue(ok)
        self.assertEqual(cols, ["TableCount"])
        self.assertGreater(rows[0][0], 10)

if __name__ == "__main__":
    unittest.main()
