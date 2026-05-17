"""Find songs in compilation/playlist folders and plan moves to artist folders."""
import json
import os
import re
from pathlib import Path
from collections import defaultdict

ZENE = Path(r"C:\Users\abele\Desktop\zene")
DATA = Path(__file__).parent / "data"
AREAS = ["us", "rnb", "rock", "magyar", "elektro", "pop", "alternate", "latino"]

COMPILATION_FOLDER_PATTERNS = [
    r"^_random$", r"^random$", r"^_usa random$", r"^_usa other$",
    r"^_other country random$", r"^_modern$", r"^_oldschool", r"^_billboard$",
    r"^_kpop$", r"^_chill$", r"^_psychedelic", r"^_youtube$",
    r"\bmix\b", r"\bplaylist\b", r"\bbest of\b", r"\bgreatest hits\b",
    r"\bbillboard\b", r"\btop \d+", r"\bhiphoptxl\b", r"\bwshh\b",
    r"\bdatpiff\b", r"\bsoundtrack\b", r"\brap caviar\b",
    r"\bsmooth vibin\b", r"\bbedtime\b", r"\b90s\b", r"\b2000s\b",
    r"\bold dance\b", r"\bclub dance\b", r"\bedm fever\b",
    r"\bdeep house\b", r"\bchill\b.*\bhouse\b", r"\bafro house\b",
    r"\bmelodic techno\b", r"\bibiza\b", r"\bparty\b",
    r"^deep$", r"^house$", r"^techno$", r"^acid$", r"^hardcore$",
    r"^elektro$", r"^electro pop$", r"^top$", r"^pop dance$",
    r"^\d{4}$",  # year folders
    r"^magyar pop", r"^magyar random", r"^nemzeti rock",
    r"^_mulatós$", r"^_oldschool$", r"^_retro$",
    r"\brap caviar\b", r"\brnb heaven\b", r"\brb heaven\b",
    r"\bsexplicit\b", r"\bvol\b.*\bdatpiff\b",
]

def is_compilation_folder(folder_name):
    low = folder_name.lower()
    return any(re.search(p, low) for p in COMPILATION_FOLDER_PATTERNS)


