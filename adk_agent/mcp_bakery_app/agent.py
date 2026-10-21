import copy
import logging
import os
from typing import AsyncGenerator

import dotenv
from google.adk.agents import LlmAgent
from google.adk.models import BaseLlm, LlmRequest, LlmResponse
from google.adk.models.google_llm import Gemini

from mcp_bakery_app import tools
from mcp_bakery_app.scoring import rank_locations

dotenv.load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "mcp1234567")
DEFAULT_MODEL = os.getenv("MODEL_NAME", "gemini-3.8-flash")
FALLBACK_MODELS = [
    DEFAULT_MODEL,
    "gemini-3.6-flash",
    "gemini-3.1-flash-lite",
]
# Ensure no duplicates while preserving order
FALLBACK_MODELS = list(dict.fromkeys(FALLBACK_MODELS))

logger = logging.getLogger("mcp_bakery_app.fallback")


class FallbackGemini(BaseLlm):
    """LLM wrapper that automatically falls back to alternative Free Tier models
    if the primary model hits rate limits (429) or high demand spikes (503).
    """

    model: str = DEFAULT_MODEL
    fallback_models: list[str] = FALLBACK_MODELS

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        last_err = None
        for m in self.fallback_models:
            try:
                req = copy.copy(llm_request)
                req.model = m
                llm = Gemini(model=m)
                async for resp in llm.generate_content_async(req, stream=stream):
                    yield resp
                return
            except Exception as e:
                last_err = e
                logger.warning(
                    f"[Fallback] Model {m} gagal ({e}), mencoba model berikutnya..."
                )
        raise last_err


INSTRUCTION = f"""
Kamu adalah analis lokasi untuk jaringan toko roti yang akan membuka cabang
baru di Los Angeles. Jawab pertanyaan pengguna dengan menggabungkan tiga
sumber berikut — dan hanya sumber-sumber ini:

1. **BigQuery (dataset `mcp_bakery`, proyek `{PROJECT_ID}`)** — data demografi
   per kode pos (termasuk indeks foot traffic), skor foot traffic per waktu,
   harga produk kompetitor, dan riwayat penjualan mingguan 3 cabang yang ada.
   Saat memanggil tool query BigQuery, selalu isi argumen projectId dengan
   "{PROJECT_ID}" dan hanya gunakan dataset `mcp_bakery`.
2. **Mesin skor `rank_locations`** — fungsi Python deterministik yang
   menghitung peringkat kode pos dari data BigQuery.
3. **OpenStreetMap (tool geocode/nearby places/routes)** — verifikasi dunia
   nyata: kompetitor dan tempat di sekitar suatu kawasan, serta rute/jarak.

ATURAN WAJIB:
- Peringkat lokasi HANYA boleh berasal dari keluaran `rank_locations`.
  Kutip angka dan urutannya apa adanya; jangan mengubah urutan, jangan
  mengarang skor. Bila pengguna minta peringkat, panggil tool itu dulu.
- Semua angka lain (populasi, harga, penjualan, skor foot traffic) HANYA dari
  hasil query BigQuery. Jangan mengarang angka.
- Cek kompetitor di sekitar titik/kawasan HANYA dari tool OpenStreetMap
  (mis. find_nearby_places / search_category untuk kategori bakery).
- Bila sebuah tool gagal atau datanya tidak ada, katakan itu dengan jujur dan
  jelaskan keterbatasannya; jangan menutupi dengan karangan.
- Jawab dalam bahasa yang dipakai pengguna.
"""

root_agent = LlmAgent(
    model=FallbackGemini(),
    name="location_intelligence_agent",
    instruction=INSTRUCTION,
    tools=[
        tools.get_bigquery_mcp_toolset(),
        tools.get_osm_mcp_toolset(),
        rank_locations,
    ],
)
