"""
PHASE 1 — INGESTION LAYER
Loads real validated CSV data into DuckDB raw layer.
This is the foundation every other layer builds on.

Tool: DuckDB (local warehouse, free, no cloud needed)
Input: data/raw/*.csv (real IRDAI filing numbers)
Output: data/duckdb/india_insurance.duckdb (raw schema tables)
"""

import duckdb
import pandas as pd
import os
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR      = os.path.join(PROJECT_ROOT, "data", "raw")
DB_PATH      = os.path.join(PROJECT_ROOT, "data", "duckdb", "india_insurance.duckdb")

print("=" * 60)
print("PHASE 1 — INGESTION TO DUCKDB")
print(f"DB: {DB_PATH}")
print("=" * 60)

con = duckdb.connect(DB_PATH)

# Create raw schema
con.execute("CREATE SCHEMA IF NOT EXISTS raw")

# ── TABLE 1: insurer_summary ──────────────────────────────────────
print("\n[1/3] Loading insurer_summary...")
con.execute("DROP TABLE IF EXISTS raw.insurer_summary")
con.execute(f"""
    CREATE TABLE raw.insurer_summary AS
    SELECT
        insurer,
        fy,
        CAST(total_premium_cr AS DOUBLE)   AS total_premium_cr,
        CAST(fyp_cr AS DOUBLE)             AS fyp_cr,
        CAST(renewal_cr AS DOUBLE)         AS renewal_cr,
        CAST(single_cr AS DOUBLE)          AS single_cr,
        CAST(gross_comm_cr AS DOUBLE)      AS gross_comm_cr,
        CAST(comm_fyp_cr AS DOUBLE)        AS comm_fyp_cr,
        CAST(comm_renewal_cr AS DOUBLE)    AS comm_renewal_cr,
        CAST(comm_single_cr AS DOUBLE)     AS comm_single_cr,
        CAST(total_acq_cost_cr AS DOUBLE)  AS total_acq_cost_cr,
        CAST(new_policies AS INTEGER)      AS new_policies,
        CAST(cac_per_policy_rs AS INTEGER) AS cac_per_policy_rs,
        CAST(persistency_13m_pct AS DOUBLE) AS persistency_13m_pct,
        CAST(persistency_61m_pct AS DOUBLE) AS persistency_61m_pct,
        CAST(lapse_rate_13m_pct AS DOUBLE)  AS lapse_rate_13m_pct,
        CAST(banca_pct AS DOUBLE)           AS banca_pct,
        source_premium,
        source_commission,
        source_persistency,
        NOW() AS ingested_at
    FROM read_csv_auto('{RAW_DIR}/insurer_summary.csv')
""")
count = con.execute("SELECT COUNT(*) FROM raw.insurer_summary").fetchone()[0]
print(f"   Loaded {count} rows")

# ── TABLE 2: persistency_cohorts ─────────────────────────────────
print("\n[2/3] Loading persistency_cohorts...")
con.execute("DROP TABLE IF EXISTS raw.persistency_cohorts")
con.execute(f"""
    CREATE TABLE raw.persistency_cohorts AS
    SELECT
        insurer,
        fy,
        CAST(cohort_month AS INTEGER)       AS cohort_month,
        CAST(persistency_pct AS DOUBLE)     AS persistency_pct,
        CAST(lapse_pct AS DOUBLE)           AS lapse_pct,
        CAST(yoy_change_bps AS DOUBLE)      AS yoy_change_bps,
        source,
        NOW() AS ingested_at
    FROM read_csv_auto('{RAW_DIR}/persistency_cohorts.csv')
""")
count = con.execute("SELECT COUNT(*) FROM raw.persistency_cohorts").fetchone()[0]
print(f"   Loaded {count} rows")

# ── TABLE 3: channel_commission ───────────────────────────────────
print("\n[3/3] Loading channel_commission...")
con.execute("DROP TABLE IF EXISTS raw.channel_commission")
con.execute(f"""
    CREATE TABLE raw.channel_commission AS
    SELECT
        insurer,
        fy,
        channel,
        CAST(channel_share_pct AS DOUBLE)       AS channel_share_pct,
        CAST(commission_cr AS DOUBLE)           AS commission_cr,
        CAST(lapse_multiplier AS DOUBLE)        AS lapse_multiplier,
        CAST(channel_lapse_rate_pct AS DOUBLE)  AS channel_lapse_rate_pct,
        CAST(leakage_cr AS DOUBLE)              AS leakage_cr,
        source,
        NOW() AS ingested_at
    FROM read_csv_auto('{RAW_DIR}/channel_commission.csv')
""")
count = con.execute("SELECT COUNT(*) FROM raw.channel_commission").fetchone()[0]
print(f"   Loaded {count} rows")

# ── VALIDATION QUERIES ────────────────────────────────────────────
print("\n── Validation ────────────────────────────────────────────")
print("\nraw.insurer_summary:")
result = con.execute("""
    SELECT insurer, fy, total_premium_cr, comm_fyp_cr,
           persistency_13m_pct, lapse_rate_13m_pct
    FROM raw.insurer_summary
    ORDER BY total_premium_cr DESC
""").df()
print(result.to_string(index=False))

print("\nraw.persistency_cohorts (FY2025 only):")
result2 = con.execute("""
    SELECT insurer, cohort_month, persistency_pct,
           lapse_pct, yoy_change_bps
    FROM raw.persistency_cohorts
    WHERE fy = 'FY2025'
    ORDER BY insurer, cohort_month
""").df()
print(result2.to_string(index=False))

print("\nraw.channel_commission:")
result3 = con.execute("""
    SELECT insurer, channel, channel_share_pct,
           commission_cr, leakage_cr
    FROM raw.channel_commission
    ORDER BY insurer, channel_share_pct DESC
""").df()
print(result3.to_string(index=False))

# ── SCHEMA SUMMARY ────────────────────────────────────────────────
print("\n── DuckDB schema created ─────────────────────────────────")
tables = con.execute("""
    SELECT table_schema, table_name,
           estimated_size
    FROM information_schema.tables
    WHERE table_schema = 'raw'
""").df()
print(tables.to_string(index=False))

con.close()
print(f"\n✅ Phase 1 complete. DB at: {DB_PATH}")
print("Next: Run ingestion/02_generate_policy_events.py (Kafka simulation)")
