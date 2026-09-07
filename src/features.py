"""Transparent, synopsis-level social-friction features."""

from __future__ import annotations

import re
from collections import Counter

import pandas as pd


RULE_TAXONOMY: dict[str, tuple[str, ...]] = {
    "Etiquette & manners": (
        "apology", "apologize", "birthday", "dinner", "etiquette", "funeral",
        "gift", "guest", "invitation", "invite", "manners", "party", "rude",
        "table", "thank", "tip", "tipping", "waiter", "wedding",
    ),
    "Truth & trust": (
        "accuse", "alibi", "betray", "deceive", "hide", "lie", "lying",
        "promise", "rumor", "secret", "suspect", "trust",
    ),
    "Space & access": (
        "airplane", "bathroom", "car", "club", "elevator", "golf", "hotel",
        "line", "office", "park", "parking", "restaurant", "seat", "store",
        "theater", "ticket",
    ),
    "Relationships & loyalty": (
        "affair", "boyfriend", "cheryl", "date", "dating", "divorce", "family",
        "friend", "girlfriend", "husband", "love", "marriage", "parents", "wife",
    ),
    "Identity & language": (
        "accent", "black", "christian", "culture", "disability", "gay",
        "handicap", "identity", "israel", "jewish", "language", "political",
        "race", "religion",
    ),
    "Money & exchange": (
        "bill", "business", "buy", "contract", "debt", "donation", "job", "loan",
        "money", "pay", "payment", "restaurant", "sell", "tip", "work",
    ),
    "Health & body": (
        "body", "death", "dentist", "doctor", "funeral", "health", "heart",
        "hospital", "illness", "injury", "kidney", "medical", "sick",
    ),
    "Reputation & status": (
        "celebrity", "credit", "embarrass", "famous", "hero", "honor", "insult",
        "offend", "reputation", "respect", "scandal", "status",
    ),
}

CONFLICT_TERMS = (
    "accuse", "angry", "argument", "awkward", "backfire", "clash", "conflict",
    "confront", "disaster", "feud", "fight", "insult", "misunderstanding",
    "offend", "refuse", "revenge", "tension", "threat", "trouble", "upset",
)

EMBARRASSMENT_TERMS = (
    "awkward", "backfire", "disaster", "embarrass", "humiliate", "misunderstanding",
)

CHARACTER_ALIASES: dict[str, tuple[str, ...]] = {
    "Larry": ("larry",),
    "Cheryl": ("cheryl",),
    "Jeff": ("jeff",),
    "Susie": ("susie",),
    "Leon": ("leon",),
    "Richard": ("richard", "lewis"),
    "Ted": ("ted", "danson"),
    "Marty": ("marty", "funkhouser"),
}


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z]+(?:'[a-z]+)?", str(text).lower())


def count_terms(text: str, terms: tuple[str, ...]) -> int:
    lowered = str(text).lower()
    return sum(len(re.findall(rf"\b{re.escape(term)}\w*\b", lowered)) for term in terms)


def score_summary(summary: str) -> dict[str, object]:
    """Create deterministic, interpretable features from an episode synopsis."""
    tokens = tokenize(summary)
    category_counts = {
        category: count_terms(summary, terms) for category, terms in RULE_TAXONOMY.items()
    }
    active_categories = [name for name, count in category_counts.items() if count > 0]
    primary_theme = max(category_counts, key=category_counts.get)
    if category_counts[primary_theme] == 0:
        primary_theme = "Other social friction"

    conflict_count = count_terms(summary, CONFLICT_TERMS)
    embarrassment_count = count_terms(summary, EMBARRASSMENT_TERMS)
    word_count = len(tokens)
    rate = 100 * conflict_count / word_count if word_count else 0.0
    # Descriptive heuristic, not a psychological measurement or model target.
    friction_score = min(
        100.0,
        8.0 * len(active_categories)
        + 7.0 * conflict_count
        + 5.0 * embarrassment_count
        + min(word_count, 100) * 0.12,
    )

    mentions = {}
    for character, aliases in CHARACTER_ALIASES.items():
        mentions[character] = int(any(count_terms(summary, (alias,)) > 0 for alias in aliases))

    result: dict[str, object] = {
        "summary_word_count": word_count,
        "rule_category_count": len(active_categories),
        "primary_rule_theme": primary_theme,
        "conflict_signal_count": conflict_count,
        "conflict_signals_per_100_words": round(rate, 3),
        "synopsis_friction_score": round(friction_score, 2),
        "character_count": sum(mentions.values()),
    }
    result.update({f"theme__{name}": value for name, value in category_counts.items()})
    result.update({f"character__{name}": value for name, value in mentions.items()})
    return result


def add_episode_features(episodes: pd.DataFrame) -> pd.DataFrame:
    features = pd.DataFrame([score_summary(summary) for summary in episodes["summary"]])
    return pd.concat([episodes.reset_index(drop=True), features], axis=1)


def taxonomy_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"category": category, "keywords": ", ".join(keywords)}
            for category, keywords in RULE_TAXONOMY.items()
        ]
    )


def character_edge_frame(features: pd.DataFrame) -> pd.DataFrame:
    """Count synopsis-level character co-mentions."""
    characters = list(CHARACTER_ALIASES)
    counter: Counter[tuple[str, str]] = Counter()
    for _, row in features.iterrows():
        present = [name for name in characters if row[f"character__{name}"] == 1]
        for index, source in enumerate(present):
            for target in present[index + 1 :]:
                counter[(source, target)] += 1
    return pd.DataFrame(
        [
            {"source": source, "target": target, "episode_count": count}
            for (source, target), count in counter.items()
        ]
    ).sort_values("episode_count", ascending=False, ignore_index=True)
