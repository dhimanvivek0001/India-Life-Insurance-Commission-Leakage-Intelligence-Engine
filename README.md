# India Life Insurance — Commission Leakage Intelligence Engine

> **₹2,880 Cr in annual economic leakage** identified across 3 major Indian life insurers using real IRDAI FY2025 public filings. A full-stack data engineering + analytics project with DuckDB, dbt, Kafka simulation, and Streamlit dashboard.

---

## The Problem

Indian life insurers pay commission upfront on every new policy — 20–45% of First Year Premium — before the policy has proven it will persist. When that policy lapses within 13 months (which happens to 12–22% of all policies), the commission is already paid and cannot be recovered. This is commission leakage.

**The root cause:** Bancassurance channel. Insurers with 90%+ banca dependency have structurally higher lapse rates because banks sell the policy and disappear — no ongoing customer relationship, no retention effort.

---

## Key Findings

| Finding | Detail |
|---|---|
| SUD Life is CRITICAL | 95.6% banca, 22.3% lapse rate, 61M persistency collapsed 520bps to 23.2% in FY2025 |
| HDFC Life largest absolute leakage | ₹762 Cr commission leakage despite best-in-class 13% lapse rate — scale amplifies everything |
| Banca = lapse correlation | Every 10% increase in banca share ≈ 1–2% higher lapse rate across all 3 insurers |
| Model ROI is extraordinary | XGBoost predictor costing ₹0.15 Cr recovers ₹305 Cr/yr at HDFC Life = 2,031x ROI |
| 61M gap tells the real story | HDFC 63% vs SUD 23.2% at 61 months = 39.8pp gap = value of post-sale engagement |

---

## Results

```
INDUSTRY TOTAL — 3 INSURERS FY2025
────────────────────────────────────
Total Economic Leakage  :  ₹2,880 Cr
Commission Leakage      :    ₹989 Cr
CAC Leakage             :  ₹1,891 Cr
Recoverable @ 40% model :    ₹396 Cr
Model Build Cost        :   ₹0.45 Cr
Combined Model ROI      :      880x
```

---

## Data Sources

All numbers from verified public sources — no synthetic data, no assumptions for primary metrics.

| Source | What it provides | URL |
|---|---|---|
| IRDAI Form L-4 (March 2025) | First Year Premium, Renewal Premium, Single Premium | insurer IRDAI disclosure pages |
| IRDAI Form L-5 (March 2025) | Commission on FYP, Renewal, Single | same disclosure |
| IRDAI Form L-6 (March 2025) | Advertisement, Business Development costs | same disclosure |
| HDFC Life FY2025 Press Release | Persistency 13M=87%, 61M=63%, distribution mix | hdfclife.com |
| ICRA Rating Report SUD Life (Jul 22 2025) | Persistency 13M=77.7%, 61M=23.2%, banca=95.6% | icra.in |
| Press Release Max Life (May 23 2025) | Persistency 13M=87.6%, 61M=59.3% | axismaxlife.com |

---

## Calculations

### Commission Leakage Formula
```
Commission leakage    = Commission on FYP × Lapse rate (13M)
CAC leakage           = Policies lapsed × CAC per policy
Total leakage         = Commission leakage + CAC leakage
Recoverable           = Commission leakage × 0.40  (XGBoost at AUC 0.75 catches ~40%)
Model ROI             = Recoverable ÷ ₹0.15 Cr build cost
```

### Per Insurer
| Metric | HDFC Life | SUD Life | Max Life |
|---|---|---|---|
| First Year Premium | ₹12,976 Cr | ₹1,345 Cr | ₹2,896 Cr |
| Commission on FYP | ₹5,860 Cr | ₹292 Cr | ₹1,308 Cr |
| 13M Lapse Rate | 13.0% | 22.3% | 12.4% |
| 61M Persistency | 63.0% | 23.2% | 59.3% |
| Banca Channel | 65% | 95.6% | 59% |
| CAC per Policy | ₹1,13,740 | ₹1,80,200 | ₹76,150 |
| Commission Leakage | ₹762 Cr | ₹65 Cr | ₹162 Cr |
| Total Economic Leakage | ₹1,794 Cr | ₹213 Cr | ₹873 Cr |
| Recoverable @ 40% | ₹305 Cr | ₹26 Cr | ₹65 Cr |
| Model ROI | 2,031x | 174x | 433x |

---

## Architecture

