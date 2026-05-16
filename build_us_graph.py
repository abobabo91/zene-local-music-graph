from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data" / "us"
ZENE = Path(r"C:\Users\abele\Desktop\zene")
MAPPINGS_PATH = DATA_DIR / "us_rap_trap_mappings.md"
NORMALIZED_DIR = DATA_DIR / "normalized"

AUDIO_EXTS = {".mp3", ".wma", ".wav", ".m4a", ".flac"}
REGION_MAP = {
    "_usa other": "USA Other",
    "_usa random": "USA",
    "new york": "New York",
    "philly": "Philadelphia",
    "phily": "Philadelphia",
    "luisiana": "Louisiana",
    "louisiana": "Louisiana",
    "dc": "DC",
    "2pac": "California",
    "atlanta": "Atlanta",
    "detroit": "Detroit",
    "california": "California",
    "texas": "Texas",
    "memphis": "Memphis",
    "florida": "Florida",
    "chicago": "Chicago",
    "toronto": "Toronto",
}
SOURCE_SCOPES = {
    "_rap": {"exclude_regions": {"_other"}},
    "_trap": {"exclude_regions": {"_other country random"}},
}
FEAT_RE = re.compile(r"\b(?:feat\.?|ft\.?|featuring|with|w\/)\b", re.IGNORECASE)
UNICODE_DASH_RE = re.compile(r"[–—]+")
NOISE_PATTERNS = [
    r"\(DatPiff\.com\)",
    r"\[DatPiff.*?\]",
    r"\[www\..*?\]",
    r"\bOfficial Music Video\b",
    r"\bOfficial Video\b",
    r"\bOfficial Audio\b",
    r"\bOfficial Lyric Video\b",
    r"\bOfficial Visualizer\b",
    r"\bOFFICIAL VIDEO\b",
    r"\bOFFICIAL AUDIO\b",
    r"\bHD\b",
    r"\bHQ\b",
    r"\[\d{3}\]",
    r"\(\d{3}\)",
]
GENERIC_FOLDER_NAMES = {
    "_random",
    "random",
    "loose",
    "misc",
    "videos",
    "music videos",
    "wshh",
    "worldstarhiphop",
    "hiphoptxl",
    "youtube",
    "various artists",
}
UPLOADER_NAMES = {"wshh", "worldstarhiphop", "hiphoptxl", "lyrical lemonade", "youtube"}
UNKNOWN_ARTIST = "N/A"
LABEL_LIKE_ARTISTS = {"cmg the label"}
YO_GOTTI_GANGSTA_ART_TITLE_ARTISTS = {
    "1st of Jan": "Yo Gotti",
    "Big League": "Yo Gotti",
    "Blac Ball": "Blac Youngsta",
    "Brick or Sum": "Tripstar",
    "Buss Down": "Yo Gotti",
    "Dog House": "Yo Gotti",
    "G Code": "Mozzy",
    "Gangsta Art": "Yo Gotti",
    "Hold Me Down": "42 Dugg",
    "Hood Rich": "Lehla Samia",
    "KeKe": "Big Boogie",
    "Major Payne": "10Percent",
    "Meant Dat": "Big Boogie",
    "Moral Of Da Story": "Yo Gotti",
    "OK": "BlocBoy JB",
    "Paparazzi": "Yo Gotti",
    "Pledge": "Lil Poppa",
    "Pole": "Yo Gotti",
    "Really": "Yo Gotti",
    "Rocky Road": "Moneybagg Yo",
    "See Wat I’m Sayin": "Moneybagg Yo",
    "SOON": "42 Dugg",
    "Steppers": "Yo Gotti",
    "Strong": "EST Gee",
    "Tomorrow": "GloRilla",
    "Top Dolla": "Tripstar",
    "Wait In Line": "Yo Gotti",
}


def normalize_key(text: str) -> str:
    value = text.lower().replace("_", " ")
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9+]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


GENERIC_FOLDER_KEYS = {normalize_key(name) for name in GENERIC_FOLDER_NAMES}


def parse_simple_mapping_block(lines: list[str]) -> dict[str, list[str]]:
    results: dict[str, list[str]] = {}
    for raw in lines:
        line = raw.strip()
        if not line.startswith("-"):
            continue
        line = line[1:].strip()
        if line.startswith("`") and line.endswith("`"):
            line = line[1:-1]
        if ":" not in line:
            continue
        left, right = line.split(":", 1)
        left = left.strip()
        values = [item.strip() for item in right.split(",") if item.strip()]
        if left:
            results[left] = values
    return results


