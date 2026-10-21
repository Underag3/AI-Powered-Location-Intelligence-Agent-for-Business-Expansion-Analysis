# Skrip PowerShell untuk memuat data ke BigQuery Sandbox (tanpa Cloud Storage Bucket)
$ErrorActionPreference = "Stop"

Write-Host "Memulai proses pemuatan data BigQuery Sandbox..." -ForegroundColor Cyan

# Menjalankan pemuatan data melalui skrip Python yang sudah terkonfigurasi dengan BigQuery Client & ADC
$pythonExe = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
$pyScript = Join-Path $PSScriptRoot "load_data_sandbox.py"

if (Test-Path $pythonExe) {
    & $pythonExe $pyScript
} else {
    python $pyScript
}

Write-Host "Pemuatan data selesai." -ForegroundColor Green
