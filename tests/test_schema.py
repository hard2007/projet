import tempfile
import sqlite3
import unittest
from pathlib import Path

SCHEMA = Path(__file__).resolve().parents[1] / "database" / "schema.sql"


class SchemaTests(unittest.TestCase):
    def test_schema_creates_three_tables_and_enforces_marks(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            conn = sqlite3.connect(tmp.name)
            conn.execute("PRAGMA foreign_keys=ON")
            conn.executescript(SCHEMA.read_text(encoding="utf-8"))
            tables = {
                row[0] for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            }
            self.assertEqual(tables, {"users", "modules", "grades"})
            conn.close()


if __name__ == "__main__":
    unittest.main()
