import unittest

from update_traffic import merge_daily


class MergeDailyTests(unittest.TestCase):
    def test_overlapping_dates_are_updated_not_accumulated(self):
        existing = [
            {
                "date": "2026-08-18",
                "views": 4,
                "unique_visitors": 3,
                "clones": 1,
                "unique_cloners": 1,
            }
        ]
        views = [
            {"timestamp": "2026-08-18T00:00:00Z", "count": 6, "uniques": 4},
            {"timestamp": "2026-08-19T00:00:00Z", "count": 2, "uniques": 1},
        ]
        clones = [
            {"timestamp": "2026-08-18T00:00:00Z", "count": 3, "uniques": 2}
        ]

        self.assertEqual(
            merge_daily(existing, views, clones),
            [
                {
                    "date": "2026-08-18",
                    "views": 6,
                    "unique_visitors": 4,
                    "clones": 3,
                    "unique_cloners": 2,
                },
                {"date": "2026-08-19", "views": 2, "unique_visitors": 1},
            ],
        )

    def test_dates_outside_current_window_are_preserved(self):
        old = [{"date": "2025-01-01", "views": 8, "unique_visitors": 5}]
        self.assertEqual(merge_daily(old, [], []), old)


if __name__ == "__main__":
    unittest.main()
