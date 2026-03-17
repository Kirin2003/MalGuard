import os
import json
from data_loader import load_test_data
from sklearn.metrics import precision_score, recall_score, f1_score
import joblib

def test():
    # 从 models 目录加载已训练的模型并测试
    models_dir = r'/Data2/hxq/MalGuard/model_training/models'

    # 可加载的模型列表
    model_files = [
        "naive_bayes",
        "decision_tree",
        "random_forest",
        "multi_layer_perceptron",
    ]

    # 测试模型在2022-01~2024-03每个月的数据集上的表现
    # 先加载所有模型为全局变量
    print("Loading all models...")
    models = {}
    for model_file in model_files:
        model_path = os.path.join(models_dir, model_file, f"{model_file}_model.pkl")
        if os.path.exists(model_path):
            models[model_file] = joblib.load(model_path)
            print(f"  Loaded: {model_file}")

    # 定义月份列表
    months = [f"{year}-{str(m).zfill(2)}" for year in range(2022, 2025) for m in range(1, 13)]

    # 为每个模型单独存储结果
    model_results = {model_file: {"month": [], "f1": [], "precision": [], "recall": []}
                     for model_file in models.keys()}

    # 先循环模型，再循环月份
    for model_file, model in models.items():
        model_name = model_file.replace("_", " ").title()
        print(f"\n{'#'*20} Testing {model_name} {'#'*20}")

        for month in months:
            if month < "2023-03":
                continue  # 跳过2023-03之前的月份
            mal_data_path = f"/Data2/hxq/MalGuard/fea_ex/dataset/malware_features_{month}.txt"
            ben_data_path = f"/Data2/hxq/MalGuard/fea_ex/dataset/benign_features_{month}.txt"

            X_test, y_test = load_test_data(mal_data_path, ben_data_path)

            # 预测并计算恶意类（label=1）的指标
            y_pred = model.predict(X_test)
            precision = precision_score(y_test, y_pred, pos_label=1, zero_division=0)
            recall = recall_score(y_test, y_pred, pos_label=1, zero_division=0)
            f1 = f1_score(y_test, y_pred, pos_label=1, zero_division=0)

            model_results[model_file]["month"].append(month)
            model_results[model_file]["f1"].append(f1)
            model_results[model_file]["precision"].append(precision)
            model_results[model_file]["recall"].append(recall)

    # 保存为4个JSON文件
    results_dir = "/Data2/hxq/MalGuard/model_training/results"
    os.makedirs(results_dir, exist_ok=True)

    for model_file, data in model_results.items():
        output_path = os.path.join(results_dir, f"malguard_{model_file}.json")
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved: {output_path}")

    print("\nAll results saved to JSON files")

if __name__ == "__main__":
    test()