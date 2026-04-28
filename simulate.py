"""模拟改进算法的完整运行过程，生成 Markdown 报告"""
import random

random.seed(42)

ITEM_NAMES = {
    1: "东湖绿道（磨山段）骑行", 2: "东湖落雁景区散步", 3: "华科校内喻家湖环湖",
    4: "华科森林公园徒步", 5: "光谷步行街逛街", 6: "光谷天地探店",
    7: "K11购物艺术中心", 8: "关山大道咖啡馆", 9: "光谷书房/独立书店",
    10: "藏龙岛湿地公园", 11: "光谷周边密室逃脱", 12: "光谷周边剧本杀",
    13: "光谷国际网球中心", 14: "花山生态城绿道骑行", 15: "鲁巷广场/光谷广场聚餐",
    16: "黄鹤楼", 17: "昙华林文艺街区", 18: "粮道街美食探店",
    19: "汉口江滩散步", 20: "武昌江滩/长江大桥", 21: "湖北省博物馆",
    22: "武汉美术馆", 23: "楚河汉街", 24: "万松园美食街",
    25: "江汉路步行街", 26: "武汉天地", 27: "武汉欢乐谷",
    28: "东湖樱花园", 29: "武汉大学（建筑/樱花）", 30: "龟山公园/汉阳江滩",
}

PATH_MAPPING = {
    "A-A-A-A-A": [3], "A-A-A-A-B": [2, 10],
    "A-A-A-B-A": [14], "A-A-A-B-B": [1, 4],
    "A-A-B-A-A": [9], "A-A-B-A-B": [7],
    "A-A-B-B-A": [8], "A-A-B-B-B": [6],
    "A-B-A-A-A": [14], "A-B-A-A-B": [1],
    "A-B-A-B-A": [4, 13], "A-B-A-B-B": [13, 4],
    "A-B-B-A-A": [12, 11], "A-B-B-A-B": [11, 12],
    "A-B-B-B-A": [5, 6, 15], "A-B-B-B-B": [15, 6, 5],
    "B-A-A-A-A": [20], "B-A-A-A-B": [19],
    "B-A-A-B-A": [28], "B-A-A-B-B": [30],
    "B-A-B-A-A": [17], "B-A-B-A-B": [29],
    "B-A-B-B-A": [22], "B-A-B-B-B": [21],
    "B-B-A-A-A": [18, 24], "B-B-A-A-B": [24, 18],
    "B-B-A-B-A": [23], "B-B-A-B-B": [26],
    "B-B-B-A-A": [25, 23], "B-B-B-A-B": [23, 25],
    "B-B-B-B-A": [16], "B-B-B-B-B": [27],
}

QUADRANT_MAP = {
    ("否", "否"): "A-A", ("否", "是"): "A-B",
    ("是", "否"): "B-A", ("是", "是"): "B-B",
}

PATH_WEIGHTS = {
    "A-A-A-A-A": 3, "A-A-A-A-B": 2, "A-A-A-B-A": 2, "A-A-A-B-B": 1,
    "A-A-B-A-A": 3, "A-A-B-A-B": 2, "A-A-B-B-A": 2, "A-A-B-B-B": 1,
    "A-B-A-A-A": 3, "A-B-A-A-B": 1, "A-B-A-B-A": 1, "A-B-A-B-B": 1,
    "A-B-B-A-A": 2, "A-B-B-A-B": 2, "A-B-B-B-A": 3, "A-B-B-B-B": 2,
    "B-A-A-A-A": 2, "B-A-A-A-B": 1, "B-A-A-B-A": 2, "B-A-A-B-B": 1,
    "B-A-B-A-A": 3, "B-A-B-A-B": 1, "B-A-B-B-A": 2, "B-A-B-B-B": 1,
    "B-B-A-A-A": 2, "B-B-A-A-B": 1, "B-B-A-B-A": 1, "B-B-A-B-B": 1,
    "B-B-B-A-A": 2, "B-B-B-A-B": 1, "B-B-B-B-A": 2, "B-B-B-B-B": 1,
}

