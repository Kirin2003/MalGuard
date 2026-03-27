import os
import json
import time
import pandas as pd
import numpy as np
from data_loader import load_train_data, load_test_data
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score
from train_with_lime import train_with_progress_bar, load_sensitive_apis


def get_next_month(month):
    """获取下一个月"""
    year, m = month.split("-")
    year, m = int(year), int(m)
    if m == 12:
        return f"{year + 1}-01"
    return f"{year}-{str(m + 1).zfill(2)}"


def load_data_up_to_month(end_month):
    """加载从2022-01到end_month的所有数据，返回训练集和验证集"""
    X_trains, y_trains = [], []
    X_vals, y_vals = [], []
    for month in [f"{year}-{str(m).zfill(2)}" for year in range(2022, 2025) for m in range(1, 13)]:
        if month > end_month:
            break
        mal_path = f"/Data2/hxq/MalGuard/fea_ex/dataset/malware_features_{month}.txt"
        ben_path = f"/Data2/hxq/MalGuard/fea_ex/dataset/benign_features_{month}.txt"

        X_train, X_val, y_train, y_val = load_train_data(mal_path, ben_path)
        X_trains.append(X_train)
        y_trains.append(y_train)
        X_vals.append(X_val)
        y_vals.append(y_val)


    X_train_final = np.vstack(X_trains)
    y_train_final = np.hstack(y_trains)
    X_val_final = np.vstack(X_vals)
    y_val_final = np.hstack(y_vals)
    return X_train_final, X_val_final, y_train_final, y_val_final


def train_and_evaluate():
    # 训练月份范围: 2023-02 到 2024-11 (需要确保有下一个月可测试)
    train_months = []
    for month in [f"{year}-{str(m).zfill(2)}" for year in range(2023, 2025) for m in range(1, 13)]:
        if month < "2023-02":
            continue
        if month > "2024-11":
            break
        train_months.append(month)

    sensitive_api_file = r"/Data2/hxq/MalGuard/API-call-graph/gpt_prompt_result_closeness.json"
    sensitive_apis = load_sensitive_apis(sensitive_api_file)
    model_save_path = r"./models_upper"
    os.makedirs(model_save_path, exist_ok=True)

    # 存储结果
    results = {"train_month": [], "test_month": [], "f1": [], "precision": [], "recall": []}

    for train_month in train_months:
        test_month = get_next_month(train_month)
        print(f"\n{'='*60}")
        print(f"Training on data up to {train_month}, testing on {test_month}")
        print(f"{'='*60}")

        # 加载训练集和验证集
        X_train, X_val, y_train, y_val = load_data_up_to_month(train_month)


        # 加载测试数据
        mal_test_path = f"/Data2/hxq/MalGuard/fea_ex/dataset/malware_features_{test_month}.txt"
        ben_test_path = f"/Data2/hxq/MalGuard/fea_ex/dataset/benign_features_{test_month}.txt"

        X_test_next, y_test_next = load_test_data(mal_test_path, ben_test_path)
        print(f"  Train samples: {len(y_train)}, Val samples: {len(y_val)}, Test(next month) samples: {len(y_test_next)}")
        print(f"  Train malicious ratio: {y_train.sum()/len(y_train):.3f}")
        print(f"  Test(next month) malicious ratio: {y_test_next.sum()/len(y_test_next):.3f}")

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        start_time = time.time()

        # 训练时用验证集（20%）监控训练过程
        train_with_progress_bar(model, X_train, y_train, X_val, y_val,
                               "Random Forest",
                               model_save_path, sensitive_apis, n_iter=100)

        train_time = time.time() - start_time

        # 预测 - 用下一个月的所有数据做最终评估
        y_pred = model.predict(X_test_next)

        # 计算指标 (恶意类 label=1)
        precision = precision_score(y_test_next, y_pred, pos_label=1, zero_division=0)
        recall = recall_score(y_test_next, y_pred, pos_label=1, zero_division=0)
        f1 = f1_score(y_test_next, y_pred, pos_label=1, zero_division=0)

        print(f"  Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
        print(f"  Training time: {train_time:.2f}s")

        # 保存结果
        results["train_month"].append(train_month)
        results["test_month"].append(test_month)
        results["f1"].append(f1)
        results["precision"].append(precision)
        results["recall"].append(recall)

    # 保存结果到JSON文件
    results_dir = "/Data2/hxq/MalGuard/model_training/results_upper"
    os.makedirs(results_dir, exist_ok=True)

    output_path = os.path.join(results_dir, "upper_random_forest.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {output_path}")

    # 保存汇总CSV
    summary_df = pd.DataFrame(results)
    summary_path = os.path.join(results_dir, "upper_summary.csv")
    summary_df.to_csv(summary_path, index=False)
    print(f"Saved summary: {summary_path}")

    # 打印汇总表
    print("\n" + "="*80)
    print("SUMMARY RESULTS")
    print("="*80)
    print(summary_df.to_string())

    return summary_df


if __name__ == "__main__":
    train_and_evaluate()