import numpy as np
import json
import os
import joblib
from tqdm import tqdm

# 配置
model_path = "/Data2/hxq/MalGuard/model_training/models/multi_layer_perceptron/multi_layer_perceptron_model.pkl"
pack_dir = "/Data2/hxq/datasets/incremental_packages"
output_dir = "/Data2/hxq/MalGuard/model_training/misclassified_analysis"
os.makedirs(output_dir, exist_ok=True)

target_months = ["2023-08", "2024-02"]

# 加载 Random Forest 模型
print("加载 Random Forest 模型...")
model = joblib.load(model_path)

# 特征维度数量（根据数据文件确定）
n_features = 177  # 从数据文件看，最后一列是标签，所以特征是177个

for month in target_months:
    print(f"\n{'='*60}")
    print(f"分析 {month}...")
    print('='*60)

    misclassified_fp = []  # 假阳性：预测恶意，实际良性
    misclassified_fn = []  # 假阴性：预测良性，实际恶意

    # 处理恶意样本 (标签=1)
    mal_month_path = os.path.join(pack_dir, month, "malicious")
    if os.path.exists(mal_month_path):
        print(f"处理恶意样本目录: {mal_month_path}")
        for package_name in tqdm(os.listdir(mal_month_path), desc=f"  恶意包"):
            package_path = os.path.join(mal_month_path, package_name)
            if not os.path.isdir(package_path):
                continue

            feature_file = os.path.join(package_path, "closeness_feature_vector_0129.json")
            if not os.path.exists(feature_file):
                continue

            with open(feature_file, 'r') as f:
                feature_vector = json.load(f)

            # 直接使用 values，顺序与 combine.py 一致
            feature_list = list(feature_vector.values())
            X = np.array([feature_list])
            y_true = 1  # 恶意

            y_pred = model.predict(X)[0]

            if y_pred != y_true:
                misclassified_fn.append({
                    'package': package_name,
                    'predicted': int(y_pred),
                    'actual': y_true,
                    'features': feature_list
                })

    # 处理良性样本 (标签=0)
    ben_month_path = os.path.join(pack_dir, month, "benign")
    if os.path.exists(ben_month_path):
        print(f"处理良性样本目录: {ben_month_path}")
        for package_name in tqdm(os.listdir(ben_month_path), desc=f"  良性包"):
            package_path = os.path.join(ben_month_path, package_name)
            if not os.path.isdir(package_path):
                continue

            feature_file = os.path.join(package_path, "closeness_feature_vector_0129.json")
            if not os.path.exists(feature_file):
                continue

            with open(feature_file, 'r') as f:
                feature_vector = json.load(f)

            feature_list = list(feature_vector.values())
            X = np.array([feature_list])
            y_true = 0  # 良性

            y_pred = model.predict(X)[0]

            if y_pred != y_true:
                misclassified_fp.append({
                    'package': package_name,
                    'predicted': int(y_pred),
                    'actual': y_true,
                    'features': feature_list
                })

    # 统计
    total_mal = len(os.listdir(mal_month_path)) if os.path.exists(mal_month_path) else 0
    total_ben = len(os.listdir(ben_month_path)) if os.path.exists(ben_month_path) else 0

    print(f"\n  统计信息:")
    print(f"    恶意样本总数: {total_mal}")
    print(f"    良性样本总数: {total_ben}")
    print(f"    分类错误总数: {len(misclassified_fp) + len(misclassified_fn)}")
    print(f"    FP (假阳性): {len(misclassified_fp)}")
    print(f"    FN (假阴性): {len(misclassified_fn)}")

    # 输出到txt文件
    output_file = os.path.join(output_dir, f"rf_misclassified_{month}.txt")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Random Forest 分类错误分析 - {month}\n")
        f.write("=" * 60 + "\n\n")

        f.write(f"恶意样本总数: {total_mal}\n")
        f.write(f"良性样本总数: {total_ben}\n")
        f.write(f"分类错误总数: {len(misclassified_fp) + len(misclassified_fn)}\n")
        f.write(f"  - FP (假阳性): {len(misclassified_fp)}\n")
        f.write(f"  - FN (假阴性): {len(misclassified_fn)}\n")
        if total_mal + total_ben > 0:
            f.write(f"准确率: {(total_mal + total_ben - len(misclassified_fp) - len(misclassified_fn)) / (total_mal + total_ben):.4f}\n")
        f.write("\n")

        # 假阳性详情
        f.write("=" * 60 + "\n")
        f.write(f"FP (假阳性) - 预测为恶意，实际为良性: {len(misclassified_fp)}个\n")
        f.write("=" * 60 + "\n")
        for i, item in enumerate(misclassified_fp, 1):
            f.write(f"\n{i}. 包名: {item['package']}\n")
            f.write(f"   预测: 恶意 (1), 实际: 良性 (0)\n")
            f.write(f"   特征向量 (非零特征): ")
            nonzero = [(j, v) for j, v in enumerate(item['features']) if v != 0]
            f.write(f"{nonzero[:20]}" if len(nonzero) > 20 else f"{nonzero}\n")

        # 假阴性详情
        f.write("\n\n" + "=" * 60 + "\n")
        f.write(f"FN (假阴性) - 预测为良性，实际为恶意: {len(misclassified_fn)}个\n")
        f.write("=" * 60 + "\n")
        for i, item in enumerate(misclassified_fn, 1):
            f.write(f"\n{i}. 包名: {item['package']}\n")
            f.write(f"   预测: 良性 (0), 实际: 恶意 (1)\n")
            f.write(f"   特征向量 (非零特征): ")
            nonzero = [(j, v) for j, v in enumerate(item['features']) if v != 0]
            f.write(f"{nonzero[:20]}" if len(nonzero) > 20 else f"{nonzero}\n")

    print(f"\n结果已保存到: {output_file}")

print(f"\n分析完成！结果保存在: {output_dir}")
