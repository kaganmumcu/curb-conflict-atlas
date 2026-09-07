"""Aggregate reproducible headline results."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .features import CHARACTER_ALIASES


def rank_correlation(left: pd.Series, right: pd.Series) -> float:
    """Spearman correlation via average ranks, without an extra dependency."""
    return float(left.rank(method="average").corr(right.rank(method="average")))


def summarize(features: pd.DataFrame) -> dict:
    highest = features.loc[features["rating"].idxmax()]
    lowest = features.loc[features["rating"].idxmin()]
    theme_counts = features["primary_rule_theme"].value_counts()
    season_means = features.groupby("season")["rating"].mean()
    character_mentions = {
        name: int(features[f"character__{name}"].sum()) for name in CHARACTER_ALIASES
    }
    supporting_mentions = {
        name: count for name, count in character_mentions.items() if name != "Larry"
    }
    top_character = max(supporting_mentions, key=supporting_mentions.get)
    return {
        "episode_count": int(len(features)),
        "season_count": int(features["season"].nunique()),
        "date_start": str(features["airdate"].min()),
        "date_end": str(features["airdate"].max()),
        "mean_episode_rating": round(float(features["rating"].mean()), 3),
        "median_episode_rating": round(float(features["rating"].median()), 3),
        "highest_rated_episode": {
            "episode_code": highest["episode_code"],
            "title": highest["title"],
            "rating": float(highest["rating"]),
        },
        "lowest_rated_episode": {
            "episode_code": lowest["episode_code"],
            "title": lowest["title"],
            "rating": float(lowest["rating"]),
        },
        "top_primary_theme": str(theme_counts.index[0]),
        "top_primary_theme_episode_count": int(theme_counts.iloc[0]),
        "mean_synopsis_friction_score": round(
            float(features["synopsis_friction_score"].mean()), 3
        ),
        "friction_rating_spearman": round(
            rank_correlation(features["synopsis_friction_score"], features["rating"]), 3
        ),
        "highest_mean_rating_season": int(season_means.idxmax()),
        "highest_mean_rating_season_value": round(float(season_means.max()), 3),
        "character_mentions": character_mentions,
        "most_mentioned_supporting_character": top_character,
    }


def write_metrics(metrics: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
