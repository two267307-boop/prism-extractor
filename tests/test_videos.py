import unittest

from scr.videos import normalize_channel_url


class NormalizeChannelUrlTests(unittest.TestCase):
    def test_handle(self):
        self.assertEqual(
            normalize_channel_url("@example"),
            "https://www.youtube.com/@example/videos",
        )

    def test_channel_url_with_suffix(self):
        self.assertEqual(
            normalize_channel_url("https://www.youtube.com/@example/shorts"),
            "https://www.youtube.com/@example/videos",
        )

    def test_video_url_is_rejected_as_channel(self):
        with self.assertRaises(ValueError):
            normalize_channel_url("https://example.com/@someone")


if __name__ == "__main__":
    unittest.main()
