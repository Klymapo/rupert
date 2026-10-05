from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CloudLayoutTests(unittest.TestCase):
    def test_cloud_files_exist(self):
        required = [
            "web/index.html",
            "web/app.js",
            "web/styles.css",
            "web/manifest.webmanifest",
            "web/sw.js",
            "supabase/config.toml",
            "supabase/migrations/20261005_001_rupert_cloud_core.sql",
            "supabase/functions/rupert/index.ts",
            "supabase/functions/rupert-transcribe/index.ts",
            ".github/workflows/pages.yml",
            "docs/CLOUD.md",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_rls_is_required_for_private_tables(self):
        sql = (ROOT / "supabase/migrations/20261005_001_rupert_cloud_core.sql").read_text(encoding="utf-8").lower()
        for table in ("rupert_memory", "rupert_messages", "rupert_settings", "rupert_audit"):
            self.assertIn(f"alter table public.{table} enable row level security", sql)
        self.assertIn("auth.uid() = user_id", sql)
        self.assertIn("rupert-private", sql)

    def test_edge_functions_use_user_auth_not_service_role(self):
        for relative in ("supabase/functions/rupert/index.ts", "supabase/functions/rupert-transcribe/index.ts"):
            source = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("auth.getUser", source)
            self.assertNotIn("SUPABASE_SERVICE_ROLE_KEY", source)
            self.assertNotIn("service_role", source.lower())

    def test_public_web_never_contains_cloudflare_secret_names(self):
        web = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "web").glob("*.*") if p.is_file())
        self.assertNotIn("CF_API_TOKEN", web)
        self.assertNotIn("CF_ACCOUNT_ID", web)
        self.assertNotIn("SUPABASE_SERVICE_ROLE", web)

    def test_unknown_language_has_no_execution_channel(self):
        source = (ROOT / "supabase/functions/rupert/index.ts").read_text(encoding="utf-8")
        self.assertIn("Unknown language is reasoning only", source)
        self.assertIn("SOLO de razonamiento y texto", source)
        self.assertNotIn("eval(", source)
        self.assertNotIn("Deno.Command", source)


if __name__ == "__main__":
    unittest.main()
