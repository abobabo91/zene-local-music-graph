import json, sys
sys.stdout.reconfigure(encoding='utf-8')

for area in ['us','rnb','rock','magyar','elektro','pop','alternate','latino']:
    p = json.loads(open(f'data/{area}/normalized/persons.json', encoding='utf-8').read())
    issues = []
    for name in sorted(p):
        words = name.split()
        songs = len(p[name].get('song_ids', []))
        is_long = len(words) >= 4
        has_dash = " - " in name
        has_kw = any(w.lower() in ['vol','album','full','mp3','320','deluxe','edition',
            'remastered','soundtrack','compilation','best','hits','discography',
            'presents','collection','official'] for w in words)
        if is_long or has_dash or has_kw:
            issues.append((name, songs))
    if issues:
        print(f"\n=== {area.upper()} ({len(issues)}) ===")
        for name, songs in sorted(issues, key=lambda x: -x[1]):
            print(f"  {songs:3d}  {name}")
