import pandas as pd
import os

def generate_html(csv_path, plan, output_path="output/dashboard.html"):
    df = pd.read_csv(csv_path)

    # Aggregate per model
    summary = df.groupby("model").agg(
        avg_latency=("latency_ms", "mean"),
        json_success=("json_valid", lambda x: (x=="✓").mean()*100)
    ).reset_index()
    summary["avg_latency"] = summary["avg_latency"].round(0)
    summary["json_success"] = summary["json_success"].round(1)

    # Find winner (highest json_success, then lowest latency)
    best = summary.sort_values(
        ["json_success", "avg_latency"],
        ascending=[False, True]
    ).iloc[0]

    recommendation = (
        f"Use {best['model']} — {best['json_success']}% JSON "
        f"success at {best['avg_latency']:.0f}ms average latency."
    )

    models_json   = summary["model"].tolist()
    latency_json  = summary["avg_latency"].tolist()
    success_json  = summary["json_success"].tolist()

    task_type = plan.get('task_type', '').title()
    
    html = f"""<!DOCTYPE html>
<html><head>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body{{background:#0D0D1A;color:#F1F5F9;font-family:sans-serif;
     padding:2rem;max-width:700px;margin:0 auto}}
h1{{color:#CBA6F7;font-size:1.3rem}}
.rec{{background:#0F2A22;border:1px solid #1A4A32;border-radius:10px;
     padding:1rem;color:#6EE7C0;margin:1rem 0}}
.chart-box{{background:#13132B;border:1px solid #2A2A4A;border-radius:10px;
     padding:1rem;margin-bottom:1rem}}
</style></head>
<body>
<h1>{task_type} Benchmark</h1>
<div class="rec">▶ {recommendation}</div>
<div class="chart-box"><canvas id="successChart"></canvas></div>
<div class="chart-box"><canvas id="latencyChart"></canvas></div>
<script>
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