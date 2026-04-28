"""数据分析与概率计算 - 收集完问卷后运行"""
import pandas as pd
import os
import json
from db_utils import get_connection

OUTPUT_DIR = "results"

PATH_MAPPING = {
    "A-A-A-A": [2, 3, 10], "A-A-A-B": [1, 14, 4],
    "A-A-B-A": [9, 7], "A-A-B-B": [8, 6],
    "A-B-A-A": [1, 14], "A-B-A-B": [4, 13],
    "A-B-B-A": [11, 12], "A-B-B-B": [5, 15, 6],
    "B-A-A-A": [19, 20], "B-A-A-B": [28, 30],
    "B-A-B-A": [17, 29], "B-A-B-B": [21, 22],
    "B-B-A-A": [18, 24], "B-B-A-B": [23, 26],
    "B-B-B-A": [25, 23], "B-B-B-B": [16, 27],
}

QUADRANT_MAP = {
    ("否", "否"): "A-A",
    ("否", "是"): "A-B",
    ("是", "否"): "B-A",
    ("是", "是"): "B-B",
}


def load_data():
    conn = get_connection()
    responses = pd.read_sql("SELECT * FROM responses", conn)
    items = pd.read_sql("SELECT * FROM items", conn)
    conn.close()
    return responses, items


def item_weights_in_path(path_code):
    item_ids = PATH_MAPPING[path_code]
    raw = {iid: 1.0 / (rank + 1) for rank, iid in enumerate(item_ids)}
    total = sum(raw.values())
    return {iid: w / total for iid, w in raw.items()}


def compute_probabilities(responses, items):
    N = len(responses)
    print(f"\n总问卷数: {N}")
    items_df = items.set_index("item_id")
    results = {}

    # 1. 路径先验 P(path)（拉普拉斯平滑）
    print("\n" + "=" * 50)
    print("1. 路径先验概率 P(path)")
    print("=" * 50)

    path_counts = responses["path_code"].value_counts().to_dict()
    path_priors = {}
    for p in PATH_MAPPING:
        cnt = path_counts.get(p, 0)
        path_priors[p] = (cnt + 1) / (N + 16)
        print(f"  {p}: {cnt}/{N} -> 平滑后 {path_priors[p]:.4f}")

    # 2. 四象限分布
    print("\n" + "=" * 50)
    print("2. 四象限用户分布")
    print("=" * 50)

    for (j1, j2), prefix in QUADRANT_MAP.items():
        cnt = sum(1 for _, r in responses.iterrows()
                  if r["path_code"].startswith(prefix))
        prob = cnt / N if N > 0 else 0
        label = f"J1={j1},J2={j2}"
        print(f"  {label}: {cnt}/{N} = {prob:.4f}")
        results[f"P({label})"] = prob

    # 3. 推荐概率 P(item | J1, J2)
    print("\n" + "=" * 50)
    print("3. 推荐结果 P(item | J1, J2)")
    print("=" * 50)

    recommendations = {}
    for (j1, j2), prefix in QUADRANT_MAP.items():
        matching = [p for p in PATH_MAPPING if p.startswith(prefix)]
        total_prior = sum(path_priors[p] for p in matching)
        path_conds = {p: path_priors[p] / total_prior for p in matching}

        item_scores = {}
        for p in matching:
            iw = item_weights_in_path(p)
            for iid, weight in iw.items():
                item_scores[iid] = item_scores.get(iid, 0.0) + path_conds[p] * weight

        sorted_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)
        key = f"J1={j1},J2={j2}"
        recommendations[key] = sorted_items

        best_id, best_prob = sorted_items[0]
        best_name = items_df.loc[best_id, "name"]
        print(f"\n  [{key}] 最优推荐: {best_name} (概率={best_prob:.4f})")
        print(f"  Top 5:")
        for rank, (iid, prob) in enumerate(sorted_items[:5], 1):
            name = items_df.loc[iid, "name"]
            print(f"    {rank}. {name}: {prob:.4f}")

        results[f"recommend_{key}"] = {
            items_df.loc[iid, "name"]: round(prob, 4)
            for iid, prob in sorted_items
        }

    # 4. 总体命中概率
    print("\n" + "=" * 50)
    print("4. 总体推荐命中概率估算")
    print("=" * 50)

    total_click_prob = 0
    for (j1, j2), prefix in QUADRANT_MAP.items():
        key = f"J1={j1},J2={j2}"
        p_quadrant = results.get(f"P({key})", 0)
        best_prob = recommendations[key][0][1]
        contribution = p_quadrant * best_prob
        total_click_prob += contribution
        print(f"  {key}: P(象限)={p_quadrant:.4f} x "
              f"P(最优|象限)={best_prob:.4f} = {contribution:.4f}")

    print(f"\n  总体最优推荐命中概率: {total_click_prob:.4f}")
    results["total_click_prob"] = total_click_prob

    return results, recommendations


def save_results(results, recommendations, items):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    serializable = {}
    for k, v in results.items():
        if isinstance(v, dict):
            serializable[k] = v
        else:
            serializable[k] = float(v)
    with open(f"{OUTPUT_DIR}/probabilities.json", "w",
              encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存到 {OUTPUT_DIR}/probabilities.json")


def main():
    print("=" * 60)
    print("  推荐系统冷启动 —— 数据分析与概率计算")
    print("=" * 60)

    responses, items = load_data()

    if len(responses) == 0:
        print("\n⚠️  数据库中没有问卷数据！请先收集数据。")
        return

    results, recommendations = compute_probabilities(responses, items)
    save_results(results, recommendations, items)

    print("\n" + "=" * 60)
    print("  分析完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