def load_mappings() -> dict:
    text = MAPPINGS_PATH.read_text(encoding="utf-8")
    sections: dict[str, list[str]] = defaultdict(list)
    current = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            current = line[3:].strip().lower()
            continue
        if current:
            sections[current].append(line)

    alias_map = parse_simple_mapping_block(sections.get("alias normalization", []))
    groups = parse_simple_mapping_block(sections.get("groups", []))
    labels = parse_simple_mapping_block(sections.get("labels", []))

    person_entries: dict[str, dict[str, list[str] | str]] = {}
    current_person = None
    for raw in sections.get("person entries", []):
        line = raw.strip()
        if line.startswith("### "):
            current_person = line[4:].strip()
            person_entries[current_person] = {"aliases": [], "groups": [], "labels": [], "notes": ""}
            continue
        if not current_person or not line.startswith("-"):
            continue
        field, _, value = line[1:].partition(":")
        key = field.strip().lower()
        value = value.strip()
        if key in {"aliases", "groups", "labels"}:
            person_entries[current_person][key] = [item.strip() for item in value.split(",") if item.strip()]
        elif key == "notes":
            person_entries[current_person][key] = value

    alias_lookup: dict[str, str] = {}
    for canonical, aliases in alias_map.items():
        alias_lookup[normalize_key(canonical)] = canonical
        for alias in aliases:
            alias_lookup[normalize_key(alias)] = canonical

    for person, info in person_entries.items():
        alias_lookup[normalize_key(person)] = person
        for alias in info.get("aliases", []):
            alias_lookup[normalize_key(alias)] = person

    canonical_groups: dict[str, list[str]] = {}
    for group_name, members in groups.items():
        canonical_group = alias_lookup.get(normalize_key(group_name), group_name)
        canonical_members = []
        for member in members:
            canonical_member = alias_lookup.get(normalize_key(member), member)
            if canonical_member not in canonical_members:
                canonical_members.append(canonical_member)
        canonical_groups[canonical_group] = canonical_members

    canonical_labels: dict[str, list[str]] = {}
    for label_name, artists in labels.items():
        canonical_artists = []
        for artist in artists:
            canonical_artist = alias_lookup.get(normalize_key(artist), artist)
            if canonical_artist not in canonical_artists:
                canonical_artists.append(canonical_artist)
        canonical_labels[label_name] = canonical_artists

    group_lookup = {normalize_key(group_name): group_name for group_name in canonical_groups}

    return {
        "alias_lookup": alias_lookup,
        "groups": canonical_groups,
        "group_lookup": group_lookup,
        "labels": canonical_labels,
        "person_entries": person_entries,
    }


def canonicalize_artist(name: str, mappings: dict) -> str:
    cleaned = clean_artist_text(name)
    if not cleaned:
        return cleaned
    return mappings["alias_lookup"].get(normalize_key(cleaned), cleaned)


def clean_artist_text(text: str) -> str:
    value = UNICODE_DASH_RE.sub("-", text).replace("_", " ").strip()
    value = re.sub(r"\(.*?datpiff.*?\)", "", value, flags=re.IGNORECASE)
    value = re.sub(r"\(.*?\)", "", value)
    value = re.sub(r"\[.*?\]", "", value)
    value = value.replace("’", "'")
    value = re.sub(r"\s+", " ", value).strip(" .-_,")
    return value


def folder_artist_from_name(name: str) -> str:
    value = clean_artist_text(name)
    lower = value.lower()

    for suffix in [
        " music videos",
        " videos",
        " greatest hits",
        " essentials",
        " discography",
        " playlist",
        " mix",
    ]:
        if lower.endswith(suffix):
            value = value[: -len(suffix)].strip(" -_,")
            lower = value.lower()

    for marker in ["wshh exclusive", "official video", "official music video", "youtube"]:
        value = re.sub(marker, "", value, flags=re.IGNORECASE).strip(" -_,")

    if " - " in value:
        left, right = value.split(" - ", 1)
        if left and any(token in right.lower() for token in ["album", "mixtape", "greatest", "hits", "full", "vol", "edition"]):
            value = left.strip()

    return value.strip(" -_,")


def is_yo_gotti_cmg_compilation(path_parts: list[str]) -> bool:
    joined = " / ".join(path_parts).lower()
    return (
        len(path_parts) >= 4
        and path_parts[0].lower() == "_trap"
        and path_parts[1].lower() == "memphis"
        and path_parts[2].lower() == "yo gotti"
        and "cmg the label" in joined
        and "gangsta art" in joined
    )


