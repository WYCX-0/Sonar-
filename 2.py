import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

# ===================== 1. 定义项目任务 =====================
tasks = {
    1: {"name": "开始", "duration": 0, "pre": []},
    2: {"name": "硬件选择A", "duration": 6, "pre": [1]},
    3: {"name": "软件配置B", "duration": 4, "pre": [1]},
    4: {"name": "安装硬件C", "duration": 3, "pre": [2]},
    5: {"name": "数据迁移D", "duration": 4, "pre": [4]},
    6: {"name": "草拟办公规程E", "duration": 3, "pre": [3]},
    7: {"name": "招聘员工F", "duration": 10, "pre": [1]},
    8: {"name": "用户培训G", "duration": 3, "pre": [6, 7]},
    9: {"name": "安装和测试H", "duration": 2, "pre": [4, 5]},
    10: {"name": "结束", "duration": 0, "pre": [8, 9]},
}

# ===================== 2. 构建图结构 =====================
def build_graph(tasks):
    G = nx.DiGraph()
    for n in tasks:
        G.add_node(n)
        for pre in tasks[n]["pre"]:
            G.add_edge(pre, n)
    return G

# ===================== 3. 计算最早开始/完成时间（正推） =====================
def compute_early_times(tasks):
    early_start = defaultdict(int)
    early_finish = defaultdict(int)
    topo_order = list(nx.topological_sort(build_graph(tasks)))

    for node in topo_order:
        es = 0
        for pre in tasks[node]["pre"]:
            es = max(es, early_finish[pre])
        early_start[node] = es
        early_finish[node] = es + tasks[node]["duration"]
    return early_start, early_finish

# ===================== 4. 计算最晚开始/完成时间（反推） =====================
def compute_late_times(tasks, early_finish):
    late_start = defaultdict(int)
    late_finish = defaultdict(int)
    topo_order = reversed(list(nx.topological_sort(build_graph(tasks))))
    project_end = early_finish[10]

    for node in topo_order:
        successors = [n for n in tasks if node in tasks[n]["pre"]]
        if not successors:
            lf = project_end
        else:
            lf = min(late_start[suc] for suc in successors)
        late_finish[node] = lf
        late_start[node] = lf - tasks[node]["duration"]
    return late_start, late_finish

# ===================== 5. 计算关键路径 =====================
def get_critical_path(tasks, es, ls):
    critical = []
    for n in tasks:
        if abs(es[n] - ls[n]) < 1e-9:
            critical.append(n)
    return critical

# ===================== 执行计算 =====================
G = build_graph(tasks)
es, ef = compute_early_times(tasks)
ls, lf = compute_late_times(tasks, ef)
critical = get_critical_path(tasks, es, ls)

# ===================== 输出结果 =====================
print("=" * 60)
print("【项目关键路径】")
path_names = [tasks[n]["name"] for n in critical]
print(" → ".join(path_names))
print(f"【项目总工期】: {ef[10]} 周")
print("=" * 60)

print("\n【任务详细信息】")
for n in sorted(tasks):
    t = tasks[n]
    status = "★ 关键任务" if n in critical else "  非关键任务"
    print(f"任务{n:2} | {t['name']:12} | 工期:{t['duration']:2} | ES:{es[n]:2} EF:{ef[n]:2} LS:{ls[n]:2} LF:{lf[n]:2} | {status}")

# ===================== 6. 绘制网络图 =====================
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 解决中文显示
plt.figure(figsize=(12, 8))

# 手动布局，让图更好看
pos = {
    1: (0, 4),
    2: (2, 6), 3: (2, 4), 7: (2, 2),
    4: (4, 6), 6: (4, 4),
    5: (6, 6), 8: (6, 3), 9: (6, 5),
    10: (8, 4)
}

# 节点颜色：关键=红色，非关键=蓝色
node_colors = ["red" if n in critical else "lightblue" for n in G.nodes]

# 画图
nx.draw(G, pos, node_color=node_colors, node_size=2500, font_size=11, font_weight="bold")
nx.draw_networkx_labels(G, pos, labels={n: tasks[n]["name"] for n in G.nodes})

plt.title("项目网络图（红色 = 关键路径）", fontsize=16)
plt.axis("off")
plt.tight_layout()
plt.show()