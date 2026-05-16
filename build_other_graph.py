"""
Generic scanner for _other/ subfolders (rock, magyar, latino, rnb).
Usage: python build_other_graph.py <area>
Areas: rock, magyar, latino, rnb
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_ROOT = PROJECT_ROOT / "data"
ZENE = Path(r"C:\Users\abele\Desktop\zene")

AUDIO_EXTS = {".mp3", ".wma", ".wav", ".m4a", ".flac"}
FEAT_RE = re.compile(r"\b(?:feat\.?|ft\.?|featuring|with|w\/)\b", re.IGNORECASE)
UNICODE_DASH_RE = re.compile(r"[–—]+")
NOISE_PATTERNS = [
    r"\(DatPiff\.com\)", r"\[DatPiff.*?\]", r"\[www\..*?\]",
    r"\bOfficial Music Video\b", r"\bOfficial Video\b", r"\bOfficial Audio\b",
    r"\bOfficial Lyric Video\b", r"\bOfficial Visualizer\b",
    r"\bOFFICIAL VIDEO\b", r"\bOFFICIAL AUDIO\b",
    r"\bWSHH\s+Exclusive\b.*", r"\bWSHH\b",
    r"\bHD\b", r"\bHQ\b", r"\[\d{3}\]", r"\(\d{3}\)",
    r"\bVideo Oficial\b", r"\bvideo oficial\b", r"\bClip Officiel\b",
    r"\bvideoclip oficial\b", r"\bOfficiel\b",
]

# ─── Per-area config ───
AREA_CONFIG = {
    "rock": {
        "scan_root": ZENE / "_other" / "_rock",
        "id_prefix": "rk",
        "generic_folders": {
            "_random", "_psychedelic rock", "random", "misc", "videos", "youtube",
            "_other", "_rock", "sled storm soundtrack",
        },
        "blocklist": {
            "n/a", "unknown", "various", "nothing", "you", "me",
            "lyrics", "audio", "download link", "m", "marooned",
            "deafheaven sunbather amusladmin", "green onions ect",
            "best of lou reed",
        },
        "split_groups": set(),
    },
    "magyar": {
        "scan_root": ZENE / "_other" / "_magyar",
        "id_prefix": "mg",
        "generic_folders": {
            "_alternativ", "_cigany", "_modern_pop", "_nepzene", "_pop",
            "_random", "_retro", "_rock", "_magyar", "_other",
            "magyar pop zenek", "magyar pop zenék", "magyar random",
            "nemzeti rock", "_mulatós", "music - youtube",
            "1990-2000-es évek magyar retró slágerei",
            "magyar retro zenék - a 60-as - 70-es - 80-as évekből",
        },
        "blocklist": {
            "n/a", "unknown", "various", "nothing", "you", "me",
            "lyrics", "audio", "music",
            "istván a király rockopera", "istván a király rockopera - youtube",
            "járom az utam in my world - youtube", "járom az utam",
            "music - youtube",
            "máramaros the lost jewish music of transylvania - youtube",
            "ez a világ nekem való this world is made for me - youtube",
            "már nem szédülök",
            "amerről hajnallott the prisoner s song - youtube",
            "nem arról hajnallik",
            "rávágok a zongorára hit the piano - youtube",
            "ég az erdő - klemencz kollar laszlo",
        },
        "split_groups": set(),
    },
    "latino": {
        "scan_root": ZENE / "_other" / "_latino",
        "id_prefix": "lt",
        "generic_folders": {
            "_random", "_oldschool", "_latino", "_other", "random", "misc",
            "videos", "youtube", "kizomba",
        },
        "blocklist": {
            "n/a", "unknown", "various", "nothing", "you", "me",
            "lyrics", "audio", "download link",
            "the furious soundtrack live", "the furious soundtrack-live",
            "latin felipe", "latin sabia que no",
        },
        "split_groups": set(),
    },
    "rnb": {
        "scan_root": ZENE / "_other" / "_rnb",
        "id_prefix": "r",
        "generic_folders": {
            "_random", "_modern", "_other", "_rnb", "random", "loose", "misc",
            "videos", "youtube", "90s 00s rnb", "rnb", "bedtime rnb",
            "smooth vibin_", "highline r&b", "rap caviar", "the way you", "other",
        },
        "blocklist": {
            "n/a", "unknown", "various", "nothing", "cd1", "cd2",
            "you", "me", "scape", "audio", "download link", "l ost", "l soundtrack",
            "step up soundtrack", "magic mike", "golden", "sickick", "sickickmusic",
            "lyrics", "lyrics on screen", "alone", "quits", "somebody", "drunk",
            "ne", "t", "bl", "st", "c", "j", "r", "ale", "010",
            "quot takin back my love quot", "wrong",
            "honey soundtrack", "ost magic mike", "rb heaven vol 9", "rnb heaven vol 13",
            "as long as you love me", "kut klose slow jams",
            "geeze so sick", "did you ever think remi",
            "snoop dogg victory in stores now",
            "g o o d music s cyhi the prynce party bullshit",
            "me do it well",
        },
        "split_groups": {"Destiny's Child"},
    },
}


def normalize_key(text: str) -> str:
    value = text.lower().replace("_", " ").replace("&", " and ")
    value = re.sub(r"[^a-z0-9+]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


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
    return re.sub(r"\s+", " ", title).strip(" .-_,")


def folder_artist(name: str) -> str:
    value = clean_artist_text(name)
    lower = value.lower()
    # Strip " - YouTube" suffix first
    if lower.endswith(" - youtube"):
        value = value[:-len(" - YouTube")].strip(" -_,")
        lower = value.lower()
    for suffix in [" music videos", " videos", " greatest hits", " essentials",
                   " discography", " playlist", " mix", " top songs", " full album list",
                   " top tracks playlist", " best songs", " official music videos",
                   " videoklippek", " video klippek", " hivatalos videoklipek",
                   " válogatás", " zenék", " dalai", " hivatalos", " vevo"]:
        if lower.endswith(suffix):
            value = value[: -len(suffix)].strip(" -_,")
            lower = value.lower()
    value = re.sub(r"\s*@\s*\d{3}\b.*$", "", value).strip(" -_,")
    value = re.sub(r"\s*\(\d{4}(?:-\d{4})?\)\s*(?:\(\d+\))?.*$", "", value).strip(" -_,")
    value = re.sub(r"\s*\(\d{4}\)\s*(?:Mp3|mp3).*$", "", value).strip(" -_,")
    if " - " in value:
        left, right = value.split(" - ", 1)
        if left and any(t in right.lower() for t in [
            "album", "mixtape", "greatest", "hits", "vol", "mp3", "320",
            "best of", "discography", "complete", "the best", "collection",
            "a legjobb", "válogatás",
        ]):
            value = left.strip()
    return value.strip(" -_,")


def load_mappings(area: str) -> dict:
    mappings_path = DATA_ROOT / area / f"{area}_mappings.md"
    if not mappings_path.exists():
        return {"alias_lookup": {}, "groups": {}, "group_lookup": {}}
    text = mappings_path.read_text(encoding="utf-8")
    sections: dict[str, list[str]] = defaultdict(list)
    current = None
    for line in text.splitlines():
        stripped = line.rstrip()
        if stripped.startswith("## "):
            current = stripped[3:].strip().lower()
            continue
        if current:
            sections[current].append(stripped)

    alias_map = _parse_mapping_block(sections.get("alias normalization", []))
    groups = _parse_mapping_block(sections.get("groups", []))

    alias_lookup: dict[str, str] = {}
    for canonical, aliases in alias_map.items():
        alias_lookup[normalize_key(canonical)] = canonical
        for alias in aliases:
            alias_lookup[normalize_key(alias)] = canonical

    canonical_groups: dict[str, list[str]] = {}
    for gname, members in groups.items():
        cg = alias_lookup.get(normalize_key(gname), gname)
        cm = [alias_lookup.get(normalize_key(m), m) for m in members]
        canonical_groups[cg] = cm

    return {
        "alias_lookup": alias_lookup,
        "groups": canonical_groups,
        "group_lookup": {normalize_key(g): g for g in canonical_groups},
    }


def _parse_mapping_block(lines: list[str]) -> dict[str, list[str]]:
    results = {}
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
        values = [v.strip() for v in right.split(",") if v.strip()]
        if left:
            results[left] = values
    return results


def is_generic(name: str, config: dict) -> bool:
    key = normalize_key(name)
    generic_keys = {normalize_key(n) for n in config["generic_folders"]}
    return key in generic_keys


def canonicalize(name: str, mappings: dict) -> str:
    cleaned = clean_artist_text(name)
    if not cleaned:
        return cleaned
    return mappings["alias_lookup"].get(normalize_key(cleaned), cleaned)


def _normalized_blocklist(config: dict) -> set[str]:
    return {normalize_key(b) for b in config["blocklist"]}


def prefer_display(name: str, mappings: dict, config: dict) -> str:
    c = canonicalize(name, mappings)
    if c and normalize_key(c) not in _normalized_blocklist(config):
        return c
    return "N/A"


def extract_primary_and_features(credit: str) -> tuple[list[str], list[str]]:
    credit = clean_artist_text(credit)
    if not credit:
        return [], []
    m = FEAT_RE.search(credit)
    if m:
        primary = credit[:m.start()].strip(" -")
        featured = credit[m.end():].strip(" -")
        return _split_artists(primary), _split_artists(featured)
    return _split_artists(credit), []


def _split_artists(text: str) -> list[str]:
    parts = re.split(r"\s*[,&×]\s*|\s+x\s+|\s+and\s+", text, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]


def first_artist_context(path_parts: list[str], mappings: dict, config: dict) -> str | None:
    for part in path_parts[:-1]:
        if is_generic(part, config):
            continue
        candidate = folder_artist(part)
        if not candidate:
            continue
        canonical = canonicalize(candidate, mappings)
        if canonical and normalize_key(canonical) not in _normalized_blocklist(config):
            return canonical
    return None


def infer_credit_and_title(path_parts: list[str], filename: str, mappings: dict, config: dict) -> tuple[str | None, str]:
    context = first_artist_context(path_parts, mappings, config)
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


def scan_area(config: dict, mappings: dict) -> list[dict]:
    songs = []
    sid = 0
    scan_root = config["scan_root"]
    prefix = config["id_prefix"]
    split_groups = config.get("split_groups", set())

    for audio_file in sorted(scan_root.rglob("*")):
        if audio_file.suffix.lower() not in AUDIO_EXTS:
            continue
        rel = audio_file.relative_to(ZENE)
        parts = list(rel.parts)

        credit_str, title = infer_credit_and_title(parts, audio_file.name, mappings, config)
        if credit_str:
            primary_raw, feat_raw = extract_primary_and_features(credit_str)
        else:
            primary_raw, feat_raw = [], []

        if not feat_raw:
            _, feat_from_title = extract_primary_and_features(title)
            if feat_from_title:
                feat_raw = feat_from_title
                title = FEAT_RE.split(title)[0].strip(" -,")

        primary = [prefer_display(a, mappings, config) for a in primary_raw]
        primary = [a for a in primary if a != "N/A"]
        featuring = [prefer_display(a, mappings, config) for a in feat_raw]
        featuring = [a for a in featuring if a != "N/A"]

        if not primary:
            primary = ["N/A"]

        credits = []
        all_artists = []
        for a in primary:
            group_name = mappings["group_lookup"].get(normalize_key(a))
            if group_name and group_name in mappings["groups"]:
                if group_name in split_groups:
                    credits.append({"entity": group_name, "entity_type": "group", "role": "primary"})
                    for member in mappings["groups"][group_name]:
                        if member not in all_artists:
                            all_artists.append(member)
                else:
                    credits.append({"entity": group_name, "entity_type": "person", "role": "primary"})
                    if group_name not in all_artists:
                        all_artists.append(group_name)
            else:
                credits.append({"entity": a, "entity_type": "person", "role": "primary"})
                if a not in all_artists:
                    all_artists.append(a)

        for a in featuring:
            credits.append({"entity": a, "entity_type": "person", "role": "feature"})
            if a not in all_artists:
                all_artists.append(a)

        sid += 1
        songs.append({
            "song_id": f"{prefix}-{sid:05d}",
            "file": str(rel),
            "title": title,
            "primary_artists": primary,
            "featuring_artists": featuring,
            "artists": all_artists,
            "credits": credits,
            "attribution_status": "attributed" if primary[0] != "N/A" else "unattributed",
        })

    return songs


def build_persons(songs: list[dict], mappings: dict, config: dict) -> dict:
    persons: dict[str, dict] = {}
    split_groups = config.get("split_groups", set())
    group_members = {g: set(m) for g, m in mappings.get("groups", {}).items()}

    for s in songs:
        for credit in s["credits"]:
            if credit["entity_type"] == "person" and credit["entity"] != "N/A":
                name = credit["entity"]
                p = persons.setdefault(name, {
                    "song_ids": [], "primary_song_ids": [], "feature_song_ids": [],
                    "via_group_song_ids": [], "groups": []
                })
                if s["song_id"] not in p["song_ids"]:
                    p["song_ids"].append(s["song_id"])
                if credit["role"] == "primary":
                    p["primary_song_ids"].append(s["song_id"])
                else:
                    p["feature_song_ids"].append(s["song_id"])
            elif credit["entity_type"] == "group" and credit["entity"] in split_groups:
                gname = credit["entity"]
                for member in group_members.get(gname, set()):
                    p = persons.setdefault(member, {
                        "song_ids": [], "primary_song_ids": [], "feature_song_ids": [],
                        "via_group_song_ids": [], "groups": []
                    })
                    if s["song_id"] not in p["song_ids"]:
                        p["song_ids"].append(s["song_id"])
                    p["via_group_song_ids"].append(s["song_id"])
                    if gname not in p["groups"]:
                        p["groups"].append(gname)
    return persons


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in AREA_CONFIG:
        print(f"Usage: python {Path(__file__).name} <{'|'.join(AREA_CONFIG)}>")
        return

    area = sys.argv[1]
    config = AREA_CONFIG[area]
    out_dir = DATA_ROOT / area / "normalized"
    out_dir.mkdir(parents=True, exist_ok=True)

    mappings = load_mappings(area)
    songs = scan_area(config, mappings)
    persons = build_persons(songs, mappings, config)
    unattributed = sum(1 for s in songs if s["attribution_status"] == "unattributed")

    metadata = {
        "song_count": len(songs),
        "person_count": len(persons),
        "unattributed_count": unattributed,
    }

    for name, data in [("songs.json", songs), ("persons.json", persons), ("metadata.json", metadata)]:
        (out_dir / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[{area}] Songs: {len(songs)}, Persons: {len(persons)}, Unattributed: {unattributed}")

    ranked = sorted(persons.items(), key=lambda x: -len(x[1]["song_ids"]))
    print(f"\nTop 20:")
    for name, p in ranked[:20]:
        try:
            print(f"  {len(p['song_ids']):3d}  {name}")
        except UnicodeEncodeError:
            print(f"  {len(p['song_ids']):3d}  {name.encode('ascii', 'replace').decode()}")


if __name__ == "__main__":
    main()