def first_artist_context(path_parts: list[str], mappings: dict) -> str | None:
    if len(path_parts) >= 2 and path_parts[1].lower() == "2pac":
        return "2Pac"
    candidates: list[str] = []
    for part in path_parts[2:-1]:
        candidate = folder_artist_from_name(part)
        if not candidate:
            continue
        if normalize_key(candidate) in GENERIC_FOLDER_KEYS:
            continue
        candidates.append(candidate)

    if not candidates:
        return None

    first = canonicalize_artist(candidates[0], mappings)
    if normalize_key(first) == normalize_key("Yo Gotti") and is_yo_gotti_cmg_compilation(path_parts):
        return None
    first_group = canonical_group_name(first, mappings)
    if first_group:
        members = {normalize_key(member): member for member in mappings["groups"].get(first_group, [])}
        for candidate in candidates[1:]:
            canonical_candidate = canonicalize_artist(candidate, mappings)
            member = members.get(normalize_key(canonical_candidate))
            if member:
                return member
    return first
    return None


def split_artist_list(text: str) -> list[str]:
    temp = text
    temp = re.sub(r"\bx\b", "|", temp, flags=re.IGNORECASE)
    temp = temp.replace("&", "|")
    temp = temp.replace("/", "|")
    temp = temp.replace(",", "|")
    temp = re.sub(r"\band\b", "|", temp, flags=re.IGNORECASE)
    parts = [clean_artist_text(part) for part in temp.split("|")]
    return [part for part in parts if part]


def extract_primary_and_features(artist_credit: str) -> tuple[list[str], list[str]]:
    credit = clean_artist_text(artist_credit)
    if not credit:
        return [], []
    match = FEAT_RE.search(credit)
    if match:
        primary = credit[: match.start()].strip(" -")
        featured = credit[match.end() :].strip(" -")
        return split_artist_list(primary), split_artist_list(featured)
    return split_artist_list(credit), []


def clean_title_from_filename(filename: str) -> str:
    title = UNICODE_DASH_RE.sub("-", Path(filename).stem)
    title = re.sub(r"^\d{1,2}\s*[-._)]\s*", "", title)
    title = re.sub(r"^\d{1,2}\s+", "", title)
    for pattern in NOISE_PATTERNS:
        title = re.sub(pattern, "", title, flags=re.IGNORECASE)
    title = re.sub(r"\bprod\.?\s+by\b.*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\bproduced by\b.*$", "", title, flags=re.IGNORECASE)
    title = title.replace("_", " ")
    title = re.sub(r"^\d{1,2}\s*-\s*", "", title)
    title = re.sub(r"\s+", " ", title).strip(" .-_,")
    return title


def infer_credit_from_loose_stem(filename: str) -> tuple[str | None, str | None]:
    stem = UNICODE_DASH_RE.sub("-", Path(filename).stem).replace("_", " ").strip()

    compact_dash = re.match(r"^([^-\[\(]{2,80}?)\s*-\s*(.+)$", stem)
    if compact_dash:
        left = clean_artist_text(compact_dash.group(1))
        right = clean_title_from_filename(compact_dash.group(2))
        left_key = normalize_key(left)
        if left and right and not left_key.isdigit() and left_key not in {normalize_key(name) for name in UPLOADER_NAMES}:
            return left, right

    chunks = [chunk.strip() for chunk in re.split(r"\s{2,}", stem) if chunk.strip()]
    if len(chunks) >= 2:
        left = clean_artist_text(chunks[0])
        right = clean_title_from_filename(" ".join(chunks[1:]))
        left_key = normalize_key(left)
        if left and right and not left_key.isdigit() and left_key not in {normalize_key(name) for name in UPLOADER_NAMES}:
            return left, right

    return None, None


def infer_credit_and_title(path_parts: list[str], filename: str, mappings: dict) -> tuple[str | None, str]:
    artist_context = first_artist_context(path_parts, mappings)

    title = clean_title_from_filename(filename)
    if " - " in title:
        prefix, suffix = title.split(" - ", 1)
        prefix_clean = clean_artist_text(prefix)
        suffix_clean = clean_title_from_filename(suffix.strip())
        if normalize_key(prefix_clean) in {normalize_key(name) for name in UPLOADER_NAMES} | {"various artists"}:
            return artist_context, suffix_clean
        if not artist_context or normalize_key(prefix_clean) != normalize_key(artist_context):
            if len(prefix_clean.split()) <= 6:
                return prefix_clean, suffix_clean
        if artist_context and normalize_key(prefix_clean) == normalize_key(artist_context):
            return artist_context, suffix_clean

    loose_credit, loose_title = infer_credit_from_loose_stem(filename)
    if loose_credit and loose_title:
        return loose_credit, loose_title

    return artist_context, title


