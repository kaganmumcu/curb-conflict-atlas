"""Build the reader-facing notebook from validated project outputs."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
METRICS = json.loads((ROOT / "outputs" / "metrics.json").read_text(encoding="utf-8"))


def markdown(text: str):
    return nbf.v4.new_markdown_cell(textwrap.dedent(text).strip())


def code(text: str):
    return nbf.v4.new_code_cell(textwrap.dedent(text).strip())


def build() -> Path:
    highest = METRICS["highest_rated_episode"]
    rho = METRICS["friction_rating_spearman"]
    notebook = nbf.v4.new_notebook()
    notebook["metadata"] = {
        "kernelspec": {
            "display_name": "Curb Conflict Atlas",
            "language": "python",
            "name": "curb-atlas",
        },
        "language_info": {"name": "python", "version": "3"},
    }
    notebook["cells"] = [
        markdown(
            f"""
            # Curb Conflict Atlas

            ## tl;dr

            This first release analyzes **{METRICS['episode_count']} episodes across {METRICS['season_count']} seasons** using public TVmaze metadata and short synopses.

            - **Season {METRICS['highest_mean_rating_season']}** has the highest mean episode rating ({METRICS['highest_mean_rating_season_value']:.2f}).
            - **{highest['title']} ({highest['episode_code']})** is the highest-rated episode in the snapshot ({highest['rating']:.1f}).
            - **{METRICS['top_primary_theme']}** is the most common primary synopsis theme ({METRICS['top_primary_theme_episode_count']} episodes).
            - The synopsis friction score has only a **weak rank correlation with rating** (Spearman ρ = {rho:.2f}). More friction language does not, by itself, identify a better-rated episode.

            The taxonomy and friction score are transparent heuristics for synopsis wording. They are not scene-level ground truth.
            """
        ),
        markdown(
            """
            ## Context & Methods

            The project asks: *How does ordinary social friction appear in Curb episode descriptions, and is that wording associated with audience ratings?*

            ### Key assumptions

            1. TVmaze episode synopses are sufficient for a lightweight first-pass taxonomy, but not for claims about full scripts or scene structure.
            2. TVmaze ratings are observational and mutable; no causal interpretation is appropriate.
            3. The keyword taxonomy is intentionally inspectable. Every category and trigger term is saved in `data/rule_taxonomy.csv`.
            4. Full transcripts are excluded from the repository to avoid redistributing copyrighted text.
            """
        ),
        code(
            """
            from pathlib import Path
            import json
            import pandas as pd
            from IPython.display import Image, display

            ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
            features = pd.read_csv(ROOT / "outputs" / "episode_features.csv")
            edges = pd.read_csv(ROOT / "outputs" / "character_edges.csv")
            taxonomy = pd.read_csv(ROOT / "data" / "rule_taxonomy.csv")
            metrics = json.loads((ROOT / "outputs" / "metrics.json").read_text())

            pd.set_option("display.max_colwidth", 80)
            """
        ),
        markdown("## Data\n\nOne row represents one regular episode. The source snapshot and retrieval timestamp are preserved in `data/` and each episode retains its TVmaze URL."),
        code(
            """
            quality_summary = pd.Series({
                "rows": len(features),
                "unique_episode_ids": features["episode_id"].nunique(),
                "seasons": features["season"].nunique(),
                "missing_summaries": features["summary"].isna().sum() + features["summary"].eq("").sum(),
                "missing_ratings": features["rating"].isna().sum(),
                "duplicate_season_episode_keys": features.duplicated(["season", "episode"]).sum(),
            })
            quality_summary.to_frame("value")
            """
        ),
        code(
            """
            features[[
                "episode_code", "title", "airdate", "rating", "primary_rule_theme",
                "synopsis_friction_score", "summary"
            ]].head(5)
            """
        ),
        markdown("## Results\n\n### 1. Ratings across the series"),
        code("display(Image(filename=ROOT / 'outputs' / 'charts' / 'season_ratings.png', width=950))"),
        code(
            """
            season_summary = features.groupby("season").agg(
                episodes=("episode_id", "size"),
                mean_rating=("rating", "mean"),
                median_rating=("rating", "median"),
                min_rating=("rating", "min"),
                max_rating=("rating", "max"),
            ).round(2)
            season_summary
            """
        ),
        markdown("### 2. Which social-rule themes appear most often?"),
        code("display(Image(filename=ROOT / 'outputs' / 'charts' / 'rule_theme_distribution.png', width=900))"),
        code("taxonomy"),
        markdown("### 3. Does more synopsis friction mean a higher rating?"),
        code("display(Image(filename=ROOT / 'outputs' / 'charts' / 'friction_vs_rating.png', width=900))"),
        code(
            """
            top_friction = features.nlargest(10, "synopsis_friction_score")[[
                "episode_code", "title", "synopsis_friction_score", "rating", "primary_rule_theme"
            ]]
            top_friction
            """
        ),
        markdown(
            f"""
            Spearman's rank correlation is **{rho:.2f}**, which is too small to support a meaningful monotonic association in this snapshot. This is a useful constraint on the story: synopsis wording alone is not a rating model.
            """
        ),
        markdown("### 4. Which characters are co-mentioned?"),
        code("display(Image(filename=ROOT / 'outputs' / 'charts' / 'character_network.png', width=900))"),
        code("edges.head(12)"),
        markdown(
            f"""
            ## Takeaways

            1. The source snapshot is complete for the intended scope: **{METRICS['episode_count']} unique regular episodes**, no missing summaries or ratings, and no duplicate season/episode keys.
            2. **Season {METRICS['highest_mean_rating_season']}** is the strongest-rated season on average in this TVmaze snapshot.
            3. Synopsis themes lean toward **relationships, loyalty, etiquette, and access to spaces**—a useful starting taxonomy for later scene-level annotation.
            4. The friction heuristic should remain descriptive. Its weak relationship with ratings suggests that future work should add richer structure: who initiates a dispute, whether Larry is vindicated, escalation steps, callbacks, and guest-star context.
            5. Character links are synopsis co-mentions, not proof that two characters share a scene.

            ### Next release

            Build a small, manually reviewed scene annotation set with `rule_broken`, `initiator`, `target`, `escalation_steps`, `larry_vindicated`, and `callback_present`. That will enable the real **Larry Vindication Score** without pretending keyword matches are ground truth.
            """
        ),
    ]

    output = ROOT / "notebooks" / "curb_conflict_atlas.ipynb"
    output.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, output)
    return output


if __name__ == "__main__":
    print(build())
