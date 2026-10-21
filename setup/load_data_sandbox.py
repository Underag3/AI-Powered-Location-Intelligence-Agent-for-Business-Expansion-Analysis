import os
from google.cloud import bigquery

PROJECT_ID = "mcp1234567"
DATASET_ID = f"{PROJECT_ID}.mcp_bakery"

client = bigquery.Client(project=PROJECT_ID)

# 1. Create Dataset if not exists
dataset = bigquery.Dataset(DATASET_ID)
dataset.location = "US"
dataset.description = "LA bakery expansion data"
dataset = client.create_dataset(dataset, exists_ok=True)
print(f"Dataset {dataset.dataset_id} ready in location {dataset.location}.")

# 2. Load Demographics Table
schema_dem = [
    bigquery.SchemaField("zip_code", "STRING"),
    bigquery.SchemaField("city", "STRING"),
    bigquery.SchemaField("neighborhood", "STRING"),
    bigquery.SchemaField("total_population", "INTEGER"),
    bigquery.SchemaField("median_age", "FLOAT"),
    bigquery.SchemaField("bachelors_degree_pct", "FLOAT"),
    bigquery.SchemaField("foot_traffic_index", "FLOAT"),
]
job_config = bigquery.LoadJobConfig(
    schema=schema_dem,
    skip_leading_rows=1,
    source_format=bigquery.SourceFormat.CSV,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
)
with open("data/demographics.csv", "rb") as f:
    job = client.load_table_from_file(f, f"{DATASET_ID}.demographics", job_config=job_config)
job.result()
print(f"Loaded demographics: {job.output_rows} rows.")

# 3. Load Foot Traffic Table
schema_ft = [
    bigquery.SchemaField("zip_code", "STRING"),
    bigquery.SchemaField("time_of_day", "STRING"),
    bigquery.SchemaField("foot_traffic_score", "FLOAT"),
]
job_config = bigquery.LoadJobConfig(
    schema=schema_ft,
    skip_leading_rows=1,
    source_format=bigquery.SourceFormat.CSV,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
)
with open("data/foot_traffic.csv", "rb") as f:
    job = client.load_table_from_file(f, f"{DATASET_ID}.foot_traffic", job_config=job_config)
job.result()
print(f"Loaded foot_traffic: {job.output_rows} rows.")

# 4. Load Bakery Prices Table
schema_prices = [
    bigquery.SchemaField("store_name", "STRING"),
    bigquery.SchemaField("product_type", "STRING"),
    bigquery.SchemaField("price", "FLOAT"),
    bigquery.SchemaField("region", "STRING"),
    bigquery.SchemaField("is_organic", "BOOLEAN"),
]
job_config = bigquery.LoadJobConfig(
    schema=schema_prices,
    skip_leading_rows=1,
    source_format=bigquery.SourceFormat.CSV,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
)
with open("data/bakery_prices.csv", "rb") as f:
    job = client.load_table_from_file(f, f"{DATASET_ID}.bakery_prices", job_config=job_config)
job.result()
print(f"Loaded bakery_prices: {job.output_rows} rows.")

# 5. Load Sales History Table
schema_sales = [
    bigquery.SchemaField("week_start_date", "DATE"),
    bigquery.SchemaField("store_location", "STRING"),
    bigquery.SchemaField("product_type", "STRING"),
    bigquery.SchemaField("quantity_sold", "INTEGER"),
    bigquery.SchemaField("total_revenue", "FLOAT"),
]
job_config = bigquery.LoadJobConfig(
    schema=schema_sales,
    skip_leading_rows=1,
    source_format=bigquery.SourceFormat.CSV,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
)
with open("data/sales_history_weekly.csv", "rb") as f:
    job = client.load_table_from_file(f, f"{DATASET_ID}.sales_history_weekly", job_config=job_config)
job.result()
print(f"Loaded sales_history_weekly: {job.output_rows} rows.")

# 6. Verify row counts
query = """
SELECT (SELECT COUNT(*) FROM `mcp1234567.mcp_bakery.demographics`) AS dem,
       (SELECT COUNT(*) FROM `mcp1234567.mcp_bakery.foot_traffic`) AS ft,
       (SELECT COUNT(*) FROM `mcp1234567.mcp_bakery.bakery_prices`) AS prices,
       (SELECT COUNT(*) FROM `mcp1234567.mcp_bakery.sales_history_weekly`) AS sales
"""
results = list(client.query(query).result())
for row in results:
    print(f"VERIFICATION: dem={row.dem}, ft={row.ft}, prices={row.prices}, sales={row.sales}")
