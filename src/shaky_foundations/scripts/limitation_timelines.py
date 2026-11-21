"""Shakiness over time for foundations whose limitations were identified in the gold-set evaluation.

Per foundation, per identified limitation and per year: distinct citing papers whose attributed
critique falls in that limitation's concept group(s) (several groups are merged when they say the
same thing), plus distinct citing papers with any attributed critique (proxy attribution,
scale_foundations hits). Cumulative counts are plotted: the project's definition of shakiness is how
many papers raise the same limitation. A foundation can have several limitations, one line each.

Layouts (config `layout`):
  grid          all examples, 2 columns, two-sentence descriptions drawn above each panel
  camera_ready  one row, 7 in wide, 8-pt type, embedded fonts, PDF + 300-dpi PNG; the descriptions
                go to caption.md in output_dir instead of into the figure

Outputs: config.yaml, timelines.csv, groups.csv (which concept groups were merged), caption.md
(camera_ready), and the figure in the track figures folder (figures.py).

    uv run python src/shaky_foundations/scripts/limitation_timelines.py configs/shaky_foundations/limitation_timelines.yaml
"""

import argparse
import shutil
import sys
import textwrap
from pathlib import Path

import matplotlib
import matplotlib.ticker
import numpy as np
import polars as pl

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.shaky_foundations.data import open_lacuna
from src.shaky_foundations.embeddings import ensure_embedded, load_vectors
from src.shaky_foundations.figures import figure_path
from src.utils import init_directory, load_config

REQUIRED = ["output_dir", "layout", "lacuna_dir", "lacuna_package", "hits_path", "scored_path", "group_layer",
            "year_max", "embedding", "examples"]
INK, MUTED, SURFACE, GRID, ANY = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e1", "#b9b8b3"
# Reference categorical palette (dataviz skill), fixed order, never cycled. Max 3 limitations per panel.
LIMIT_COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")
    if config["layout"] not in {"grid", "camera_ready"}:
        raise ValueError(f"FATAL: layout must be grid or camera_ready, got {config['layout']}")
    for ex in config["examples"]:
        for key in ["title", "short", "limitations", "foundation_desc", "limitation_desc"]:
            if key not in ex:
                raise ValueError(f"FATAL: example {ex.get('short', ex.get('title'))} is missing {key}")
        if not 1 <= len(ex["limitations"]) <= len(LIMIT_COLORS):
            raise ValueError(f"FATAL: {ex['short']}: 1-{len(LIMIT_COLORS)} limitations per foundation")
        used = [r for lim in ex["limitations"] for r in lim["ranks"]]
        if len(used) != len(set(used)):
            raise ValueError(f"FATAL: {ex['short']}: a concept group is assigned to two limitations")


def build_timelines(config: dict, hits: pl.DataFrame, scored: pl.DataFrame, labels: dict) -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    ymax = config["year_max"]
    rows, grows, members = [], [], []
    for ex in config["examples"]:
        f = scored.filter(pl.col("title").str.to_lowercase() == ex["title"].lower())
        if f.height != 1:
            raise ValueError(f"FATAL: {ex['title']} not found once in {config['scored_path']}")
        pid, fyear = f["pid"][0], f["year"][0]
        h = hits.filter((pl.col("foundation") == pid) & (pl.col("year") <= ymax))
        ranked = (h.group_by("gid").agg(n=pl.col("citer").n_unique())
                  .sort(["n", "gid"], descending=[True, False]).with_row_index("rank", offset=1))
        series = [("any critique", h)]
        for lim in ex["limitations"]:
            chosen = ranked.filter(pl.col("rank").is_in(lim["ranks"]))
            if chosen.height != len(lim["ranks"]):
                raise ValueError(f"FATAL: {ex['short']}: ranks {lim['ranks']} not all present")
            for r in chosen.iter_rows(named=True):
                grows.append({"foundation": ex["short"], "limitation": lim["label"], "rank": r["rank"],
                              "n_critics": r["n"], "group": labels[r["gid"]]})
            sub = h.filter(pl.col("gid").is_in(chosen["gid"].implode()))
            series.append((lim["label"], sub))
            for citer, year in sub.group_by("citer").agg(pl.col("year").min()).iter_rows():
                members.append({"foundation": ex["short"], "limitation": lim["label"], "citer": citer, "year": year,
                                "gids": chosen["gid"].to_list()})
        for name, sub in series:
            for y in range(fyear, ymax + 1):
                rows.append({"foundation": ex["short"], "title": ex["title"], "pub_year": fyear, "series": name,
                             "year": y, "new_critics": sub.filter(pl.col("year") == y)["citer"].n_unique(),
                             "cum_critics": sub.filter(pl.col("year") <= y)["citer"].n_unique()})
    return pl.DataFrame(rows), pl.DataFrame(grows), pl.DataFrame(members)


