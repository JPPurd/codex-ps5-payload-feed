import unittest

from update_payloads import build_catalog, latest_standalone_elf


class CatalogTests(unittest.TestCase):
    def test_ignores_newer_portal_only_release(self):
        releases = [
            {"tag_name": "portal-abcdef", "published_at": "2026-10-10T22:00:00Z", "assets": [
                {"name": "codex-portal.tar.gz", "browser_download_url": "https://example.invalid/portal"}
            ]},
            {"tag_name": "v0.0.4", "published_at": "2026-10-07T23:00:00Z", "assets": [
                {"name": "assistant-service.elf", "browser_download_url": "https://example.invalid/elf", "digest": "sha256:" + "a" * 64}
            ]},
        ]
        release, asset = latest_standalone_elf(releases)
        self.assertEqual(release["tag_name"], "v0.0.4")
        self.assertEqual(build_catalog(release, asset)["payloads"][0]["checksum"], "a" * 64)

    def test_finds_most_recent_standalone_elf(self):
        releases = [
            {"tag_name": "v0.0.4", "published_at": "2026-10-07T23:00:00Z", "assets": [
                {"name": "assistant-service.elf", "browser_download_url": "https://example.invalid/old"}
            ]},
            {"tag_name": "v0.0.5", "published_at": "2026-10-12T23:00:00Z", "assets": [
                {"name": "assistant-service.elf", "browser_download_url": "https://example.invalid/new"}
            ]},
        ]
        release, _ = latest_standalone_elf(releases)
        self.assertEqual(release["tag_name"], "v0.0.5")

    def test_refuses_to_remove_feed_when_no_elf_found(self):
        with self.assertRaises(RuntimeError):
            latest_standalone_elf([{"tag_name": "portal-x", "assets": []}])

    def test_missing_digest_is_allowed(self):
        catalog = build_catalog({"tag_name": "v1"}, {"browser_download_url": "https://example.invalid/service.elf"})
        self.assertNotIn("checksum", catalog["payloads"][0])
        self.assertEqual(catalog["payloads"][0]["filename"], "assistant-service.elf")


if __name__ == "__main__":
    unittest.main()
