#!/usr/bin/env bash
set -euo pipefail
PROJECT=mcp1234567

bq --project_id=$PROJECT mk --dataset --description "LA bakery expansion data" $PROJECT:mcp_bakery || true

bq --project_id=$PROJECT load --replace --source_format=CSV --skip_leading_rows=1 \
  mcp_bakery.demographics ./data/demographics.csv \
  zip_code:STRING,city:STRING,neighborhood:STRING,total_population:INTEGER,median_age:FLOAT,bachelors_degree_pct:FLOAT,foot_traffic_index:FLOAT

bq --project_id=$PROJECT load --replace --source_format=CSV --skip_leading_rows=1 \
  mcp_bakery.foot_traffic ./data/foot_traffic.csv \
  zip_code:STRING,time_of_day:STRING,foot_traffic_score:FLOAT

bq --project_id=$PROJECT load --replace --source_format=CSV --skip_leading_rows=1 \
  mcp_bakery.bakery_prices ./data/bakery_prices.csv \
  store_name:STRING,product_type:STRING,price:FLOAT,region:STRING,is_organic:BOOLEAN

bq --project_id=$PROJECT load --replace --source_format=CSV --skip_leading_rows=1 \
  mcp_bakery.sales_history_weekly ./data/sales_history_weekly.csv \
  week_start_date:DATE,store_location:STRING,product_type:STRING,quantity_sold:INTEGER,total_revenue:FLOAT
