"""数据分析与概率计算 - 收集完问卷后运行"""
import pandas as pd
import os
import json
from db_utils import get_connection

OUTPUT_DIR = "results"

PATH_MAPPING = {
    "A-A-A-A": [2, 3, 10],
    "A-A-A-B": [1, 14, 4],
    "A-A-B-A": [9, 7],
    "A-A-B-B": [8, 6],
    "A-B-A-A": [1, 14],
    "A-B-A-B": [4, 13],
    "A-B-B-A": [11, 12],
    "A-B-B-B": [5, 15, 6],
    "B-A-A-A": [16, 17],
    "B-A-A-B": [16, 29, 17],
    "B-A-B-A": [19, 20, 28, 30],
    "B-A-B-B": [21, 22],
    "B-B-A-A": [18, 24],
    "B-B-A-B": [23, 26],
    "B-B-B-A": [25, 23],
    "B-B-B-B": [27],
}


def load_data():
    conn = get_connection()
    responses = pd.read_sql("SELECT * FROM responses", conn)
    items = pd.read_sql("SELECT * FROM items", conn)
    conn.close()
    return responses, items


def map_judgment(row):
    j1 = "是" if row["q1"] == "B" else "否"
    if row["q1"] == "A":
        j2 = "是" if row["q2"] == "B" else "否"
    else:
        path = row["path_code"]
        high_energy_far = ["B-A-A-B", "B-B-B-B", "B-B-B-A", "B-B-A-B"]
        j2 = "是" if path in high_energy_far else "否"
    return pd.Series({"j1": j1, "j2": j2})


def compute_probabilities(responses, items):
    N = len(responses)
    print(f"\n总问卷数: {N}")

    judgments = responses.apply(map_judgment, axis=1)
    responses = pd.concat([responses, judgments], axis=1)

    responses["mapped_items"] = responses["path_code"].apply(
        lambda p: PATH_MAPPING.get(p, [])
    )

    results = {}

    # 1. 四类用户的分布 P(J1, J2)
    print("\n" + "=" * 50)
    print("1. 四类用户分布 P(J1, J2)")
    print("=" * 50)

    quadrants = responses.groupby(["j1", "j2"]).size()
    for (j1, j2), count in quadrants.items():
        prob = count / N
        label = f"J1={j1}, J2={j2}"
        print(f"  {label}: {count}/{N} = {prob:.4f}")
        results[f"P(J1={j1},J2={j2})"] = prob

    # 2. 每个项目的先验概率（拉普拉斯平滑）
    print("\n" + "=" * 50)
    print("2. 项目先验概率 P(项目_i)")
    print("=" * 50)

    item_counts = {}
    for _, row in responses.iterrows():
        for item_id in row["mapped_items"]:
            item_counts[item_id] = item_counts.get(item_id, 0) + 1

    item_priors = {}
    for i in range(1, 31):
        n_i = item_counts.get(i, 0)
        prior = (n_i + 1) / (N + 30)
        item_priors[i] = prior

    items_df = items.set_index("item_id")
    for item_id in sorted(item_priors.keys()):
        name = items_df.loc[item_id, "name"]
        raw = item_counts.get(item_id, 0)
        print(f"  项目{item_id:2d} ({name}): "
              f"原始={raw}/{N}, 平滑后={item_priors[item_id]:.4f}")

    # 3. 条件概率 P(J1,J2 | 项目_i)
    print("\n" + "=" * 50)
    print("3. 条件概率 P(J1,J2 | 项目_i)")
    print("=" * 50)

    cond_probs = {}
    for item_id in range(1, 31):
        cond_probs[item_id] = {}
        n_i = item_counts.get(item_id, 0)
        for j1_val in ["是", "否"]:
            for j2_val in ["是", "否"]:
                mask = (responses["j1"] == j1_val) & (responses["j2"] == j2_val)
                subset = responses[mask]
                n_ij = sum(
                    1 for _, row in subset.iterrows()
                    if item_id in row["mapped_items"]
                )
                prob = (n_ij + 1) / (n_i + 4)
                cond_probs[item_id][(j1_val, j2_val)] = prob

    # 4. 后验概率 P(项目_i | J1, J2)
    print("\n" + "=" * 50)
    print("4. 后验概率 P(项目_i | J1, J2) —— 推荐结果")
    print("=" * 50)

    recommendations = {}
    for j1_val in ["是", "否"]:
        for j2_val in ["是", "否"]:
            scores = {}
            for item_id in range(1, 31):
                prior = item_priors[item_id]
                likelihood = cond_probs[item_id][(j1_val, j2_val)]
                scores[item_id] = prior * likelihood

            total = sum(scores.values())
            posteriors = {k: v / total for k, v in scores.items()}

            sorted_items = sorted(posteriors.items(),
                                  key=lambda x: x[1], reverse=True)

            key = f"J1={j1_val},J2={j2_val}"
            recommendations[key] = sorted_items
            best_id, best_prob = sorted_items[0]
            best_name = items_df.loc[best_id, "name"]

            print(f"\n  [{key}] 最优推荐: {best_name} "
                  f"(概率={best_prob:.4f})")
            print(f"  Top 5:")
            for rank, (iid, prob) in enumerate(sorted_items[:5], 1):
                name = items_df.loc[iid, "name"]
                print(f"    {rank}. {name}: {prob:.4f}")

            results[f"recommend_{key}"] = {
                items_df.loc[iid, "name"]: round(prob, 4)
                for iid, prob in sorted_items
            }

    # 5. 总体点击概率估算
    print("\n" + "=" * 50)
    print("5. 总体推荐成功概率估算")
    print("=" * 50)

    total_click_prob = 0
    for j1_val in ["是", "否"]:
        for j2_val in ["是", "否"]:
            key = f"J1={j1_val},J2={j2_val}"
            p_quadrant = results.get(f"P({key})", 0)
            best_prob = recommendations[key][0][1]
            contribution = p_quadrant * best_prob
            total_click_prob += contribution
            print(f"  {key}: P(象限)={p_quadrant:.4f} × "
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
