import unittest

import pandas as pd

from src.analysis import rank_correlation
from src.data import normalize_episodes, strip_html
from src.features import add_episode_features, character_edge_frame, score_summary


class DataTests(unittest.TestCase):
    def test_strip_html(self):
        self.assertEqual(strip_html("<p>Larry &amp; Jeff argue.</p>"), "Larry & Jeff argue.")

    def test_normalize_episode(self):
        payload = {
            "_embedded": {
                "episodes": [
                    {
                        "id": 1,
                        "season": 2,
                        "number": 3,
                        "name": "Test",
                        "airdate": "2001-01-01",
                        "runtime": 30,
                        "rating": {"average": 8.1},
                        "summary": "<p>Larry argues.</p>",
                        "url": "https://example.com",
                    }
                ]
            }
        }
        frame = normalize_episodes(payload)
        self.assertEqual(frame.loc[0, "episode_code"], "S02E03")
        self.assertEqual(frame.loc[0, "summary"], "Larry argues.")


class FeatureTests(unittest.TestCase):
    def test_score_is_deterministic_and_bounded(self):
        summary = "Larry lies about a dinner invitation and the argument backfires."
        first = score_summary(summary)
        second = score_summary(summary)
        self.assertEqual(first, second)
        self.assertGreater(first["rule_category_count"], 0)
        self.assertTrue(0 <= first["synopsis_friction_score"] <= 100)

    def test_edges_count_co_mentions(self):
        episodes = pd.DataFrame(
            {
                "summary": ["Larry and Jeff argue.", "Larry meets Cheryl.", "Jeff sees Cheryl."],
            }
        )
        features = add_episode_features(episodes)
        edges = character_edge_frame(features)
        pairs = {(row.source, row.target): row.episode_count for row in edges.itertuples()}
        self.assertEqual(pairs[("Larry", "Jeff")], 1)

    def test_rank_correlation(self):
        left = pd.Series([1, 2, 3, 4])
        right = pd.Series([10, 20, 30, 40])
        self.assertAlmostEqual(rank_correlation(left, right), 1.0)


if __name__ == "__main__":
    unittest.main()

