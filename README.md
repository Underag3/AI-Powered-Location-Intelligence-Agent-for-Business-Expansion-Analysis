# AI-Powered Location Intelligence Agent for Business Expansion Analysis

An AI-powered location intelligence agent built using **Google Agent Development Kit (ADK)**, **Model Context Protocol (MCP)**, **BigQuery Sandbox**, and **OpenStreetMap (OSM)**.  
This project demonstrates how an autonomous AI agent can combine structured enterprise data with real-world geospatial intelligence to support data-driven retail expansion decisions—completely free of charge (**Rp0 / Zero Billing**).

---

## 📌 Background & Context

This project originated from the author's participation in the **Google Cloud Gen AI Academy APAC** program, building upon and extending the official academy materials.

The initial codelab implementation depended on Vertex AI, Google Maps Platform APIs, and Google Cloud Storage (GCS) buckets, which strictly require active Google Cloud billing. To ensure this project is fully reproducible, educational, and cost-free, the architecture was re-engineered:
- **Zero-Billing Architecture**: Runs BigQuery in **Sandbox Mode** (free 10 GB storage and 1 TiB query/month, without requiring a credit card or active billing).
- **OpenStreetMap MCP Server**: Replaced Google Maps Platform with the open-source `osm-mcp-server` executed via `uvx`, providing geocoding, POI discovery, and routing over standard stdio without requiring any API keys.
- **Deterministic Scoring Engine (`scoring.py`)**: Replaced probabilistic LLM guessing with a mathematically grounded Python scoring function (`rank_locations`), preventing AI hallucinations.
- **Multi-Model Resilient Fallback**: Designed a dynamic fallback wrapper across Google AI Studio Free Tier models (`gemini-3.8-flash` ➔ `gemini-3.6-flash` ➔ `gemini-3.1-flash-lite`) to guarantee zero downtime during peak demand (503) or daily rate limits (429).

---

## 🏗️ System Architecture

```text
                           +---------------------------+
                           |           User            |
                           +-------------+-------------+
                                         |
                                         v asks location questions
                       +-----------------------------------+
                       |    Google ADK Root Agent          |
                       | (Multi-Model Resilient Fallback)  |
                       |    - gemini-3.8-flash (Primary)   |
                       |    - gemini-3.6-flash (Fallback)  |
                       |    - gemini-3.1-flash-lite        |
                       +-----------------+-----------------+
                                         |
                                         | decides tool execution
            +----------------------------+----------------------------+
            |                            |                            |
            v                            v                            v
+-----------------------+   +-------------------------+   +-------------------------+
| BigQuery MCP Server   |   | OpenStreetMap MCP       |   | Deterministic Scoring   |
| (Remote HTTP Stream)  |   | (Local stdio / uvx)     |   | Engine (scoring.py)     |
| URL: bigquery.goog... |   | osm-mcp-server          |   | rank_locations()        |
+-----------+-----------+   +------------+------------+   +------------+------------+
            |                            |                             |
            | Demographics, Traffic,     | Real-world Places,          | Strict Multi-Factor   |
            | Prices, Weekly Sales       | Competitors, Routes         | Mathematical Ranking  |
            v                            v                             v
+-----------------------------------------------------------------------------------+
|                        Integrated Business Recommendation                         |
+-----------------------------------------------------------------------------------+
```

---

## 🛠️ Tech Stack

| Technology | Purpose | Cost / Tier |
|---|---|---|
| **Google ADK (Agent Development Kit)** | Framework for orchestrating the multi-tool AI agent | Open Source |
| **Google AI Studio (Gemini)** | LLM reasoning engine with dynamic model failover | Free Tier (Rp0) |
| **Model Context Protocol (MCP)** | Open standard protocol connecting LLM to external data tools | Open Standard |
| **BigQuery MCP Server** | Remote MCP server querying structured business data | Sandbox Mode (Rp0) |
| **OpenStreetMap MCP Server** | Local stdio MCP server for geocoding, POIs, and route calculation | Open Source (Rp0) |
| **Python & Pandas** | Deterministic ranking engine (`rank_locations`) & data loading | Open Source |

---

## 📁 Repository Structure

```text
AI-Powered-Location-Intelligence-Agent-for-Business-Expansion-Analysis/
├── .gitignore                          # Ignores credentials, .env, and local venvs
├── README.md                           # Comprehensive documentation & evaluation results
├── requirements.txt                    # All required production dependencies
├── .env.example                        # Template for environment configuration
├── architecture_diagram.png            # Visual architecture overview
├── adk_agent/
│   └── mcp_bakery_app/
│       ├── __init__.py                 # Package initializer
│       ├── agent.py                    # Root agent with FallbackGemini & anti-hallucination prompt
│       ├── tools.py                    # BigQuery MCP and OpenStreetMap MCP configuration
│       └── scoring.py                  # Deterministic ranking engine (rank_locations)
├── data/                               # Ground-truth datasets (California & Los Angeles)
│   ├── demographics.csv                # 305 ZIP codes: population, age, education, foot traffic index
│   ├── foot_traffic.csv                # 915 rows: foot traffic scores by time of day
│   ├── bakery_prices.csv               # 50 rows: competitor pricing across bakery categories
│   └── sales_history_weekly.csv        # 936 rows: historical weekly sales across 3 branch locations
└── setup/
    ├── load_data_sandbox.py            # Automated BigQuery Sandbox dataset creation & CSV loader
    ├── load_data_sandbox.sh            # Shell script for loading data (Linux/macOS)
    ├── load_data_sandbox.ps1           # PowerShell script for loading data (Windows)
    ├── setup_env.sh                    # [LEGACY] Original GCP codelab setup (requires billing)
    └── setup_bigquery.sh               # [LEGACY] Original GCS-to-BQ setup (requires billing)
```

