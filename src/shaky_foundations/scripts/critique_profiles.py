"""Critique profiles for recent foundations: is criticism converging on a limitation yet, or scattered?

Too recent for timelines (Lacuna dates papers by year only), so each foundation gets one horizontal bar:
bar = 100% of its distinct critics; coloured segments = shares in its most common limitation groups
(groups with identical labels merged); grey = critics whose critiques fall only in other groups. The
critic count and top limitations are printed in a text column.
A large first segment means a direction is emerging; a mostly grey bar means critique is still diffuse.

Outputs: config.yaml, profiles.csv, and the figure in the track figures folder.

    uv run python src/shaky_foundations/scripts/critique_profiles.py configs/shaky_foundations/critique_profiles.yaml
"""

import argparse
import shutil
import sys
import textwrap
from pathlib import Path

import matplotlib
import matplotlib.transforms as transforms
import polars as pl

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.shaky_foundations.data import open_lacuna
from src.shaky_foundations.figures import figure_path
from src.utils import init_directory, load_config

REQUIRED = ["output_dir", "lacuna_dir", "lacuna_package", "hits_path", "scored_path", "group_layer", "n_papers",
            "top_groups", "title"]
INK, MUTED, GRID, OTHER = "#0b0b0b", "#52514e", "#e6e5e1", "#d4d3ce"
GROUP_COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]  # reference categorical palette, fixed order


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")
    if not 1 <= config["top_groups"] <= len(GROUP_COLORS):
        raise ValueError(f"FATAL: top_groups must be 1-{len(GROUP_COLORS)}")


def short_label(label: str) -> str:
    return label.split(" / ")[0]


def short_title(title: str, n: int = 30) -> str:
    t = title.split(":")[0] if ":" in title and len(title.split(":")[0]) >= 4 else title
    t = t.replace(" Technical Report", "")
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config_path)
    validate_config(config)
    out = init_directory(config["output_dir"] + ("_debug" if args.debug else ""), overwrite=args.overwrite)
    shutil.copy(args.config_path, out / "config.yaml")

    hits = pl.read_parquet(config["hits_path"])
    scored = pl.read_csv(config["scored_path"])
    con = open_lacuna(config["lacuna_dir"], config["lacuna_package"])
    labels = dict(con.sql(f"SELECT concept_id, label FROM concepts_{config['group_layer']}").fetchall())
    K = config["top_groups"]

    papers = (scored.filter(~pl.col("is_review") & pl.col("n_critics").is_not_null())
              .sort("cites_lacuna_2025", descending=True).head(config["n_papers"]))
    # Groups whose short labels are identical are near-duplicate concepts: merge them (distinct critics).
    hits = hits.with_columns(group=pl.col("gid").replace_strict({g: short_label(l) for g, l in labels.items()},
                                                                 return_dtype=pl.Utf8))
    rows = []
    for p in papers.iter_rows(named=True):
        h = hits.filter(pl.col("foundation") == p["pid"])
        ranked = h.group_by("group").agg(n=pl.col("citer").n_unique()).sort(["n", "group"], descending=[True, False])
        top = ranked.head(K)
        n_total = h["citer"].n_unique()
        in_top = h.filter(pl.col("group").is_in(top["group"].implode()))["citer"].n_unique()
        row = {"pid": p["pid"], "title": p["title"], "year": p["year"], "cites": p["cites_lacuna_2025"],
               "n_critics": n_total, "n_groups": ranked.height, "n_other_only": n_total - in_top,
               "share_2026": float((h["year"] == 2026).mean()) if h.height else 0.0}
        for i in range(K):
            row[f"g{i + 1}_n"] = top["n"][i] if i < top.height else 0
            row[f"g{i + 1}_label"] = top["group"][i] if i < top.height else ""
        rows.append(row)
    prof = pl.DataFrame(rows)
    prof.write_csv(out / "profiles.csv")

    # Figure: bars are shares of each paper's critics (convergence is the point, not volume); the
    # critic count and the top limitations sit in a text column (own axes, shared y) on the right.
    plt.rcParams.update({"pdf.fonttype": 42, "font.family": "DejaVu Sans"})
    overrides = config.get("short_titles", {})
    n = prof.height
    row_h = 0.36
    H = row_h * n + 1.05
    fig = plt.figure(figsize=(7.2, H), facecolor="white")
    bottom, height = 0.42 / H, 1 - 1.05 / H
    ax = fig.add_axes([0.215, bottom, 0.24, height])
    tax = fig.add_axes([0.47, bottom, 0.52, height], sharey=ax)
    tax.axis("off")
    blend = transforms.blended_transform_factory(tax.transAxes, tax.transData)
    for r_i, r in enumerate(prof.iter_rows(named=True)):
        y = n - 1 - r_i
        left = 0.0
        for i in range(K):
            w = r[f"g{i + 1}_n"] / r["n_critics"] * 100
            if w:
                ax.barh(y, w, left=left, height=0.64, color=GROUP_COLORS[i], edgecolor="white", linewidth=0.8)
                left += w
        ax.barh(y, max(100 - left, 0), left=left, height=0.64, color=OTHER, edgecolor="white", linewidth=0.8)
        tops = "  ·  ".join(f"{r[f'g{i + 1}_label']} {r[f'g{i + 1}_n']}" for i in range(K) if r[f"g{i + 1}_n"])
        tops = textwrap.fill(textwrap.shorten(tops, width=150, placeholder=" …"), 78)
        tax.text(0.045, y, str(r["n_critics"]), transform=blend, fontsize=6.5, color=INK, va="center", ha="right")
        tax.text(0.07, y, tops, transform=blend, fontsize=6.1, color=INK, va="center", linespacing=1.15)
    ax.set_ylim(-0.6, n - 0.4)
    names_y = [overrides.get(t, short_title(t)) + f" ({yr})" for t, yr in zip(prof["title"][::-1], prof["year"][::-1])]
    ax.set_yticks(range(n), names_y, fontsize=6.8)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100], ["0", "25", "50", "75", "100%"])
    ax.set_xlabel("share of the paper's critics", fontsize=6.8, color=INK)
    ax.tick_params(axis="x", labelsize=6.3, colors=MUTED, length=0)
    ax.tick_params(axis="y", length=0, colors=INK)
    for sp in ["top", "right", "left", "bottom"]:
        ax.spines[sp].set_visible(False)
    tax.text(0.045, n - 0.25, "critics", transform=blend, fontsize=6.3, color=MUTED, ha="right", va="bottom")
    tax.text(0.07, n - 0.25, "most common limitations (critics each)", transform=blend, fontsize=6.3, color=MUTED,
             va="bottom")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in GROUP_COLORS[:K]] + [plt.Rectangle((0, 0), 1, 1, color=OTHER)]
    labels_leg = ["1st", "2nd", "3rd"][:K] + ["other"]
    ax.legend(handles, labels_leg, loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=K + 1, frameon=False,
              fontsize=6.3, handlelength=1.0, columnspacing=0.7, handletextpad=0.35, borderaxespad=0.2)
    fig.text(0.01, 1 - 0.06 / H, config["title"], fontsize=8, color=INK, va="top", weight="bold")
    base = figure_path(out, "profiles")
    for ext, dpi in [("pdf", None), ("png", 300)]:
        fig.savefig(base.with_suffix(f".{ext}"), dpi=dpi, facecolor="white")
    plt.close(fig)
    with pl.Config(tbl_rows=30, tbl_width_chars=200, fmt_str_lengths=40):
        print(prof.select("year", "cites", "n_critics", "n_groups", "g1_n", "g1_label", "share_2026", "title"))
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
