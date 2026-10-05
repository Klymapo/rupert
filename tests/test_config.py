import os
import tempfile
import unittest
from pathlib import Path
from rupert.config import load_local_env


class ConfigTests(unittest.TestCase):
    def test_existing_env_wins(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ".env"
            p.write_text('X_TEST_ENV="from-file"\n', encoding="utf-8")
            os.environ["X_TEST_ENV"] = "from-process"
            load_local_env(p)
            self.assertEqual(os.environ["X_TEST_ENV"], "from-process")
            del os.environ["X_TEST_ENV"]


if __name__ == "__main__":
    unittest.main()
