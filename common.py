"""Shared constants and utilities for local-music-graph scripts."""
from __future__ import annotations

import re
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_ROOT = PROJECT_ROOT / "data"
ZENE = Path(r"C:\Users\abele\Desktop\zene")

# ── Constants ──────────────────────────────────────────────────────────────────
AUDIO_EXTS = {".mp3", ".wma", ".wav", ".m4a", ".flac"}

# ── Regexes ────────────────────────────────────────────────────────────────────
FEAT_RE = re.compile(r"\b(?:feat\.?|ft\.?|featuring|with|w\/)\b", re.IGNORECASE)
UNICODE_DASH_RE = re.compile(r"[–—]+")

NOISE_PATTERNS = [
    r"\(DatPiff\.com\)", r"\[DatPiff.*?\]", r"\[www\..*?\]",
    r"\bOfficial Music Video\b", r"\bOfficial Video\b", r"\bOfficial Audio\b",
    r"\bOfficial Lyric Video\b", r"\bOfficial Visualizer\b",
    r"\bOFFICIAL VIDEO\b", r"\bOFFICIAL AUDIO\b",
    r"\bWSHH\s+Exclusive\b.*", r"\bWSHH\s+Premiere\b.*", r"\bWSHH\b",
    r"\bHD\b", r"\bHQ\b", r"\[\d{3}\]", r"\(\d{3}\)",
    r"\bVideo Oficial\b", r"\bvideo oficial\b", r"\bClip Officiel\b",
    r"\bvideoclip oficial\b", r"\bOfficiel\b",
    r"\(Original Mix\)", r"\(Radio Edit\)", r"\(Extended Mix\)",
    r"\[NCS Release\]", r"\[NCS\]",
    r"\bOriginal Mix\b", r"\bRadio Edit\b",
    r"\bFull Version\b", r"\bLyric Video\b", r"\bLyrics\b",
]

_ACCENT_MAP = str.maketrans(
    "áàâäãåéèêëíìîïóòôöõőúùûüűýñçšž",
    "aaaaaaeeeeiiiioooooouuuuuyncsz",
)


# ── Text utilities ─────────────────────────────────────────────────────────────

