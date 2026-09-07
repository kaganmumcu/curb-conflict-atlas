"""Static charts for the notebook and README."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


INK = "#20242A"
BLUE = "#35618D"
GOLD = "#D3A83B"
ORANGE = "#D8753B"
LIGHT_BLUE = "#D9E5F0"
GRID = "#D9DDE2"


def _style_axis(ax: plt.Axes) -> None:
    ax.set_facecolor("white")
    ax.grid(axis="y", color=GRID, linewidth=0.8, alpha=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#AEB5BD")
    ax.tick_params(colors=INK, labelsize=9)


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_season_ratings(features: pd.DataFrame, path: Path) -> None:
    season_stats = features.groupby("season")["rating"].agg(["mean", "min", "max"])
    fig, ax = plt.subplots(figsize=(10, 5.5))
    rng = np.random.default_rng(42)
    for season, group in features.groupby("season"):
        x = np.full(len(group), season) + rng.normal(0, 0.055, len(group))
        ax.scatter(x, group["rating"], s=24, color=LIGHT_BLUE, edgecolor=BLUE, linewidth=0.5)
    ax.plot(season_stats.index, season_stats["mean"], color=BLUE, linewidth=2.2, marker="o")
    best_season = int(season_stats["mean"].idxmax())
    best_value = season_stats.loc[best_season, "mean"]
    ax.annotate(
        f"Highest season mean: S{best_season} ({best_value:.2f})",
        (best_season, best_value),
        xytext=(12, 20),
        textcoords="offset points",
        color=INK,
        arrowprops={"arrowstyle": "-", "color": INK},
    )
    ax.set_title("Episode ratings by season", loc="left", fontsize=16, weight="bold", color=INK, pad=32)
    ax.text(0, 1.01, "Dots are episodes; line shows the season mean · 120 episodes", transform=ax.transAxes, fontsize=10, color="#59616A")
    ax.set_xlabel("Season", color=INK)
    ax.set_ylabel("TVmaze user rating (0–10)", color=INK)
    ax.set_xticks(range(1, 13))
    ax.set_ylim(5.5, 9.3)
    _style_axis(ax)
    _save(fig, path)


def plot_theme_distribution(features: pd.DataFrame, path: Path) -> None:
    counts = features["primary_rule_theme"].value_counts().sort_values()
    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.barh(counts.index, counts.values, color=BLUE, edgecolor="#244869")
    ax.bar_label(bars, padding=4, fontsize=9, color=INK)
    ax.set_title("Primary social-rule theme in episode synopses", loc="left", fontsize=16, weight="bold", color=INK, pad=32)
    ax.text(0, 1.01, "Deterministic keyword taxonomy · one primary theme per episode", transform=ax.transAxes, fontsize=10, color="#59616A")
    ax.set_xlabel("Episode count", color=INK)
    ax.set_ylabel("")
    ax.set_xlim(0, counts.max() * 1.16)
    _style_axis(ax)
    ax.grid(axis="x", color=GRID, linewidth=0.8, alpha=0.8)
    ax.grid(axis="y", visible=False)
    _save(fig, path)


def plot_friction_vs_rating(features: pd.DataFrame, path: Path) -> None:
    x = features["synopsis_friction_score"].to_numpy(dtype=float)
    y = features["rating"].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    line_x = np.linspace(x.min(), x.max(), 100)
    fig, ax = plt.subplots(figsize=(9, 5.8))
    ax.scatter(x, y, s=42, color=LIGHT_BLUE, edgecolor=BLUE, linewidth=0.7, alpha=0.9)
    ax.plot(line_x, intercept + slope * line_x, color=ORANGE, linewidth=2)
    for _, row in features.nlargest(4, "synopsis_friction_score").iterrows():
        ax.annotate(row["episode_code"], (row["synopsis_friction_score"], row["rating"]), xytext=(5, 5), textcoords="offset points", fontsize=8, color=INK)
    ax.set_title("Synopsis friction score and episode rating", loc="left", fontsize=16, weight="bold", color=INK, pad=32)
    ax.text(0, 1.01, "Heuristic score from synopsis language; association is descriptive, not causal", transform=ax.transAxes, fontsize=10, color="#59616A")
    ax.set_xlabel("Synopsis friction score (0–100)", color=INK)
    ax.set_ylabel("TVmaze user rating (0–10)", color=INK)
    _style_axis(ax)
    ax.grid(axis="both", color=GRID, linewidth=0.8, alpha=0.8)
    _save(fig, path)


def plot_character_network(edges: pd.DataFrame, features: pd.DataFrame, path: Path) -> None:
    graph = nx.Graph()
    for _, row in edges.iterrows():
        graph.add_edge(row["source"], row["target"], weight=int(row["episode_count"]))
    mentions = {
        column.removeprefix("character__"): int(features[column].sum())
        for column in features.columns
        if column.startswith("character__")
    }
    graph.add_nodes_from(mentions)
    positions = nx.spring_layout(graph, seed=42, weight="weight", k=1.2)
    weights = [graph[u][v]["weight"] for u, v in graph.edges]
    max_weight = max(weights) if weights else 1
    widths = [0.8 + 5.2 * weight / max_weight for weight in weights]
    node_sizes = [500 + 45 * mentions.get(node, 0) for node in graph.nodes]

    fig, ax = plt.subplots(figsize=(9, 6.4))
    nx.draw_networkx_edges(graph, positions, width=widths, edge_color="#AEB5BD", alpha=0.8, ax=ax)
    nx.draw_networkx_nodes(graph, positions, node_size=node_sizes, node_color=GOLD, edgecolors=INK, linewidths=1, ax=ax)
    nx.draw_networkx_labels(graph, positions, font_size=10, font_color=INK, ax=ax)
    ax.set_title("Character co-mentions in episode synopses", loc="left", fontsize=16, weight="bold", color=INK, pad=32)
    ax.text(0, 1.01, "Node size = synopsis mentions; edge width = episodes mentioning both characters", transform=ax.transAxes, fontsize=10, color="#59616A")
    ax.axis("off")
    _save(fig, path)


def build_all_charts(features: pd.DataFrame, edges: pd.DataFrame, chart_dir: Path) -> None:
    plot_season_ratings(features, chart_dir / "season_ratings.png")
    plot_theme_distribution(features, chart_dir / "rule_theme_distribution.png")
    plot_friction_vs_rating(features, chart_dir / "friction_vs_rating.png")
    plot_character_network(edges, features, chart_dir / "character_network.png")
