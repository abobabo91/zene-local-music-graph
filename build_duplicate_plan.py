"""Generate a duplicate cleanup action plan based on user preferences:
- Keep files in artist folders (album subfolders preferred over playlists/mixes)
- For same quality: delete the playlist/mix copy
- For different quality: keep higher bitrate, move to artist folder if needed
"""
import os
import re
from pathlib import Path
from collections import defaultdict

ZENE = Path(r"C:\Users\abele\Desktop\zene")
SKIP = {"new", "new good", "_music_scripts", "_playlists"}
AUDIO_EXTS = {".mp3", ".wma", ".wav", ".m4a", ".flac"}
OUT = Path(__file__).parent

PLAYLIST_PATTERNS = [
    r"\bmix\b", r"\bplaylist\b", r"\bbest of\b", r"\bgreatest hits\b",
    r"\bbillboard\b", r"\btop \d+", r"\bchill\b", r"\brelax\b",
    r"\brandom\b", r"\b_random\b", r"\bvarious\b", r"\bcompilation\b",
    r"\bsoundtrack\b", r"\bessentials\b", r"\bcollection\b",
    r"\byoutube\b", r"\b_usa random\b", r"\b_usa other\b",
    r"\b_other country random\b", r"\brap caviar\b",
]


def is_playlist_path(path_str):
    low = path_str.lower()
    return any(re.search(p, low) for p in PLAYLIST_PATTERNS)


def path_score(path_str):
    parts = Path(path_str).parts
    if is_playlist_path(path_str):
        return 0
    depth = len(parts)
    if depth >= 5:
        return 3  # artist/album/file
    if depth >= 4:
        return 2  # artist/file
    return 1


def get_duration(path):
    try:
        from mutagen import File
        f = File(path)
        if f and f.info:
            return round(f.info.length, 1)
    except Exception:
        pass
    return None


def norm(name):
    name = Path(name).stem.lower()
    name = re.sub(r"^\d{1,3}[\s._)-]+", "", name)
    for p in [r"\(official.*?\)", r"\(audio\)", r"\(lyric.*?\)", r"\(prod\.?.*?\)",
              r"\[.*?\]", r"\(feat\.?.*?\)", r"\bft\.?\b.*"]:
        name = re.sub(p, "", name)
    name = re.sub(r"[^a-z0-9 ]", " ", name)
    return re.sub(r"\s+", " ", name).strip()


def has_remix(name):
    t = name.lower()
    return any(x in t for x in ["remix", "refix", "bootleg", "rework", "acoustic",
        "live", "instrumental", "acapella", "cover", "remaster", "demo", "vip mix"])


def fmt_size(s):
    return f"{s/1024/1024:.1f}MB" if s > 1024*1024 else f"{s/1024:.0f}KB"


