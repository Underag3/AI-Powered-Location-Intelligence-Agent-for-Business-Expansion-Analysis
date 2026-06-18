# AI-Powered Location Intelligence Agent for Business Expansion Analysis

An AI-powered location intelligence agent built using **Google Agent Development Kit (ADK)**, **Model Context Protocol (MCP)**, **BigQuery**, and **Google Maps**.  
This project demonstrates how an AI agent can combine structured business data and real-world location data to support data-driven business expansion decisions.

## Overview

Choosing the right business location requires more than intuition. Businesses need to consider customer demographics, foot traffic, competitor density, sales potential, pricing strategy, and accessibility.

This project builds an AI agent that can analyze business expansion opportunities by connecting to:

- **BigQuery** for structured business and demographic data
- **Google Maps MCP Server** for real-world location intelligence
- **Google ADK** for building and running the AI agent
- **Gemini** as the reasoning model behind the agent

The agent can help answer questions such as:

- Which area has the strongest potential for business expansion?
- Which ZIP code or district has high foot traffic?
- How competitive is a specific location?
- What nearby competitors exist around a target area?
- Is the location accessible and suitable for business operations?
- What recommendation can be made based on data and map-based context?

## Project Purpose

The purpose of this project is to demonstrate how an AI agent can support **business expansion analysis** by combining multiple data sources and external tools.

Instead of only generating responses from a language model, the agent can use tools to retrieve, analyze, and validate information before giving a recommendation.

This project is suitable for showcasing skills in:

- AI Agent development
- Google ADK
- MCP tool integration
- BigQuery-based analytics
- Google Maps / location intelligence
- Business data analysis
- Cloud-based AI workflow

## Tech Stack

| Technology | Purpose |
|---|---|
| Google ADK | Framework for building the AI agent |
| Gemini | Large language model used by the agent |
| MCP | Tool connection protocol for external services |
| BigQuery | Data warehouse for structured business data |
| Google Maps MCP | Location search, competitor analysis, and route context |
| Python | Main programming language |
| Google Cloud | Cloud environment and authentication |
| Shell Script | Setup and cleanup automation |

## Project Architecture

```text
User
 |
 | asks business location questions
 v
Google ADK Agent
 |
 | decides which tool to use
 |
 +------------------------+
 |                        |
 v                        v
BigQuery MCP Server       Google Maps MCP Server
 |                        |
 | structured data         | real-world location data
 | demographics            | competitors
 | sales history           | nearby places
 | pricing                 | accessibility
 | foot traffic            | route context
 v                        v
Combined Analysis and Recommendation


```

## Repository Structure

```
├── adk_agent/
│   └── mcp_bakery_app/
│       ├── __init__.py
│       ├── agent.py
│       └── tools.py
│
├── cleanup/
│   └── cleanup_env.sh
│
├── data/
│   └── .gitkeep
│
├── setup/
│   ├── setup_bigquery.sh
│   └── setup_env.sh
│
├── architecture_diagram.png
├── requirements.txt
├── .gitignore
└── README.md
```

## Main Features
1. AI Agent for Business Expansion

The agent is designed to assist users in analyzing potential business locations. It can reason through business questions and combine multiple sources of information before giving a recommendation.

2. BigQuery Integration

The agent uses BigQuery to access structured data such as:

Demographic data
Foot traffic data
Historical sales data
Pricing data
Area-level business indicators
3. Google Maps Integration

The agent uses Google Maps through MCP to analyze real-world location context, such as:

Nearby competitors
Nearby points of interest
Accessibility
Distance and route information
Location suitability
4. MCP-Based Tool Calling

This project demonstrates how MCP can be used to connect an AI agent with external tools. The agent does not work as a simple chatbot; it can use tools to retrieve information and support its reasoning.

## Example Use Case

A business owner wants to open a new branch in a specific city or area. The agent can help compare possible locations by analyzing:

Customer potential
Foot traffic
Competitor presence
Historical sales patterns
Pricing opportunity
Accessibility and surrounding area

Example user question:

Which location has the strongest potential for a new business branch based on foot traffic, competition, and customer demographics?

The agent can then query BigQuery, validate the area using Google Maps, and provide a recommendation.

## Example Questions

You can test the agent using questions such as:

Which area has the highest potential for business expansion?
Analyze the competition around the recommended location.
Which location has the best combination of high foot traffic and low competition?
Can you compare the top three possible expansion areas?
What business recommendation can be made based on the available data?