> [!NOTE]
> The scripts `setup/setup_env.sh` and `setup/setup_bigquery.sh` are preserved as **legacy files** from the original Google Cloud codelab. They assume Google Maps Platform API keys and Cloud Storage buckets which require active Google Cloud billing. For the free-tier Sandbox workflow, use `setup/load_data_sandbox.py` (or `.sh` / `.ps1`).

---

## 📊 Deterministic Location Scoring Logic (`scoring.py`)

To eliminate LLM hallucinations when evaluating expansion targets, the agent uses a mathematically locked multi-factor scoring formula:

$$\text{Total Score} = 0.40 \times \text{Traffic Score} + 0.35 \times \text{Market Score} + 0.25 \times \text{Purchasing Score}$$

### Score Components:
1. **Traffic Score (40%)**:
   $$\text{traffic\_raw} = 0.5 \times \text{avg\_ft} + 0.5 \times \text{foot\_traffic\_index}$$
   Combined average morning/afternoon/evening foot traffic scores with area mobility index, scaled via Min-Max ($0 - 100$).
2. **Market Score (35%)**:
   $$\text{market\_raw} = \text{total\_population}$$
   Total population count within the ZIP code, scaled via Min-Max ($0 - 100$).
3. **Purchasing Score (25%)**:
   $$\text{purchasing\_raw} = \text{bachelors\_degree\_pct}$$
   Percentage of population aged 25+ with a bachelor's degree or higher (proxy for artisanal bakery purchasing power), scaled via Min-Max ($0 - 100$).
4. **Competitor Handling**:
   Competitor pricing data is aggregated at the regional level (Los Angeles Metro, SF Bay Area, San Diego), not by physical radius. Therefore, competitor presence is **excluded from the numeric formula** and validated separately via OpenStreetMap MCP (`find_nearby_places`).

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites
- **Python 3.10 to 3.13** installed.
- **`uv` package manager**:
  - Windows: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
  - macOS / Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Google Cloud Application Default Credentials (ADC)**:
  Run `gcloud auth application-default login` on your machine (or copy `~/.config/gcloud/application_default_credentials.json` from Cloud Shell to `%APPDATA%\gcloud\application_default_credentials.json`).

### 2. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/Underag3/AI-Powered-Location-Intelligence-Agent-for-Business-Expansion-Analysis.git
cd AI-Powered-Location-Intelligence-Agent-for-Business-Expansion-Analysis

# Create virtual environment and install dependencies
uv venv --python 3.13 .venv
uv pip install -r requirements.txt --python .venv/Scripts/python.exe
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` and fill in your free Google AI Studio API key:
```env
GOOGLE_API_KEY=AIzaSy...
GOOGLE_CLOUD_PROJECT=mcp1234567
MODEL_NAME=gemini-3.8-flash
OSM_MCP_COMMAND=uvx
```

### 4. Load Data into BigQuery Sandbox
Run the sandbox loader script to create dataset `mcp_bakery` and load the 4 tables directly without Cloud Storage buckets:
- **Python (Cross-platform)**:
  ```bash
  .venv/Scripts/python setup/load_data_sandbox.py
  ```
- **Windows PowerShell**:
  ```powershell
  .\setup\load_data_sandbox.ps1
  ```
- **Linux / macOS**:
  ```bash
  bash setup/load_data_sandbox.sh
  ```

Verified row count:
* `demographics`: **305 rows**
* `foot_traffic`: **915 rows**
* `bakery_prices`: **50 rows**
* `sales_history_weekly`: **936 rows**

### 5. Run the Agent
From the `adk_agent/` directory:
- **Web UI Mode**:
  ```bash
  adk web
  ```
  Open the local URL displayed in the terminal (e.g., `http://127.0.0.1:8000`).
- **CLI Direct Query Mode**:
  ```bash
  adk run mcp_bakery_app "Berapa populasi kode pos 90001?"
  ```

---

## 📈 Evaluation & Ground Truth Benchmark

All questions below have been mathematically verified directly against the underlying dataset and deterministic engine:

