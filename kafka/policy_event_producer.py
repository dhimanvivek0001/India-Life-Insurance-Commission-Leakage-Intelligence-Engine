"""
PHASE 2A — KAFKA PRODUCER (Policy Event Stream)
Simulates real-time policy events derived from real insurer data.
Each event = one policy action (new_policy / lapse / renewal / surrender)

Tool: kafka-python (free, local)
In production: Confluent Cloud free tier OR Docker Kafka
Here: runs as a local producer you can test without Docker

WHAT THIS TEACHES:
- Event-driven architecture for insurance data
- Why Kafka matters: IRDAI data is quarterly batch
  but insurers process policies DAILY. Kafka bridges that gap.
- Every policy action = one Kafka message = real-time leakage tracking
"""

import json
import random
import time
from datetime import datetime, timedelta
import uuid

# ── REAL PARAMETERS FROM VALIDATED DATA ──────────────────────────
# These distributions are derived from real filing numbers
INSURERS = {
    "HDFC Life": {
        "daily_new_policies": 1912,      # 698,000 / 365
        "lapse_rate_13m": 0.130,
        "avg_premium_rs": 58000,
        "channels": {"Bancassurance": 0.65, "Agency": 0.18,
                     "Broker": 0.07, "Direct": 0.10},
        "cac_rs": 113740,
        "comm_rate_fyp": 0.451,
    },
    "SUD Life": {
        "daily_new_policies": 101,       # 36,853 / 365
        "lapse_rate_13m": 0.223,
        "avg_premium_rs": 510000,        # high ticket banca
        "channels": {"Bancassurance": 0.956, "Other": 0.044},
        "cac_rs": 180200,
        "comm_rate_fyp": 0.217,
    },
    "Max Life": {
        "daily_new_policies": 2062,      # 752,936 / 365
        "lapse_rate_13m": 0.124,
        "avg_premium_rs": 38000,         # agent model, lower ticket
        "channels": {"Bancassurance": 0.59, "Agency": 0.29,
                     "Direct": 0.12},
        "cac_rs": 76150,
        "comm_rate_fyp": 0.452,
    },
}

STATES = ["Maharashtra", "Tamil Nadu", "Karnataka", "Gujarat",
          "Delhi", "Rajasthan", "UP", "West Bengal",
          "Andhra Pradesh", "Telangana"]

PRODUCTS = {
    "HDFC Life": ["Non-Par Savings", "ULIP", "Term", "Par", "Annuity"],
    "SUD Life":  ["Non-Par Savings", "ULIP", "Par"],
    "Max Life":  ["Non-Par Savings", "Term", "ULIP", "Par"],
}

PRODUCT_WEIGHTS = {
    "HDFC Life": [0.32, 0.39, 0.05, 0.19, 0.05],
    "SUD Life":  [0.53, 0.34, 0.13],
    "Max Life":  [0.45, 0.20, 0.25, 0.10],
}

def pick_channel(insurer_name):
    ins = INSURERS[insurer_name]
    channels = list(ins["channels"].keys())
    weights = list(ins["channels"].values())
    return random.choices(channels, weights=weights)[0]

def pick_product(insurer_name):
    products = PRODUCTS[insurer_name]
    weights  = PRODUCT_WEIGHTS[insurer_name]
    return random.choices(products, weights=weights)[0]

def lapse_prob(insurer_name, channel, product, age, premium):
    """
    Compute per-policy lapse probability.
    Based on real channel and product risk factors.
    This is what the XGBoost model learns to predict.
    """
    base = INSURERS[insurer_name]["lapse_rate_13m"]

    # Channel effect (real: banca = higher lapse)
    ch_mult = {"Bancassurance": 1.35, "Agency": 0.85,
               "Broker": 0.90, "Direct": 0.70, "Other": 1.10}
    base *= ch_mult.get(channel, 1.0)

    # Product effect
    pd_mult = {"Term": 1.15, "ULIP": 1.20, "Non-Par Savings": 0.90,
               "Par": 0.85, "Annuity": 0.30}
    base *= pd_mult.get(product, 1.0)

    # Age effect
    if age < 30:   base *= 1.20
    elif age > 55: base *= 1.10
    else:          base *= 0.90

    # Premium effect (lower premium = higher lapse)
    if premium < 20000:   base *= 1.35
    elif premium < 50000: base *= 1.10
    elif premium > 200000: base *= 0.75

    return min(max(base, 0.01), 0.85)

