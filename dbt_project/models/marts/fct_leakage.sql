-- models/marts/fct_leakage.sql
-- FINAL FACT TABLE — The consulting deliverable
-- Every row = one insurer's complete leakage profile
-- This is what feeds Kibana, Streamlit, and the XGBoost model

WITH leakage AS (
    SELECT * FROM {{ ref('int_leakage_calculations') }}
),

channel AS (
    SELECT
        insurer,
        fy,
        SUM(CASE WHEN channel ILIKE '%banca%' OR channel ILIKE '%corp%'
                 THEN leakage_cr ELSE 0 END) AS banca_channel_leakage_cr,
        SUM(CASE WHEN channel ILIKE '%agency%'
                 THEN leakage_cr ELSE 0 END) AS agency_channel_leakage_cr,
        MAX(channel_lapse_rate_pct)           AS max_channel_lapse_pct,
        COUNT(DISTINCT channel)               AS num_channels
    FROM raw.channel_commission
    GROUP BY insurer, fy
),

cohort AS (
    SELECT
        insurer,
        MAX(CASE WHEN cohort_month = 13 THEN yoy_change_bps END) AS persistency_13m_yoy_bps,
        MAX(CASE WHEN cohort_month = 61 THEN yoy_change_bps END) AS persistency_61m_yoy_bps,
        MAX(CASE WHEN cohort_month = 61 THEN persistency_pct  END) AS persistency_61m_latest
    FROM raw.persistency_cohorts
    WHERE fy = 'FY2025'
    GROUP BY insurer
),

final AS (
    SELECT
        -- ── IDENTIFIERS ───────────────────────────────────────────
        l.insurer_name,
        l.financial_year,
        l.leakage_risk_tier,
        l.longterm_retention_flag,

        -- ── SCALE ────────────────────────────────────────────────
        l.total_premium_cr,
        l.first_year_premium_cr,
        l.new_policies,
        ROUND(l.first_year_premium_cr / l.new_policies * 100, 0)
                                            AS avg_ticket_size_rs,

        -- ── COMMISSION (REAL L-5 NUMBERS) ────────────────────────
        l.gross_commission_cr,
        l.commission_fyp_cr,
        l.commission_rate_fyp_pct,
        l.blended_commission_rate_pct,
        l.total_acquisition_cost_cr,
        l.cac_per_policy_rs,

        -- ── PERSISTENCY ──────────────────────────────────────────
        l.persistency_13m_pct,
        l.persistency_61m_pct,
        l.lapse_rate_13m_pct,
        l.banca_channel_pct,
        co.persistency_13m_yoy_bps,
        co.persistency_61m_yoy_bps,

        -- ── LEAKAGE (THE HEADLINE NUMBERS) ───────────────────────
        l.commission_leakage_cr,
        l.policies_lapsed_est,
        l.cac_leakage_cr,
        l.total_economic_leakage_cr,
        l.leakage_pct_of_commission,
        l.banca_commission_leakage_cr,

        -- ── CHANNEL BREAKDOWN ────────────────────────────────────
        ch.banca_channel_leakage_cr,
        ch.agency_channel_leakage_cr,
        ch.max_channel_lapse_pct,

        -- ── MODEL VALUE ──────────────────────────────────────────
        l.recoverable_40pct_model_cr,
        l.model_roi_x,
        0.15                                AS model_build_cost_cr,

        -- ── RETENTION (KPOINT) ───────────────────────────────────
        l.kpoint_spend_cr,
        l.customers_retained_kpoint,

        -- ── RANKINGS ─────────────────────────────────────────────
        RANK() OVER (ORDER BY l.total_economic_leakage_cr DESC)
                                            AS leakage_rank,
        RANK() OVER (ORDER BY l.persistency_13m_pct DESC)
                                            AS persistency_rank_best,
        RANK() OVER (ORDER BY l.lapse_rate_13m_pct DESC)
                                            AS lapse_risk_rank_worst,

        -- ── METADATA ─────────────────────────────────────────────
        CURRENT_TIMESTAMP                   AS model_run_at

    FROM leakage l
    LEFT JOIN channel ch
        ON l.insurer_name = ch.insurer
        AND l.financial_year = ch.fy
    LEFT JOIN cohort co
        ON l.insurer_name = co.insurer
)

SELECT * FROM final
ORDER BY total_economic_leakage_cr DESC
