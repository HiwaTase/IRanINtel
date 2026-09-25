# Iran International Telegram analysis scripts

This package covers the **entire article analysis**: 2018–2025 coverage, framing vocabulary, national and geographic naming, Jina and slogan usage, Kurdish parties and their leaders, cited organisations, Ilam and Kermanshah, and seven reconstructed charts.

**Provenance:** The article and the [v1 Telegram archive](https://github.com/HiwaTase/IRanINtel/releases/tag/v1) were available, but the original analysis scripts and the final hand-checked coding decisions were not. These are newly reconstructed, inspectable scripts. They must **not** be presented as the original code that generated every published number. `comparison.csv` makes differences visible. The Telegram channel is a proxy for the broadcaster's output, not a complete record of TV broadcasts.

## Run

Python 3.9+ is required. The standard-library analysis loads the 620 MB JSON export into memory, so allow several GB of RAM. Figures additionally require matplotlib.

```bash
bash download_data.sh
python3 analyze_article.py result.json --out article_output
python3 analyze_provinces.py result.json --out province_output
python3 -m pip install -r requirements.txt
python3 make_figures.py article_output --out figures
```

The download script verifies the release asset's SHA-256. The archive stays outside Git: `.gitignore` excludes it and generated outputs.

## Outputs and article sections

| File | Purpose |
| --- | --- |
| `article_output/post_flags.csv` | Post IDs, text, every dictionary flag, and place matches for audit |
| `annual_visibility.csv`, `monthly_visibility.csv` | Figure 1 and busiest months |
| `annual_visibility.csv` framing columns | Figure 2 |
| `summary.json`, `comparison.csv` | Nation/territory terminology, article-to-script comparison |
| `names_and_slogans.csv` | Figure 4 |
| `party_year.csv`, `party_frames.csv` | Figures 5 and 6 |
| `leaders.csv` | Leader table; speech keyword is only an **unreviewed proxy** |
| `sources.csv` | Figure 7 |
| `places.csv` | Geographic names in the whole corpus and matched subset |
| `province_output/*` | Dedicated Ilam/Kermanshah counts, posts and four quoted sources |
| `figures/*.png` | Seven charts from the reconstructed data |

`figure_3_nation_names.png` plots **raw phrase candidates**, since one “Kurdish nation” candidate in the archive is a false positive and contextual review is necessary. The leader “speaks” column in the article also requires human coding; `leaders.csv` deliberately labels its keyword count as a proxy. Do not substitute either raw result for the article's reviewed claim.

## Important discrepancy

The article reports **4,250 Kurdish-related posts**. The reconstructed broad dictionary currently flags **5,631**. It also differs on some other measures; see `article_output/comparison.csv`. The article describes the screening terms but does not supply the exact regular expressions, exclusions and manual corrections used for its final set. The scripts preserve that discrepancy rather than tuning a search until it happens to match a published total. The patterns are near the top of `analyze_article.py`, and every flagged post can be checked in `post_flags.csv` before revising them.

The province script independently reproduces the added section's literal-name counts: **1,230** Kermanshah mentions, **444** Ilam mentions, and **47**, **8**, and **176** mentions of Kermanshah, Ilam and Sanandaj respectively during 16 September–31 December 2022. Those are not synonymous with coverage of Kurdish politics. The wording quoted in the article comes from the four original Persian posts in `province_output/quoted_posts.json`.
