import tempfile
import unittest
from pathlib import Path

from orka.core.storage import SQLiteStorage


class SQLiteStorageTests(unittest.TestCase):
    def test_storage_persists_runs_and_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = SQLiteStorage(str(Path(temp_dir) / "storage.db"))
            storage.reset()

            storage.save_run("run-1", {"run_id": "run-1", "timestamp": "2026-01-01T00:00:00+00:00"})
            storage.create_customer(
                {"id": "cust_1", "name": "Alice", "city": "Pune", "status": "created"},
                created_at="2026-01-01T00:00:00+00:00",
            )
            storage.create_email(
                {"to": "alice@example.com", "message": "hi", "status": "sent"},
                created_at="2026-01-01T00:00:01+00:00",
            )

            self.assertEqual(storage.get_run("run-1")["run_id"], "run-1")
            self.assertEqual(len(storage.list_runs()), 1)
            self.assertEqual(len(storage.list_customers()), 1)
            self.assertEqual(len(storage.list_emails()), 1)


if __name__ == "__main__":
    unittest.main()