all_paths = list(PATH_WEIGHTS.keys())
weights = [PATH_WEIGHTS[p] for p in all_paths]
total_w = sum(weights)
probs = [w / total_w for w in weights]
N = 50
survey_data = random.choices(all_paths, weights=probs, k=N)

lines = []
def w(text=""):
    lines.append(text)

w("# 改进算法模拟运行报告")
w()
w("## 0. 问题背景")
w()
w("我们的推荐系统分两个阶段：")
w("1. **数据收集阶段**：让50名同学填写5道动态选择题，每人产生一个 path_code（如 `A-B-A-B-A`）")
w("2. **推荐阶段**：一个全新用户只回答2道判断题（J1=距离、J2=体力），系统推荐一个景点")
w()
w('**核心难点**：填问卷的人和用推荐的人是不同的人。我们没有"某人回答J1/J2后去了哪个景点"的数据。')
w("所以不能直接统计 P(景点 | J1, J2)。")
w()
w("**解决思路**：利用决策树的结构特性——path_code 的前两位天然编码了 J1 和 J2 的信息：")
w("- 第1位（Q1）：A=近、B=远 → 对应 J1（距离）")
w("- 第2位（Q2）：A=想放松、B=精力充沛 → 对应 J2（体力）")
w()
w('**关键改动**：原设计中 Q1=B（远）后的 Q2 问的是"核心目的（文化风景 vs 吃喝玩乐）"，')
w('这与 J2（体力）的含义不匹配。改进后，无论近远，Q2 统一问"精力状态"，')
w("使得 path_code 前两位与 J1、J2 严格对应。")
w()
w("| J1(远?) | J2(体力?) | 匹配的路径前缀 | 含义 |")
w("|---------|-----------|---------------|------|")
w("| 否 | 否 | A-A-\\*-\\*-\\* | 近+放松 |")
w("| 否 | 是 | A-B-\\*-\\*-\\* | 近+活跃 |")
w("| 是 | 否 | B-A-\\*-\\*-\\* | 远+放松 |")
w("| 是 | 是 | B-B-\\*-\\*-\\* | 远+活跃 |")
w()
w("### 改动后的远距离问卷分支")
w()
w("**Q2（Q1=B 时）**：今天的精力状态如何？")
w("- A. 想放松（散步、看展、拍照）")
w("- B. 精力充沛（爬山、逛街、找美食、游乐场）")
w()
w("**Q3（B-A 远+放松）**：更想看什么？")
w("- A. 自然风景（江滩、花园、公园）→ Q5区分时间")
w("- B. 文化艺术（老街、校园、博物馆）→ Q5区分时间")
w()
w("**Q3（B-B 远+活跃）**：今天的重点是？")
w("- A. 美食探店 → Q5区分预算")
w("- B. 逛街/观光/游乐 → Q5区分预算")
w()
w("**Q4（B-A-A）**：想去哪个方向？ A.江边 B.湖边/山边 → Q5: A半天/B一整天")
w("**Q4（B-A-B）**：更偏向？ A.历史建筑 B.艺术展览 → Q5: A半天/B一整天")
w("**Q4（B-B-A）**：想吃什么风格？ A.街头小吃 B.商圈餐厅 → Q5: A免费低/B可以花")
w("**Q4（B-B-B）**：更想去？ A.逛街购物 B.观光/游乐 → Q5: A免费低/B可以花")
w()
w("---")
w()

# === Step 1: 路径先验 ===
w("## Step 1：统计路径先验概率 P(path)")
w()
w("**含义**：从50份问卷中，统计每条路径被走过多少次。这反映了华科学生群体的真实偏好分布。")
w()
w("**为什么需要**：这是唯一来自真实数据的概率。路径被走得越多，说明这类偏好越普遍，推荐权重越高。")
w()
w("**拉普拉斯平滑**：给每条路径加1次虚拟计数，避免概率为0：")
w()
w("$$P(\\text{path}) = \\frac{\\text{该path出现次数} + 1}{\\text{总问卷数} + 32}$$")
w()

