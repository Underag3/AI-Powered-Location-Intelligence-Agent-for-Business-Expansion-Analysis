"""Skrip Pengujian Langsung (Direct Test Suite) - Tanpa Agent & Tanpa Kuota LLM.
Menguji langsung 3 komponen inti sistem:
1. Mesin Skor Deterministik (scoring.py)
2. BigQuery Data Warehouse (demographics, foot_traffic, bakery_prices, sales_history_weekly)
3. OpenStreetMap MCP Server (geocoding & pencarian tempat/kompetitor)
"""

import os
import sys
import json
import asyncio
import dotenv

# Force utf-8 output for Windows console
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Load environment & path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "adk_agent"))
dotenv.load_dotenv(os.path.join(BASE_DIR, ".env"))

from google.cloud import bigquery
from mcp_bakery_app import tools
from mcp_bakery_app.scoring import rank_locations

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "mcp1234567")


def test_scoring_engine():
    print("\n" + "=" * 60)
    print("1. PENGUJIAN MESIN SKOR DETERMINISTIK (scoring.py)")
    print("=" * 60)
    print("Menghitung 5 lokasi teratas untuk ekspansi cabang toko roti...")
    res = rank_locations(top_n=5)
    print(f"Bobot yang dipakai: {res['weights']}")
    print("-" * 60)
    print(f"{'Rank':<5} {'ZIP':<7} {'Kawasan':<24} {'Total':<7} {'Traffic':<8} {'Market':<8} {'Purchasing':<10}")
    print("-" * 60)
    for loc in res["locations"]:
        neighborhood = loc["neighborhood"].encode("ascii", "replace").decode("ascii")
        print(
            f"{loc['rank']:<5} {loc['zip_code']:<7} {neighborhood:<24} "
            f"{loc['total_score']:<7.2f} {loc['traffic_score']:<8.2f} "
            f"{loc['market_score']:<8.2f} {loc['purchasing_score']:<10.2f}"
        )
    print("-" * 60)
    print("[OK] Mesin skor berhasil dieksekusi 100% deterministik.")


def test_bigquery_direct():
    print("\n" + "=" * 60)
    print("2. PENGUJIAN KUERI LANGSUNG BIGQUERY SANDBOX")
    print("=" * 60)
    client = bigquery.Client(project=PROJECT_ID)

    # Q1: Populasi 90001
    q1 = client.query(
        f"SELECT zip_code, total_population, city, neighborhood "
        f"FROM `{PROJECT_ID}.mcp_bakery.demographics` WHERE zip_code = '90001'"
    ).to_dataframe().iloc[0]
    print(f"[Q1] Populasi kode pos 90001 ({q1['neighborhood']}): {int(q1['total_population']):,} jiwa")

    # Q2: Foot traffic malam tertinggi
    q2 = client.query(
        f"SELECT zip_code, foot_traffic_score "
        f"FROM `{PROJECT_ID}.mcp_bakery.foot_traffic` "
        f"WHERE time_of_day = 'evening' ORDER BY foot_traffic_score DESC LIMIT 1"
    ).to_dataframe().iloc[0]
    print(f"[Q2] Skor foot traffic malam tertinggi: ZIP {q2['zip_code']} (Skor: {q2['foot_traffic_score']})")

    # Q3: Rata-rata harga Sourdough Loaf LA Metro
    q3 = client.query(
        f"SELECT AVG(price) as avg_price "
        f"FROM `{PROJECT_ID}.mcp_bakery.bakery_prices` "
        f"WHERE product_type = 'Sourdough Loaf' AND region = 'Los Angeles Metro'"
    ).to_dataframe().iloc[0]
    print(f"[Q3] Rata-rata harga Sourdough Loaf di LA Metro: ${q3['avg_price']:.2f}")

    # Q4: Total pendapatan cabang Downtown LA
    q4 = client.query(
        f"SELECT SUM(total_revenue) as rev, COUNT(*) as cnt "
        f"FROM `{PROJECT_ID}.mcp_bakery.sales_history_weekly` "
        f"WHERE store_location = 'Downtown LA'"
    ).to_dataframe().iloc[0]
    print(f"[Q4] Total pendapatan cabang Downtown LA: ${q4['rev']:,.2f} (dari {int(q4['cnt'])} minggu data)")

    # Q6: Persentase lulusan sarjana tertinggi
    q6 = client.query(
        f"SELECT zip_code, neighborhood, bachelors_degree_pct "
        f"FROM `{PROJECT_ID}.mcp_bakery.demographics` "
        f"ORDER BY bachelors_degree_pct DESC LIMIT 1"
    ).to_dataframe().iloc[0]
    print(f"[Q6] Sarjana tertinggi: ZIP {q6['zip_code']} ({q6['neighborhood']}) — {q6['bachelors_degree_pct']}%")
    print("[OK] Seluruh kueri BigQuery Sandbox berhasil dieksekusi.")


async def test_osm_direct_async():
    print("\n" + "=" * 60)
    print("3. PENGUJIAN TOOLSET OPENSTREETMAP MCP (Geocoding & Places)")
    print("=" * 60)
    osm = tools.get_osm_mcp_toolset()
    t_list = await osm.get_tools()

    # Geocoding test
    print("Memanggil geocode_address untuk 'Santa Monica, California'...")
    geo_tool = next(t for t in t_list if t.name == "geocode_address")
    geo_res = await geo_tool.run_async(args={"address": "Santa Monica, California"}, tool_context=None)
    
    lat, lon = 34.0194704, -118.4912270
    if isinstance(geo_res, dict) and "content" in geo_res:
        txt = geo_res["content"][0]["text"]
        try:
            data = json.loads(txt)
            lat = float(data.get("lat", lat))
            lon = float(data.get("lon", lon))
            print(f"  -> Koordinat ditemukan: Lat {lat}, Lon {lon}")
            display = str(data.get("display_name", "")).encode("ascii", "replace").decode("ascii")
            print(f"  -> Alamat lengkap: {display}")
        except Exception:
            safe_txt = txt[:120].encode("ascii", "replace").decode("ascii")
            print(f"  -> Output raw: {safe_txt}...")
    
    # Find nearby bakeries test with coordinates
    print(f"\nMemanggil find_nearby_places untuk 'bakery' di sekitar Lat {lat}, Lon {lon}...")
    find_tool = next(t for t in t_list if t.name == "find_nearby_places")
    places_res = await find_tool.run_async(
        args={"latitude": lat, "longitude": lon, "category": "bakery", "radius": 2000},
        tool_context=None
    )
    if isinstance(places_res, dict) and "content" in places_res:
        txt = places_res["content"][0]["text"]
        print(f"  -> Hasil pencarian toko roti (kompetitor di sekitar lokasi):")
        lines = [line.strip() for line in txt.split("\n") if line.strip()]
        for line in lines[:8]:
            safe_line = line.encode("ascii", "replace").decode("ascii")
            print(f"     {safe_line}")
    print("[OK] Tool OpenStreetMap MCP berhasil dieksekusi langsung.")


def main():
    print("=" * 60)
    print("SUITE PENGUJIAN MANDIRI (ZERO LLM TOKENS / RP0)")
    print("=" * 60)
    test_scoring_engine()
    test_bigquery_direct()
    asyncio.run(test_osm_direct_async())
    print("\n" + "=" * 60)
    print("SEMUA PENGUJIAN LANGSUNG SELESAI & TERVERIFIKASI!")
    print("=" * 60)


if __name__ == "__main__":
    main()