## Setup Instructions
1. Clone the Repository
git clone https://github.com/Underag3/AI-Powered-Location-Intelligence-Agent-for-Business-Expansion-Analysis.git
cd AI-Powered-Location-Intelligence-Agent-for-Business-Expansion-Analysis
2. Create a Virtual Environment
python -m venv .venv

Activate the virtual environment:

For Windows:

.venv\Scripts\activate

For macOS or Linux:

source .venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt

Recommended requirements.txt:

google-adk==1.28.0
python-dotenv
google-auth
google-cloud-bigquery
pandas
numpy
4. Configure Environment Variables

Create a .env file in the project root.

GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your_google_cloud_project_id
GOOGLE_CLOUD_LOCATION=global
MAPS_API_KEY=your_google_maps_api_key

Do not upload the .env file to GitHub.

You can also provide an example file named .env.example:

GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your_project_id_here
GOOGLE_CLOUD_LOCATION=global
MAPS_API_KEY=your_google_maps_api_key_here
5. Authenticate Google Cloud

Make sure you are authenticated with Google Cloud:

gcloud auth application-default login

Set your Google Cloud project:

gcloud config set project your_google_cloud_project_id
6. Prepare BigQuery Data

This project expects business-related data to be available in BigQuery.

Example tables may include:

Table	Description
demographics	Area-level demographic information
foot_traffic	Foot traffic data by area or time period
sales_history_weekly	Historical weekly sales data
bakery_prices	Product pricing data

If you use your own business use case, you can replace these tables with your own dataset, such as:

Table	Description
area_demographics	Population, age group, income level, and education data
poi_places	Nearby universities, offices, cafés, or business facilities
venue_options	Possible business or event locations
event_history	Historical business or event performance data
7. Run the ADK Web App

From the project directory, run:

adk web

Then open the local URL provided by ADK in your browser.

Environment Variables
Variable	Description
GOOGLE_GENAI_USE_VERTEXAI	Enables Vertex AI usage
GOOGLE_CLOUD_PROJECT	Your Google Cloud project ID
GOOGLE_CLOUD_LOCATION	Google Cloud region or location
MAPS_API_KEY	Google Maps API key
Important Security Notes

Do not upload the following files or credentials to GitHub:

.env
Google Maps API key
Google Cloud credential JSON files
OAuth tokens
Service account keys
Billing-related credentials

Make sure these files are included in .gitignore.

Current Limitations

This project is intended as a portfolio and educational implementation. Some limitations include:

The sample business data may be synthetic or simplified.
The recommendation quality depends on the quality of the input data.
Google Maps API usage may require billing to be enabled.
BigQuery queries may generate cloud usage costs.
The agent still requires careful prompt and tool design to avoid inaccurate recommendations.
Future Improvements

Possible improvements for this project:

Replace sample data with real public datasets.
Add synthetic data generation scripts.
Add dashboard visualizations for location comparison.
Add evaluation metrics for recommendation quality.
Support Indonesian city-level business expansion use cases.
Add Streamlit or web-based frontend.
Add sample screenshots of agent responses.
Add automated data pipeline for BigQuery ingestion.
Add clearer business scoring logic for location ranking.
Portfolio Value

This project demonstrates the ability to build an AI-powered data application that connects reasoning models with real-world tools. It combines AI agent development, cloud data analytics, and location intelligence into one practical business use case.

Key skills demonstrated:

Building an AI agent with Google ADK
Connecting external tools using MCP
Querying structured data from BigQuery
Using Google Maps for real-world location analysis
Designing data-driven business recommendations
Managing environment variables and cloud-based configuration
Attribution

This project is adapted from Google's codelab:

Build a Location Intelligence ADK Agent with MCP servers for BigQuery and Google Maps

Original resources:

Google Codelab: Build a Location Intelligence ADK Agent with MCP servers for BigQuery and Google Maps
Google MCP Repository: https://github.com/google/mcp

The original codelab content is licensed under the Creative Commons Attribution 4.0 License.
The original code samples are licensed under the Apache License 2.0.

This repository modifies and adapts the original concept for portfolio and educational purposes, including changes to the repository structure, documentation, and business expansion analysis framing.

License

This project includes code and concepts adapted from Google MCP examples.
If this repository contains modified code from the original Google MCP repository, it should follow the Apache License 2.0.

Please refer to the original license from the Google MCP repository for more details.

Author

Mohammad Tyas Subianto
GitHub: Underag3