path_counts = {}
for p in all_paths:
    path_counts[p] = 0
for p in survey_data:
    path_counts[p] += 1

path_priors = {}
for p in all_paths:
    path_priors[p] = (path_counts[p] + 1) / (N + 32)

w("### 模拟数据（50份问卷的路径分布）")
w()
w("| 路径 | 原始次数 | 平滑后 P(path) |")
w("|------|---------|---------------|")
for p in all_paths:
    w(f"| {p} | {path_counts[p]} | {path_priors[p]:.4f} |")
w()
w(f"总计：{N} 份问卷，32 条路径，平滑后概率之和 = {sum(path_priors.values()):.4f}")
w()
w("---")
w()

# === Step 2: 条件概率 ===
w("## Step 2：给定 (J1, J2)，筛选匹配路径并归一化")
w()
w("**含义**：用户回答J1和J2后，锁定8条匹配路径，将先验概率归一化为条件概率。")
w()
w("**为什么这样做**：J1和J2把32条路径筛到8条，8条之间的权重比完全由问卷数据决定。")
w()
w("$$P(\\text{path} \\mid J_1, J_2) = \\frac{P(\\text{path})}{\\sum_{\\text{匹配的8条path}} P(\\text{path})}$$")
w()

for (j1, j2), prefix in QUADRANT_MAP.items():
    q_near = "近" if j1 == "否" else "远"
    q_energy = "低体力" if j2 == "否" else "高体力"
    w(f"### 象限：J1={j1}（{q_near}），J2={j2}（{q_energy}）")
    w()
    matching = [p for p in all_paths if p.startswith(prefix)]
    total = sum(path_priors[p] for p in matching)
    w("| 匹配路径 | P(path) | P(path \\| J1,J2) | 推荐项目 |")
    w("|---------|---------|-----------------|---------|")
    for p in matching:
        cond = path_priors[p] / total
        items_str = ", ".join(ITEM_NAMES[i] for i in PATH_MAPPING[p])
        w(f"| {p} | {path_priors[p]:.4f} | {cond:.4f} | {items_str} |")
    w()

w("---")
w()

# === Step 3: 项目概率 ===
w("## Step 3：计算每个景点的推荐概率 P(item | J1, J2)")
w()
w('**含义**：把路径级别的概率"传递"到景点级别。路径概率越高，其中的景点被推荐的概率越高。')
w()
w("**优先级加权**：同一路径中排在前面的景点权重更高（用 1/排名 衰减）：")
w()
w("$$P(\\text{item}_i \\mid \\text{path}) = \\frac{w_i}{\\sum_j w_j}, \\quad w_j = \\frac{1}{\\text{rank}_j}$$")
w()
w("**最终公式**：")
w()
w("$$P(\\text{item}_i \\mid J_1, J_2) = \\sum_{\\text{path}} P(\\text{path} \\mid J_1, J_2) \\times P(\\text{item}_i \\mid \\text{path})$$")
w()

def item_weights_in_path(path_code):
    items = PATH_MAPPING[path_code]
    raw = {iid: 1.0 / (rank + 1) for rank, iid in enumerate(items)}
    total = sum(raw.values())
    return {iid: wt / total for iid, wt in raw.items()}

final_results = {}

