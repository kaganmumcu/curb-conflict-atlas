"""Run the complete Curb Conflict Atlas pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from .analysis import summarize, write_metrics
from .data import load_or_fetch_episode_data
from .features import add_episode_features, character_edge_frame, taxonomy_frame
from .visualize import build_all_charts


ROOT = Path(__file__).resolve().parents[1]


def run(refresh: bool = False) -> dict:
    data_dir = ROOT / "data"
    output_dir = ROOT / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    episodes, provenance = load_or_fetch_episode_data(data_dir, refresh=refresh)
    features = add_episode_features(episodes)
    edges = character_edge_frame(features)

    taxonomy_frame().to_csv(data_dir / "rule_taxonomy.csv", index=False)
    features.to_csv(output_dir / "episode_features.csv", index=False)
    edges.to_csv(output_dir / "character_edges.csv", index=False)
    metrics = summarize(features)
    metrics["source"] = provenance
    write_metrics(metrics, output_dir / "metrics.json")
    build_all_charts(features, edges, output_dir / "charts")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Refresh TVmaze source data")
    args = parser.parse_args()
    metrics = run(refresh=args.refresh)
    print(
        f"Built {metrics['episode_count']} episodes across "
        f"{metrics['season_count']} seasons."
    )


if __name__ == "__main__":
    main()
