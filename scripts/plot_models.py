#!/usr/bin/env python3
"""Human-only comparison plots: data vs MINERvA GENIE vs the current model and up to 5 earlier versions.

    $PY scripts/plot_models.py <ws> <ver> [--only id ...] [--entries-as-of]

Run with the workspace environment (source scripts/env.sh <ws>) so that the cloned xsec is imported.
Writes <ws>/plots/model_<ver>/<id>/{projections,slices_<k>}.png, the same figures as
xsec.corpus_plots.plot_entry with the model history added.  The earlier versions shown are spaced
evenly between v0 and <ver> (select_versions) among those whose model_out/model_v<j>.root exists.
Model predictions per version are cached in <ws>/model_out/pred/model_v<j>/<id>.npy.
--entries-as-of: only the entries that existed while <ver> was current (to redraw an old folder).
"""
import argparse
import glob
import itertools
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from xsec.compare import chi2  # noqa: E402
from xsec.corpus import axis_projection, err, load_genie, load_index, make_measurement, valid_bins  # noqa: E402
from xsec.corpus_plots import DATA, GENIE, _pair  # noqa: E402  (also applies the shared rcParams)

N_PREV = 5
# ordinal blue ramp, oldest (light) -> newest; the current model takes the darkest step
RAMP = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]
CURRENT = "#0b2a52"


def vnum(v):
    return int(str(v).lstrip("v"))


def select_versions(cur, available):
    """Up to N_PREV earlier versions, spaced evenly from v0 to cur (rounded half up), among `available`."""
    want = sorted({int(np.floor(t + 0.5)) for t in np.linspace(0, cur, N_PREV + 1)[:-1]} - {cur})
    have = sorted(j for j in available if j < cur)
    out = []
    for w in want:  # nearest available version to each target, without repeats
        cand = [j for j in have if j not in out]
        if cand:
            out.append(min(cand, key=lambda j: (abs(j - w), j)))
    return sorted(out)


def added_version(entry, steps):
    o = entry.get("origin", "seed")
    if o == "seed":
        return 0
    n = int(o.split("-")[1])
    s = next((s for s in steps if s.get("step") == n), None)
    return vnum(s["model_version"]) if s else None


class Predictions:
    """Per-version model predictions, cached on disk; each model file is opened at most once."""

    def __init__(self, ws):
        self.ws, self.samples = ws, {}

    def root(self, j):
        return os.path.join(self.ws, "model_out", f"model_v{j}.root")

    def get(self, j, entry, corpus):
        cache = os.path.join(self.ws, "model_out", "pred", f"model_v{j}", f"{entry['id']}.npy")
        root = self.root(j)
        if os.path.exists(cache) and os.path.getmtime(cache) >= os.path.getmtime(root):
            return np.load(cache)
        d = os.path.join(corpus, entry["id"])
        vf = os.path.join(d, "model_version.txt")
        if os.path.exists(vf) and open(vf).read().strip() == f"v{j}" and os.path.exists(os.path.join(d, "model.npy")) \
                and os.path.getmtime(os.path.join(d, "model.npy")) >= os.path.getmtime(root):
            p = np.load(os.path.join(d, "model.npy"))
        else:
            if j not in self.samples:
                from xsec.genpred import GeneratorSample
                print(f"  loading {root}", flush=True)
                self.samples = {j: GeneratorSample(root)}  # keep one sample in memory
            p = self.samples[j].predict(make_measurement(entry))
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        np.save(cache, p)
        return p


def _stats(p, x, C, used, vol):
    if not np.all(np.isfinite(p[used])):
        return None
    c2, ndf = chi2(p, x, C, used)
    return c2, ndf, float((p * vol)[used].sum() / (x * vol)[used].sum())