for (j1, j2), prefix in QUADRANT_MAP.items():
    matching = [p for p in all_paths if p.startswith(prefix)]
    total_prior = sum(path_priors[p] for p in matching)
    path_conds = {p: path_priors[p] / total_prior for p in matching}

    item_scores = {}
    for p in matching:
        iw = item_weights_in_path(p)
        for iid, weight in iw.items():
            item_scores[iid] = item_scores.get(iid, 0.0) + path_conds[p] * weight

    sorted_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)
    final_results[(j1, j2)] = sorted_items

    w(f"### 象限：J1={j1}, J2={j2}")
    w()
    best_id = sorted_items[0][0]
    w(f"以 **{ITEM_NAMES[best_id]}** 为例（排名第1）：")
    for p in matching:
        iw = item_weights_in_path(p)
        if best_id in iw:
            w(f"- P({p}|J1,J2) x P(item|{p}) = {path_conds[p]:.4f} x {iw[best_id]:.4f} = {path_conds[p]*iw[best_id]:.4f}")
    w(f"- 合计 = {sorted_items[0][1]:.4f}")
    w()
    w("| 排名 | 景点 | P(item \\| J1,J2) |")
    w("|------|------|-----------------|")
    for rank, (iid, prob) in enumerate(sorted_items, 1):
        w(f"| {rank} | {ITEM_NAMES[iid]} | {prob:.4f} |")
    w()

w("---")
w()

# === Step 4: 最终推荐 ===
w("## Step 4：最终推荐结果")
w()
w("| 用户回答 | 象限含义 | 推荐景点 | 推荐概率 |")
w("|---------|---------|---------|---------|")
for (j1, j2), sorted_items in final_results.items():
    best_id, best_prob = sorted_items[0]
    q_near = "远" if j1 == "是" else "近"
    q_energy = "高体力" if j2 == "是" else "低体力"
    w(f"| J1={j1}, J2={j2} | {q_near}+{q_energy} | {ITEM_NAMES[best_id]} | {best_prob:.4f} |")
w()

# === Step 5: 总体命中率 ===
w("## Step 5：总体推荐命中概率估算")
w()
w("$$P(\\text{hit}) = \\sum_{(J_1,J_2)} P(J_1,J_2) \\times P(\\text{best item} \\mid J_1,J_2)$$")
w()

quadrant_counts = {}
for p in survey_data:
    prefix = p[:3]
    for (j1, j2), pf in QUADRANT_MAP.items():
        if prefix == pf:
            quadrant_counts[(j1, j2)] = quadrant_counts.get((j1, j2), 0) + 1

total_hit = 0
w("| 象限 | 问卷人数 | P(象限) | 最优概率 | 贡献 |")
w("|------|---------|--------|---------|------|")
for (j1, j2), sorted_items in final_results.items():
    cnt = quadrant_counts.get((j1, j2), 0)
    p_quad = cnt / N
    best_prob = sorted_items[0][1]
    contrib = p_quad * best_prob
    total_hit += contrib
    w(f"| J1={j1},J2={j2} | {cnt} | {p_quad:.4f} | {best_prob:.4f} | {contrib:.4f} |")

w()
w(f"**总体推荐命中概率 = {total_hit:.4f} ({total_hit*100:.1f}%)**")
w()
w("---")
w()
w("## 算法优势总结")
w()
w("1. **数据来源合法**：只使用问卷中真实的 path_code 频率，不虚构任何标签")
w("2. **Q2统一为能量维度**：近和远分支的Q2都问精力状态，与J2严格对应")
w("3. **问卷数据真正起作用**：50份问卷决定了同一象限内8条路径的权重分配")
w("4. **优先级保留**：路径内的项目排序通过 1/rank 加权保留")
w("5. **可解释性强**：每一步计算都有明确的概率含义")

report = "\n".join(lines)
with open("模拟运行.md", "w", encoding="utf-8") as f:
    f.write(report)

print(f"报告已生成：模拟运行.md（{len(lines)} 行）")
print(f"\n最终推荐结果：")
for (j1, j2), sorted_items in final_results.items():
    best_id, best_prob = sorted_items[0]
    print(f"  J1={j1}, J2={j2} -> {ITEM_NAMES[best_id]} ({best_prob:.4f})")