def normalize_primary_candidates(primary_artists: list[str], featuring: list[str]) -> tuple[list[str], list[str]]:
    kept = [name for name in primary_artists if normalize_key(name) not in LABEL_LIKE_ARTISTS]
    if not kept:
        return primary_artists, featuring
    if len(kept) == 1:
        return kept, featuring
    merged_featuring = kept[1:] + featuring
    deduped = []
    seen = set()
    for name in merged_featuring:
        key = normalize_key(name)
        if key and key not in seen and key != normalize_key(kept[0]):
            seen.add(key)
            deduped.append(name)
    return [kept[0]], deduped


def yo_gotti_compilation_artist_from_title(title: str) -> str | None:
    return YO_GOTTI_GANGSTA_ART_TITLE_ARTISTS.get(title)


def infer_groups_and_labels(artist: str, mappings: dict) -> tuple[list[str], list[str]]:
    groups = []
    labels = []
    artist_key = normalize_key(artist)

    for group, members in mappings["groups"].items():
        if any(normalize_key(member) == artist_key for member in members):
            groups.append(group)

    for label, artists in mappings["labels"].items():
        if any(normalize_key(entry) == artist_key for entry in artists):
            labels.append(label)

    person_entry = mappings["person_entries"].get(artist, {})
    for group in person_entry.get("groups", []):
        if group and group not in groups:
            groups.append(group)
    for label in person_entry.get("labels", []):
        if label and label not in labels:
            labels.append(label)

    return groups, labels


def canonical_group_name(name: str, mappings: dict) -> str | None:
    cleaned = clean_artist_text(name)
    if not cleaned:
        return None
    return mappings["group_lookup"].get(normalize_key(cleaned))


def prefer_display_name(name: str, mappings: dict) -> str:
    canonical = canonicalize_artist(name, mappings)
    if canonical:
        return canonical
    return clean_artist_text(name)


def ensure_person_entry(persons: dict[str, dict], artist: str, groups: list[str] | None = None, labels: list[str] | None = None) -> dict:
    return persons.setdefault(
        artist,
        {
            "song_count": 0,
            "regions": Counter(),
            "sources": Counter(),
            "groups": set(groups or []),
            "labels": set(labels or []),
            "songs": [],
        },
    )


def append_song(target: dict, track: dict, via_group: str | None = None) -> None:
    target["song_count"] += 1
    target["regions"][track["region"]] += 1
    target["sources"][track["source"]] += 1
    song_payload = {
        "file": track["file"],
        "title": track["title"],
        "region": track["region"],
        "source": track["source"],
        "featuring": track["featuring"],
    }
    if via_group:
        song_payload["via_group"] = via_group
    target["songs"].append(song_payload)


def region_from_folder(folder_name: str) -> str:
    return REGION_MAP.get(folder_name.lower(), folder_name)


def iter_scoped_audio_files():
    for root_name, config in SOURCE_SCOPES.items():
        root_path = ZENE / root_name
        for region_dir in sorted(root_path.iterdir()):
            if not region_dir.is_dir():
                continue
            if region_dir.name in config["exclude_regions"]:
                continue
            for file_path in region_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in AUDIO_EXTS:
                    yield root_name, region_dir.name, file_path


