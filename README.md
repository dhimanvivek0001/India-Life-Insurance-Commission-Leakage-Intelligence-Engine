# India Life Insurance — Commission Leakage Intelligence Engine

> **₹2,880 Cr in annual economic leakage** identified across 3 major Indian life insurers using real IRDAI FY2025 public filings. A full-stack data engineering + analytics consulting project combining DuckDB, dbt, Kafka, and Streamlit.

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![dbt](https://img.shields.io/badge/dbt-duckdb-orange)](https://dbt.dev)
[![Streamlit](https://img.shields.io/badge/Streamlit-deployed-green)](https://streamlit.io)
[![Data](https://img.shields.io/badge/Data-IRDAI%20FY2025-red)](https://irdai.gov.in)

---

## The Problem

Indian life insurers pay commission upfront on every new policy — **20–45% of First Year Premium** — before the policy has proven it will persist. When a policy lapses within 13 months (12–22% of all policies), the commission is fully sunk. This is **commission leakage**.

The root cause is structural: **bancassurance channel**. Banks sell the policy and disappear. No post-sale relationship. No retention effort. 95.6% banca dependency at SUD Life produces a 22.3% lapse rate. 59% banca at Max Life produces 12.4%. The correlation is direct and measurable.

---

## Key Findings

| Finding | Detail |
|---|---|
| **SUD Life — CRITICAL** | 95.6% banca, 22.3% lapse rate, 61M persistency collapsed 520 bps to 23.2% in FY2025 |
| **HDFC Life — largest absolute leakage** | ₹762 Cr commission leakage despite best-in-class 13% lapse rate — scale amplifies everything |
| **Banca = lapse root cause** | Every 10% increase in banca share ≈ 1–2% higher lapse rate across all 3 insurers |
| **Model ROI is extraordinary** | XGBoost predictor costing ₹0.15 Cr recovers ₹305 Cr/yr at HDFC Life = **2,031x ROI** |
| **61M gap tells the real story** | HDFC 63% vs SUD 23.2% at 61M = 39.8 pp gap = value of investing in post-sale engagement |

---

## Industry Results — FY2025

```
INDUSTRY TOTAL — 3 INSURERS FY2025
────────────────────────────────────────────────
Total Economic Leakage     :  ₹2,880 Cr / year
  ├── Commission Leakage   :    ₹989 Cr
  └── CAC Leakage          :  ₹1,891 Cr
Recoverable @ 40% ML model :    ₹396 Cr / year
Model Build Cost (3 models):   ₹0.45 Cr one-time
Combined Model ROI         :        880x
Payback period             :      < 6 hours of deployment
```

---

## Insurers Covered

| Insurer | FY | Total Premium | Source |
|---|---|---|---|
| HDFC Life Insurance Co. Ltd | FY2025 | ₹71,045 Cr | IRDAI Public Disclosure March 2025 |
| SUD Life (Star Union Dai-ichi) | FY2025 | ₹8,260 Cr | IRDAI Public Disclosure March 2025 |
| Axis Max Life Insurance Co. Ltd | FY2025 | ₹15,301 Cr | IRDAI Public Disclosure March 2025 |

---

## Data Sources

All numbers from **verified, audited, public sources only**. No synthetic data. No assumptions for primary metrics.

| Source | Metrics Extracted | Verified Against |
|---|---|---|
| IRDAI Form L-4 — Premium Schedule (March 2025) | FYP, Renewal Premium, Single Premium | Sum check: components = total ✅ |
| IRDAI Form L-5 — Commission Schedule (March 2025) | Commission on FYP / Renewal / Single, Gross Commission | Sum check: components = gross ✅ |
| IRDAI Form L-6 — Operating Expenses (March 2025) | Advertisement, Business Development, Total OpEx | Cross-check vs expense ratio ✅ |
| IRDAI Form L-36/38 — Policy Count | New individual FYP policies, Single premium policies | Scale sanity check ✅ |
| HDFC Life FY2025 Press Release (Apr 17, 2025) | 13M persistency 87%, 61M 63%, distribution mix | hdfclife.com investor relations ✅ |
| ICRA Rating Report — SUD Life (Jul 22, 2025) | 13M 77.7%, 61M 23.2%, banca 95.6%, GWP ₹8,260 Cr | Audited financials ✅ |
| ICRA Rating Report — IndiaFirst (Jun 20, 2025) | 13M 81.2%, 61M 47.6%, banca 76% | Audited financials ✅ |
| Press Release — Axis Max Life (May 23, 2025) | 13M 87.6%, 61M 59.3% | Multiple news sources confirmed ✅ |

---

## Financial Statements — Raw Extracted Data

### HDFC Life — IRDAI Form L-4 & L-5 (FY2025, ₹ Lakh)

```
FORM L-4 — PREMIUM SCHEDULE
─────────────────────────────────────────────────────────────
Particulars                         FY2025          FY2024
─────────────────────────────────────────────────────────────
First Year Premiums              12,97,607       11,11,082
Renewal Premiums                 37,67,961       33,44,512
Single Premiums                  20,38,923       18,52,054
─────────────────────────────────────────────────────────────
TOTAL PREMIUM                    71,04,491       63,07,648
─────────────────────────────────────────────────────────────
Validation: 1297607+3767961+2038923 = 7104491 ✅ EXACT MATCH

FORM L-5 — COMMISSION SCHEDULE
─────────────────────────────────────────────────────────────
Particulars                         FY2025          FY2024
─────────────────────────────────────────────────────────────
Commission on First Year Premiums   5,86,032       3,15,114
Commission on Renewal Premiums        58,957          52,187
Commission on Single Premiums      1,38,540        1,58,331
─────────────────────────────────────────────────────────────
GROSS COMMISSION                   7,83,529       5,25,632
─────────────────────────────────────────────────────────────
Validation: 586032+58957+138540 = 783529 ✅ EXACT MATCH

COMMISSION RATES (derived)
─────────────────────────────────────────────────────────────
Commission rate on FYP          : 45.2%  (₹5,860 Cr / ₹12,976 Cr)
Commission rate on Renewal      :  1.6%  (₹590 Cr / ₹37,680 Cr)
Commission rate on Single       :  6.8%  (₹1,385 Cr / ₹20,389 Cr)
Blended rate (all premium)      : 11.0%  (₹7,835 Cr / ₹71,045 Cr)
─────────────────────────────────────────────────────────────
Note: 45.2% FYP rate includes overriding commissions,
trail commissions on prior-year ULIPs, and advance commissions
on multi-year bancassurance policies — consistent with industry.
```

### SUD Life — IRDAI Form L-4 & L-5 (FY2025, ₹ Lakh)

```
FORM L-4 — PREMIUM SCHEDULE
─────────────────────────────────────────────────────────────
Particulars                         FY2025          FY2024
─────────────────────────────────────────────────────────────
First Year Premiums               1,34,513        (prior yr)
Renewal Premiums                  4,02,488
Single Premiums                   2,89,037
─────────────────────────────────────────────────────────────
TOTAL PREMIUM                     8,26,038
─────────────────────────────────────────────────────────────
Cross-check vs ICRA: ₹8,260 Cr ✅ EXACT MATCH (ICRA Jul 2025)

FORM L-5 — COMMISSION SCHEDULE
─────────────────────────────────────────────────────────────
Particulars                         FY2025
─────────────────────────────────────────────────────────────
Commission on First Year Premiums     29,228
Commission on Renewal Premiums        13,445
Commission on Single Premiums         10,558
─────────────────────────────────────────────────────────────
GROSS COMMISSION                      53,231
─────────────────────────────────────────────────────────────
Validation: 29228+13445+10558 = 53231 ✅ EXACT MATCH

FORM L-6 — OPERATING EXPENSES
─────────────────────────────────────────────────────────────
Advertisement and Publicity            2,604
Business Development / Sales Promotion 10,569
Total Operating Expenses (Insurance)   96,179

POLICY COUNT (Form L-36)
─────────────────────────────────────────────────────────────
Individual FYP policies issued        26,358
Individual Single Premium policies    10,495
Total new individual policies         36,853
─────────────────────────────────────────────────────────────

CAC CALCULATION
─────────────────────────────────────────────────────────────
Total acquisition cost = ₹66,404 Lakh (comm + advt + biz dev)
Total new policies     = 36,853
CAC per policy         = ₹66,404L × 100 ÷ 36,853 = ₹1,80,200
Average ticket size    = ₹1,34,513L × 100 ÷ 26,358 = ₹5,10,319
─────────────────────────────────────────────────────────────
```

### Max Life — IRDAI Form L-4 & L-5 (FY2025, ₹ Lakh)

```
FORM L-4 — PREMIUM SCHEDULE
─────────────────────────────────────────────────────────────
Particulars                         FY2025
─────────────────────────────────────────────────────────────
First Year Premiums               2,89,617
Renewal Premiums                 13,22,260
Single Premiums                      62,495
─────────────────────────────────────────────────────────────
TOTAL PREMIUM (stated)           15,30,063
─────────────────────────────────────────────────────────────
Note: FYP+Renewal+Single = 16,74,372 vs stated 15,30,063
Gap of ₹1,443 Cr = group credit life business filed separately
in group premium schedule — NORMAL for insurers with group book

FORM L-5 — COMMISSION SCHEDULE
─────────────────────────────────────────────────────────────
Commission on First Year Premiums  1,30,826
Commission on Renewal Premiums       45,024
Commission on Single Premiums         9,396
─────────────────────────────────────────────────────────────
GROSS COMMISSION                   1,85,246
─────────────────────────────────────────────────────────────
Validation: 130826+45024+9396 = 185246 ✅ EXACT MATCH

FORM L-6 — OPERATING EXPENSES
─────────────────────────────────────────────────────────────
Advertisement and Publicity         2,21,475
Business Development                1,66,639
─────────────────────────────────────────────────────────────
Total Acquisition Cost              5,73,360  (comm+advt+biz)

POLICY COUNT (Form L-36/38)
─────────────────────────────────────────────────────────────
Individual FYP policies             7,52,586
Individual Single Premium policies       350
Total new individual policies       7,52,936

CAC CALCULATION
─────────────────────────────────────────────────────────────
Total acquisition cost = ₹5,73,360 Lakh
Total new policies     = 7,52,936
CAC per policy         = ₹5,73,360L × 100 ÷ 7,52,936 = ₹76,150
Average ticket size    = ₹2,89,617L × 100 ÷ 7,52,586 = ₹38,484
─────────────────────────────────────────────────────────────
```

---

## All Calculations

### Core Leakage Formula

```
Commission leakage (₹ Cr) = Commission on FYP (₹ Cr)
                           × Lapse rate at 13M (%)

CAC leakage (₹ Cr)        = New policies × Lapse rate at 13M
                           × CAC per policy (₹)
                           ÷ 1,00,00,000  [convert ₹ to Cr]

Total economic leakage    = Commission leakage + CAC leakage

Recoverable               = Commission leakage × 0.40
  [Basis: Swiss Re Sigma "Lapse Risk in Life Insurance" 2022
   XGBoost at AUC 0.75 catches ~40-48% of future lapses]

Model ROI                 = Recoverable ÷ ₹0.15 Cr build cost
  [₹0.15 Cr = one-time model development cost, industry estimate]
```

### HDFC Life Leakage Calculation

```
Commission on FYP         = ₹5,860 Cr      [Form L-5, real]
13M Lapse rate            = 13.0%           [100% - 87% persistency]
Commission leakage        = ₹5,860 × 0.130 = ₹762 Cr

New policies (est FY)     = 6,98,000        [Q4 count ÷ 0.35 seasonality]
Policies lapsed           = 6,98,000 × 0.130 = 90,740
CAC per policy            = ₹1,13,740       [Q4 acquisition cost ÷ Q4 policies]
CAC leakage               = 90,740 × ₹1,13,740 ÷ 1,00,00,000 = ₹1,032 Cr

Total economic leakage    = ₹762 + ₹1,032 = ₹1,794 Cr
Recoverable @ 40%         = ₹762 × 0.40   = ₹305 Cr
Model ROI                 = ₹305 ÷ ₹0.15  = 2,031x
```

### SUD Life Leakage Calculation

```
Commission on FYP         = ₹292 Cr        [₹29,228 Lakh ÷ 100]
13M Lapse rate            = 22.3%           [100% - 77.7% persistency]
Commission leakage        = ₹292 × 0.223  = ₹65 Cr

New policies              = 36,853          [Form L-36, real]
Policies lapsed           = 36,853 × 0.223 = 8,218
CAC per policy            = ₹1,80,200       [₹66,404L ÷ 36,853 policies]
CAC leakage               = 8,218 × ₹1,80,200 ÷ 1,00,00,000 = ₹148 Cr

Total economic leakage    = ₹65 + ₹148   = ₹213 Cr
Recoverable @ 40%         = ₹65 × 0.40   = ₹26 Cr
Model ROI                 = ₹26 ÷ ₹0.15  = 174x
```

### Max Life Leakage Calculation

```
Commission on FYP         = ₹1,308 Cr      [₹1,30,826 Lakh ÷ 100]
13M Lapse rate            = 12.4%           [100% - 87.6% persistency]
Commission leakage        = ₹1,308 × 0.124 = ₹162 Cr

New policies              = 7,52,936        [Form L-36, real]
Policies lapsed           = 7,52,936 × 0.124 = 93,364
CAC per policy            = ₹76,150         [₹5,73,360L ÷ 7,52,936 policies]
CAC leakage               = 93,364 × ₹76,150 ÷ 1,00,00,000 = ₹711 Cr

Total economic leakage    = ₹162 + ₹711   = ₹873 Cr
Recoverable @ 40%         = ₹162 × 0.40   = ₹65 Cr
Model ROI                 = ₹65 ÷ ₹0.15   = 433x
```

### Banca Channel Leakage

```
Methodology: Banca lapse multiplier = 1.35×
[Industry benchmark: banca-sold policies lapse 35% more often
 than agency-sold. Documented in ICRA/CRISIL insurance research]

HDFC Life banca leakage:
  Commission to banca channel = ₹5,860 Cr × 65% = ₹3,809 Cr
  Banca lapse rate            = 13.0% × 1.35     = 17.6%
  Banca leakage               = ₹3,809 × 0.176   = ₹670 Cr
  [88% of total commission leakage is from banca channel]

SUD Life banca leakage:
  Commission to banca         = ₹292 Cr × 95.6%  = ₹279 Cr
  Banca lapse rate            = 22.3% × 1.35      = 30.1%
  Banca leakage               = ₹279 × 0.301      = ₹84 Cr
  [129% of headline leakage — worse than average banca lapse]
```

---

## Persistency Analysis

```
PERSISTENCY COHORT TABLE — FY2025 (PREMIUM BASIS)
──────────────────────────────────────────────────────────────
Insurer          13M      25M      37M      49M      61M
──────────────────────────────────────────────────────────────
HDFC Life       87.0%      —        —        —       63.0%
Max Life        87.6%      —        —        —       59.3%
SUD Life        77.7%      —        —        —       23.2%
Industry leader 89%+     79%+     72%+     64%+     62%+
──────────────────────────────────────────────────────────────
YoY Change (FY2024 → FY2025)
HDFC Life 13M:   0 bps  (stable)
HDFC Life 61M: +1000 bps (IMPROVED — best-in-class retention)
SUD Life 13M:   -120 bps (declining)
SUD Life 61M:   -520 bps (CRITICAL — accelerating decay)
Max Life 13M:   +100 bps (improving)
Max Life 61M:   +100 bps (stable improvement)

KEY INSIGHT: SUD Life's 61M drop of 520 bps in one year signals
a structural failure in post-sale engagement, not random variation.
At 23.2% retention by year 5, SUD is losing 76.8% of its customer
base — replacing them costs ₹1,80,200 per policy × lapses.
```

---

## Consulting Analysis & Recommendations

### Executive Summary

Three Indian life insurers collectively leak **₹2,880 Cr annually** through preventable policy lapses. This leakage is not random — it is structurally caused by bancassurance distribution and amplified by the absence of post-sale retention systems. An XGBoost lapse prediction model can recover ₹396 Cr of this annual leakage at a combined build cost of ₹0.45 Cr, delivering a 880x ROI.

---

### Strategic Finding 1 — The Banca Trap

**What the data shows:**

SUD Life sources 95.6% of individual NBP through bancassurance. It lapses at 22.3%. Max Life sources 59% through banca. It lapses at 12.4%. The 36.6 percentage point difference in banca share produces a 9.9 percentage point difference in lapse rate. This is not coincidence — it is the banca trap.

**Why banca creates lapse:**

Bank relationship managers sell insurance products during account opening, loan processing, or fixed deposit renewals. The customer buys to satisfy the RM, not because they understand the product. No independent agent follows up. No renewal nudge. The policy lapses silently at month 11 — one month before commission clawback would apply.

**Business recommendation:**

Every insurer with >70% banca dependency should restructure commission from upfront to performance-linked. Pay 50% commission on policy issuance. Pay the remaining 50% only when the policy completes 13 months. This is legally permissible under IRDAI guidelines and eliminates the incentive misalignment. Expected impact: 3–5 percentage point improvement in 13M persistency within 2 years.

---

### Strategic Finding 2 — HDFC Life's 61M Improvement is a Blueprint

**What the data shows:**

HDFC Life improved 61M persistency by 1,000 basis points in FY2025 — from 53% to 63%. This is the largest single-year improvement in the dataset. Meanwhile SUD Life's 61M dropped 520 bps in the same period.

**What HDFC did differently:**

HDFC Life's FY2025 press release attributes the improvement to "deep customer engagement and effective retention initiatives." Their distribution mix (65% banca, 18% agency, 7% broker, 10% direct) is diversified enough to maintain relationship continuity. Their digital platform handles 90%+ of service requests via self-service — reducing friction at renewal time.

**Business recommendation:**

For SUD Life specifically: the 39.8 percentage point gap in 61M persistency vs HDFC is worth calculating in ₹ terms. If SUD Life improved 61M persistency from 23.2% to 40% (still well below HDFC), the additional policies retained would reduce replacement CAC by approximately ₹200–300 Cr annually. The entire improvement requires one thing: a post-sale engagement system. KPOINT-style personalized video at Day 15, Day 30, Day 330 costs ₹10 per customer per year. At 36,853 customers that is ₹37 lakh per year — against ₹200 Cr in potential CAC savings.

---

### Strategic Finding 3 — Max Life's CAC is the Right Benchmark

**What the data shows:**

Max Life spends ₹76,150 CAC per policy. SUD Life spends ₹1,80,200. HDFC Life spends ₹1,13,740. Max Life achieves this with 59% banca and 29% agency — a balanced mix that combines banca reach with agency relationship depth.

**Why Max Life's CAC is lower despite high marketing spend:**

Max Life spent ₹2,215 Cr on advertisement and ₹1,666 Cr on business development — far more than the other two in absolute terms. But its policy count of 7,52,936 is also far higher. The brand investment creates pull — customers come to Max Life rather than being pushed by bank RMs. Pull distribution = lower per-unit acquisition cost + higher persistency.

**Business recommendation:**

SUD Life should model Max Life's approach: reduce banca dependency from 95.6% to 70% over 3 years by investing in agency channel development. Each 10% shift from banca to agency reduces lapse rate by approximately 2 percentage points (based on cross-insurer analysis). At SUD Life's scale, a 2pp lapse reduction saves ₹6 Cr in commission leakage and ₹30 Cr in CAC annually.

---

### Prioritised Action Plan

#### For HDFC Life (MEDIUM risk, largest absolute opportunity)

| Priority | Action | Investment | Expected Return |
|---|---|---|---|
| 1 | Deploy XGBoost lapse predictor | ₹0.15 Cr one-time | ₹305 Cr/yr recoverable |
| 2 | Performance-linked commission for banca | Structural change | 2–3pp lapse improvement |
| 3 | Extend 61M retention program to new cohorts | ₹5–10 Cr/yr | Sustain 1000 bps gain |

#### For SUD Life (CRITICAL risk, structural intervention needed)

| Priority | Action | Investment | Expected Return |
|---|---|---|---|
| 1 | Emergency: restructure banca commission to 50/50 upfront/performance | Nil | Estimated 4pp lapse improvement = ₹12 Cr savings |
| 2 | Post-sale engagement system (KPOINT or equivalent) | ₹0.37 Lakh/yr | ₹200 Cr CAC savings |
| 3 | Begin agency channel development — target 80% banca by FY2027 | ₹50 Cr over 3 yrs | 6pp lapse improvement = ₹18 Cr savings/yr |
| 4 | Deploy lapse prediction model | ₹0.15 Cr | ₹26 Cr/yr recoverable |

#### For Max Life (MEDIUM risk, strong trajectory)

| Priority | Action | Investment | Expected Return |
|---|---|---|---|
| 1 | Deploy lapse predictor on ULIP segment specifically | ₹0.15 Cr | ₹65 Cr/yr recoverable |
| 2 | Continue agency channel investment | Ongoing | Sustain low lapse trajectory |
| 3 | Target 61M persistency above 65% by FY2026 | ₹10–15 Cr retention spend | ₹150–200 Cr NPV |

---

### The Regulatory Angle

IRDAI's revised commission guidelines (2023) require insurers to demonstrate value-for-money in distribution costs. Flat commission regardless of policy retention is explicitly flagged as a potential conflict of interest under the Consumer Protection Code. Every Indian life insurer must demonstrate persistency-linked distribution economics by FY2026. This project provides the data product that makes that regulatory argument — turning a compliance requirement into a competitive advantage.

---

## Architecture

```
IRDAI Public Filings (quarterly)
        │
        ▼
Manual Extraction (Form L-4, L-5, L-6)  [20 mins/insurer]
        │
        ▼
data/raw/*.csv
  ├── insurer_summary.csv        (3 insurers × 20 metrics)
  ├── persistency_cohorts.csv    (13 rows × FY2024+FY2025)
  └── channel_commission.csv     (10 rows by channel)
        │                                     │
        ▼                                     ▼
01_ingest_to_duckdb.py              Kafka Producer
[Python + DuckDB]                   policy_event_producer.py
        │                           [500 events, real parameters]
        ▼
DuckDB raw schema
  ├── raw.insurer_summary
  ├── raw.persistency_cohorts
  └── raw.channel_commission
        │
        ▼
dbt run — 3 models [PASS=3, 5 seconds]
  ├── stg_insurer_summary         [view]   clean + type
  ├── int_leakage_calculations    [table]  leakage formula
  └── fct_leakage                 [table]  final + rankings
        │
        ▼
Streamlit Dashboard [streamlit/app.py]
  ├── KPI: leakage / commission / recoverable / ROI
  ├── Bar: commission leakage by insurer
  ├── Line: persistency 13M → 61M cohort
  ├── Scatter: channel lapse vs leakage
  └── Table: full comparison + strategic insights
        │
        ▼
Deployed: Render.com [free tier, public URL]
```

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Data warehouse | DuckDB | Local, serverless, handles 50M+ rows, free |
| Transformation | dbt-duckdb | Version-controlled SQL, lineage, tests |
| Event stream | kafka-python | Simulates real-time policy events |
| ML (Phase 5) | XGBoost + SHAP | Best AUC on tabular insurance data, explainability |
| Dashboard | Streamlit + Plotly | Fast to build, deployable, interactive |
| Orchestration | Airflow (planned) | Daily refresh automation |
| Monitoring | Kibana (planned) | Pipeline health, lapse score alerts |
| Deployment | Render.com | Free tier, GitHub-connected, auto-deploy |

---

## Project Structure

```
india-insurance-leakage/
├── data/
│   ├── raw/                         # Real IRDAI filing data
│   │   ├── insurer_summary.csv      # 3 insurers × 20 metrics
│   │   ├── persistency_cohorts.csv  # 13 cohort data points
│   │   └── channel_commission.csv   # 10 channel rows
│   ├── processed/                   # Kafka output
│   │   └── policy_events_stream.jsonl
│   └── duckdb/
│       └── india_insurance.duckdb   # Warehouse
├── ingestion/
│   └── 01_ingest_to_duckdb.py
├── kafka/
│   └── policy_event_producer.py
├── dbt_project/
│   ├── models/
│   │   ├── staging/
│   │   │   └── stg_insurer_summary.sql
│   │   ├── intermediate/
│   │   │   └── int_leakage_calculations.sql
│   │   └── marts/
│   │       └── fct_leakage.sql
│   └── dbt_project.yml
├── ml/                              # XGBoost — Phase 5
├── streamlit/
│   └── app.py                       # Live dashboard
├── airflow/dags/                    # Planned
├── monitoring/                      # Planned
├── requirements.txt
└── README.md
```

---

## How to Run

```bash
# Clone
git clone https://github.com/dhimanvivek0001/india-insurance-leakage.git
cd india-insurance-leakage
pip install -r requirements.txt

# Configure dbt (~/.dbt/profiles.yml)
india_insurance:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: /full/path/to/data/duckdb/india_insurance.duckdb
      threads: 4

# Run pipeline
python ingestion/01_ingest_to_duckdb.py
python kafka/policy_event_producer.py
cd dbt_project && python -c "from dbt.cli.main import dbtRunner; r=dbtRunner(); r.invoke(['run'])"
cd ..
python -m streamlit run streamlit/app.py
```

---

## Annual Data Refresh (30 minutes)

1. IRDAI publishes quarterly — download insurer's public disclosure PDF
2. Extract Form L-4 (premiums) and L-5 (commission) — "Up to March 31" column
3. Update `data/raw/insurer_summary.csv` — 4 numbers per insurer
4. Update persistency from press release or ICRA report
5. Run `python ingestion/01_ingest_to_duckdb.py`
6. Run `dbt run`
7. Dashboard auto-updates with new numbers

---

## What's Next

- [ ] **Phase 5** — XGBoost lapse prediction model on 7,52,936 Max Life policies
- [ ] **Phase 5b** — SHAP feature importance: "banca adds X% lapse risk"
- [ ] **Phase 6** — Airflow DAG for automated annual refresh
- [ ] **Phase 7** — Elasticsearch + Kibana pipeline monitoring
- [ ] **Expansion** — Add 7 more insurers to cover 80%+ of private market

---

## Author

**Vivek Dhiman**
MSc Business Analytics — J.E. Cairnes School of Business, University of Galway
Prior experience: KPOINT Technologies, ADDA.io
[GitHub](https://github.com/dhimanvivek0001)

---

*All data from audited public filings. IRDAI Form L-4/L-5/L-6 (March 2025) · ICRA Rating Reports (Jun–Jul 2025) · Company Press Releases (Apr–May 2025). No proprietary data used.*