def generate_event(event_type="new_policy"):
    """Generate one policy event with realistic attributes."""
    insurer = random.choice(list(INSURERS.keys()))
    ins     = INSURERS[insurer]
    channel = pick_channel(insurer)
    product = pick_product(insurer)
    age     = random.randint(22, 65)

    # Premium with realistic distribution
    avg = ins["avg_premium_rs"]
    premium = max(5000, int(random.gauss(avg, avg * 0.4)))
    premium = (premium // 1000) * 1000  # round to nearest 1K

    lp = lapse_prob(insurer, channel, product, age, premium)
    commission = premium * ins["comm_rate_fyp"]

    event = {
        "event_id":          str(uuid.uuid4()),
        "event_type":        event_type,
        "event_timestamp":   datetime.now().isoformat(),
        "policy_id":         f"POL-{insurer[:3].upper()}-{random.randint(100000, 999999)}",
        "insurer":           insurer,
        "product_type":      product,
        "channel":           channel,
        "state":             random.choice(STATES),
        "age_at_issue":      age,
        "age_band":          ("18-30" if age < 30 else
                              "31-45" if age < 46 else "46-60"),
        "annual_premium_rs": premium,
        "premium_band":      ("< 20K" if premium < 20000 else
                              "20K-50K" if premium < 50000 else
                              "50K-2L" if premium < 200000 else "> 2L"),
        "commission_rs":     round(commission, 2),
        "lapse_probability": round(lp, 4),
        "lapse_risk_tier":   ("HIGH" if lp > 0.25 else
                              "MEDIUM" if lp > 0.15 else "LOW"),
        "cac_rs":            ins["cac_rs"],
        "economic_at_risk_rs": round(commission + ins["cac_rs"], 2),
        "fy":                "FY2025",
        "source":            "kafka_simulation_from_real_irdai_data",
    }
    return event

def run_producer(n_events=100, sleep_ms=50, topic="policy_events"):
    """
    Run as local producer.
    In production: connects to real Kafka broker.
    Here: writes to JSONL file (same data, no broker needed for dev).
    """
    output_file = "data/processed/policy_events_stream.jsonl"
    os.makedirs("data/processed", exist_ok=True)

    print(f"Producing {n_events} policy events → {output_file}")
    print(f"Topic (production): {topic}")
    print("-" * 50)

    stats = {"new_policy": 0, "lapse": 0, "renewal": 0}
    high_risk = 0

    with open(output_file, "w") as f:
        for i in range(n_events):
            # Event type distribution: 60% new, 30% renewal, 10% lapse
            etype = random.choices(
                ["new_policy", "renewal", "lapse"],
                weights=[0.60, 0.30, 0.10]
            )[0]

            event = generate_event(etype)
            f.write(json.dumps(event) + "\n")
            stats[etype] += 1
            if event["lapse_risk_tier"] == "HIGH":
                high_risk += 1

            if (i + 1) % 20 == 0:
                print(f"  Produced {i+1}/{n_events} events...")

            time.sleep(sleep_ms / 1000)

    print("\n── Event summary ────────────────────────────────────")
    for etype, count in stats.items():
        print(f"  {etype:<15}: {count:>5}")
    print(f"  High risk flagged : {high_risk:>5} ({high_risk/n_events*100:.1f}%)")
    print(f"\n✅ Stream written to: {output_file}")
    return output_file

import os
if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    run_producer(n_events=500, sleep_ms=0)