def critic_candidates(con, members: pl.DataFrame, config: dict) -> pl.DataFrame:
    """Every paper counted on a limitation line, with its own mechanism atom closest to that limitation
    (cosine to the mean centroid of the line's concept groups, real bge-large vectors). For reading:
    which critics also propose a (partial) fix? Those are listed as `solvers` in the config."""
    cent = np.load(Path(config["lacuna_dir"]) / f"centroids_{config['group_layer']}.npy").astype(np.float32)
    con.register("crit", members.select("citer").unique())
    mech = con.sql("""SELECT a.pid AS citer, a.atom_id, a.text FROM atoms a JOIN crit ON crit.citer = a.pid
                      WHERE a.run_rank = 1 AND a.type = 'mechanism'""").pl()
    emb = config["embedding"]
    ensure_embedded(con, mech["atom_id"].to_list(), emb["cache_dir"], emb["model"], emb["device"])
    index, vec = load_vectors(emb["cache_dir"], mech["atom_id"].to_list())
    rows = []
    for r in members.iter_rows(named=True):
        target = cent[r["gids"]].mean(axis=0)
        target /= np.linalg.norm(target)
        m = mech.filter(pl.col("citer") == r["citer"])
        if m.height:
            sims = vec[[index[a] for a in m["atom_id"]]].astype(np.float32) @ target
            best = int(np.argmax(sims))
            rows.append({**{k: r[k] for k in ["foundation", "limitation", "citer", "year"]},
                         "mech_sim": float(sims[best]), "best_mechanism": m["text"][best]})
        else:
            rows.append({**{k: r[k] for k in ["foundation", "limitation", "citer", "year"]},
                         "mech_sim": None, "best_mechanism": None})
    papers = con.sql("SELECT pid AS citer, title, cites_total_2025 FROM papers").pl()
    return (pl.DataFrame(rows).join(papers, on="citer", how="left")
            .sort(["foundation", "limitation", "mech_sim"], descending=[False, False, True], nulls_last=True))


