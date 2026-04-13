# System Architecture and Data Flow
## India Life Insurance Commission Leakage Intelligence Engine

---

## 1. System Overview

This system ingests real regulatory filing data from three Indian life insurers, transforms it through a layered data pipeline, applies leakage calculations, and delivers an interactive intelligence dashboard. The architecture follows a medallion pattern: raw data preserved as-is, staging layer for cleaning, intermediate layer for business logic, and a marts layer for final output.

The system has two data paths: a batch path processing annual IRDAI filings, and an event simulation path generating real-time policy events for demonstration of streaming architecture.

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SOURCE LAYER                                                                │
│                                                                             │
│  IRDAI Public Disclosures (quarterly)                                       │
│  ├── HDFC Life: hdfclife.com/about-us/public-disclosure                     │
│  ├── SUD Life: sudlife.in — IRDAI disclosures                               │
│  └── Max Life: axismaxlife.com — public disclosures                         │
│                                                                             │
│  Forms extracted: L-4 (Premium), L-5 (Commission), L-6 (Expenses), L-36   │
│  Supplementary: ICRA Rating Reports, Company Press Releases                 │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │ Manual extraction (20 min/insurer/quarter)
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  INGESTION LAYER — data/raw/                                                │
│                                                                             │
│  insurer_summary.csv        3 rows × 20 columns                             │
│  ├── Premium: FYP, Renewal, Single                                          │
│  ├── Commission: FYP, Renewal, Single, Gross                                │
│  ├── Acquisition: Total cost, New policies, CAC per policy                  │
│  ├── Persistency: 13M, 61M, Lapse rate                                     │
│  └── Channel: Banca %, source references                                   │
│                                                                             │
│  persistency_cohorts.csv    13 rows                                         │
│  └── Insurer × FY × Cohort month × Persistency × YoY change               │
│                                                                             │
│  channel_commission.csv     10 rows                                         │
│  └── Insurer × Channel × Share % × Commission × Lapse multiplier           │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │ ingestion/01_ingest_to_duckdb.py
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  WAREHOUSE — DuckDB (data/duckdb/india_insurance.duckdb)                    │
│                                                                             │
│  Schema: raw                                                                │
│  ├── raw.insurer_summary        (3 rows, 22 columns, typed)                 │
│  ├── raw.persistency_cohorts    (13 rows, 8 columns, typed)                 │
│  └── raw.channel_commission     (10 rows, 9 columns, typed)                 │
│                                                                             │
│  Engine: DuckDB 1.5.1, local file, no server required                      │
│  Adapter: dbt-duckdb 1.8.2                                                  │
└─────────────────────────────────┬───────────────────────────────────────────┘
                  ┌───────────────┴──────────────────────┐
                  ▼                                       ▼
┌─────────────────────────┐             ┌─────────────────────────────────────┐
│  EVENT STREAM            │             │  TRANSFORMATION — dbt               │
│                          │             │                                     │
│  kafka/                  │             │  Model 1: stg_insurer_summary       │
│  policy_event_producer.py│             │  Type: View                         │
│                          │             │  Input: raw.insurer_summary         │
│  500 events per run      │             │  Output: Clean typed columns        │
│  Insurer mix: real share │             │  Adds: Commission rates, derived    │
│  Channel mix: real %     │             │  ratios, acquisition cost ratios    │
│  Lapse probability:      │             │                                     │
│    base × channel mult   │             │  Model 2: int_leakage_calculations  │
│    × age × premium       │             │  Type: Table                        │
│    × product × tenure    │             │  Input: stg_insurer_summary         │
│                          │             │  Applies: Core leakage formula      │
│  Output: JSONL stream    │             │  Calculates: Commission leakage,    │
│  data/processed/         │             │  CAC leakage, banca leakage,        │
│  policy_events_stream    │             │  recoverable, model ROI,            │
│  .jsonl                  │             │  KPOINT retention value             │
│                          │             │                                     │
│  In production:          │             │  Model 3: fct_leakage               │
│  Real Kafka broker        │             │  Type: Table                        │
│  Topic: policy_events    │             │  Input: int_leakage_calculations +  │
│  Partitioned by insurer  │             │  raw.channel_commission +           │
│                          │             │  raw.persistency_cohorts            │
│                          │             │  Produces: Final fact table with    │
│                          │             │  rankings, risk tiers, all          │
│                          │             │  calculated metrics joined          │
└─────────────────────────┘             └─────────────────┬───────────────────┘
                                                          │
                                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER — streamlit/app.py                                      │
