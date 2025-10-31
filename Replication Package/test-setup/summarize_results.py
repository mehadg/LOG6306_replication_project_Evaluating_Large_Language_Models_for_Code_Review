import json, pathlib, math, collections

def load_jsonl(p):
    rows=[]
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def summarize(path):
    rows = load_jsonl(path)
    n = len(rows)
    correct = sum(1 for r in rows if r.get("score", -2.0) == 1.0)
    unusable = sum(1 for r in rows if r.get("score", -2.0) == -1.0)
    avg_score = sum(0 if r["score"] in (-1.0, None) else r["score"] for r in rows)/max(1, n - unusable)
    # correction/regression need prev_score/prev_label fields the script wrote
    corr = sum(1 for r in rows if r.get("prev_label") == "Incorrect" and r.get("label_after_exc") == "Correct")
    reg  = sum(1 for r in rows if r.get("prev_label") == "Correct" and r.get("label_after_exc") == "Incorrect")
    return {
        "items": n,
        "accuracy_%": round(100*correct/max(1,n),1),
        "invalid_%":  round(100*unusable/max(1,n),1),
        "avg_score_valid_only": round(100*avg_score,1),
        "correction_%": round(100*corr/max(1,n),1),
        "regression_%": round(100*reg/max(1,n),1),
    }

base = pathlib.Path("results")
for p in sorted(base.glob("*.jsonl")):
    print(p.name, summarize(p))
