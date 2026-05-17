"""Execute the duplicate cleanup: delete extras, move higher quality to artist folders."""
import os
import shutil
from pathlib import Path

ZENE = Path(r"C:\Users\abele\Desktop\zene")
HERE = Path(__file__).parent
SKIP_PATTERNS = ["ROCKSTAR [256]"]


def main():
    # Read delete list
    delete_list = []
    skipped = 0
    with open(HERE / "duplicates_delete.txt", encoding="utf-8") as f:
        for line in f:
            path = line.strip()
            if not path:
                continue
            if any(s in path for s in SKIP_PATTERNS):
                skipped += 1
                continue
            delete_list.append(path)

    # Read move list
    move_list = []
    with open(HERE / "duplicates_move.txt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if any(s in line for s in SKIP_PATTERNS):
                skipped += 1
                continue
            parts = line.split(" -> ")
            if len(parts) == 2:
                move_list.append((parts[0].strip(), parts[1].strip()))

    print(f"DELETE: {len(delete_list)} files")
    print(f"MOVE: {len(move_list)} files")
    print(f"Skipped (ROCKSTAR): {skipped}")

    # Execute moves first
    moved = 0
    move_errors = 0
    for src, dst in move_list:
        src_full = ZENE / src
        dst_full = ZENE / dst
        if not src_full.exists():
            move_errors += 1
            continue
        dst_full.parent.mkdir(parents=True, exist_ok=True)
        if dst_full.exists():
            move_errors += 1
            continue
        shutil.move(str(src_full), str(dst_full))
        moved += 1

    # Execute deletes
    deleted = 0
    not_found = 0
    for path in delete_list:
        full = ZENE / path
        if full.exists():
            full.unlink()
            deleted += 1
        else:
            not_found += 1

    print(f"\nResults:")
    print(f"  Moved: {moved}/{len(move_list)} (errors: {move_errors})")
    print(f"  Deleted: {deleted}/{len(delete_list)} (not found: {not_found})")


if __name__ == "__main__":
    main()
