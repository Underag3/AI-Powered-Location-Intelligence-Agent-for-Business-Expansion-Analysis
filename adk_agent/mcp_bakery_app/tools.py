import os

import dotenv
import google.auth
import google.auth.transport.requests
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StdioConnectionParams,
    StreamableHTTPConnectionParams,
)
from mcp import StdioServerParameters

BIGQUERY_MCP_URL = "https://bigquery.googleapis.com/mcp"


def get_bigquery_mcp_toolset():
    """Toolset BigQuery MCP resmi (remote). Autentikasi OAuth dari ADC lokal.

    Token diambil sekali saat agent menyala dan berlaku ±1 jam; bila query
    mulai gagal dengan error autentikasi setelah agent lama menyala,
    mulai ulang `adk web` untuk menyegarkan token.
    """
    credentials, project_id = google.auth.default(
        scopes=["https://www.googleapis.com/auth/bigquery"]
    )
    credentials.refresh(google.auth.transport.requests.Request())
    project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "mcp1234567")
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "x-goog-user-project": project_id,
    }
    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=BIGQUERY_MCP_URL,
            headers=headers,
            timeout=30.0,
            sse_read_timeout=300.0,
        )
    )


def get_osm_mcp_toolset():
    """Toolset OpenStreetMap MCP (lokal, stdio). Tanpa API key dan tanpa billing.

    Bawaan: server dijalankan lewat `uvx --with "mcp<2" osm-mcp-server`.
    Bila `uvx` tidak tersedia: `pip install osm-mcp-server`, lalu set
    OSM_MCP_COMMAND=osm-mcp-server di .env.
    """
    command = os.getenv("OSM_MCP_COMMAND", "uvx")
    args = ["--with", "mcp<2", "osm-mcp-server"] if command == "uvx" else []
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(command=command, args=args),
            timeout=30.0,
        )
    )
