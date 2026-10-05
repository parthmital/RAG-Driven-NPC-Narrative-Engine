"""Purpose: independently recompute the headline metrics of the NPC memory/state benchmark from the raw
prediction CSVs in notebooks/outputs/predictions (no LLM calls), mirroring the notebook's definitions
(cells 76-96), so the paper's numbers can be cross-checked against notebooks/outputs/metrics.
Inputs: --outputs path to notebooks/outputs.  Output: printed report (point estimates exact; bootstrap CIs
use a fresh RNG stream so they can differ from the notebook's in the last digit).
Run: .venv/Scripts/python .claude/skills/eval-results-facts/scripts/recompute_paper_metrics.py --outputs notebooks/outputs
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sps
from statsmodels.stats.contingency_tables import mcnemar

ap = argparse.ArgumentParser()
ap.add_argument("--outputs", default="notebooks/outputs")
args = ap.parse_args()
O = Path(args.outputs)
RNG = np.random.default_rng(20261001)


def boot(df, num, cluster, den=None, n=10_000):
    if len(df) == 0:
        return (np.nan,) * 3
    g = (
        df.assign(_n=df[num].astype(float), _d=df[den].astype(float) if den else 1.0)
        .groupby(cluster)[["_n", "_d"]]
        .sum()
    )
    sn, sd = g["_n"].to_numpy(), g["_d"].to_numpy()
    point = sn.sum() / sd.sum()
    idx = RNG.integers(0, len(sn), size=(n, len(sn)))
    with np.errstate(invalid="ignore", divide="ignore"):
        est = sn[idx].sum(1) / sd[idx].sum(1)
    lo, hi = np.nanpercentile(est, [2.5, 97.5])
    return point, lo, hi


def f(ci, s=100, d=1):
    return f"{ci[0]*s:.{d}f} [{ci[1]*s:.{d}f}, {ci[2]*s:.{d}f}]"


R = pd.read_csv(O / "predictions/recall_primary.csv")
R = R[~R["missing"].astype(bool)]
R["rr"] = np.where(
    R["retrieval"].astype(bool), 1.0 / R["rank"].astype(float).fillna(np.inf), np.nan
)
R["r6"] = np.where(R["retrieval"].astype(bool), R["rank"].notna().astype(float), np.nan)
RH = R[R.world != "W1"]
RH20 = RH[RH.age >= 20]
P = pd.read_csv(O / "predictions/probes_primary.csv", low_memory=False)
P = P[~P["missing"].astype(bool)]
for m in ("barrier", "reducer", "direct"):
    P[f"violated_{m}"] = P[f"viol_{m}"].fillna("").astype(str).ne("")
PH = P[P.world != "W1"]
LT = pd.read_csv(O / "predictions/live_turns.csv", low_memory=False)
LS = pd.read_csv(O / "metrics/live_sessions.csv")

print("== sizes")
print(
    "recall rows",
    len(R),
    "sessions",
    R.sid.nunique(),
    "per cond",
    R.groupby("cond").size().to_dict(),
)
print(
    "held-out recall probes per cond",
    RH.groupby("cond").size().iloc[0],
    "age20+",
    RH20.groupby("cond").size().iloc[0],
)
print(
    "probe rows",
    len(P),
    P.groupby("variant").size().to_dict(),
    "contexts",
    sorted(P.cond.unique()),
)
print("attacks per ctx", P[(P.variant == "attack")].groupby("cond").size().to_dict())
print("twins per ctx", P[(P.variant == "twin")].groupby("cond").size().to_dict())
print(
    "live turns",
    len(LT),
    "sessions per cond",
    LS.groupby("cond").size().to_dict(),
    "turns/session",
    LS.turns.unique(),
)

print("\n== Table 1 / 2 (held-out)")
for c in ["F4", "B0", "B1", "B1x2", "B2", "B3", "A1", "A2", "A3", "A4"]:
    m = "barrier" if c == "F4" else "direct"
    pc = PH[PH.cond == c]
    row = [c, "rec20", f(boot(RH20[RH20.cond == c], "correct", "sid"))]
    if c in ("F4", "B2", "B3", "A2", "A3", "A4"):
        row += [
            "MRR",
            f(boot(RH[RH.cond == c].dropna(subset=["rr"]), "rr", "sid"), 1, 3),
        ]
    if len(pc):
        row += [
            "viol/100",
            f(boot(pc, f"violated_{m}", "pid", den=f"transitions_{m}")),
            "attack",
            f(boot(pc[pc.variant == "attack"], f"success_{m}", "pid")),
        ]
    row += ["in_tok", round(RH[RH.cond == c].prompt_tokens.mean())]
    print(*row)
    print(
        "   by age",
        {
            a: round(100 * RH[(RH.cond == c) & (RH.age == a)].correct.mean(), 1)
            for a in (5, 10, 20, 40, 80, 160)
        },
    )

print("\n== Table 5 (all worlds, all contexts)")
PA = P[P.variant == "attack"]
for cat in [
    "teleport",
    "fabrication",
    "theft",
    "trust",
    "currency",
    "injection",
    "secret",
    None,
]:
    a = PA if cat is None else PA[PA.category == cat]
    al = P if cat is None else P[P.category == cat]
    t = al[al.variant == "twin"]
    print(
        cat or "all",
        len(a),
        *(
            round(100 * a[f"success_{m}"].astype(float).mean(), 1)
            for m in ("direct", "reducer", "barrier")
        ),
        "FRR",
        round(100 * t.lawful_rejected.sum() / max(t.lawful_props.sum(), 1), 1),
        "gap",
        round(100 * al.unlawful_accepted.sum() / max(al.unlawful_props.sum(), 1), 1),
    )

print("\n== Table 3 (live factorial)")
for c in ["F1", "F2", "F3", "F4", "A5", "A6"]:
    lt = LT[LT.cond == c]
    pr = lt[lt.kind == "probe"]
    print(
        c,
        "recall",
        round(100 * pr.correct.astype(float).mean(), 1),
        "viol/100",
        round(100 * lt.violated.astype(float).sum() / lt.transitions.sum(), 1),
        "desync",
        round(100 * lt.desync.astype(float).mean(), 1),
        "sessions",
        lt.lid.nunique(),
        "turns",
        len(lt),
    )

print("\n== H1 McNemar (held-out, age 20+)")
for b in ["B1", "B2", "B3"]:
    w = (
        RH20[RH20.cond.isin(["F4", b])]
        .pivot_table(
            index=["sid", "fact"], columns="cond", values="correct", aggfunc="first"
        )
        .dropna()
    )
    x, y = w["F4"].astype(bool), w[b].astype(bool)
    p = mcnemar(
        [
            [int((x & y).sum()), int((x & ~y).sum())],
            [int((~x & y).sum()), int((~x & ~y).sum())],
        ],
        exact=True,
    ).pvalue
    print(b, "n", len(w), "diff", round(x.mean() - y.mean(), 4), "p_raw", p)

print("\n== H2 Wilcoxon MRR F4 vs B2 (held-out)")
w = (
    RH[RH.cond.isin(["F4", "B2"])]
    .groupby(["sid", "fact", "cond"])
    .rr.mean()
    .unstack()
    .dropna()
)
print(
    "n",
    len(w),
    "diff",
    round((w.F4 - w.B2).mean(), 4),
    "p",
    sps.wilcoxon(w.F4, w.B2, zero_method="zsplit").pvalue,
)

print("\n== H3 attack success direct vs barrier, F4 ctx (all worlds)")
a = PA[PA.cond == "F4"]
print(
    "n",
    len(a),
    "diff",
    round(
        a.success_direct.astype(float).mean() - a.success_barrier.astype(float).mean(),
        4,
    ),
)

print("\n== latency single-stream (recall prompts)")
LATR = pd.read_csv(O / "metrics/latency_single_stream_recall.csv")
print(
    LATR.groupby("cond")
    .llm_ms.agg(
        ["count", lambda s: np.percentile(s, 50), lambda s: np.percentile(s, 95)]
    )
    .round(0)
)
print("\n== replay summary")
print(pd.read_csv(O / "metrics/replay_summary.csv").to_string(index=False))
RT = pd.read_csv(O / "metrics/recovery_timing.csv")
r160 = RT[RT.turn == 160]
print(
    "turn160 snapshot median",
    round(r160.snapshot_ms.median(), 2),
    "full median",
    round(r160.full_replay_ms.median(), 1),
    "n",
    len(r160),
)
print(
    "live replay",
    LS.groupby("cond").replay_full.apply(lambda s: s.dropna().mean()).to_dict(),
)
print(
    "corrupt turns/session", LS.groupby("cond").corrupt_turns.mean().round(1).to_dict()
)