def normalize_key(text: str) -> str:
    value = text.lower().replace("_", " ").replace("&", " and ")
    value = value.translate(_ACCENT_MAP)
    value = re.sub(r"[^a-z0-9+]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def clean_artist_text(text: str) -> str:
    value = UNICODE_DASH_RE.sub("-", text).replace("_", " ").strip()
    value = re.sub(r"\(.*?datpiff.*?\)", "", value, flags=re.IGNORECASE)
    value = re.sub(r"\(.*?\)", "", value)
    value = re.sub(r"\[.*?\]", "", value)
    value = value.replace("\u2019", "'")
    return re.sub(r"\s+", " ", value).strip(" .-_,")


def clean_title(filename: str) -> str:
    title = UNICODE_DASH_RE.sub("-", Path(filename).stem)
    # Strip billboard-style "YYYY-NNN " or "NNN-" prefixes
    title = re.sub(r"^\d{4}[-_]\d{2,3}\s+", "", title)
    title = re.sub(r"^\d{2,3}[-._]\s*", "", title)
    title = re.sub(r"^\d{1,2}\s*[-._)]\s*", "", title)
    title = re.sub(r"^\d{1,2}\s+", "", title)
    for p in NOISE_PATTERNS:
        title = re.sub(p, "", title, flags=re.IGNORECASE)
    title = re.sub(r"\bprod\.?\s+by\b.*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\bproduced by\b.*$", "", title, flags=re.IGNORECASE)
    title = title.replace("_", " ")
    # Only strip leading "NN - rest" if rest doesn't start with a digit and has
    # no further " - " (avoids mangling "50 Cent - In Da Club")
    m = re.match(r"^(\d{1,2})\s*-\s*(.+)$", title)
    if m:
        first_char = m.group(2).strip()[:1] if m.group(2).strip() else ""
        if not first_char.isdigit():
            remainder = m.group(2).strip()
            if " - " not in remainder:
                title = remainder
    return re.sub(r"\s+", " ", title).strip(" .-_,")


def folder_artist(name: str) -> str:
    value = clean_artist_text(name)
    lower = value.lower()
    # Strip " - YouTube" suffix
    if lower.endswith(" - youtube"):
        value = value[:-len(" - YouTube")].strip(" -_,")
        lower = value.lower()
    for suffix in [
        " music videos", " videos", " greatest hits", " essentials",
        " discography", " playlist", " mix", " top songs", " full album list",
        " top tracks playlist", " best songs", " official music videos",
        " videoklippek", " video klippek", " hivatalos videoklipek",
        " válogatás", " zenék", " dalai", " hivatalos", " vevo",
    ]:
        if lower.endswith(suffix):
            value = value[:-len(suffix)].strip(" -_,")
            lower = value.lower()
    # Strip video-platform markers anywhere in the name
    for marker in [r"\bwshh exclusive\b", r"\bofficial video\b",
                   r"\bofficial music video\b"]:
        value = re.sub(marker, "", value, flags=re.IGNORECASE).strip(" -_,")
    lower = value.lower()
    # Strip "Mix – " prefix (YouTube autoplay folders)
    if lower.startswith("mix \u2013 ") or lower.startswith("mix - "):
        value = value[6:].strip(" -_,")
        lower = value.lower()
    # Strip "Legnépszerűbb számok -- " prefix (Hungarian YouTube)
    if "legnépszerűbb" in lower or "top-titel" in lower:
        if " -- " in value:
            value = value.split(" -- ", 1)[1].strip(" -_,")
        elif " \u2013 " in value:
            value = value.split(" \u2013 ", 1)[1].strip(" -_,")
        lower = value.lower()
    value = re.sub(r"\s*@\s*\d{3}\b.*$", "", value).strip(" -_,")
    value = re.sub(r"\s*\(\d{4}(?:-\d{4})?\)\s*(?:\(\d+\))?.*$", "", value).strip(" -_,")
    value = re.sub(r"\s*\(\d{4}\)\s*(?:Mp3|mp3).*$", "", value).strip(" -_,")
    if " - " in value:
        left, right = value.split(" - ", 1)
        if left and any(t in right.lower() for t in [
            "album", "mixtape", "greatest", "hits", "vol", "mp3", "320",
            "best of", "discography", "complete", "the best", "collection",
            "a legjobb", "válogatás", "full", "edition",
        ]):
            value = left.strip()
    return value.strip(" -_,")


def split_artists(text: str) -> list[str]:
    parts = re.split(r"\s*[,&/×]\s*|\s+x\s+|\s+and\s+", text, flags=re.IGNORECASE)
    return [clean_artist_text(p) for p in parts if clean_artist_text(p)]


def extract_primary_and_features(credit: str) -> tuple[list[str], list[str]]:
    credit = clean_artist_text(credit)
    if not credit:
        return [], []
    m = FEAT_RE.search(credit)
    if m:
        primary = credit[:m.start()].strip(" -")
        featured = credit[m.end():].strip(" -")
        return split_artists(primary), split_artists(featured)
    return split_artists(credit), []


# ── Mapping parser ─────────────────────────────────────────────────────────────

def parse_mapping_block(lines: list[str]) -> dict[str, list[str]]:
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
        values = [v.strip() for v in right.split(",") if v.strip()]
        if left:
            results[left] = values
    return results


# ── Junk detection ─────────────────────────────────────────────────────────────

def is_junk_name(name: str, key: str, blocklist: set[str]) -> bool:
    if key in blocklist:
        return True
    if re.match(r"^\d+$", key):
        return True
    if re.match(r"^\d{1,3}\s+", key):
        return True
    if re.match(r"^\d{1,3}\.\s+", key):
        return True
    if re.match(r"^\d{4}\s*-\s*\d{2,3}\s+", key):
        return True
    if "(" in name and ")" not in name:
        return True
    if re.match(r"^\d{1,2}\s*-\s*", key):
        return True
    if len(key) <= 1:
        return True
    if any(ord(c) > 8000 for c in name):
        return True
    return False