def build_graph() -> dict:
    mappings = load_mappings()
    tracks = []
    persons: dict[str, dict] = {}
    groups_index: dict[str, dict] = {}
    duplicates = set()
    display_name_by_key: dict[str, str] = {}

    for source, region_folder, file_path in iter_scoped_audio_files():
        rel_path = file_path.relative_to(ZENE)
        rel_parts = list(rel_path.parts)
        rel_key = rel_path.as_posix()
        if rel_key in duplicates:
            continue
        duplicates.add(rel_key)

        credit, title = infer_credit_and_title(rel_parts, file_path.name, mappings)
        primary_artists, featuring = extract_primary_and_features(credit or "")
        primary_artists, featuring = normalize_primary_candidates(primary_artists, featuring)
        if is_yo_gotti_cmg_compilation(rel_parts):
            if "type beat" in file_path.stem.lower():
                primary_artists = []
                featuring = []
            mapped_artist = yo_gotti_compilation_artist_from_title(title)
            if mapped_artist:
                primary_artists = [mapped_artist]
        if not primary_artists:
            context_artist = first_artist_context(rel_parts, mappings)
            primary_artists = [context_artist] if context_artist else []
        if not primary_artists or not primary_artists[0]:
            primary_artists = [UNKNOWN_ARTIST]

        primary_artist = prefer_display_name(primary_artists[0], mappings)
        if normalize_key(primary_artist) in {"unknown artist", "various artists"}:
            primary_artist = UNKNOWN_ARTIST
        primary_key = normalize_key(primary_artist)
        primary_artist = display_name_by_key.setdefault(primary_key, primary_artist)
        featuring = [prefer_display_name(name, mappings) for name in featuring if name]
        featuring = [display_name_by_key.setdefault(normalize_key(name), name) for name in featuring if name]
        groups, labels = infer_groups_and_labels(primary_artist, mappings)
        primary_group = canonical_group_name(primary_artist, mappings)

        track = {
            "file": rel_key,
            "title": title,
            "artist": primary_artist,
            "role": "primary",
            "featuring": featuring,
            "region": region_from_folder(region_folder),
            "region_folder": region_folder,
            "source": source,
            "group": groups[0] if groups else None,
            "label": labels[0] if labels else None,
        }
        tracks.append(track)

        if primary_artist == UNKNOWN_ARTIST:
            continue

        if primary_group:
            group_entry = groups_index.setdefault(
                primary_group,
                {
                    "members": mappings["groups"].get(primary_group, []),
                    "song_count": 0,
                    "regions": Counter(),
                    "sources": Counter(),
                    "labels": set(labels),
                    "songs": [],
                },
            )
            group_entry["labels"].update(labels)
            append_song(group_entry, track)

            for member in mappings["groups"].get(primary_group, []):
                member_groups, member_labels = infer_groups_and_labels(member, mappings)
                person = ensure_person_entry(persons, member, member_groups, member_labels)
                person["groups"].update(member_groups)
                person["labels"].update(member_labels)
                append_song(person, track, via_group=primary_group)
            continue

        person = ensure_person_entry(persons, primary_artist, groups, labels)
        person["groups"].update(groups)
        person["labels"].update(labels)
        append_song(person, track)

    for group_name, members in mappings["groups"].items():
        group_entry = groups_index.setdefault(
            group_name,
            {
                "members": members,
                "song_count": 0,
                "regions": Counter(),
                "sources": Counter(),
                "labels": set(),
                "songs": [],
            },
        )
        group_entry["member_song_count"] = sum(persons.get(member, {}).get("song_count", 0) for member in members)

    labels_index: dict[str, dict] = {}
    for label_name, artists in mappings["labels"].items():
        labels_index[label_name] = {
            "artists": artists,
            "artist_song_count": sum(persons.get(artist, {}).get("song_count", 0) for artist in artists),
        }

    for person_name, payload in persons.items():
        payload["groups"] = sorted(payload["groups"])
        payload["labels"] = sorted(payload["labels"])
        payload["regions"] = dict(payload["regions"].most_common())
        payload["sources"] = dict(payload["sources"].most_common())

    for group_name, payload in groups_index.items():
        payload["labels"] = sorted(payload["labels"])
        payload["regions"] = dict(payload["regions"].most_common())
        payload["sources"] = dict(payload["sources"].most_common())

    tracks.sort(key=lambda row: row["file"].lower())
    unattributed_count = sum(1 for track in tracks if track["artist"] == UNKNOWN_ARTIST)
    return {
        "metadata": {
            "scope": {
                "_rap": {"excluded": ["_other"]},
                "_trap": {"excluded": ["_other country random"]},
            },
            "track_count": len(tracks),
            "artist_count": len(persons),
            "group_count": len(groups_index),
            "unattributed_track_count": unattributed_count,
        },
        "tracks": tracks,
        "persons": dict(sorted(persons.items(), key=lambda item: (-item[1]["song_count"], item[0].lower()))),
        "groups": dict(sorted(groups_index.items(), key=lambda item: (-item[1]["song_count"], item[0].lower()))),
        "labels": labels_index,
    }



# ── Normalization ─────────────────────────────────────────────────────────────


def sorted_unique(values: list[str]) -> list[str]:
    return sorted({value for value in values if value}, key=str.lower)