│                                                                             │
│  Data loading: DuckDB (primary) → CSV fallback (for cloud deployment)      │
│                                                                             │
│  Dashboard components:                                                      │
│  ├── Sidebar: Insurer filter, model catch rate slider, build cost slider    │
│  ├── KPI row: Total leakage, Commission leakage, Recoverable, Model ROI    │
│  ├── Bar chart: Commission leakage by insurer (Plotly)                      │
│  ├── Insurer cards: Per-insurer detail with risk badge                      │
│  ├── Line chart: Persistency cohort 13M through 61M                        │
│  ├── Scatter chart: Channel lapse rate vs leakage bubble chart              │
│  ├── Comparison table: Full 10-metric insurer comparison                    │
│  └── Strategic insights: Three annotated findings                          │
│                                                                             │
│  Deployment: Render.com free tier                                           │
│  URL: https://india-insurance-leakage.onrender.com                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow — Step by Step

### Step 1: Source Identification

IRDAI requires every registered life insurer to publish quarterly public disclosures. These are available on the insurer's investor relations page. The relevant forms are L-4 (Premium Schedule), L-5 (Commission Schedule), L-6 (Operating Expenses Schedule), and L-36 or L-38 (Policy Count).

For persistency data, two sources are used: (a) company press releases published within 30 days of quarter end, which typically contain 13-month and 61-month persistency ratios; (b) ICRA or CRISIL rating reports for non-listed insurers, which contain audited financial data from the rating exercise.

### Step 2: Manual Extraction

For each insurer, the following numbers are extracted from the full-year (Q4 cumulative) column:

From Form L-4: First Year Premiums, Renewal Premiums, Single Premiums, Total Premium.

From Form L-5: Commission on First Year Premiums, Commission on Renewal Premiums, Commission on Single Premiums, Gross Commission Total.

From Form L-6: Advertisement and Publicity, Business Development and Sales Promotion.

From Form L-36: Individual First Year Policies issued, Individual Single Premium Policies, Total New Individual Policies.

From press release or ICRA report: 13-month persistency, 61-month persistency, distribution channel mix.

Each extraction is validated: premium components are summed and checked against stated total; commission components are summed and checked against gross commission; policy counts are summed and checked against total. Any mismatch is investigated before the number is used.

### Step 3: CSV Population

Validated numbers are entered into three CSV files:

insurer_summary.csv — one row per insurer, 20 columns covering all metrics above plus derived fields.

persistency_cohorts.csv — one row per insurer per cohort month per financial year. Contains both FY2024 and FY2025 data to enable year-on-year comparison.

channel_commission.csv — one row per channel per insurer. Contains channel share, commission amount, lapse multiplier, and estimated leakage by channel.

### Step 4: Ingestion to DuckDB

The script ingestion/01_ingest_to_duckdb.py reads the three CSV files using duckdb read_csv_auto, applies explicit type casting for all numeric columns, adds an ingested_at timestamp, and writes to the raw schema in the DuckDB file.

The script runs a validation query after loading each table, printing row counts and a sample of key metrics to the console. If the DuckDB file does not exist, it is created automatically.

Run time: approximately 3 seconds for all three tables.

### Step 5: Kafka Event Simulation