def spread(values: list[float], min_gap: float) -> list[float]:
    """Nudge label y-positions apart (same order) so no two are closer than min_gap."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = list(values)
    for a, b in zip(order, order[1:]):
        if out[b] - out[a] < min_gap:
            out[b] = out[a] + min_gap
    return out


def draw_panel(ax, tl: pl.DataFrame, ex: dict, ymax: int, fs: float, lw: float, label_names: bool,
               show_any: bool = True, solver_years: dict | None = None, dot_size: float = 9) -> None:
    """One foundation: a cumulative step line per limitation (+ grey any-critique line if show_any),
    with end labels nudged apart so they never overlap."""
    d = tl.filter(pl.col("foundation") == ex["short"])
    names = (["any critique"] if show_any else []) + [lim["label"] for lim in ex["limitations"]]
    colors = ([ANY] if show_any else []) + LIMIT_COLORS[:len(ex["limitations"])]
    top = d.filter(pl.col("series").is_in(names))["cum_critics"].max()
    ylim = max(top * 1.08, 5)
    ends = []
    for name, color in zip(names, colors):
        s = d.filter(pl.col("series") == name).sort("year")
        xs = s["year"].to_list() + [ymax + 1]
        ys = s["cum_critics"].to_list()
        ax.step(xs, ys + [ys[-1]], where="post", color=color, lw=lw, zorder=3 if name != "any critique" else 2)
        ends.append(ys[-1])
        # Dots: one per year on the line, area proportional to how many of that year's critics also
        # propose a (partial) fix. Placed mid-year on the step, where the line sits for that year.
        years = (solver_years or {}).get(name, [])
        cum = dict(zip(s["year"].to_list(), ys))
        for yr in sorted(set(years)):
            ax.scatter([yr + 0.5], [cum[yr]], s=dot_size * years.count(yr), color=color, edgecolor="white",
                       linewidth=0.6, zorder=4)
    label_y = spread(ends, min_gap=ylim * 0.075)
    for name, color, y_end, y_lab in zip(names, colors, ends, label_y):
        n_fix = len((solver_years or {}).get(name, []))
        text = (f"{y_end}  {name}" + (f" ({n_fix})" if solver_years is not None and name != "any critique" else "")
                if label_names else str(y_end))
        ax.text(ymax + 1.35, y_lab, text, fontsize=fs, color=INK if name != "any critique" else MUTED,
                va="center", clip_on=False)
    ax.set_ylim(0, ylim)
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=5, integer=True))
    ax.set_xlim(2010, ymax + 1)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.tick_params(labelsize=fs, colors=MUTED, length=0)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    for sp in ["left", "bottom"]:
        ax.spines[sp].set_color(GRID)


def solver_years_for(ex: dict, critics: pl.DataFrame) -> dict:
    """{limitation label: [year of each solver paper]}; every solver must be a critic on that line."""
    out = {}
    for lim in ex["limitations"]:
        c = critics.filter((pl.col("foundation") == ex["short"]) & (pl.col("limitation") == lim["label"]))
        pids = lim.get("solvers", [])
        missing = set(pids) - set(c["citer"].to_list())
        if missing:
            raise ValueError(f"FATAL: {ex['short']} / {lim['label']}: solvers not among its critics: {sorted(missing)}")
        out[lim["label"]] = c.filter(pl.col("citer").is_in(pids))["year"].to_list()
    return out


def plot_grid(tl, config, path):
    ymax, n, ncol = config["year_max"], len(config["examples"]), 2
    nrow = -(-n // ncol)
    fig = plt.figure(figsize=(7.6 * ncol, 4.9 * nrow), facecolor=SURFACE)
    outer = fig.add_gridspec(nrow, ncol, hspace=0.22, wspace=0.42, top=0.965, bottom=0.03, left=0.05, right=0.86)
    for i, ex in enumerate(config["examples"]):
        cell = outer[i // ncol, i % ncol].subgridspec(2, 1, height_ratios=[0.62, 1.0], hspace=0.04)
        tax, ax = fig.add_subplot(cell[0]), fig.add_subplot(cell[1])
        year = tl.filter(pl.col("foundation") == ex["short"])["pub_year"][0]
        tax.axis("off")
        tax.text(0, 1.0, f"{ex['short']} ({year})", fontsize=11, color=INK, va="top", weight="bold")
        body = (textwrap.fill("Foundation: " + ex["foundation_desc"], 112) + "\n\n"
                + textwrap.fill("Limitation: " + ex["limitation_desc"], 112))
        tax.text(0, 0.84, body, fontsize=8, color=INK, va="top", linespacing=1.3)
        draw_panel(ax, tl, ex, ymax, fs=8, lw=2, label_names=True)
        ax.set_ylabel("cumulative citing papers", fontsize=8, color=MUTED)
    fig.text(0.05, 0.995, "Cumulative distinct citing papers raising each identified limitation (coloured) "
             "vs any critique of the foundation (grey)", fontsize=9.5, color=INK, va="top")
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def plot_camera_ready(tl, config, base: Path, critics: pl.DataFrame):
    plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.family": "DejaVu Sans"})
    ymax, n = config["year_max"], len(config["examples"])
    fig, axes = plt.subplots(1, n, figsize=(7.0, 2.5), facecolor="white")
    fig.subplots_adjust(left=0.065, right=0.765, top=0.80, bottom=0.19, wspace=0.86)
    for i, (ax, ex) in enumerate(zip(axes, config["examples"])):
        # No grey any-critique line here: it would set the scale and flatten the limitation lines.
        draw_panel(ax, tl, ex, ymax, fs=7, lw=1.6, label_names=True, show_any=False,
                   solver_years=solver_years_for(ex, critics), dot_size=7)
        total = tl.filter((pl.col("foundation") == ex["short"]) & (pl.col("series") == "any critique")
                          & (pl.col("year") == ymax))["cum_critics"][0]
        ax.text(0, 1.03, f"{total} citing papers raise any critique of it", transform=ax.transAxes, fontsize=6.5,
                color=MUTED, va="bottom")
        ax.set_facecolor("white")
        ax.set_title(f"{'abcdefgh'[i]}   {ex['short']} ({ex['paper']})", fontsize=8.5, color=INK, loc="left",
                     pad=14, weight="bold")
        ax.set_xticks(range(2012, ymax + 1, 4))
        if i == 0:
            ax.set_ylabel("Citing papers (cumulative)", fontsize=7.5, color=INK)
    if any(lim.get("solvers") for ex in config["examples"] for lim in ex["limitations"]):
        sizes = [1, 5, 10]
        handles = [plt.scatter([], [], s=7 * k, color=MUTED, edgecolor="white", linewidth=0.6) for k in sizes]
        fig.legend(handles, [str(k) for k in sizes], loc="lower left", bbox_to_anchor=(0.055, -0.015), ncol=3,
                   frameon=False, fontsize=6.5, handletextpad=0.1, columnspacing=0.8,
                   title="Dots: citing papers that year that raise the limitation and propose a (partial) fix; "
                         "(n) = total", title_fontsize=6.5, alignment="left")
    for ext, dpi in [("pdf", None), ("png", 300)]:
        fig.savefig(base.with_suffix(f".{ext}"), dpi=dpi, facecolor="white")
    plt.close(fig)


def caption(config: dict, tl: pl.DataFrame, critics: pl.DataFrame) -> str:
    parts = ["**Limitations raised against two foundations over time.** Lines show the cumulative number of "
             "distinct citing papers (Lacuna AI corpus, through 2025) whose critique atoms are attributed to the "
             "foundation and fall in each identified limitation; the note in each panel gives the number raising "
             "any critique of it. Dot area is the number of that year's citing papers that raise the limitation "
             "and also propose a (partial) fix for it, with the total in parentheses (judged by hand from each "
             "paper's title and mechanism; fixes not themselves counted as critics of the foundation, such as "
             "Linformer or ResNet, cannot appear). "]
    for i, ex in enumerate(config["examples"]):
        d = tl.filter(pl.col("foundation") == ex["short"])
        counts = ", ".join(f"{lim['label']} ({d.filter((pl.col('series') == lim['label']) & (pl.col('year') == config['year_max']))['cum_critics'][0]})"
                           for lim in ex["limitations"])
        fixes = "; ".join(f"{lim['label']}: {len(lim.get('solvers', []))} of them propose fixes"
                          + (f" (e.g. {', '.join(lim['notable_solvers'])})" if lim.get("notable_solvers") else "")
                          for lim in ex["limitations"])
        parts.append(f"(**{'abcdefgh'[i]}**) {ex['short']} ({ex['paper']}): {ex['foundation_desc']} "
                     f"{ex['limitation_desc']} Identified limitations, in citing papers: {counts}; {fixes}. ")
    parts.append("Critiques are attributed by embedding similarity between a citing paper's limitation atoms and "
                 "its references; individual attributions are noisy (about 25% precise in a hand-labelled sample), "
                 "so counts are indicative.")
    return "".join(parts) + "\n"


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
    scored = pl.read_csv(config["scored_path"]).select("pid", "title", "year")
    con = open_lacuna(config["lacuna_dir"], config["lacuna_package"])
    labels = dict(con.sql(f"SELECT concept_id, label FROM concepts_{config['group_layer']}").fetchall())

    tl, groups, members = build_timelines(config, hits, scored, labels)
    critics = critic_candidates(con, members, config)
    critics.write_csv(out / "critics.csv")
    tl.write_csv(out / "timelines.csv")
    groups.write_csv(out / "groups.csv")
    if config["layout"] == "grid":
        plot_grid(tl, config, figure_path(out, "timelines.png"))
    else:
        plot_camera_ready(tl, config, figure_path(out, "timelines"), critics)
        (out / "caption.md").write_text(caption(config, tl, critics))
    with pl.Config(tbl_rows=40, fmt_str_lengths=70):
        print(groups)
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
