"""Mesin skor lokasi ekspansi — deterministik, tanpa LLM.

Skor per kode pos dari data BigQuery (dataset mcp_bakery):
    skor_total = 0,40*skor_keramaian + 0,35*skor_pasar + 0,25*skor_daya_beli

- keramaian : rata-rata foot_traffic_score (pagi/siang/malam) digabung
              foot_traffic_index, lalu dinormalisasi min-max 0..100.
- pasar     : total_population, dinormalisasi min-max 0..100.
- daya_beli : bachelors_degree_pct (proksi pendidikan/daya beli),
              dinormalisasi min-max 0..100.
Kompetisi sengaja TIDAK masuk skor (data harga kompetitor hanya per wilayah);
kompetisi diverifikasi terpisah lewat OpenStreetMap.
"""

import pandas as pd
from google.cloud import bigquery

PROJECT_ID = "mcp1234567"
DATASET = "mcp_bakery"
WEIGHTS = {"traffic": 0.40, "market": 0.35, "purchasing": 0.25}


def _minmax(series: pd.Series) -> pd.Series:
    span = series.max() - series.min()
    if span == 0:
        return pd.Series(50.0, index=series.index)
    return 100.0 * (series - series.min()) / span


def rank_locations(top_n: int = 10) -> dict:
    """Hitung peringkat kode pos terbaik untuk cabang toko roti baru.

    Args:
        top_n: berapa peringkat teratas yang dikembalikan (bawaan 10).

    Returns:
        Dict berisi bobot yang dipakai dan daftar lokasi terurut menurun
        berdasarkan skor total, masing-masing dengan rincian skor komponen.
    """
    client = bigquery.Client(project=PROJECT_ID)
    dem = client.query(
        f"SELECT zip_code, city, neighborhood, total_population, "
        f"bachelors_degree_pct, foot_traffic_index "
        f"FROM `{PROJECT_ID}.{DATASET}.demographics`"
    ).to_dataframe()
    ft = client.query(
        f"SELECT zip_code, AVG(foot_traffic_score) AS avg_ft "
        f"FROM `{PROJECT_ID}.{DATASET}.foot_traffic` GROUP BY zip_code"
    ).to_dataframe()

    d = dem.merge(ft, on="zip_code", how="inner")
    d["traffic_raw"] = 0.5 * d["avg_ft"] + 0.5 * d["foot_traffic_index"]
    d["traffic_score"] = _minmax(d["traffic_raw"])
    d["market_score"] = _minmax(d["total_population"])
    d["purchasing_score"] = _minmax(d["bachelors_degree_pct"])
    d["total_score"] = (
        WEIGHTS["traffic"] * d["traffic_score"]
        + WEIGHTS["market"] * d["market_score"]
        + WEIGHTS["purchasing"] * d["purchasing_score"]
    )
    d = d.sort_values(["total_score", "zip_code"], ascending=[False, True])
    d = d.head(top_n).round(2)

    locations = []
    for rank, (_, r) in enumerate(d.iterrows(), start=1):
        locations.append(
            {
                "rank": rank,
                "zip_code": str(r["zip_code"]),
                "neighborhood": r["neighborhood"],
                "city": r["city"],
                "total_score": float(r["total_score"]),
                "traffic_score": float(r["traffic_score"]),
                "market_score": float(r["market_score"]),
                "purchasing_score": float(r["purchasing_score"]),
            }
        )
    return {"weights": WEIGHTS, "count": len(locations), "locations": locations}
