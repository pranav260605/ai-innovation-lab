import pandas as pd
import os
from consensus_checker import (
    build_consensus_table,
    calculate_model_agreement_rates,
    find_disagreement_cases
)


def generate_html(csv_path, plan, output_path="output/dashboard.html",
                   label_field="classification"):
    df = pd.read_csv(csv_path)

    # ── Speed + JSON success (existing) ─────────────────────────
    summary = df.groupby("model").agg(
        avg_latency=("latency_ms", "mean"),
        json_success=("json_valid", lambda x: (x == "✓").mean() * 100)
    ).reset_index()
    summary["avg_latency"] = summary["avg_latency"].round(0)
    summary["json_success"] = summary["json_success"].round(1)

    # ── NEW: Consensus / agreement rate (no ground truth needed) ─
    consensus_table = build_consensus_table(csv_path, label_field)
    agreement_rates = calculate_model_agreement_rates(consensus_table)
    disagreements   = find_disagreement_cases(consensus_table)

    # Merge agreement rate into summary
    summary = summary.merge(agreement_rates, on="model", how="left")
    summary["agreement_rate_pct"] = summary["agreement_rate_pct"].fillna(0)

    # ── Winner: now based on agreement rate first, then speed ────
    best = summary.sort_values(
        ["agreement_rate_pct", "avg_latency"],
        ascending=[False, True]
    ).iloc[0]

    recommendation = (
        f"Use {best['model']} — {best['agreement_rate_pct']}% consensus "
        f"agreement at {best['avg_latency']:.0f}ms average latency "
        f"({best['json_success']}% JSON success). "
        f"{len(disagreements)} of {len(consensus_table)} samples had "
        f"model disagreement — worth manual review."
    )

    models_json    = summary["model"].tolist()
    latency_json   = summary["avg_latency"].tolist()
    success_json   = summary["json_success"].tolist()
    agreement_json = summary["agreement_rate_pct"].tolist()

    html = f"""<!DOCTYPE html>
<html><head>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body{{background:#0D0D1A;color:#F1F5F9;font-family:sans-serif;
     padding:2rem;max-width:700px;margin:0 auto}}
h1{{color:#CBA6F7;font-size:1.3rem}}
.rec{{background:#0F2A22;border:1px solid #1A4A32;border-radius:10px;
     padding:1rem;color:#6EE7C0;margin:1rem 0;line-height:1.6}}
.chart-box{{background:#13132B;border:1px solid #2A2A4A;border-radius:10px;
     padding:1rem;margin-bottom:1rem}}
.note{{background:#2E2410;border:1px solid #854F0B;border-radius:10px;
      padding:.85rem 1rem;color:#FBBF24;font-size:.85rem;margin-bottom:1rem}}
</style></head>
<body>
<h1>{plan.get('task_type','').title()} Benchmark</h1>
<div class="rec">▶ {recommendation}</div>
<div class="note">
  ⚠ No ground truth labels used. "Agreement rate" measures how often
  each model's answer matched the majority vote across all 3 models —
  not necessarily the objectively correct answer.
</div>
<div class="chart-box"><canvas id="agreementChart"></canvas></div>
<div class="chart-box"><canvas id="successChart"></canvas></div>
<div class="chart-box"><canvas id="latencyChart"></canvas></div>
<script>
new Chart(document.getElementById('agreementChart'), {{
  type: 'bar',
  data: {{
    labels: {models_json},
    datasets: [{{label: 'Consensus Agreement %',
      data: {agreement_json}, backgroundColor: '#CBA6F7'}}]
  }},
  options: {{plugins:{{title:{{display:true,
    text:'Cross-Model Agreement Rate (no ground truth)',color:'#F1F5F9'}}}},
    scales:{{y:{{ticks:{{color:'#94A3B8'}}}},
    x:{{ticks:{{color:'#94A3B8'}}}}}}}}
}});
new Chart(document.getElementById('successChart'), {{
  type: 'bar',
  data: {{
    labels: {models_json},
    datasets: [{{label: 'JSON Success %',
      data: {success_json}, backgroundColor: '#534AB7'}}]
  }},
  options: {{plugins:{{title:{{display:true,
    text:'JSON Success Rate',color:'#F1F5F9'}}}},
    scales:{{y:{{ticks:{{color:'#94A3B8'}}}},
    x:{{ticks:{{color:'#94A3B8'}}}}}}}}
}});
new Chart(document.getElementById('latencyChart'), {{
  type: 'bar',
  data: {{
    labels: {models_json},
    datasets: [{{label: 'Avg Latency (ms)',
      data: {latency_json}, backgroundColor: '#10A37F'}}]
  }},
  options: {{plugins:{{title:{{display:true,
    text:'Average Latency',color:'#F1F5F9'}}}},
    scales:{{y:{{ticks:{{color:'#94A3B8'}}}},
    x:{{ticks:{{color:'#94A3B8'}}}}}}}}
}});
</script>
</body></html>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  📊 Dashboard saved → {output_path}")
    print(f"  📌 {recommendation}")
    return recommendation