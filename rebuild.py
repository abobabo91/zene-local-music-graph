"""Rebuild all areas, toplists, and visualization. Only rebuilds what changed."""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ZENE = Path(r"C:\Users\abele\Desktop\zene")
DATA = HERE / "data"
STATE_FILE = HERE / ".last_rebuild"

SCAN_ROOTS = {
    "us": [ZENE / "_rap", ZENE / "_trap"],
    "rnb": [ZENE / "_other" / "_rnb"],
    "rock": [ZENE / "_other" / "_rock"],
    "magyar": [ZENE / "_other" / "_magyar"],
    "elektro": [ZENE / "_other" / "_elektro"],
    "pop": [ZENE / "_other" / "_pop"],
    "alternate": [ZENE / "_other" / "_alternate"],
    "latino": [ZENE / "_other" / "_latino"],
}
AUDIO_EXTS = {".mp3", ".wma", ".wav", ".m4a", ".flac"}


def get_last_rebuild() -> float:
    if STATE_FILE.exists():
        return float(STATE_FILE.read_text().strip())
    return 0.0


def save_rebuild_time(t: float):
    STATE_FILE.write_text(str(t))


def has_changes(roots: list[Path], since: float, area: str) -> bool:
    # Check for new/modified files
    for root in roots:
        if not root.exists():
            continue
        for dirpath, _, files in os.walk(root):
            for f in files:
                if Path(f).suffix.lower() in AUDIO_EXTS:
                    full = Path(dirpath) / f
                    try:
                        if full.stat().st_mtime > since:
                            return True
                    except OSError:
                        continue
    # Check for moved/deleted files (paths in songs.json that no longer exist on disk)
    songs_path = DATA / area / "normalized" / "songs.json"
    if songs_path.exists():
        songs = json.loads(songs_path.read_text(encoding="utf-8"))
        for s in songs:
            if not (ZENE / s["file"]).exists():
                return True  # a file was moved or deleted
    return False


def run(cmd: list[str], desc: str):
    print(f"  {desc}...")
    r = subprocess.run([sys.executable] + cmd, cwd=str(HERE), capture_output=True, text=True)
    if r.returncode != 0:
        print(f"    ERROR: {r.stderr[:200]}")
    else:
        # Print first line of output (summary)
        first = r.stdout.strip().split("\n")[0] if r.stdout.strip() else "done"
        print(f"    {first}")


def main():
    last = get_last_rebuild()
    now = os.path.getmtime(__file__)  # use current time
    import time
    now = time.time()

    if last > 0:
        from datetime import datetime
        print(f"Last rebuild: {datetime.fromtimestamp(last).strftime('%Y-%m-%d %H:%M')}")
    else:
        print("First run — rebuilding everything.")

    changed = []
    for area, roots in SCAN_ROOTS.items():
        if last == 0 or has_changes(roots, last, area):
            changed.append(area)

    if not changed:
        print("No changes detected. Nothing to rebuild.")
        return

    print(f"Changes detected in: {', '.join(changed)}")

    # Rebuild changed areas
    for area in changed:
        if area == "us":
            run(["build_us_graph.py"], f"US rap/trap")
        else:
            run(["build_other_graph.py", area], f"{area}")

    # Always rebuild toplists + visualization if anything changed
    run(["build_toplists.py"], "Toplists")
    run(["build_visualization.py"], "Visualization")

    # Copy visualization as index.html for GitHub Pages
    viz = HERE / "visualization.html"
    idx = HERE / "index.html"
    if viz.exists():
        idx.write_bytes(viz.read_bytes())

    save_rebuild_time(now)

    # Git commit + push if there are changes
    r = subprocess.run(["git", "status", "--porcelain"], cwd=str(HERE), capture_output=True, text=True)
    if r.stdout.strip():
        print("\nCommitting and pushing...")
        subprocess.run(["git", "add", "-A"], cwd=str(HERE))
        subprocess.run(["git", "commit", "-m", "Rebuild: " + ", ".join(changed)], cwd=str(HERE))
        subprocess.run(["git", "push"], cwd=str(HERE))
        print("Pushed to GitHub.")
    else:
        print("\nNo data changes to commit.")


if __name__ == "__main__":
    main()