```
IRDAI Public Filings (quarterly)
        │
        ▼
Manual Extraction (Form L-4, L-5, L-6)
        │
        ▼
data/raw/*.csv  ──────────────────────────────────────────────
        │                                                     │
        ▼                                                     ▼
01_ingest_to_duckdb.py                          Kafka Producer
(Python + DuckDB)                          (policy_event_producer.py)
        │                                    500 policy events/run
        ▼                                          │
raw.insurer_summary                               ▼
raw.persistency_cohorts          data/processed/policy_events.jsonl
raw.channel_commission
        │
        ▼
dbt run (3 models)
├── stg_insurer_summary      → clean view, typed columns
├── int_leakage_calculations → leakage formula in SQL
└── fct_leakage              → final fact table, rankings, risk tiers
        │
        ▼
Streamlit Dashboard (streamlit/app.py)
├── KPI cards: total leakage, commission leakage, recoverable, ROI
├── Bar chart: commission leakage by insurer
├── Line chart: persistency cohort 13M → 61M
├── Scatter: channel lapse rate vs leakage
└── Comparison table + strategic insights
        │
        ▼
Deployed on Render.com (free tier)
```

---

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Data warehouse | DuckDB | Local SQL database, no cloud needed |
| Transformation | dbt-duckdb | SQL models: staging → intermediate → marts |
| Event streaming | kafka-python | Simulates real-time policy event stream |
| ML (next phase) | XGBoost + SHAP | Lapse prediction + explainability |
| Dashboard | Streamlit + Plotly | Interactive leakage intelligence app |
| Orchestration | Airflow (planned) | Daily pipeline automation |
| Monitoring | Kibana (planned) | Pipeline health + anomaly detection |
| Deployment | Render.com | Free public URL |

---

## Project Structure

```
india-insurance-leakage/
├── data/
│   ├── raw/                    # Real IRDAI filing data (3 CSVs)
│   │   ├── insurer_summary.csv
│   │   ├── persistency_cohorts.csv
│   │   └── channel_commission.csv
│   ├── processed/              # Kafka event stream output
│   └── duckdb/                 # DuckDB database file
├── ingestion/
│   └── 01_ingest_to_duckdb.py  # Phase 1: CSV → DuckDB
├── kafka/
│   └── policy_event_producer.py # Phase 2: event simulation
├── dbt_project/
│   ├── models/
│   │   ├── staging/            # stg_insurer_summary.sql
│   │   ├── intermediate/       # int_leakage_calculations.sql
│   │   └── marts/              # fct_leakage.sql
│   └── dbt_project.yml
├── ml/                         # XGBoost model (coming)
├── streamlit/
│   └── app.py                  # Dashboard
├── airflow/                    # DAGs (coming)
├── monitoring/                 # Kibana config (coming)
├── requirements.txt
└── README.md
```

---

## How to Run

### Prerequisites
- Python 3.11+
- Git

### Setup
```bash
git clone https://github.com/dhimanvivek0001/india-insurance-leakage.git
cd india-insurance-leakage
pip install -r requirements.txt
```

### Configure dbt
Create `~/.dbt/profiles.yml`:
```yaml
india_insurance:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: /path/to/india-insurance-leakage/data/duckdb/india_insurance.duckdb
      threads: 4
```

### Run the pipeline
```bash
# Phase 1 — Ingest data into DuckDB
python ingestion/01_ingest_to_duckdb.py

# Phase 2 — Simulate policy event stream
python kafka/policy_event_producer.py

# Phase 3 — Run dbt transformations
cd dbt_project
python -c "from dbt.cli.main import dbtRunner; r = dbtRunner(); r.invoke(['run'])"
cd ..

# Phase 4 — Launch dashboard
python -m streamlit run streamlit/app.py
```

---

## Annual Data Refresh

When IRDAI publishes new quarterly disclosures:

1. Download Form L-4 and L-5 from insurer's IRDAI disclosure page
2. Extract FYP, Renewal, Single premiums and commission figures
3. Update `data/raw/insurer_summary.csv`
4. Update persistency from press releases or ICRA reports
5. Re-run ingestion script → dbt → dashboard auto-updates

Total manual effort: ~30 minutes per refresh.

---

## What's Next

- [ ] XGBoost lapse prediction model (Phase 5)
- [ ] SHAP feature importance — "banca adds X% lapse risk"
- [ ] Airflow DAG for automated pipeline (Phase 6)
- [ ] Elasticsearch + Kibana monitoring (Phase 7)
- [ ] Expand to 10 insurers using same methodology

---

## Author

**Vivek Dhiman**  
MSc Business Analytics — University of Galway  
[GitHub](https://github.com/dhimanvivek0001)

---

*All data from audited public filings. IRDAI Form L-4/L-5 (March 2025), ICRA Rating Reports (June–July 2025), Company Press Releases (April–May 2025).*
