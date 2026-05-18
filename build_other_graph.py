"""
Generic scanner for _other/ subfolders (rock, magyar, latino, rnb, etc.).
Usage: python build_other_graph.py <area>
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

from common import (
    AUDIO_EXTS, DATA_ROOT, FEAT_RE, ZENE,
    clean_artist_text, clean_title, extract_primary_and_features,
    folder_artist, is_junk_name, normalize_key, parse_mapping_block,
)

# ─── Per-area config ───
AREA_CONFIG = {
    "rock": {
        "scan_root": ZENE / "_other" / "_rock",
        "id_prefix": "rk",
        "generic_folders": {
            "_random", "_psychedelic rock", "random", "misc", "videos", "youtube",
            "_other", "_rock", "sled storm soundtrack", "trip",
        },
        "blocklist": {
            "n/a", "unknown", "various", "nothing", "you", "me",
            "lyrics", "audio", "download link", "m", "marooned",
            "deafheaven sunbather amusladmin", "green onions ect",
            "best of lou reed", "scarface soundtrack", "dirty dancing",
            "sled storm soundtrack", "the ultimate psychedelic acid rock",
            "60s 70s stoner psychedelic rock", "psychedelic rock modern",
            "the ultimate pop punk", "mod stuff", "celebration rock",
            "capricorn", "attack", "from yesterday", "hurricane",
            "high hopes", "keep talking", "lost for words", "pigs",
            "cluster one", "crumb", "green onions", "the pretender",
            "love said no", "and life", "inc", "ambiance",
            "sleeping", "sirens", "a curse", "hollywood", "electric blue", "bosnia",
            "i call your name montezuma demo",
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
            "subscribe", "open stage", "premium studio",
            "magyar mulatos zene", "revizios dalok", "vassal rock",
            "szeresd a testem baby", "ha megegyszer lathatnam",
            "omega nepstadion",
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
            "bachata", "latin old academia", "reguetoneo del bueno",
            "deseandote", "ella baila sola", "ella quiere", "la bachata",
            "lejos del cielo", "voice", "the fast", "friday nigh",
            "xtreme my fantasy", "kiznyou productions",
            "oral b image of a pimp", "cardi b taki taki",
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
            "step up 2 soundtrack", "medicine", "flow", "houston", "nathan",
            "claude", "bubba spar", "anderson",
            "2 chainz juicy j chris brown trey songz show me",
            "mariah carey kiss me", "red cafe gucci mane shake dat",
            "tj luva boy new gang", "young blacc in love with the bitches",
            "the weeknd omarion trey songs more rnb heav",
            "frank ocean chris brownlloydcassiedjwispasPre",
            "chris brown usher zayn", "chingy bed",
            "jeremih ftloverance", "jeremih stefflon don krept konan",
            "kelly chris brown", "tyga chris brown",
            "rihanna wiz khalifa", "mac miller anderson paak",
            "major lazer mo justin bieber", "dj mustard nicki minaj jeremih",
            "enrique iglesias tinashe javada", "lil jon machel montano",
            "o t genasis young dolph", "snakehips zayn",
            "christian radke turk", "2 chainz spoaty", "ashanti w biggie",
            "chingy nate dogg", "jacques greene tinashe",
        },
        "split_groups": {"Destiny's Child"},
    },
    "pop": {
        "scan_root": ZENE / "_other" / "_pop",
        "id_prefix": "pp",
        "generic_folders": {
            "_billboard", "_kpop", "_modern", "_oldschool_pop", "_random",
            "_pop", "_other", "random", "misc", "videos", "youtube",
            "groove it you move it", "felicita y mas",
            "00s", "00s - youtube",
            # Billboard year folders
            "1990", "1991", "1992", "1993", "1994", "1995", "1996", "1997",
            "1998", "1999", "2000", "2001", "2002", "2003", "2004", "2005",
            "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013",
            "2014", "2015", "2016", "2017", "2018", "2019", "2020",
        },
        "blocklist": {
            "n/a", "unknown", "various", "nothing", "you", "me",
            "lyrics", "audio", "download link",
            "billboard top 100 hits of 2007",
            "uk hot 100 best of 2014",
            "fifa 2000 soundtrack", "the matrix soundtrack",
            "kpop fav", "quave lyric video",
            "ariana grande ft", "it", "no",
            "lil jon get buck in here", "lil wayne im da man", "lil wayne soldier",
            "uncle charlie wilson beautiful", "ying yang twins get low",
            "christina aguilera tell me", "nino mochella kiss the sky",
            "willa ford willa was here", "eve no", "rimk du 113 deconnectes",
            "lee hi all songs", "the dream throw it in the bag",
            "cassie tyga trey songz wale fabolous diced pineapples",
            "christina aquilera lil kim mya pink",
            "snoop dogg rick ross all i do is win",
        },
        "split_groups": set(),
    },
    "elektro": {
        "scan_root": ZENE / "_other" / "_elektro",
        "id_prefix": "el",
        "generic_folders": {
            "_elektro", "_other", "random", "misc", "videos", "youtube",
            # subgenre folders
            "deep_house", "dnb_dubstep", "edm_electronic_pop", "experimental",
            "experimental_chill", "goa_psytrance", "hardcore_hardstyle",
            "house_afro_organic", "house_techno", "trance_dance_rave",
            # compilation/mix/playlist folders
            "deep", "house", "house_chill", "tech house", "techno", "acid",
            "dnb_chill", "deepchill", "electro pop", "elektro", "top",
            "hardcore", "random", "party mode", "never ends",
            "chill deep house", "deep house relax",
            "deep house summer vibes", "chillout lounge",
            "famous house tracks", "free tracks",
            "club dance", "edm fever", "pop dance",
            "chill edm playlist 2024", "chill synthwave",
            "music i m embarrassed that i listen to",
            "90s dance", "2000s dance", "old dance",
            "30 years three decades of dance ministry of sound",
            "party like it s 2000", "dark drum n bass",
            "ibiza summer mix 2021", "coca", "belac", "fnknschlg",
            "you are liquid", "ft-ne-17",
            "after lsd", "who loves the sun chill bun 2024",
            "afro house 2025", "afro house remix sabia que no x reezy",
            "tracz 25 afro house",
            "melodic techno progressive house playlist 2025",
            "the road you ll never walk",
            "electro classics daft punk moby fatboy slim",
            "human traffic soundtrack",
            "chill organic house",
            "keinemusik the party is over",
            "atmosphere fisher kita alexander",
        },
        "blocklist": {
            "n/a", "unknown", "various", "nothing", "you", "me",
            "lyrics", "audio", "download link",
            "original mix", "original", "vip", "remix",
            "2000s dance", "90s dance", "old dance",
            "sharon den adel in", "out of love",
            "topic", "top 100 tracks", "me feat",
            "al001", "al039", "1991",
            "melodic techno progressive house playlist 2025 best",
            "lost at night aaaron remix", "sanctuary ep",
        },
        "split_groups": set(),
    },
    "alternate": {
        "scan_root": ZENE / "_other" / "_alternate",
        "id_prefix": "al",
        "generic_folders": {
            "_random", "_chill", "_alternate", "_other",
            "random", "misc", "videos", "youtube",
            "best jazzanova",
        },
        "blocklist": {
            "n/a", "unknown", "various", "nothing", "you", "me",
            "lyrics", "audio", "download link",
            "twin peaks season i", "peaky blinders soundtrack",
            "the fault in our stars", "against all odds",
            "in the air tonight", "i am stretched on your grave",
            "planet caravan", "el cerro raro y me vio un pinche cuervo",
            "official somewhere over the rainbow", "scarborough fair",
            "the less i know the better", "these boots are made for walking or in these shoes",
            "a fine selection of nice music", "me feat",
            "a million", "kimbra somebody that i used to know official film clip",
            "flight attendant", "tg cf",
        },
        "split_groups": set(),
    },
}


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

    alias_map = parse_mapping_block(sections.get("alias normalization", []))
    groups = parse_mapping_block(sections.get("groups", []))

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


def is_generic(name: str, config: dict) -> bool:
    key = normalize_key(name)
    if key.isdigit():
        return True  # pure year folders like "2011"
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
    bl = _normalized_blocklist(config)
    c = canonicalize(name, mappings)
    if c and not is_junk_name(c, normalize_key(c), bl):
        return c
    return "N/A"


def first_artist_context(path_parts: list[str], mappings: dict, config: dict) -> str | None:
    for part in path_parts[:-1]:
        if is_generic(part, config):
            continue
        candidate = folder_artist(part)
        if not candidate:
            continue
        canonical = canonicalize(candidate, mappings)
        if canonical and not is_junk_name(canonical, normalize_key(canonical), _normalized_blocklist(config)):
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
