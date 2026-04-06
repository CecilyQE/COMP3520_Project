import os
import json
import glob

base_dir = r"C:\Users\吴彦祖\Desktop\comp3520\artifacts\full_experiments"
print("| 模型 (Model) | 样本量 (Samples) | 未识别项 (Unresolved) | R1 Cross JSD | R1 Cross Top1 | R1 Human EN JSD | R1 Human ZH JSD |")
print("|---|---|---|---|---|---|---|")

results = []

for root, dirs, files in os.walk(base_dir):
    if "run_manifest.json" in files:
        manifest_path = os.path.join(root, "run_manifest.json")
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                run_id = manifest.get('run_id', 'unknown')
        except:
            continue
            
        metrics_path = os.path.join(root, "summary_metrics.json")
        cross_jsd, cross_top1, human_en, human_zh = "N/A", "N/A", "N/A", "N/A"
        if os.path.exists(metrics_path):
            try:
                with open(metrics_path, 'r', encoding='utf-8') as f:
                    metrics_list = json.load(f)
            except:
                metrics_list = []
                
            if metrics_list and isinstance(metrics_list, list):
                for m in metrics_list:
                    if m.get('metric_family') == 'cross_lingual' and m.get('round_index') == 1:
                        val_jsd = m.get('mean_jsd')
                        val_top1 = m.get('mean_top1_match')
                        cross_jsd = f"{val_jsd:.4f}" if isinstance(val_jsd, (float, int)) else val_jsd
                        cross_top1 = f"{val_top1:.4f}" if isinstance(val_top1, (float, int)) else val_top1
                    if m.get('metric_family') == 'human_alignment' and m.get('round_index') == 1:
                        lang = m.get('prompt_language')
                        val_jsd = m.get('mean_jsd')
                        if lang in ('English', 'en'):
                            human_en = f"{val_jsd:.4f}" if isinstance(val_jsd, (float, int)) else val_jsd
                        elif lang == 'zh':
                            human_zh = f"{val_jsd:.4f}" if isinstance(val_jsd, (float, int)) else val_jsd

        raw_gens_path = os.path.join(root, "raw_generations.jsonl")
        model = "unknown"
        if os.path.exists(raw_gens_path):
            with open(raw_gens_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                if first_line:
                    try:
                        model = json.loads(first_line).get('model', 'unknown')
                    except:
                        pass
        
        raw_count = manifest.get('raw_record_count', 0)
        unresolved = manifest.get('unresolved_count', 0)
        # Avoid duplicate printing if we have multiple runs for same model, just collect them
        results.append((model, raw_count, unresolved, cross_jsd, cross_top1, human_en, human_zh))

# Sort by R1 Cross JSD or Top1 if available
def sort_key(x):
    jsd = x[3]
    try:
        return float(jsd)
    except:
        return 999.0

results.sort(key=sort_key)

seen = set()
for r in results:
    model_name = r[0]
    # To keep it informative, we can just print all or distinct ones
    print(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} |")