def ensure_person(persons: dict[str, dict], name: str) -> dict:
    return persons.setdefault(
        name,
        {
            "type": "person",
            "labels": [],
            "groups": [],
            "regions": [],
            "sources": [],
            "song_ids": [],
            "primary_song_ids": [],
            "feature_song_ids": [],
            "via_group_song_ids": [],
        },
    )


def ensure_group(groups: dict[str, dict], name: str) -> dict:
    return groups.setdefault(
        name,
        {
            "type": "group",
            "members": [],
            "labels": [],
            "regions": [],
            "sources": [],
            "song_ids": [],
            "primary_song_ids": [],
            "feature_song_ids": [],
        },
    )


def build_normalized(legacy: dict) -> dict[str, object]:

    legacy_tracks = legacy["tracks"]
    legacy_persons = legacy["persons"]
    legacy_groups = legacy["groups"]
    legacy_labels = legacy["labels"]
    legacy_person_names = set(legacy_persons)
    legacy_group_names = set(legacy_groups)

    persons: dict[str, dict] = {}
    groups: dict[str, dict] = {}

    for name, payload in legacy_persons.items():
        entry = ensure_person(persons, name)
        entry["labels"] = sorted_unique(entry["labels"] + payload.get("labels", []))
        entry["groups"] = sorted_unique(entry["groups"] + payload.get("groups", []))
        entry["regions"] = sorted_unique(entry["regions"] + list(payload.get("regions", {}).keys()))
        entry["sources"] = sorted_unique(entry["sources"] + list(payload.get("sources", {}).keys()))

    for name, payload in legacy_groups.items():
        entry = ensure_group(groups, name)
        entry["members"] = sorted_unique(entry["members"] + payload.get("members", []))
        entry["labels"] = sorted_unique(entry["labels"] + payload.get("labels", []))
        entry["regions"] = sorted_unique(entry["regions"] + list(payload.get("regions", {}).keys()))
        entry["sources"] = sorted_unique(entry["sources"] + list(payload.get("sources", {}).keys()))
        for member in entry["members"]:
            if member in legacy_person_names:
                person = ensure_person(persons, member)
                person["groups"] = sorted_unique(person["groups"] + [name])

    person_song_details: dict[str, dict[str, dict]] = defaultdict(dict)
    for person_name, payload in legacy_persons.items():
        for song in payload.get("songs", []):
            person_song_details[person_name][song["file"]] = song

    group_song_details: dict[str, dict[str, dict]] = defaultdict(dict)
    for group_name, payload in legacy_groups.items():
        for song in payload.get("songs", []):
            group_song_details[group_name][song["file"]] = song

    songs = []
    song_id_by_file: dict[str, str] = {}
    unattributed_song_ids: list[str] = []

    for index, track in enumerate(sorted(legacy_tracks, key=lambda row: row["file"].lower()), start=1):
        song_id = f"u-{index:05d}"
        file_path = track["file"]
        song_id_by_file[file_path] = song_id

        primary_artist = track["artist"]
        is_unattributed = primary_artist == UNKNOWN_ARTIST
        is_group_primary = primary_artist in legacy_group_names
        primary_artists = [] if is_unattributed or is_group_primary else [primary_artist]

        primary_group_names = []
        if is_group_primary:
            primary_group_names.append(primary_artist)
        for group_name, payload in legacy_groups.items():
            if file_path in group_song_details.get(group_name, {}):
                primary_group_names.append(group_name)
        primary_group_names = sorted_unique(primary_group_names)

        credits = []
        if primary_artists:
            credits.append({"entity": primary_artist, "entity_type": "person", "role": "primary"})
        for group_name in primary_group_names:
            credits.append({"entity": group_name, "entity_type": "group", "role": "primary"})
        for feature in track.get("featuring", []):
            credits.append({"entity": feature, "entity_type": "person", "role": "feature"})

        artists = set(primary_artists)
        artists.update(track.get("featuring", []))
        for group_name in primary_group_names:
            artists.update(groups.get(group_name, {}).get("members", []))

        song = {
            "song_id": song_id,
            "file": file_path,
            "title": track["title"],
            "source_root": track["source"],
            "folder_region": track["region"],
            "primary_artists": sorted(primary_artists, key=str.lower),
            "featuring_artists": sorted_unique(track.get("featuring", [])),
            "artists": sorted(artists, key=str.lower),
            "credits": sorted(
                credits,
                key=lambda item: (item["entity_type"], item["role"], item["entity"].lower()),
            ),
            "attribution_status": "unattributed" if is_unattributed else "attributed",
        }
        songs.append(song)

        if is_unattributed:
            unattributed_song_ids.append(song_id)

        for artist_name in primary_artists:
            person = ensure_person(persons, artist_name)
            person["song_ids"].append(song_id)
            person["primary_song_ids"].append(song_id)
            person["regions"] = sorted_unique(person["regions"] + [track["region"]])
            person["sources"] = sorted_unique(person["sources"] + [track["source"]])

        for feature_name in track.get("featuring", []):
            if feature_name not in persons:
                continue
            person = ensure_person(persons, feature_name)
            person["song_ids"].append(song_id)
            person["feature_song_ids"].append(song_id)
            person["regions"] = sorted_unique(person["regions"] + [track["region"]])
            person["sources"] = sorted_unique(person["sources"] + [track["source"]])

        for group_name in primary_group_names:
            group = ensure_group(groups, group_name)
            group["song_ids"].append(song_id)
            group["primary_song_ids"].append(song_id)
            group["regions"] = sorted_unique(group["regions"] + [track["region"]])
            group["sources"] = sorted_unique(group["sources"] + [track["source"]])
            for member in group["members"]:
                if member not in legacy_person_names:
                    continue
                person = ensure_person(persons, member)
                if song_id not in person["song_ids"]:
                    person["song_ids"].append(song_id)
                person["via_group_song_ids"].append(song_id)
                person["regions"] = sorted_unique(person["regions"] + [track["region"]])
                person["sources"] = sorted_unique(person["sources"] + [track["source"]])

    for payload in persons.values():
        payload["labels"] = sorted_unique(payload["labels"])
        payload["groups"] = sorted_unique(payload["groups"])
        payload["regions"] = sorted_unique(payload["regions"])
        payload["sources"] = sorted_unique(payload["sources"])
        payload["song_ids"] = sorted_unique(payload["song_ids"])
        payload["primary_song_ids"] = sorted_unique(payload["primary_song_ids"])
        payload["feature_song_ids"] = sorted_unique(payload["feature_song_ids"])
        payload["via_group_song_ids"] = sorted_unique(payload["via_group_song_ids"])

    for payload in groups.values():
        payload["members"] = sorted_unique(payload["members"])
        payload["labels"] = sorted_unique(payload["labels"])
        payload["regions"] = sorted_unique(payload["regions"])
        payload["sources"] = sorted_unique(payload["sources"])
        payload["song_ids"] = sorted_unique(payload["song_ids"])
        payload["primary_song_ids"] = sorted_unique(payload["primary_song_ids"])
        payload["feature_song_ids"] = sorted_unique(payload["feature_song_ids"])

    labels: dict[str, dict] = {}
    for label_name, payload in legacy_labels.items():
        entry = labels.setdefault(
            label_name,
            {
                "type": "label",
                "persons": [],
                "groups": [],
                "regions": [],
                "sources": [],
                "song_ids": [],
            },
        )
        entry["persons"] = sorted_unique(entry["persons"] + payload.get("artists", []))

    for person_name, payload in persons.items():
        for label_name in payload["labels"]:
            entry = labels.setdefault(
                label_name,
                {
                    "type": "label",
                    "persons": [],
                    "groups": [],
                    "regions": [],
                    "sources": [],
                    "song_ids": [],
                },
            )
            entry["persons"] = sorted_unique(entry["persons"] + [person_name])
            entry["song_ids"] = sorted_unique(entry["song_ids"] + payload["song_ids"])
            entry["regions"] = sorted_unique(entry["regions"] + payload["regions"])
            entry["sources"] = sorted_unique(entry["sources"] + payload["sources"])

    for group_name, payload in groups.items():
        for label_name in payload["labels"]:
            entry = labels.setdefault(
                label_name,
                {
                    "type": "label",
                    "persons": [],
                    "groups": [],
                    "regions": [],
                    "sources": [],
                    "song_ids": [],
                },
            )
            entry["groups"] = sorted_unique(entry["groups"] + [group_name])
            entry["song_ids"] = sorted_unique(entry["song_ids"] + payload["song_ids"])
            entry["regions"] = sorted_unique(entry["regions"] + payload["regions"])
            entry["sources"] = sorted_unique(entry["sources"] + payload["sources"])

    for payload in labels.values():
        payload["persons"] = sorted_unique(payload["persons"])
        payload["groups"] = sorted_unique(payload["groups"])
        payload["regions"] = sorted_unique(payload["regions"])
        payload["sources"] = sorted_unique(payload["sources"])
        payload["song_ids"] = sorted_unique(payload["song_ids"])

    regions: dict[str, dict] = {}
    for song in songs:
        region_name = song["folder_region"]
        entry = regions.setdefault(
            region_name,
            {
                "type": "region",
                "persons": [],
                "groups": [],
                "labels": [],
                "sources": [],
                "song_ids": [],
            },
        )
        entry["song_ids"].append(song["song_id"])
        entry["sources"].append(song["source_root"])
        for artist in song["primary_artists"] + song["featuring_artists"]:
            if artist in persons:
                entry["persons"].append(artist)
        for credit in song["credits"]:
            if credit["entity_type"] == "group":
                entry["groups"].append(credit["entity"])

    for label_name, payload in labels.items():
        for region_name in payload["regions"]:
            region = regions.setdefault(
                region_name,
                {
                    "type": "region",
                    "persons": [],
                    "groups": [],
                    "labels": [],
                    "sources": [],
                    "song_ids": [],
                },
            )
            region["labels"].append(label_name)

    for payload in regions.values():
        payload["persons"] = sorted_unique(payload["persons"])
        payload["groups"] = sorted_unique(payload["groups"])
        payload["labels"] = sorted_unique(payload["labels"])
        payload["sources"] = sorted_unique(payload["sources"])
        payload["song_ids"] = sorted_unique(payload["song_ids"])

    validation = {
        "legacy_track_count_metadata": legacy["metadata"].get("track_count"),
        "legacy_track_count_actual": len(legacy_tracks),
        "legacy_person_count_metadata": legacy["metadata"].get("artist_count"),
        "legacy_person_count_actual": len(legacy_persons),
        "legacy_group_count_metadata": legacy["metadata"].get("group_count"),
        "legacy_group_count_actual": len(legacy_groups),
        "legacy_label_count_actual": len(legacy_labels),
        "legacy_unattributed_track_count_metadata": legacy["metadata"].get("unattributed_track_count", 0),
        "normalized_song_count": len(songs),
        "normalized_person_count": len(persons),
        "normalized_group_count": len(groups),
        "normalized_label_count": len(labels),
        "normalized_region_count": len(regions),
        "normalized_unattributed_song_count": len(unattributed_song_ids),
        "checks": {
            "song_count_matches_legacy_tracks": len(songs) == len(legacy_tracks),
            "person_count_matches_legacy_persons": len(persons) == len(legacy_persons),
            "group_count_matches_legacy_groups": len(groups) == len(legacy_groups),
            "unattributed_count_matches_legacy_metadata": len(unattributed_song_ids)
            == legacy["metadata"].get("unattributed_track_count", 0),
        },
    }

    metadata = {
        "source_format": "legacy_us_track_first_plus_indexes",
        "schema_version": 1,
        "scope": legacy["metadata"].get("scope", {}),
        "counts": {
            "songs": len(songs),
            "persons": len(persons),
            "groups": len(groups),
            "labels": len(labels),
            "regions": len(regions),
            "unattributed_songs": len(unattributed_song_ids),
        },
        "notes": [
            "Songs are the source of truth.",
            "Persons, groups, labels, and regions are separate derived indexes.",
            "Feature artists are attached to songs directly even when they do not have a full person index entry.",
        ],
    }

    return {
        "metadata": metadata,
        "songs": songs,
        "persons": dict(sorted(persons.items(), key=lambda item: item[0].lower())),
        "groups": dict(sorted(groups.items(), key=lambda item: item[0].lower())),
        "labels": dict(sorted(labels.items(), key=lambda item: item[0].lower())),
        "regions": dict(sorted(regions.items(), key=lambda item: item[0].lower())),
        "validation": validation,
    }


def write_outputs(normalized: dict[str, object]) -> None:
    NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)
    outputs = {
        "metadata.json": normalized["metadata"],
        "songs.json": normalized["songs"],
        "persons.json": normalized["persons"],
        "groups.json": normalized["groups"],
        "labels.json": normalized["labels"],
        "regions.json": normalized["regions"],
        "validation.json": normalized["validation"],
    }
    for filename, payload in outputs.items():
        (NORMALIZED_DIR / filename).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )



def main() -> int:
    graph = build_graph()
    normalized = build_normalized(graph)
    write_outputs(normalized)
    m = normalized["metadata"]["counts"]
    print(f"Songs: {m['songs']}")
    print(f"Persons: {m['persons']}")
    print(f"Groups: {m['groups']}")
    print(f"Labels: {m['labels']}")
    print(f"Regions: {m['regions']}")
    print(f"Unattributed: {m['unattributed_songs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
