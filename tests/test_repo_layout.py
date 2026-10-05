from pathlib import Path
import unittest


class LayoutTests(unittest.TestCase):
    def test_required_files_exist(self):
        root = Path(__file__).resolve().parents[1]
        required = [
            root / "README.md",
            root / "pyproject.toml",
            root / ".gitignore",
            root / ".env.example",
            root / "config" / "upstreams.lock.json",
            root / "src" / "rupert" / "obsidian_bridge.py",
            root / "src" / "rupert" / "router.py",
            root / "docs" / "ARCHITECTURE.md",
            root / "docs" / "SECURITY.md",
        ]
        missing = [str(p) for p in required if not p.exists()]
        self.assertFalse(missing, f"Missing: {missing}")


if __name__ == "__main__":
    unittest.main()
