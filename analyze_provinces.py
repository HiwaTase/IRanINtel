#!/usr/bin/env python3
"""Reproduce the Ilam/Kermanshah place-name analysis of Iran International's Telegram export.

Standard library only. The 620 MB export is loaded into memory; allow several GB of RAM.
Counts are literal text matches, not manual classifications of a post's meaning.
"""
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

PLACE_PATTERNS = {
    "Kermanshah": r"(?<![\wآ-ی])(?:کرمانشاه|کرماشان|کەرماشان|Kermanshah|Kirmashan)(?![\wآ-ی])",
    "Ilam": r"(?<![\wآ-ی])(?:ایلام|ئیلام|Ilam|Îlam)(?![\wآ-ی])",
    "Sanandaj": r"(?<![\wآ-ی])(?:سنندج|سنە|Sanandaj)(?![\wآ-ی])",
}
# Broad co-occurrence screen, not an interpretation of the surrounding sentence.
KURDISH_TERM = re.compile(
    r"کردستان|کوردستان|کردها|کوردها|کردی|کوردی|کردنشین|کوردنشین|ملت کرد|روژهلات|ڕۆژهەڵات"
)
PROTEST_TERM = re.compile(
    r"اعتراض|معترض|تظاهرات|خیزش|اعتصاب|تجمع|سرکوب|زن،? زندگی،? آزادی|ژن،? ژیان،? ئازادی"
)
PLACES = {name: re.compile(pattern, re.IGNORECASE) for name, pattern in PLACE_PATTERNS.items()}
UPRISING_START, UPRISING_END = "2022-09-16", "2022-12-31"
QUOTE_IDS = {138647, 148484, 27868, 43698}


def flatten_text(value):
    """Telegram exports text either as a string or as string/entity pieces."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(piece if isinstance(piece, str) else piece.get("text", "")
                       for piece in value)
    return ""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Path to the v1 release's result.json")
    parser.add_argument("--out", type=Path, default=Path("province_output"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    with args.archive.open(encoding="utf-8") as handle:
        messages = json.load(handle)["messages"]

    annual = defaultdict(Counter)
    total = Counter()
    quotes = {}
    with (args.out / "matched_posts.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "id", "date", "place", "kurdish_term", "protest_term", "uprising_period", "text"
        ])
        writer.writeheader()
        for msg in messages:
            date = msg.get("date", "")[:10]
            year = date[:4]
            if msg.get("type") != "message" or not ("2018" <= year <= "2025"):
                continue
            annual[year]["all_messages"] += 1
            total["all_messages"] += 1
            text = flatten_text(msg.get("text", ""))
            if msg.get("id") in QUOTE_IDS:
                quotes[msg["id"]] = {"date": date, "text": text}
            for place, pattern in PLACES.items():
                if not pattern.search(text):
                    continue
                kurdish = bool(KURDISH_TERM.search(text))
                protest = bool(PROTEST_TERM.search(text))
                uprising = UPRISING_START <= date <= UPRISING_END
                annual[year][place] += 1
                total[place] += 1
                if kurdish:
                    annual[year][f"{place}_with_kurdish_term"] += 1
                    total[f"{place}_with_kurdish_term"] += 1
                if protest:
                    annual[year][f"{place}_with_protest_term"] += 1
                if uprising:
                    annual[year][f"{place}_uprising_period"] += 1
                    total[f"{place}_uprising_period"] += 1
                writer.writerow({
                    "id": msg["id"], "date": date, "place": place,
                    "kurdish_term": int(kurdish), "protest_term": int(protest),
                    "uprising_period": int(uprising), "text": text,
                })

    fields = ["year", "all_messages"]
    for place in PLACES:
        fields.extend([place, f"{place}_with_kurdish_term",
                       f"{place}_with_protest_term", f"{place}_uprising_period"])
    with (args.out / "annual_counts.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for year in sorted(annual):
            writer.writerow({"year": year, **annual[year]})

    with (args.out / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump({"years": "2018–2025", "counts": dict(total),
                   "uprising_period": [UPRISING_START, UPRISING_END],
                   "method": "literal place-name match; one row per place per matched post"},
                  handle, ensure_ascii=False, indent=2)
    with (args.out / "quoted_posts.json").open("w", encoding="utf-8") as handle:
        json.dump(quotes, handle, ensure_ascii=False, indent=2)

    print(json.dumps(dict(total), ensure_ascii=False, indent=2))
    print(f"Outputs written to {args.out}")


if __name__ == "__main__":
    main()
