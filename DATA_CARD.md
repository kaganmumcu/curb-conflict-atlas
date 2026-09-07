# Data Card

## Dataset

The project uses episode-level metadata and synopses for *Curb Your Enthusiasm* from the public TVmaze API. The source snapshot contains 120 regular episodes across 12 seasons, from 2000-10-15 through 2024-04-07.

## Intended use

This dataset supports a portfolio demonstration of reproducible data collection, transparent text feature engineering, exploratory analysis, and network visualization. It is not designed for psychological, behavioral, or causal claims about performers, writers, audiences, or real people.

## Derived features

The social-rule themes and synopsis friction score are deterministic keyword-based features. They describe wording in short episode synopses—not complete scripts, scene structure, intent, or the actual frequency of conflicts in an episode.

## Provenance

- Source: [TVmaze public API](https://www.tvmaze.com/api)
- Show page: [Curb Your Enthusiasm](https://www.tvmaze.com/shows/551/curb-your-enthusiasm)
- Retrieval timestamp: recorded in `data/provenance.json`

TVmaze source URLs are retained per episode. Users should review TVmaze's attribution and licensing terms before redistribution.

## Known limitations

- TVmaze ratings can change and are not a controlled measure of episode quality.
- Vote counts are not included in this API response, so rating reliability cannot be weighted.
- Synopses vary in length and detail, which affects keyword-derived features.
- Character co-mentions are not scene-level interactions.
- Correlations are descriptive and do not imply causation.
- Full transcripts are intentionally excluded from the repository.

