#!/usr/bin/env python3
"""Per-country OSM contribution evaluation.

Reads matched_osm_only.csv and matched_osm_full.csv, writes evaluation.csv
and evaluation_by_fueltype.csv."""

import ast
from pathlib import Path

import country_converter as coco
import pandas as pd
from powerplantmatching.data import IRENASTAT

EVAL_DIR = Path(__file__).resolve().parent
MATCHED_ONLY = EVAL_DIR / "matching" / "matched_osm_only.csv"
MATCHED_FULL = EVAL_DIR / "matching" / "matched_osm_full.csv"
OUT_CSV = EVAL_DIR / "evaluation.csv"
OUT_FT_CSV = EVAL_DIR / "evaluation_by_fueltype.csv"

cc = coco.CountryConverter()


def short(series: pd.Series) -> pd.Series:
    uniq = series.dropna().unique().tolist()
    mapping = dict(zip(uniq, cc.convert(names=uniq, to="short_name", not_found=None)))
    return series.map(mapping)


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
    only = pd.read_csv(MATCHED_ONLY, index_col=0, low_memory=False)
    full = pd.read_csv(MATCHED_FULL, index_col=0, low_memory=False)
    only["Country"] = short(only["Country"])
    full["Country"] = short(full["Country"])

    only_keys = only["projectID"].map(lambda p: set(ast.literal_eval(p)))
    full_keys = full["projectID"].map(lambda p: set(ast.literal_eval(p)))
    ppm = only[only_keys != {"OSM"}]
    osm_only_gross = only[only_keys == {"OSM"}]
    osm_only_filt = full[full_keys == {"OSM"}]

    ir = IRENASTAT()
    ir = ir[ir.Year == ir.Year.max()].copy()
    ir["Country"] = short(ir["Country"])

    out = pd.DataFrame({
        "n_ppm": ppm.groupby("Country").size(),
        "cap_ppm_MW": ppm.groupby("Country")["Capacity"].sum(),
        "n_osm_only": osm_only_gross.groupby("Country").size(),
        "cap_osm_only_MW": osm_only_gross.groupby("Country")["Capacity"].sum(),
        "n_osm_only_filtered": osm_only_filt.groupby("Country").size(),
        "cap_osm_only_filtered_MW": osm_only_filt.groupby("Country")["Capacity"].sum(),
        "cap_irena_MW": ir.groupby("Country")["Capacity"].sum(),
    }).fillna(0)
    out["cap_total_MW"] = out.cap_ppm_MW + out.cap_osm_only_MW
    out["osm_only_share"] = (out.cap_osm_only_MW / out.cap_total_MW).where(out.cap_total_MW > 0)
    out["bucket"] = out.apply(classify, axis=1)
    out = out.sort_values("cap_osm_only_MW", ascending=False)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV)

    ft = pd.DataFrame({
        "cap_ppm_MW": ppm.groupby(["Country", "Fueltype"])["Capacity"].sum(),
        "cap_osm_only_MW": osm_only_gross.groupby(["Country", "Fueltype"])["Capacity"].sum(),
        "cap_osm_only_filtered_MW": osm_only_filt.groupby(["Country", "Fueltype"])["Capacity"].sum(),
        "cap_irena_MW": ir.groupby(["Country", "Fueltype"])["Capacity"].sum(),
    }).fillna(0)
    ft["cap_total_MW"] = ft.cap_ppm_MW + ft.cap_osm_only_MW
    ft["hidden_duplicate_risk"] = (
        (ft.cap_osm_only_MW > 0)
        & (ft.cap_irena_MW > 0)
        & (ft.cap_total_MW > 2 * ft.cap_irena_MW)
    )
    ft = ft.sort_values("cap_osm_only_MW", ascending=False)
    ft.to_csv(OUT_FT_CSV)


if __name__ == "__main__":
    main()
