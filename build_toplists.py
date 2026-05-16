from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_ROOT = PROJECT_ROOT / "data"
AREAS = ("hungarian", "us")
AREA_DISPLAY = {"hungarian": "Hungarian", "us": "US"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_region_overrides(area: str) -> tuple[dict[str, str], dict[str, str]]:
    """Load manual person->region and group->region overrides if the file exists."""
    path = DATA_ROOT / area / "normalized" / "region_overrides.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("persons", {}), data.get("groups", {})
    return {}, {}


def compute_top_region(
    name: str,
    song_ids: list[str],
    song_map: dict[str, dict],
    region_overrides: dict[str, str] | None = None,
) -> str:
    if region_overrides and name in region_overrides:
        return region_overrides[name]
    counts = Counter()
    for song_id in song_ids:
        song = song_map.get(song_id)
        if not song:
            continue
        region = song.get("folder_region")
        if region:
            counts[region] += 1
    return counts.most_common(1)[0][0] if counts else ""


def compute_normalized_scores(
    songs: list[dict], groups: dict[str, dict]
) -> dict[str, float]:
    """For each song, expand all credits to unique persons, give each 1/N."""
    scores: dict[str, float] = {}
    for song in songs:
        persons_on_song: set[str] = set()
        for credit in song.get("credits", []):
            if credit["entity_type"] == "person":
                persons_on_song.add(credit["entity"])
            elif credit["entity_type"] == "group":
                group_data = groups.get(credit["entity"])
                if group_data:
                    for member in group_data.get("members", []):
                        persons_on_song.add(member)
        if not persons_on_song:
            continue
        share = 1.0 / len(persons_on_song)
        for person in persons_on_song:
            scores[person] = scores.get(person, 0.0) + share
    return scores


# Adjusted v2 overrides: person -> group -> custom weight
# Other members keep their normal 1/N; the override person gets this instead.
GROUP_WEIGHT_OVERRIDES: dict[str, dict[str, float]] = {
    "Eminem": {"D12": 1 / 3},
    "50 Cent": {"G-Unit": 1 / 2},
    "Ketioz": {"Jam Balaya": 1 / 2},
    "Scarface": {"Geto Boys": 1 / 2},
    "Ice Cube": {"N.W.A": 1 / 3},
    "Dr. Dre": {"N.W.A": 1 / 3},
    "Eazy-E": {"N.W.A": 1 / 3},
    "Birdman": {"Big Tymers": 1 / 2},
    "Mannie Fresh": {"Big Tymers": 1 / 2},
}


def compute_adjusted_scores(
    songs: list[dict], groups: dict[str, dict]
) -> dict[str, float]:
    """Adjusted v2: solo/individual primary gets 1.0, group members divide, features get 1/N."""
    scores: dict[str, float] = {}
    # Build set of all group members for quick lookup
    all_group_members: dict[str, set[str]] = {}  # group_name -> members
    for gname, gdata in groups.items():
        all_group_members[gname] = set(gdata.get("members", []))

    for song in songs:
        primary_persons: set[str] = set()
        feature_persons: set[str] = set()
        credited_groups: dict[str, set[str]] = {}  # group_name -> members

        for credit in song.get("credits", []):
            if credit["entity_type"] == "person":
                if credit["role"] == "primary":
                    primary_persons.add(credit["entity"])
                else:
                    feature_persons.add(credit["entity"])
            elif credit["entity_type"] == "group":
                if credit["entity"] in all_group_members:
                    credited_groups[credit["entity"]] = all_group_members[credit["entity"]]

        # All unique persons on this song
        all_persons: set[str] = set()
        all_persons.update(primary_persons)
        all_persons.update(feature_persons)
        for members in credited_groups.values():
            all_persons.update(members)

        if not all_persons:
            continue

        n_total = len(all_persons)

        # Persons who are on this song via a credited group
        via_group_persons: set[str] = set()
        for members in credited_groups.values():
            via_group_persons.update(members)

        # Solo primary: exactly 1 primary person and no group credits
        solo_primary = (
            len(primary_persons - via_group_persons) == 1
            and len(credited_groups) == 0
        )

        for person in all_persons:
            if person in via_group_persons:
                # Group member: check for override, otherwise 1/N
                override_share = None
                for group_name, members in credited_groups.items():
                    if person in members:
                        overrides = GROUP_WEIGHT_OVERRIDES.get(person, {})
                        if group_name in overrides:
                            override_share = overrides[group_name]
                            break
                share = override_share if override_share is not None else 1.0 / n_total
            elif person in primary_persons and solo_primary:
                # Sole primary artist gets full credit
                share = 1.0
            else:
                # Co-primary or feature: 1/N
                share = 1.0 / n_total

            scores[person] = scores.get(person, 0.0) + share

    return scores


def person_rows(
    persons: dict[str, dict],
    song_map: dict[str, dict],
    norm_scores: dict[str, float],
    adj_scores: dict[str, float],
    region_overrides: dict[str, str] | None = None,
) -> list[str]:
    ranked = sorted(
        persons.items(),
        key=lambda item: (-adj_scores.get(item[0], 0.0), item[0].lower()),
    )
    rows = []
    for idx, (name, payload) in enumerate(ranked, start=1):
        groups = ", ".join(payload.get("groups", [])) or "-"
        labels = ", ".join(payload.get("labels", [])) or "-"
        norm = norm_scores.get(name, 0.0)
        adj = adj_scores.get(name, 0.0)
        rows.append(
            "| {idx} | {name} | {songs} | {norm} | {adj} | {primary} | {feature} | {via_group} | {region} | {labels} | {groups} |".format(
                idx=idx,
                name=name,
                songs=len(payload.get("song_ids", [])),
                norm=f"{norm:.1f}",
                adj=f"{adj:.1f}",
                primary=len(payload.get("primary_song_ids", [])),
                feature=len(payload.get("feature_song_ids", [])),
                via_group=len(payload.get("via_group_song_ids", [])),
                region=compute_top_region(name, payload.get("song_ids", []), song_map, region_overrides) or "-",
                labels=labels,
                groups=groups,
            )
        )
    return rows


def group_rows(
    groups: dict[str, dict],
    song_map: dict[str, dict],
    group_region_overrides: dict[str, str] | None = None,
) -> list[str]:
    ranked = sorted(
        groups.items(),
        key=lambda item: (-len(item[1].get("song_ids", [])), item[0].lower()),
    )
    rows = []
    for idx, (name, payload) in enumerate(ranked, start=1):
        region = (group_region_overrides or {}).get(name) or compute_top_region(
            name, payload.get("song_ids", []), song_map
        ) or "-"
        rows.append(
            "| {idx} | {name} | {songs} | {members} | {region} | {labels} |".format(
                idx=idx,
                name=name,
                songs=len(payload.get("song_ids", [])),
                members=", ".join(payload.get("members", [])) or "-",
                region=region,
                labels=", ".join(payload.get("labels", [])) or "-",
            )
        )
    return rows


def label_rows(labels: dict[str, dict]) -> list[str]:
    ranked = sorted(
        labels.items(),
        key=lambda item: (-len(item[1].get("song_ids", [])), item[0].lower()),
    )
    rows = []
    for idx, (name, payload) in enumerate(ranked, start=1):
        rows.append(
            "| {idx} | {name} | {songs} | {persons} | {groups} | {regions} |".format(
                idx=idx,
                name=name,
                songs=len(payload.get("song_ids", [])),
                persons=len(payload.get("persons", [])),
                groups=len(payload.get("groups", [])),
                regions=", ".join(payload.get("regions", [])) or "-",
            )
        )
    return rows


def region_rows(regions: dict[str, dict] | dict) -> list[str]:
    if isinstance(regions, dict) and regions.get("status"):
        return [
            f"Regions status: `{regions['status']}`",
            "",
            regions.get("note", ""),
        ]
    ranked = sorted(
        regions.items(),
        key=lambda item: (-len(item[1].get("song_ids", [])), item[0].lower()),
    )
    rows = []
    for idx, (name, payload) in enumerate(ranked, start=1):
        rows.append(
            "| {idx} | {name} | {songs} | {persons} | {groups} | {labels} | {sources} |".format(
                idx=idx,
                name=name,
                songs=len(payload.get("song_ids", [])),
                persons=len(payload.get("persons", [])),
                groups=len(payload.get("groups", [])),
                labels=len(payload.get("labels", [])),
                sources=", ".join(payload.get("sources", [])) or "-",
            )
        )
    return rows


def build_area_toplist(area: str) -> None:
    base = DATA_ROOT / area / "normalized"
    metadata = load_json(base / "metadata.json")
    songs = load_json(base / "songs.json")
    song_map = {song["song_id"]: song for song in songs}
    persons = load_json(base / "persons.json")
    groups = load_json(base / "groups.json")
    labels = load_json(base / "labels.json")
    regions = load_json(base / "regions.json")

    lines = [
        f"# {AREA_DISPLAY.get(area, area.capitalize())} Local Music Toplists",
        "",
        f"Songs: `{metadata['counts']['songs']}`",
        f"Persons: `{metadata['counts']['persons']}`",
        f"Groups: `{metadata['counts']['groups']}`",
        f"Labels: `{metadata['counts']['labels']}`",
        f"Regions: `{metadata['counts']['regions']}`",
    ]
    if "unattributed_songs" in metadata["counts"]:
        lines.append(f"Unattributed songs: `{metadata['counts']['unattributed_songs']}`")
    norm_scores = compute_normalized_scores(songs, groups)
    adj_scores = compute_adjusted_scores(songs, groups)
    person_region_overrides, group_region_overrides = load_region_overrides(area)

    lines.extend(
        [
            "",
            "## Persons",
            "",
            "| # | Artist | Songs | Norm | Adj | Primary | Feature | Via Group | Top Region | Labels | Groups |",
            "|---|--------|-------|------|-----|---------|---------|-----------|------------|--------|--------|",
            *person_rows(persons, song_map, norm_scores, adj_scores, person_region_overrides),
            "",
            "## Groups",
            "",
            "| # | Group | Songs | Members | Top Region | Labels |",
            "|---|-------|-------|---------|------------|--------|",
            *group_rows(groups, song_map, group_region_overrides),
            "",
            "## Labels",
            "",
            "| # | Label | Songs | Persons | Groups | Regions |",
            "|---|-------|-------|---------|--------|---------|",
            *label_rows(labels),
            "",
            "## Regions",
            "",
        ]
    )

    region_section = region_rows(regions)
    if region_section and region_section[0].startswith("|"):
        lines.extend(
            [
                "| # | Region | Songs | Persons | Groups | Labels | Sources |",
                "|---|--------|-------|---------|--------|--------|---------|",
                *region_section,
            ]
        )
    else:
        lines.extend(region_section)

    (base / "toplists.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    for area in AREAS:
        build_area_toplist(area)
    print("Wrote normalized toplists for Hungarian and US.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
