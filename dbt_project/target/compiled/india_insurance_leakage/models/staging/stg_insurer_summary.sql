-- models/staging/stg_insurer_summary.sql
-- Staging layer: clean types, rename, add basic derived fields
-- Source: raw.insurer_summary (real IRDAI L-4 + L-5 data)

WITH source AS (
    SELECT * FROM raw.insurer_summary
),

cleaned AS (
    SELECT
        -- identifiers
        insurer                                         AS insurer_name,
        fy                                              AS financial_year,

        -- premium (₹ Crore)
        total_premium_cr,
        fyp_cr                                          AS first_year_premium_cr,
        renewal_cr                                      AS renewal_premium_cr,
        single_cr                                       AS single_premium_cr,

        -- commission (₹ Crore) — real Form L-5 numbers
        gross_comm_cr                                   AS gross_commission_cr,
        comm_fyp_cr                                     AS commission_fyp_cr,
        comm_renewal_cr                                 AS commission_renewal_cr,
        comm_single_cr                                  AS commission_single_cr,

        -- acquisition
        total_acq_cost_cr                               AS total_acquisition_cost_cr,
        new_policies,
        cac_per_policy_rs,

        -- persistency (real press release / ICRA numbers)
        persistency_13m_pct,
        persistency_61m_pct,
        lapse_rate_13m_pct,
        banca_pct                                       AS banca_channel_pct,

        -- derived: commission rates
        ROUND(comm_fyp_cr / NULLIF(fyp_cr, 0) * 100, 2)
                                                        AS commission_rate_fyp_pct,
        ROUND(gross_comm_cr / NULLIF(total_premium_cr, 0) * 100, 2)
                                                        AS blended_commission_rate_pct,

        -- derived: expense ratios
        ROUND(total_acq_cost_cr / NULLIF(total_premium_cr, 0) * 100, 2)
                                                        AS acquisition_cost_ratio_pct,

        -- sources
        source_premium,
        source_commission,
        source_persistency,
        ingested_at

    FROM source
)

SELECT * FROM cleaned