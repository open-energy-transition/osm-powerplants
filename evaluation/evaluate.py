#!/usr/bin/env python3
"""Per-country OSM contribution evaluation. Writes evaluation/evaluation.csv."""

import ast
from pathlib import Path

import country_converter as coco
import pandas as pd
from powerplantmatching.data import IRENASTAT

EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parent
MATCHED = EVAL_DIR / "matching" / "matched_osm_matching.csv"
OSM_WORLD = REPO_ROOT / "osm_global.csv"
OUT_CSV = EVAL_DIR / "evaluation.csv"
OUT_FT_CSV = EVAL_DIR / "evaluation_by_fueltype.csv"

cc = coco.CountryConverter()


def short(series: pd.Series) -> pd.Series:
    uniq = series.dropna().unique().tolist()
    mapping = dict(zip(uniq, cc.convert(names=uniq, to="short_name", not_found=None)))
    return series.map(mapping)


def matched_osm_ids(df: pd.DataFrame) -> set[str]:
    ids: set[str] = set()
    for p in df["projectID"].dropna():
        try:
            d = ast.literal_eval(p)
        except Exception:
            continue
        if "OSM" in d:
            ids.update(d["OSM"])
    return ids


def classify(r) -> str:
    ppm, osm, ir = r.cap_ppm_MW, r.cap_osm_only_MW, r.cap_irena_MW
    total = ppm + osm
    share = (osm / total) if total > 0 else 0
    if pd.isna(ir) or ir == 0:
        if total < 50:
            return "insufficient_reference"
        return "osm_primary" if share > 0.5 else "ppm_already_sufficient"
    if total > 2 * ir:
        return "likely_duplicates"
    if ppm < 0.1 * ir and share > 0.5:
        return "osm_primary"
    if share < 0.1:
        return "ppm_already_sufficient"
    return "osm_complements"


def main() -> None:
    matched = pd.read_csv(MATCHED, index_col=0, low_memory=False)
    osm = pd.read_csv(OSM_WORLD, low_memory=False)
    matched["Country"] = short(matched["Country"])
    osm["Country"] = short(osm["Country"])

    osm_only = osm[~osm["projectID"].isin(matched_osm_ids(matched))]

    ir = IRENASTAT()
    ir = ir[ir.Year == ir.Year.max()].copy()
    ir["Country"] = short(ir["Country"])

    out = pd.DataFrame({
        "n_ppm": matched.groupby("Country").size(),
        "cap_ppm_MW": matched.groupby("Country")["Capacity"].sum(),
        "n_osm_only": osm_only.groupby("Country").size(),
        "cap_osm_only_MW": osm_only.groupby("Country")["Capacity"].sum(),
        "cap_irena_MW": ir.groupby("Country")["Capacity"].sum(),
    }).fillna({"n_ppm": 0, "cap_ppm_MW": 0.0, "n_osm_only": 0, "cap_osm_only_MW": 0.0})
    out["cap_total_MW"] = out.cap_ppm_MW + out.cap_osm_only_MW
    out["osm_only_share"] = (out.cap_osm_only_MW / out.cap_total_MW).where(out.cap_total_MW > 0)
    out["bucket"] = out.apply(classify, axis=1)
    out = out.sort_values("cap_osm_only_MW", ascending=False)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV)

    # Per-(country, fueltype) breakdown
    ft = pd.DataFrame({
        "cap_ppm_MW": matched.groupby(["Country", "Fueltype"])["Capacity"].sum(),
        "cap_osm_only_MW": osm_only.groupby(["Country", "Fueltype"])["Capacity"].sum(),
        "cap_irena_MW": ir.groupby(["Country", "Fueltype"])["Capacity"].sum(),
    }).fillna(0.0)
    ft["cap_total_MW"] = ft.cap_ppm_MW + ft.cap_osm_only_MW
    ft["hidden_duplicate_risk"] = (
        (ft.cap_osm_only_MW > 0)
        & (ft.cap_irena_MW > 0)
        & (ft.cap_total_MW > 2 * ft.cap_irena_MW)
    )
    ft = ft.sort_values("cap_osm_only_MW", ascending=False)
    ft.to_csv(OUT_FT_CSV)

    print(f"wrote {OUT_CSV} ({len(out)} countries)")
    print(f"wrote {OUT_FT_CSV} ({len(ft)} country×fueltype rows)")
    print(f"OSM-only: {len(osm_only):,} plants / {osm_only.Capacity.sum()/1000:.0f} GW")
    good = out[out.bucket.isin(["osm_primary", "osm_complements"])]
    print(f"defensible contribution: {good.cap_osm_only_MW.sum()/1000:.0f} GW across {len(good)} countries")
    print("\nbuckets:")
    print(out.bucket.value_counts().to_string())

    # Per-fueltype duplicate-risk summary, restricted to countries in the
    # recommended fully_included list (osm_primary + osm_complements).
    good_countries = set(good.index)
    risk = ft[ft.hidden_duplicate_risk & ft.index.get_level_values(0).isin(good_countries)]
    print(f"\nhidden per-fueltype duplicate risk rows (in fully_included countries): {len(risk)}")
    if len(risk):
        print(risk.head(20).to_string())


if __name__ == "__main__":
    main()