def norm_artist(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def find_artist_folders():
    """Scan disk to find where each artist has a dedicated folder."""
    artist_folders = {}  # norm_name -> (full_path, display_name)

    # Scan known genre root folders for artist subfolders
    genre_roots = [
        ZENE / "_rap", ZENE / "_trap",
        ZENE / "_magyar rap", ZENE / "_magyar trap",
        ZENE / "_other" / "_rnb",
        ZENE / "_other" / "_rock",
        ZENE / "_other" / "_pop",
        ZENE / "_other" / "_alternate",
        ZENE / "_other" / "_latino",
        ZENE / "_other" / "_elektro",
        ZENE / "_other" / "_magyar",
    ]

    for root in genre_roots:
        if not root.exists():
            continue
        for dirpath, dirs, files in os.walk(root):
            depth = len(Path(dirpath).relative_to(root).parts)
            if depth > 3:  # don't go too deep
                continue
            for d in dirs:
                if d.startswith("_") or d.startswith("."):
                    continue
                if is_compilation_folder(d):
                    continue
                if re.match(r"^\d{4}$", d):  # year folder
                    continue
                full = Path(dirpath) / d
                key = norm_artist(d)
                if len(key) > 2:
                    # Clean folder name for display
                    cleaned = re.sub(r"\s*[-_]\s*(discography|greatest hits|best of|playlist|youtube|top songs|essentials|music videos).*$", "", d, flags=re.IGNORECASE).strip()
                    cleaned = re.sub(r"\s*@\s*\d{3}.*$", "", cleaned).strip()
                    cleaned = re.sub(r"\s*\(\d{4}.*$", "", cleaned).strip()
                    norm_cleaned = norm_artist(cleaned)
                    if norm_cleaned not in artist_folders:
                        artist_folders[norm_cleaned] = (str(full), cleaned)

    return artist_folders


def main():
    print("Finding artist folders on disk...")
    artist_folders = find_artist_folders()
    print(f"Found {len(artist_folders)} artist folders")

    print("Reading song data...")
    all_songs = []
    for area in AREAS:
        songs_path = DATA / area / "normalized" / "songs.json"
        if not songs_path.exists():
            continue
        songs = json.loads(songs_path.read_text(encoding="utf-8"))
        for s in songs:
            s["_area"] = area
            all_songs.append(s)

    print(f"Total songs: {len(all_songs)}")

    # Find songs in compilation folders that have a known artist with a folder
    moves = []
    no_folder = defaultdict(list)  # artist -> songs (no folder exists)

    for s in all_songs:
        primary = [a for a in s.get("primary_artists", []) if a != "N/A"]
        if not primary:
            continue
        artist = primary[0]
        path = s["file"]
        parts = Path(path).parts

        # Check if any folder in the path is a compilation folder
        in_compilation = False
        for part in parts[:-1]:
            if is_compilation_folder(part):
                in_compilation = True
                break

        if not in_compilation:
            continue

        # Check if this artist already lives in the path (their own subfolder)
        na = norm_artist(artist)
        path_has_artist = any(norm_artist(p) == na for p in parts[:-1])
        if path_has_artist:
            continue  # song is in a compilation INSIDE the artist's own folder tree

        # Check if artist has a dedicated folder elsewhere
        if na in artist_folders:
            dest_folder, dest_name = artist_folders[na]
            src = str(ZENE / path)
            filename = parts[-1]
            dst = os.path.join(dest_folder, filename)

            # Skip if destination already exists
            if os.path.exists(dst):
                continue

            moves.append({
                "artist": artist,
                "src": path,
                "dst": str(Path(dst).relative_to(ZENE)),
                "dst_folder": dest_name,
                "area": s["_area"],
            })
        else:
            no_folder[artist].append(path)

    # Write plan
    lines = [
        "# Song Reorganization Plan", "",
        f"Songs in compilation/playlist folders that can be moved to artist folders.", "",
        f"- **Moveable**: {len(moves)} songs (artist folder exists)",
        f"- **No folder**: {len(no_folder)} artists with {sum(len(v) for v in no_folder.values())} songs (would need new folders)",
        "",
    ]

    # Group moves by artist
    by_artist = defaultdict(list)
    for m in moves:
        by_artist[m["artist"]].append(m)

    lines.append(f"## Moveable songs ({len(moves)} songs, {len(by_artist)} artists)")
    lines.append("")
    for artist in sorted(by_artist, key=lambda a: -len(by_artist[a])):
        items = by_artist[artist]
        lines.append(f"### {artist} -> {items[0]['dst_folder']}/ ({len(items)} songs)")
        for m in items:
            lines.append(f"  - {m['src']}")
        lines.append("")

    # No-folder artists (informational)
    lines.append(f"## No artist folder exists ({len(no_folder)} artists)")
    lines.append("")
    for artist in sorted(no_folder, key=lambda a: -len(no_folder[a])):
        songs = no_folder[artist]
        if len(songs) >= 2:  # only show artists with 2+ songs
            lines.append(f"- **{artist}** ({len(songs)} songs)")

    out = Path(__file__).parent / "reorg_plan.md"
    out.write_text("\n".join(lines), encoding="utf-8")

    # Also write machine-readable move list
    with open(Path(__file__).parent / "reorg_moves.txt", "w", encoding="utf-8") as f:
        for m in moves:
            f.write(f"{m['src']} -> {m['dst']}\n")

    print(f"\nMoveable: {len(moves)} songs to {len(by_artist)} artist folders")
    print(f"No folder: {sum(len(v) for v in no_folder.values())} songs for {len(no_folder)} artists")
    print(f"\nFiles: reorg_plan.md, reorg_moves.txt")


if __name__ == "__main__":
    main()