The script kafka/policy_event_producer.py generates 500 policy events using parameters derived directly from the real insurer data. For each event, the insurer is selected proportionally to market share, the channel is selected proportionally to real channel mix, and the lapse probability is computed using a formula that applies multipliers for channel, product, customer age, premium band, agent tenure, and cross-sell indicator.

Each event contains: event_id, event_type, event_timestamp, policy_id, insurer, product_type, channel, state, age_at_issue, age_band, annual_premium_rs, premium_band, commission_rs, lapse_probability, lapse_risk_tier, cac_rs, economic_at_risk_rs.

Output is written as newline-delimited JSON to data/processed/policy_events_stream.jsonl. In a production deployment, the Kafka producer would connect to a Kafka broker and write to the policy_events topic, with one partition per insurer.

### Step 6: dbt Transformation

Three dbt models run in sequence. The dependency chain is enforced by dbt using the ref() function: fct_leakage depends on int_leakage_calculations, which depends on stg_insurer_summary.

Model 1 (stg_insurer_summary, view): Renames columns to business-friendly names, casts all types explicitly, computes commission rates, blended commission rate, and acquisition cost ratio. Does not perform any business logic calculations.

Model 2 (int_leakage_calculations, table): Applies the core leakage formula. Computes commission leakage, estimated policies lapsed, CAC leakage, total economic leakage, leakage as a percentage of total commission, banca channel leakage, recoverable at 40% model catch rate, model ROI, KPOINT retention spend, and customers retained via KPOINT model. Assigns a risk tier (CRITICAL / HIGH / MEDIUM / LOW) based on lapse rate and banca share thresholds.

Model 3 (fct_leakage, table): Joins the intermediate leakage calculations with channel data from raw.channel_commission and year-on-year persistency changes from raw.persistency_cohorts. Adds average ticket size, ranks each insurer by total economic leakage and by persistency, and attaches a run timestamp.

Full dbt run time: 5–6 seconds.

### Step 7: Dashboard

The Streamlit application reads from the DuckDB warehouse using the duckdb Python library. If the warehouse file is not found (e.g. in cloud deployment), it falls back to reading the CSV files directly. All leakage calculations are replicated in Python functions using the same formulas as the dbt models, ensuring consistency.

The dashboard refreshes all calculated values dynamically when the user moves the model catch rate or model build cost sliders, without re-querying the database.

---

## 4. dbt Model Lineage

```
raw.insurer_summary
        │
        ▼
stg_insurer_summary  (view)
  Cleans and types raw data
  Adds commission rates and expense ratios
        │
        ▼
int_leakage_calculations  (table)
  Applies leakage formula
  Calculates all monetary outputs
  Assigns risk tiers
        │
        ├── raw.channel_commission
        │         (joined for channel-level leakage)
        │
        ├── raw.persistency_cohorts
        │         (joined for YoY persistency changes)
        │
        ▼
fct_leakage  (table)
  Final fact table
  Rankings, risk tiers, all metrics joined
  Used by Streamlit dashboard
```

---

## 5. Annual Refresh Process

The pipeline is designed for an annual full refresh triggered by IRDAI's quarterly disclosure cycle. The March quarter disclosure (full year figures) is the primary refresh trigger.

```
Trigger: IRDAI March quarter disclosure published
  (typically April–May each year)
          │
          ▼
Action 1: Download PDF disclosures for each insurer
  Time: 15 minutes
          │
          ▼
Action 2: Extract L-4, L-5, L-6, L-36 figures
  Validate each extraction (sum checks)
  Time: 20 minutes per insurer = 1 hour total
          │
          ▼
Action 3: Update insurer_summary.csv
  Add new FY row per insurer
  Update persistency_cohorts.csv with new data point
  Time: 10 minutes
          │
          ▼
Action 4: Run ingestion script
  python ingestion/01_ingest_to_duckdb.py
  Time: < 30 seconds
          │
          ▼
Action 5: Run dbt
  dbt run
  Time: < 10 seconds
          │
          ▼
Action 6: Verify dashboard
  Open Streamlit app
  Check new figures loaded correctly
  Time: 5 minutes
          │
          ▼
Output: Dashboard updated with new year's leakage numbers
Total manual effort: approximately 90 minutes per annual refresh
```