def main():
    print("Scanning...")
    all_files = []
    for dirpath, dirs, files in os.walk(ZENE):
        rel = Path(dirpath).relative_to(ZENE)
        if rel.parts and rel.parts[0] in SKIP:
            continue
        for f in files:
            if Path(f).suffix.lower() in AUDIO_EXTS:
                full = Path(dirpath) / f
                try:
                    size = full.stat().st_size
                except Exception:
                    continue
                all_files.append({"path": str(full.relative_to(ZENE)), "full": str(full),
                                  "name": f, "size": size})

    print(f"{len(all_files)} files. Grouping...")
    by_name = defaultdict(list)
    for f in all_files:
        key = norm(f["name"])
        if len(key) > 5:
            by_name[key].append(f)

    dupes = {k: v for k, v in by_name.items() if len(v) >= 2}

    print(f"{len(dupes)} groups. Reading durations...")
    n = 0
    for key, files in dupes.items():
        for f in files:
            f["duration"] = get_duration(f["full"])
            f["score"] = path_score(f["path"])
            n += 1
            if n % 200 == 0:
                print(f"  {n}...")

    print("Building action plan...")
    to_delete = []
    to_move = []
    exact_actions = []
    quality_actions = []

    for key, files in dupes.items():
        remix_flags = [has_remix(f["name"]) for f in files]
        if any(remix_flags) and not all(remix_flags):
            continue

        durations = [f["duration"] for f in files]
        sizes = [f["size"] for f in files]

        if any(d is None for d in durations):
            continue

        min_d, max_d = min(durations), max(durations)
        if max_d - min_d > 5.0:
            continue

        ranked = sorted(files, key=lambda f: (-f["score"], -f["size"]))
        keep = ranked[0]
        remove = ranked[1:]

        if max_d - min_d <= 1.0 and max(sizes) - min(sizes) < min(sizes) * 0.05:
            for r in remove:
                to_delete.append(r["path"])
            exact_actions.append((key, keep, remove))
        elif max_d - min_d <= 1.0:
            biggest = max(files, key=lambda f: f["size"])
            best_loc = max(files, key=lambda f: f["score"])

            if biggest == best_loc or biggest["score"] >= best_loc["score"]:
                for f in files:
                    if f != biggest:
                        to_delete.append(f["path"])
                quality_actions.append(("keep", key, biggest, [f for f in files if f != biggest]))
            else:
                dst_dir = str(Path(best_loc["path"]).parent)
                dst_path = str(Path(dst_dir) / biggest["name"])
                to_move.append((biggest["path"], dst_path))
                for f in files:
                    if f != biggest:
                        to_delete.append(f["path"])
                quality_actions.append(("move", key, biggest, best_loc, [f for f in files if f != biggest]))

    # Write plan
    lines = ["# Duplicate Cleanup Action Plan", "",
        f"- Files to DELETE: {len(to_delete)}",
        f"- Files to MOVE (better quality to artist folder): {len(to_move)}",
        f"- Exact duplicate groups: {len(exact_actions)}",
        f"- Quality upgrade groups: {len(quality_actions)}", ""]

    lines.append(f"## EXACT duplicates ({len(exact_actions)} groups)")
    lines.append("")
    for key, keep, remove in exact_actions:
        lines.append(f"### {key}")
        lines.append(f"  KEEP: {keep['path']} ({fmt_size(keep['size'])}, score:{keep['score']})")
        for r in remove:
            lines.append(f"  DELETE: {r['path']} ({fmt_size(r['size'])})")
        lines.append("")

    lines.append(f"## Quality upgrades ({len(quality_actions)} groups)")
    lines.append("")
    for action in quality_actions:
        if action[0] == "keep":
            _, key, best, others = action
            lines.append(f"### {key}")
            lines.append(f"  KEEP: {best['path']} ({fmt_size(best['size'])})")
            for o in others:
                lines.append(f"  DELETE: {o['path']} ({fmt_size(o['size'])})")
            lines.append("")
        else:
            _, key, best, good_loc, others = action
            lines.append(f"### {key}")
            lines.append(f"  MOVE: {best['path']} ({fmt_size(best['size'])}) -> {str(Path(good_loc['path']).parent)}/")
            for o in others:
                lines.append(f"  DELETE: {o['path']} ({fmt_size(o['size'])})")
            lines.append("")

    (OUT / "duplicates_action_plan.md").write_text("\n".join(lines), encoding="utf-8")

    with open(OUT / "duplicates_delete.txt", "w", encoding="utf-8") as f:
        for p in to_delete:
            f.write(p + "\n")

    with open(OUT / "duplicates_move.txt", "w", encoding="utf-8") as f:
        for src, dst in to_move:
            f.write(f"{src} -> {dst}\n")

    print(f"\nDELETE: {len(to_delete)} files")
    print(f"MOVE: {len(to_move)} files")
    print(f"Exact: {len(exact_actions)} groups")
    print(f"Quality: {len(quality_actions)} groups")


if __name__ == "__main__":
    main()