| # | Question | Ground Truth / Target Answer | Verified Source |
|---|---|---|---|
| **Q1** | Berapa populasi kode pos 90001? | **33.626 jiwa** | `demographics.csv` |
| **Q2** | Kode pos mana yang skor foot traffic malam harinya (evening) paling tinggi, dan berapa skornya? | **91723 — 55,0** | `foot_traffic.csv` |
| **Q3** | Berapa rata-rata harga Sourdough Loaf di wilayah Los Angeles Metro? | **$11,25** | `bakery_prices.csv` |
| **Q4** | Berapa total pendapatan cabang Downtown LA dari seluruh data penjualan? | **$502.166,75** (312 minggu) | `sales_history_weekly.csv` |
| **Q5** | Kode pos mana yang paling berpotensi untuk cabang baru? Sebutkan 5 teratas beserta skornya. | **Tabel Acuan Q5 (di bawah)** | `scoring.rank_locations(5)` |
| **Q6** | Kode pos mana dengan persentase lulusan sarjana tertinggi? | **90402 (Santa Monica) — 95,0%** | `demographics.csv` |
| **Q7** | Toko roti apa saja yang ada di sekitar Santa Monica? | Daftar nama tempat nyata | OpenStreetMap (`find_nearby_places`) |
| **Q8** | Bandingkan tiga kawasan teratas untuk cabang baru. | Rincian skor komponen 91301 vs 91011 vs 91108 | `scoring.py` |
| **Q9** | Kenapa 91301 peringkatnya di atas 90265? | Skor pasar 94,88 vs 69,88; total 91,91 vs 86,32 | `scoring.py` |
| **Q10** | Berapa jarak/rute dari Downtown Los Angeles ke Agoura Hills? | Jarak dan estimasi rute nyata | OpenStreetMap (`get_route_directions`) |

### Benchmark Output: Top 5 Location Ranking (Q5)
```json
{
  "weights": { "traffic": 0.4, "market": 0.35, "purchasing": 0.25 },
  "count": 5,
  "locations": [
    {
      "rank": 1,
      "zip_code": "91301",
      "neighborhood": "Agoura Hills",
      "city": "Los Angeles",
      "total_score": 91.91,
      "traffic_score": 88.53,
      "market_score": 94.88,
      "purchasing_score": 93.18
    },
    {
      "rank": 2,
      "zip_code": "91011",
      "neighborhood": "La Cañada Flintridge",
      "city": "Los Angeles",
      "total_score": 91.05,
      "traffic_score": 86.62,
      "market_score": 89.71,
      "purchasing_score": 100.00
    },
    {
      "rank": 3,
      "zip_code": "91108",
      "neighborhood": "San Marino",
      "city": "Los Angeles",
      "total_score": 90.81,
      "traffic_score": 100.00,
      "market_score": 73.76,
      "purchasing_score": 100.00
    },
    {
      "rank": 4,
      "zip_code": "91302",
      "neighborhood": "Calabasas",
      "city": "Los Angeles",
      "total_score": 87.07,
      "traffic_score": 77.94,
      "market_score": 91.80,
      "purchasing_score": 95.06
    },
    {
      "rank": 5,
      "zip_code": "90265",
      "neighborhood": "Malibu",
      "city": "Los Angeles",
      "total_score": 86.32,
      "traffic_score": 92.16,
      "market_score": 69.88,
      "purchasing_score": 100.00
    }
  ]
}
```

---

## ⚠️ Known Limitations & Operational Notes

1. **BigQuery Sandbox 60-Day Table TTL**:  
   Tables created under BigQuery Sandbox automatically expire after 60 days. If tables expire, simply re-run `python setup/load_data_sandbox.py` to restore all 4 tables in seconds.
2. **OAuth Token Lifecycle**:  
   Google OAuth tokens refreshed via Application Default Credentials (ADC) last approximately 1 hour. If a long-running `adk web` session encounters an authentication error, restart the server to refresh credentials.
3. **OpenStreetMap Coverage vs. Google Maps**:  
   OpenStreetMap (OSM) relies on community contributions. While rich in urban POIs and street geometry, business categorization in certain suburban areas may differ from proprietary commercial APIs like Google Places.

---

## 📜 Attribution

This project is adapted and modified from Google's codelab:
* **Google Codelab**: *Build a Location Intelligence ADK Agent with MCP servers for BigQuery and Google Maps*
* **Google MCP Repository**: [https://github.com/google/mcp](https://github.com/google/mcp)

The original codelab content is licensed under the **Creative Commons Attribution 4.0 License**.  
The original code samples are licensed under the **Apache License 2.0**.

This repository re-engineers the original concept for standalone portfolio, zero-cost, and educational purposes—including the elimination of cloud billing requirements, replacement with OpenStreetMap MCP, addition of deterministic mathematical ranking logic, and resilient multi-model failover mechanisms.

---

## 📄 License

This project includes code and concepts adapted from Google MCP examples licensed under the **Apache License 2.0**. Please refer to the original Google MCP repository for upstream terms.

---

## 👨‍💻 Author

**Mohammad Tyas Subianto**  
* GitHub: [@Underag3](https://github.com/Underag3)