---

## 6. Technology Decisions

**DuckDB over PostgreSQL or BigQuery:** The dataset is small (under 1,000 rows across all tables) and entirely read-heavy. DuckDB runs as a local file, requires no server, no credentials, and no cloud account. It supports full SQL including window functions and analytical queries. dbt-duckdb is a production-quality adapter. For a portfolio project that needs to run on any machine, DuckDB is the correct choice.

**dbt over raw SQL scripts:** dbt provides version-controlled, tested, documented SQL models with automatic lineage tracking. The three-layer architecture (staging, intermediate, marts) separates concerns cleanly. Any reviewer of the repository can understand the data transformation logic by reading three SQL files. Raw scripts would not provide this transparency.

**Kafka simulation over live Kafka:** A live Kafka broker requires Docker or a managed service. The event producer generates exactly the same data structure as a live Kafka consumer would receive. The JSONL output can be replaced by a real Kafka consumer with two lines of code change. The architecture decision is fully forward-compatible.

**Streamlit over Tableau or Power BI:** Streamlit is code-first, deployable as a web service, and free. The dashboard can be modified in the same environment as the rest of the codebase without switching tools. It deploys on Render with a single start command.

---

## 7. File Structure

```
india-insurance-leakage/
│
├── data/
│   ├── raw/
│   │   ├── insurer_summary.csv          Real IRDAI data, 3 insurers
│   │   ├── persistency_cohorts.csv      FY2024 and FY2025 cohort data
│   │   └── channel_commission.csv       Channel-level breakdown
│   ├── processed/
│   │   └── policy_events_stream.jsonl   Kafka simulation output
│   └── duckdb/
│       └── india_insurance.duckdb       Warehouse file
│
├── ingestion/
│   └── 01_ingest_to_duckdb.py           CSV to DuckDB loader
│
├── kafka/
│   └── policy_event_producer.py         Event stream simulator
│
├── dbt_project/
│   ├── dbt_project.yml                  dbt configuration
│   ├── models/
│   │   ├── staging/
│   │   │   └── stg_insurer_summary.sql
│   │   ├── intermediate/
│   │   │   └── int_leakage_calculations.sql
│   │   └── marts/
│   │       └── fct_leakage.sql
│   └── tests/                           (planned: not-null, accepted values)
│
├── ml/                                  XGBoost model (Phase 5)
├── streamlit/
│   └── app.py                           Dashboard
├── airflow/
│   └── dags/                            Orchestration (planned)
├── monitoring/
│   └── kibana/                          Pipeline monitoring (planned)
│
├── requirements.txt
└── README.md
```

---

## 8. Planned Additions

**Phase 5 — XGBoost Lapse Prediction Model**

Train on the 500 policy events from the Kafka simulation. Features: channel (one-hot encoded), product_type, premium_band, age_band, state, lapse_probability_score. Target: is_lapsed (binary). Output: per-policy lapse probability score between 0 and 1. SHAP values provide feature importance — the output will quantify exactly how much banca channel increases lapse risk versus the base rate.

**Phase 6 — Airflow DAG**

One DAG file with four tasks: ingest_raw_data, run_dbt_models, score_new_policies (XGBoost), send_alert_if_threshold_breached. Scheduled for annual run on April 1. Monitored via Airflow UI at localhost:8080.

**Phase 7 — Elasticsearch and Kibana**

Index the fct_leakage output into Elasticsearch. Build three Kibana dashboards: pipeline run history and data quality metrics; leakage by insurer over time; lapse score distribution from the ML model. Run locally via Docker Desktop. Adds observable infrastructure layer to the portfolio.

---

*Architecture documentation for India Life Insurance Commission Leakage Intelligence Engine. All data from IRDAI public disclosures FY2025.*
