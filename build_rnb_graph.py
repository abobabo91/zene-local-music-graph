"""
Scan _other/_rnb/ and build a normalized song-by-song JSON for the R&B collection.
Simpler than the US rap/trap graph: no regions, no labels — just songs, artists, groups.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data" / "rnb"
ZENE = Path(r"C:\Users\abele\Desktop\zene")
RNB_ROOT = ZENE / "_other" / "_rnb"
NORMALIZED_DIR = DATA_DIR / "normalized"
MAPPINGS_PATH = DATA_DIR / "rnb_mappings.md"

AUDIO_EXTS = {".mp3", ".wma", ".wav", ".m4a", ".flac"}
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
    r"\bWSHH\s+Exclusive\b.*",
    r"\bWSHH\b",
    r"\bHD\b",
    r"\bHQ\b",
    r"\[\d{3}\]",
    r"\(\d{3}\)",
]
GENERIC_FOLDER_NAMES = {
    "_random", "_modern", "_other", "_rnb", "random", "loose", "misc", "videos", "youtube",
    "90s 00s rnb", "rnb", "bedtime rnb", "smooth vibin_", "highline r&b",
    "rap caviar", "the way you", "other",
}
COMPILATION_PREFIXES = {"dj_wispas", "dj ", "mix - ", "mix -"}
BLOCKLIST_ARTISTS = {
    "n/a", "unknown", "various", "nothing", "cd1", "cd2",
    "you", "me", "scape", "audio", "download link", "l ost", "l soundtrack",
    "step up soundtrack", "magic mike", "golden", "sickick", "sickickmusic",
    "lyrics", "lyrics on screen", "alone", "quits", "somebody", "drunk",
    "ne", "t", "bl", "st", "c", "j", "r", "ale", "010",
    "quot takin back my love quot", "wrong", "wRoNg",
    "honey soundtrack", "ost magic mike", "rb heaven vol 9", "rnb heaven vol 13",
    "as long as you love me", "kut klose slow jams",
    "geeze so sick", "did you ever think remi",
    "snoop dogg victory in stores now",
    "g o o d music s cyhi the prynce party bullshit",
    "me do it well",
}
UNKNOWN_ARTIST = "N/A"


def normalize_key(text: str) -> str:
    value = text.lower().replace("_", " ").replace("&", " and ")
    value = re.sub(r"[^a-z0-9+]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


GENERIC_FOLDER_KEYS = {normalize_key(name) for name in GENERIC_FOLDER_NAMES}
COMPILATION_PREFIX_KEYS = [normalize_key(p) for p in COMPILATION_PREFIXES]


def is_generic_folder(name: str) -> bool:
    key = normalize_key(name)
    if key in GENERIC_FOLDER_KEYS:
        return True
    return any(key.startswith(p) for p in COMPILATION_PREFIX_KEYS)


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
    if not MAPPINGS_PATH.exists():
        return {"alias_lookup": {}, "groups": {}, "group_lookup": {}}
    text = MAPPINGS_PATH.read_text(encoding="utf-8")
    sections: dict[str, list[str]] = defaultdict(list)
    current = None
    for line in text.splitlines():
        stripped = line.rstrip()
        if stripped.startswith("## "):
            current = stripped[3:].strip().lower()
            continue
        if current:
            sections[current].append(stripped)

    alias_map = parse_simple_mapping_block(sections.get("alias normalization", []))
    groups = parse_simple_mapping_block(sections.get("groups", []))

    alias_lookup: dict[str, str] = {}
    for canonical, aliases in alias_map.items():
        alias_lookup[normalize_key(canonical)] = canonical
        for alias in aliases:
            alias_lookup[normalize_key(alias)] = canonical

    canonical_groups: dict[str, list[str]] = {}
    for group_name, members in groups.items():
        cg = alias_lookup.get(normalize_key(group_name), group_name)
        cm = []
        for m in members:
            c = alias_lookup.get(normalize_key(m), m)
            if c not in cm:
                cm.append(c)
        canonical_groups[cg] = cm

    group_lookup = {normalize_key(g): g for g in canonical_groups}

    return {
        "alias_lookup": alias_lookup,
        "groups": canonical_groups,
        "group_lookup": group_lookup,
    }


def clean_artist_text(text: str) -> str:
    value = UNICODE_DASH_RE.sub("-", text).replace("_", " ").strip()
    value = re.sub(r"\(.*?\)", "", value)
    value = re.sub(r"\[.*?\]", "", value)
    value = value.replace("\u2019", "'")
    return re.sub(r"\s+", " ", value).strip(" .-_,")


def clean_title(filename: str) -> str:
    title = UNICODE_DASH_RE.sub("-", Path(filename).stem)
    title = re.sub(r"^\d{1,2}\s*[-._)]\s*", "", title)
    title = re.sub(r"^\d{1,2}\s+", "", title)
    for p in NOISE_PATTERNS:
        title = re.sub(p, "", title, flags=re.IGNORECASE)
    title = re.sub(r"\bprod\.?\s+by\b.*$", "", title, flags=re.IGNORECASE)
    title = title.replace("_", " ")
    title = re.sub(r"\s+", " ", title).strip(" .-_,")
    return title


def folder_artist(name: str) -> str:
    value = clean_artist_text(name)
    lower = value.lower()
    for suffix in [" music videos", " videos", " greatest hits", " essentials",
                   " discography", " playlist", " mix", " top songs", " full album list"]:
        if lower.endswith(suffix):
            value = value[: -len(suffix)].strip(" -_,")
            lower = value.lower()
    # Strip bitrate/source tags like "@ 320 (10 Albums)(R_B)(by dragan09)"
    value = re.sub(r"\s*@\s*\d{3}\b.*$", "", value).strip(" -_,")
    # Strip " - ALBUM TITLE (YEAR)..." suffix
    if " - " in value:
        left, right = value.split(" - ", 1)
        if left and any(t in right.lower() for t in ["album", "mixtape", "greatest", "hits", "vol", "mp3", "320"]):
            value = left.strip()
    return value.strip(" -_,")


def canonicalize(name: str, mappings: dict) -> str:
    cleaned = clean_artist_text(name)
    if not cleaned:
        return cleaned
    return mappings["alias_lookup"].get(normalize_key(cleaned), cleaned)


def prefer_display(name: str, mappings: dict) -> str:
    c = canonicalize(name, mappings)
    if c and normalize_key(c) not in BLOCKLIST_ARTISTS:
        return c
    return UNKNOWN_ARTIST


def extract_primary_and_features(credit: str) -> tuple[list[str], list[str]]:
    credit = clean_artist_text(credit)
    if not credit:
        return [], []
    m = FEAT_RE.search(credit)
    if m:
        primary = credit[: m.start()].strip(" -")
        featured = credit[m.end():].strip(" -")
        return split_artists(primary), split_artists(featured)
    return split_artists(credit), []


def split_artists(text: str) -> list[str]:
    parts = re.split(r"\s*[,&x×]\s*|\s+and\s+", text, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]


def first_artist_context(path_parts: list[str], mappings: dict) -> str | None:
    """Walk path parts to find the first artist-like folder name."""
    for part in path_parts[:-1]:  # skip filename
        if is_generic_folder(part):
            continue
        candidate = folder_artist(part)
        if not candidate:
            continue
        canonical = canonicalize(candidate, mappings)
        if canonical and normalize_key(canonical) not in BLOCKLIST_ARTISTS:
            return canonical
    return None


def infer_credit_and_title(path_parts: list[str], filename: str, mappings: dict) -> tuple[str | None, str]:
    context = first_artist_context(path_parts, mappings)
    title = clean_title(filename)
    if " - " in title:
        prefix, suffix = title.split(" - ", 1)
        prefix_clean = clean_artist_text(prefix)
        suffix_clean = clean_title(suffix)
        if prefix_clean and len(prefix_clean.split()) <= 6:
            if not context or normalize_key(prefix_clean) != normalize_key(context):
                return prefix_clean, suffix_clean
            return context, suffix_clean
    return context, title


def scan_rnb(mappings: dict) -> list[dict]:
    songs = []
    song_id = 0
    for audio_file in sorted(RNB_ROOT.rglob("*")):
        if audio_file.suffix.lower() not in AUDIO_EXTS:
            continue
        rel = audio_file.relative_to(ZENE)
        parts = list(rel.parts)

        credit_str, title = infer_credit_and_title(parts, audio_file.name, mappings)
        if credit_str:
            primary_raw, feat_raw = extract_primary_and_features(credit_str)
        else:
            primary_raw, feat_raw = [], []

        # Also check filename for featuring
        if not feat_raw:
            _, feat_from_title = extract_primary_and_features(title)
            if feat_from_title:
                feat_raw = feat_from_title
                # Clean title of feat part
                title = FEAT_RE.split(title)[0].strip(" -,")

        primary = [prefer_display(a, mappings) for a in primary_raw if prefer_display(a, mappings) != UNKNOWN_ARTIST]
        featuring = [prefer_display(a, mappings) for a in feat_raw if prefer_display(a, mappings) != UNKNOWN_ARTIST]

        if not primary:
            primary = [UNKNOWN_ARTIST]

        # Check if primary is a group
        credits = []
        all_artists = []
        for a in primary:
            group_name = mappings["group_lookup"].get(normalize_key(a))
            if group_name and group_name in mappings["groups"]:
                credits.append({"entity": group_name, "entity_type": "group", "role": "primary"})
                for member in mappings["groups"][group_name]:
                    if member not in all_artists:
                        all_artists.append(member)
            else:
                credits.append({"entity": a, "entity_type": "person", "role": "primary"})
                if a not in all_artists:
                    all_artists.append(a)

        for a in featuring:
            credits.append({"entity": a, "entity_type": "person", "role": "feature"})
            if a not in all_artists:
                all_artists.append(a)

        song_id += 1
        songs.append({
            "song_id": f"r-{song_id:05d}",
            "file": str(rel),
            "title": title,
            "primary_artists": primary,
            "featuring_artists": featuring,
            "artists": all_artists,
            "credits": credits,
            "attribution_status": "attributed" if primary[0] != UNKNOWN_ARTIST else "unattributed",
        })

    return songs


def build_persons(songs: list[dict], mappings: dict) -> dict:
    persons: dict[str, dict] = {}
    groups = mappings.get("groups", {})
    group_members_map = {g: set(m) for g, m in groups.items()}

    for s in songs:
        for credit in s["credits"]:
            if credit["entity_type"] == "person" and credit["entity"] != UNKNOWN_ARTIST:
                name = credit["entity"]
                p = persons.setdefault(name, {
                    "song_ids": [], "primary_song_ids": [], "feature_song_ids": [], "via_group_song_ids": [], "groups": []
                })
                if s["song_id"] not in p["song_ids"]:
                    p["song_ids"].append(s["song_id"])
                if credit["role"] == "primary":
                    p["primary_song_ids"].append(s["song_id"])
                else:
                    p["feature_song_ids"].append(s["song_id"])
            elif credit["entity_type"] == "group":
                gname = credit["entity"]
                members = group_members_map.get(gname, set())
                for member in members:
                    p = persons.setdefault(member, {
                        "song_ids": [], "primary_song_ids": [], "feature_song_ids": [], "via_group_song_ids": [], "groups": []
                    })
                    if s["song_id"] not in p["song_ids"]:
                        p["song_ids"].append(s["song_id"])
                    p["via_group_song_ids"].append(s["song_id"])
                    if gname not in p["groups"]:
                        p["groups"].append(gname)
    return persons


def build_groups(songs: list[dict], mappings: dict) -> dict:
    groups_out = {}
    for gname, members in mappings.get("groups", {}).items():
        song_ids = []
        for s in songs:
            if any(c["entity"] == gname and c["entity_type"] == "group" for c in s["credits"]):
                song_ids.append(s["song_id"])
        if song_ids:
            groups_out[gname] = {"members": members, "song_ids": song_ids}
    return groups_out


def main():
    NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)
    mappings = load_mappings()
    songs = scan_rnb(mappings)
    persons = build_persons(songs, mappings)
    groups = build_groups(songs, mappings)

    unattributed = sum(1 for s in songs if s["attribution_status"] == "unattributed")

    metadata = {
        "song_count": len(songs),
        "person_count": len(persons),
        "group_count": len(groups),
        "unattributed_count": unattributed,
    }

    for name, data in [("songs.json", songs), ("persons.json", persons),
                       ("groups.json", groups), ("metadata.json", metadata)]:
        (NORMALIZED_DIR / name).write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    print(f"Songs: {len(songs)}")
    print(f"Persons: {len(persons)}")
    print(f"Groups: {len(groups)}")
    print(f"Unattributed: {unattributed}")

    # Show top artists
    ranked = sorted(persons.items(), key=lambda x: -len(x[1]["song_ids"]))
    print("\nTop 20 artists:")
    for name, p in ranked[:20]:
        print(f"  {len(p['song_ids']):3d}  {name}")


if __name__ == "__main__":
    main()
