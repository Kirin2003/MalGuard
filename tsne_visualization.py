import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import BASE_START_MONTH, BASE_END_MONTH
from utils.month_utils import generate_month_range

# 四个时间段
# 1. 基础月份范围
# 2. 2023-11
# 3. 2023-12
# 4. 2024-01
base_months = generate_month_range(BASE_START_MONTH, BASE_END_MONTH)
periods = {
    f'{BASE_START_MONTH}~{BASE_END_MONTH}': base_months,
    # '2023-11': ['2023-11'],
    '2023-12': ['2023-12'],
    '2024-01': ['2024-01'],
}

DATA_DIR = '/Data2/hxq/MalGuard/fea_ex/dataset'
# COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # 蓝、橙、绿、红
COLORS = ['#1f77b4',  '#2ca02c', '#d62728'] 

def load_features(months):
    """加载某时间段的恶意包特征"""
    all_features = []
    for month in months:
        mal_file = os.path.join(DATA_DIR, f'malware_features_{month}.txt')
        with open(mal_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                features = [float(x) for x in parts[1:]]  # 跳过ID
                all_features.append(features)
    return np.array(all_features)

# 加载所有数据
X_list = []
for period_name in periods:
    X = load_features(periods[period_name])
    X_list.append(X)
    print(f"{period_name}: {X.shape[0]} 恶意样本")

# 合并
X_all = np.vstack(X_list)
period_labels = np.concatenate([
    np.full(len(X_list[i]), i) for i in range(len(X_list))
])
print(f"\n总样本数: {X_all.shape[0]}, 特征维度: {X_all.shape[1]}")

# t-SNE 降维到 2D
for perplexity in range(5, 51, 5):
    print(f"\n正在运行 t-SNE (perplexity={perplexity})...")
    tsne = TSNE(
        n_components=2,
        perplexity=perplexity,
        learning_rate=200,
        n_iter=1000,
        random_state=42,
        init='pca'
    )
    X_tsne = tsne.fit_transform(X_all)
    print("t-SNE 完成!")

    # 绘图
    plt.figure(figsize=(12, 9))
    for i, (period_name, color) in enumerate(zip(periods.keys(), COLORS)):
        mask = period_labels == i
        plt.scatter(X_tsne[mask, 0], X_tsne[mask, 1],
                    c=color, s=15, alpha=0.7, label=period_name)

    plt.xlabel('t-SNE Dimension 1')
    plt.ylabel('t-SNE Dimension 2')
    plt.legend(loc='best', fontsize=10)
    plt.title(f't-SNE Visualization of Malware Package Features (perplexity={perplexity})')
    plt.tight_layout()
    plt.savefig(f'/Data2/hxq/MalGuard/tsne_result_perplexity{perplexity}.png', dpi=150)
    # plt.savefig(f'/Data2/hxq/MalGuard/tsne_result_perplexity{perplexity}.pdf')
    print(f"图片已保存: tsne_result_perplexity{perplexity}.png")

print("\n所有图片已保存完成!")