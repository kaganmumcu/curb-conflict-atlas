"""Fetch and normalize episode metadata from TVmaze."""

from __future__ import annotations

import html
import json
import re
import ssl
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

import pandas as pd
import certifi


API_URL = "https://api.tvmaze.com/singlesearch/shows?q={query}&embed=episodes"
SHOW_NAME = "Curb Your Enthusiasm"


def strip_html(value: str | None) -> str:
    """Convert simple HTML summaries to plain text."""
    if not value:
        return ""
    plain = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(plain)).strip()


def fetch_show_payload(show_name: str = SHOW_NAME) -> dict:
    """Fetch one show and all episodes from TVmaze's public API."""
    url = API_URL.format(query=quote(show_name))
    request = Request(url, headers={"User-Agent": "curb-conflict-atlas/1.0"})
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    with urlopen(request, timeout=30, context=ssl_context) as response:
        payload = json.load(response)
    if payload.get("name") != show_name:
        raise ValueError(f"Expected {show_name!r}, received {payload.get('name')!r}")
    return payload


def normalize_episodes(payload: dict) -> pd.DataFrame:
    """Return one clean row per regular episode."""
    episodes = payload.get("_embedded", {}).get("episodes", [])
    rows = []
    for episode in episodes:
        if episode.get("season") is None or episode.get("number") is None:
            continue
        airdate = episode.get("airdate")
        rows.append(
            {
                "episode_id": int(episode["id"]),
                "season": int(episode["season"]),
                "episode": int(episode["number"]),
                "episode_code": f"S{int(episode['season']):02d}E{int(episode['number']):02d}",
                "title": episode.get("name", ""),
                "airdate": airdate,
                "year": int(airdate[:4]) if airdate else pd.NA,
                "runtime_minutes": episode.get("runtime"),
                "rating": episode.get("rating", {}).get("average"),
                "summary": strip_html(episode.get("summary")),
                "source_url": episode.get("url", ""),
            }
        )
    frame = pd.DataFrame(rows).sort_values(["season", "episode"]).reset_index(drop=True)
    return frame


def validate_episode_data(frame: pd.DataFrame) -> None:
    """Raise a clear error when the downloaded episode table is incomplete."""
    required = {
        "episode_id",
        "season",
        "episode",
        "episode_code",
        "title",
        "airdate",
        "runtime_minutes",
        "rating",
        "summary",
        "source_url",
    }
    missing_columns = required.difference(frame.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")
    if frame.empty:
        raise ValueError("Episode table is empty")
    if frame["episode_id"].duplicated().any():
        raise ValueError("Episode IDs are not unique")
    if frame[["season", "episode"]].duplicated().any():
        raise ValueError("Season/episode keys are not unique")
    if frame["summary"].str.strip().eq("").any():
        raise ValueError("At least one episode summary is missing")
    if frame["rating"].isna().any():
        raise ValueError("At least one episode rating is missing")
    if not frame["rating"].between(0, 10).all():
        raise ValueError("Ratings must fall between 0 and 10")


def load_or_fetch_episode_data(
    data_dir: Path, refresh: bool = False
) -> tuple[pd.DataFrame, dict]:
    """Use a cached source snapshot, or refresh it from TVmaze."""
    data_dir.mkdir(parents=True, exist_ok=True)
    raw_path = data_dir / "tvmaze_curb_raw.json"
    csv_path = data_dir / "episode_metadata.csv"
    provenance_path = data_dir / "provenance.json"

    if refresh or not raw_path.exists():
        payload = fetch_show_payload()
        raw_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        provenance = {
            "show": SHOW_NAME,
            "source": "TVmaze public API",
            "source_url": API_URL.format(query=quote(SHOW_NAME)),
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "license_note": "Check TVmaze attribution and API terms before redistribution.",
        }
        provenance_path.write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    else:
        payload = json.loads(raw_path.read_text(encoding="utf-8"))
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))

    frame = normalize_episodes(payload)
    validate_episode_data(frame)
    frame.to_csv(csv_path, index=False)
    return frame, provenance
