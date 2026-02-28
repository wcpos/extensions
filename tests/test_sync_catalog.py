import unittest

from scripts.sync_catalog import apply_release, normalize_version, parse_github_repo, select_download_url


class ParseGithubRepoTests(unittest.TestCase):
    def test_parses_https_github_repo_url(self):
        self.assertEqual(
            parse_github_repo("https://github.com/wcpos/sumup-terminal-for-woocommerce"),
            ("wcpos", "sumup-terminal-for-woocommerce"),
        )


class NormalizeVersionTests(unittest.TestCase):
    def test_strips_leading_v(self):
        self.assertEqual(normalize_version("v1.2.3"), "1.2.3")


class SelectDownloadUrlTests(unittest.TestCase):
    def test_prefers_slug_zip_asset(self):
        release = {
            "assets": [
                {"name": "other.zip", "browser_download_url": "https://example.com/other.zip"},
                {
                    "name": "sumup-terminal-for-woocommerce.zip",
                    "browser_download_url": "https://example.com/sumup-terminal-for-woocommerce.zip",
                },
            ]
        }

        self.assertEqual(
            select_download_url(release, "sumup-terminal-for-woocommerce", "https://existing.example/old.zip"),
            "https://example.com/sumup-terminal-for-woocommerce.zip",
        )


class ApplyReleaseTests(unittest.TestCase):
    def test_updates_catalog_fields_from_release(self):
        entry = {
            "slug": "sumup-terminal-for-woocommerce",
            "version": "0.0.5",
            "latest_version": "0.0.5",
            "download_url": "https://example.com/old.zip",
            "released_at": "2025-01-01T00:00:00Z",
        }
        release = {
            "tag_name": "v0.0.6",
            "published_at": "2026-02-18T20:00:00Z",
            "assets": [
                {
                    "name": "sumup-terminal-for-woocommerce.zip",
                    "browser_download_url": "https://example.com/new.zip",
                }
            ],
        }

        updated, changed = apply_release(entry, release)

        self.assertTrue(changed)
        self.assertEqual(updated["version"], "0.0.6")
        self.assertEqual(updated["latest_version"], "0.0.6")
        self.assertEqual(updated["download_url"], "https://example.com/new.zip")
        self.assertEqual(updated["released_at"], "2026-02-18T20:00:00Z")


if __name__ == "__main__":
    unittest.main()