def _draw(ax, rax, edges, y, ey, ys, ey_stat=None):
    """xsec.corpus_plots._draw with a line width per prediction; ys: list of (label, color, lw, values)."""
    edges = np.asarray(edges, float)
    c = 0.5 * (edges[1:] + edges[:-1])
    good = y != 0
    rr = np.where(good, ey / np.where(good, np.abs(y), 1), np.nan)
    rax.fill_between(edges, 1 - np.append(rr, rr[-1]), 1 + np.append(rr, rr[-1]), step="post", color=DATA,
                     alpha=0.15, lw=0)
    rax.axhline(1, color=DATA, lw=0.8)
    for lab, col, lw, v in ys:
        if not np.all(np.isfinite(v)):
            continue
        ax.step(edges, np.append(v, v[-1]), where="post", color=col, lw=lw, label=lab)
        r = np.where(good, v / np.where(good, y, 1), np.nan)
        rax.step(edges, np.append(r, r[-1]), where="post", color=col, lw=lw * 0.85)
    ax.errorbar(c, y, yerr=ey, fmt="o", color=DATA, ms=3.5, elinewidth=1.0, label="data (total unc.)", zorder=5)
    if ey_stat is not None:
        ax.errorbar(c, y, yerr=ey_stat, fmt="none", ecolor=DATA, elinewidth=1.8, capsize=2, zorder=5)
    rax.set_ylim(0.0, 2.0)
    rax.set_ylabel("pred / data", fontsize=8)


