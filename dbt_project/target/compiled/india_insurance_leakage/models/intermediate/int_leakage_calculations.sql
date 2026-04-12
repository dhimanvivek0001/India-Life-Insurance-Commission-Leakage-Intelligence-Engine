-- models/intermediate/int_leakage_calculations.sql
-- Core leakage calculation engine
-- This is where your strategic insight becomes SQL logic:
-- "Banca = higher lapse = commission paid on dead policies = leakage"

WITH base AS (
    SELECT * FROM "india_insurance"."main_staging"."stg_insurer_summary"
),

leakage AS (
    SELECT
        insurer_name,
        financial_year,

        -- ── PREMIUM LAYER ────────────────────────────────────────
        total_premium_cr,
        first_year_premium_cr,
        renewal_premium_cr,

        -- ── COMMISSION LAYER (real L-5 numbers) ──────────────────
        gross_commission_cr,
        commission_fyp_cr,
        blended_commission_rate_pct,
        commission_rate_fyp_pct,

        -- ── PERSISTENCY LAYER ────────────────────────────────────
        persistency_13m_pct,
        persistency_61m_pct,
        lapse_rate_13m_pct,
        banca_channel_pct,

        -- ── CAC LAYER ────────────────────────────────────────────
        new_policies,
        cac_per_policy_rs,
        total_acquisition_cost_cr,

        -- ── LEAKAGE CALCULATIONS ──────────────────────────────────
        -- Commission leakage: commission on FYP × lapse rate
        -- Logic: commission paid upfront, policy lapses = money wasted
        ROUND(commission_fyp_cr * (lapse_rate_13m_pct / 100), 2)
                                            AS commission_leakage_cr,

        -- Policies lapsed estimate
        ROUND(new_policies * (lapse_rate_13m_pct / 100), 0)
                                            AS policies_lapsed_est,

        -- CAC leakage: lapsed policies × cost to acquire them
        ROUND(
            (new_policies * (lapse_rate_13m_pct / 100) * cac_per_policy_rs)
            / 10000000.0,  -- convert to Cr
        2)                                  AS cac_leakage_cr,

        -- Total economic leakage
        ROUND(
            commission_fyp_cr * (lapse_rate_13m_pct / 100) +
            (new_policies * (lapse_rate_13m_pct / 100) * cac_per_policy_rs) / 10000000.0,
        2)                                  AS total_economic_leakage_cr,

        -- Leakage as % of total commission
        ROUND(
            (commission_fyp_cr * (lapse_rate_13m_pct / 100))
            / NULLIF(gross_commission_cr, 0) * 100,
        2)                                  AS leakage_pct_of_commission,

        -- ── BANCA LEAKAGE ─────────────────────────────────────────
        -- Banca has 35% higher lapse than average (industry benchmark)
        ROUND(
            commission_fyp_cr * (banca_channel_pct / 100) *
            (lapse_rate_13m_pct / 100 * 1.35),
        2)                                  AS banca_commission_leakage_cr,

        -- ── ML MODEL VALUE ────────────────────────────────────────
        -- If XGBoost catches 40% of lapses before commission is paid
        -- (Swiss Re Sigma 2022: AUC 0.75 model catches ~48%, conservative 40%)
        ROUND(
            commission_fyp_cr * (lapse_rate_13m_pct / 100) * 0.40,
        2)                                  AS recoverable_40pct_model_cr,

        -- Model ROI (build cost = ₹0.15 Cr one-time)
        ROUND(
            (commission_fyp_cr * (lapse_rate_13m_pct / 100) * 0.40)
            / 0.15,
        0)                                  AS model_roi_x,

        -- ── RETENTION ROI (KPOINT model) ──────────────────────────
        -- ₹10/customer/yr engagement nudge
        -- 1% conversion on lapsed customers
        ROUND(
            (new_policies * (lapse_rate_13m_pct / 100)) * 10 / 10000000.0,
        4)                                  AS kpoint_spend_cr,

        ROUND(
            new_policies * (lapse_rate_13m_pct / 100) * 0.01,
        0)                                  AS customers_retained_kpoint,

        -- ── RISK TIER ─────────────────────────────────────────────
        CASE
            WHEN lapse_rate_13m_pct > 20 AND banca_channel_pct > 90
                THEN 'CRITICAL'
            WHEN lapse_rate_13m_pct > 15 OR banca_channel_pct > 70
                THEN 'HIGH'
            WHEN lapse_rate_13m_pct > 12
                THEN 'MEDIUM'
            ELSE 'LOW'
        END                                 AS leakage_risk_tier,

        -- ── 61M DETERIORATION FLAG ────────────────────────────────
        CASE
            WHEN persistency_61m_pct < 30
                THEN 'CRITICAL - majority lost by yr5'
            WHEN persistency_61m_pct < 50
                THEN 'POOR - half lost by yr5'
            WHEN persistency_61m_pct < 65
                THEN 'MODERATE'
            ELSE 'GOOD'
        END                                 AS longterm_retention_flag

    FROM base
)

SELECT * FROM leakage
ORDER BY total_economic_leakage_cr DESC