def plot_entry(entry, TB, x, e_stat, e_tot, cov, genie, genie_label, models, outdir):
    """models: list of (version number, prediction), oldest first, current last."""
    os.makedirs(outdir, exist_ok=True)
    for f in glob.glob(os.path.join(outdir, "*.png")):
        os.remove(f)
    used, vol = valid_bins(x, cov), TB.widths()
    cur = models[-1][0]
    series = []  # (label, color, lw, full prediction), drawn in this order
    for k, (j, p) in enumerate(models[:-1]):
        st = _stats(p, x, cov, used, vol)
        lab = f"model v{j}" + (f" (χ² {st[0]:.0f}/{st[1]})" if st else "")
        series.append((lab, RAMP[len(RAMP) - (len(models) - 1) + k], 1.0, p))
    gst = _stats(genie, x, cov, used, vol) if genie is not None else None
    if genie is not None:
        series.append(((genie_label or "MINERvA GENIE") + (f" (χ² {gst[0]:.0f}/{gst[1]})" if gst else ""),
                       GENIE, 1.4, genie))
    mst = _stats(models[-1][1], x, cov, used, vol)
    series.append((f"model v{cur}" + (f" (χ² {mst[0]:.0f}/{mst[1]})" if mst else ""), CURRENT, 2.0, models[-1][1]))
    line = []
    if mst:
        line.append(f"model v{cur}: χ² {mst[0]:.0f}/{mst[1]}, norm {mst[2]:.2f}")
    if gst:
        line.append(f"GENIE: χ² {gst[0]:.0f}/{gst[1]}, norm {gst[2]:.2f}")
    title = f"{entry['id']}: {entry.get('title', '')}\n" + "    ".join(line)

    nd = TB.ndim
    fig = plt.figure(figsize=(4.6 * nd, 4.4))
    gs = fig.add_gridspec(1, nd, wspace=0.3)
    for axn in range(nd):
        P = axis_projection(TB, axn)
        a, b = _pair(fig, gs[0, axn])
        _draw(a, b, TB.edges[axn], P @ x, np.sqrt(np.clip(np.diag(P @ cov @ P.T), 0, None)),
              [(lab, col, lw, P @ v) for lab, col, lw, v in series])
        a.set_ylabel(f"dσ/d{TB.names[axn]} [cm²/nucleon/unit]")
        b.set_xlabel(TB.names[axn])
        if axn == 0:
            a.legend(fontsize=6.5)
    fig.suptitle(title, fontsize=9, y=1.02)
    fig.savefig(os.path.join(outdir, "projections.png"), bbox_inches="tight")
    plt.close(fig)
    if nd < 2:
        return
    # slices: x = axis 0, panels = axis 1, one figure per combination of axes >= 2
    nb = TB.nb
    idx = np.indices(nb[::-1]).reshape(nd, -1)[::-1]
    for fi, combo in enumerate(itertools.product(*[range(n) for n in nb[2:]])):
        n1 = nb[1]
        ncol = min(4, n1)
        nrow = int(np.ceil(n1 / ncol))
        fig = plt.figure(figsize=(4.0 * ncol, 3.6 * nrow))
        gs = fig.add_gridspec(nrow, ncol, hspace=0.45, wspace=0.3)
        sub = " ".join(f"{TB.names[2 + k]}∈[{TB.edges[2 + k][j]:.3g},{TB.edges[2 + k][j + 1]:.3g}]"
                       for k, j in enumerate(combo))
        for j in range(n1):
            sel = idx[1] == j
            for k, jj in enumerate(combo):
                sel &= idx[2 + k] == jj
            ii = np.flatnonzero(sel)
            ii = ii[np.argsort(idx[0][ii])]
            a, b = _pair(fig, gs[j // ncol, j % ncol])
            _draw(a, b, TB.edges[0], x[ii], e_tot[ii], [(lab, col, lw, v[ii]) for lab, col, lw, v in series],
                  e_stat[ii])
            a.set_title(f"{TB.names[1]}∈[{TB.edges[1][j]:.3g},{TB.edges[1][j + 1]:.3g}]", fontsize=8)
            b.set_xlabel(TB.names[0])
            if j == 0:
                a.legend(fontsize=5.5)
        fig.suptitle(title + ("\n" + sub if sub else ""), fontsize=9, y=1.0)
        fig.savefig(os.path.join(outdir, f"slices_{fi}.png"), bbox_inches="tight")
        plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ws")
    ap.add_argument("ver", help="model version of the plot folder, e.g. v5")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--entries-as-of", action="store_true",
                    help="only entries added while <ver> was (or before it became) the current model")
    args = ap.parse_args()
    ws, cur = os.path.realpath(args.ws), vnum(args.ver)
    corpus = os.path.join(ws, "corpus")
    private = os.environ.get("MVA_PRIVATE") or os.path.join(ws, "plots", "_genie")
    preds = Predictions(ws)
    if not os.path.exists(preds.root(cur)):
        raise SystemExit(f"no model file {preds.root(cur)}")
    avail = [vnum(os.path.basename(f)[6:-5]) for f in glob.glob(os.path.join(ws, "model_out", "model_v*.root"))]
    prev = select_versions(cur, avail)
    steps = json.load(open(os.path.join(ws, "state.json"))).get("steps", []) \
        if os.path.exists(os.path.join(ws, "state.json")) else []
    entries = [e for e in load_index(corpus) if not args.only or e["id"] in args.only]
    if args.entries_as_of:
        entries = [e for e in entries if (added_version(e, steps) if added_version(e, steps) is not None else cur) <= cur]
    print(f"== plots/model_v{cur}: {len(entries)} entries, models {['v%d' % j for j in prev + [cur]]}")
    outroot = os.path.join(ws, "plots", f"model_v{cur}")
    # version-major loop, so that each model file is loaded once
    P = {e["id"]: {} for e in entries}
    for j in prev + [cur]:
        for e in entries:
            P[e["id"]][j] = preds.get(j, e, corpus)
    for e in entries:
        r = dict(np.load(os.path.join(corpus, e["id"], "result.npz")))
        TB = make_measurement(e).true_binning
        x, C, Cs = r["xsec"], r["cov_total"], r["cov_stat"]
        g, glabel = load_genie(private, e["id"])
        plot_entry(e, TB, x, err(Cs), err(C), C, g, glabel, [(j, P[e["id"]][j]) for j in prev + [cur]],
                   os.path.join(outroot, e["id"]))
        print(f"  {e['id']}")


if __name__ == "__main__":
    main()
