import os
import json
import joblib
from pathlib import Path

# 配置路径
MODEL_PATH = r"/Data2/hxq/MalGuard/model_training/models/random_forest/random_forest_model.pkl"
FEATURE_SET_PATH = r"/Data2/hxq/MalGuard/API-call-graph/gpt_prompt_result_closeness.json"
MALICIOUS_DIR = r"/Data2/hxq/datasets/incremental_packages_dynamic_capping_subset/malicious/2024-01"
BENIGN_DIR = r"/Data2/hxq/datasets/incremental_packages_dynamic_capping_subset/benign/2024-01"
OUTPUT_PATH = r"/Data2/hxq/MalGuard/model_training/misclassified_packages.json"


def load_feature_set():
    """加载特征集，获取特征的顺序"""
    with open(FEATURE_SET_PATH, 'r', encoding='utf-8') as f:
        feature_set = json.load(f)
    return [api["api_name"] for api in feature_set["apis"]]


def load_package_features(package_dir, feature_order):
    """加载单个包的特征向量，按特征集顺序排列"""
    feature_file = os.path.join(package_dir, "closeness_feature_vector.json")
    if not os.path.exists(feature_file):
        return None

    with open(feature_file, 'r', encoding='utf-8') as f:
        feature_vector = json.load(f)

    # 按特征集顺序构建特征向量
    return [feature_vector.get(api, 0) for api in feature_order]


def test_model():
    # 加载模型
    print(f"Loading model from {MODEL_PATH}...")
    model = joblib.load(MODEL_PATH)

    # 加载特征顺序
    feature_order = load_feature_set()
    print(f"Loaded {len(feature_order)} features from feature set")

    mismatches = []
    malicious_total = 0
    benign_total = 0
    malicious_mismatches = 0
    benign_mismatches = 0

    # 测试恶意包 (label=1, pred_class=1)
    print(f"\nTesting malicious packages in {MALICIOUS_DIR}...")
    malicious_dir = Path(MALICIOUS_DIR)
    for package_dir in malicious_dir.iterdir():
        if not package_dir.is_dir():
            continue
        features = load_package_features(package_dir, feature_order)
        if features is None:
            print(f"  Warning: {package_dir.name} has no feature file, skipping")
            continue

        X = [features]
        pred = model.predict(X)[0]
        prob = model.predict_proba(X)[0]
        prob_benign = float(prob[0])
        prob_malicious = float(prob[1])

        malicious_total += 1
        if pred == 0:  # 恶意包被预测为良性
            malicious_mismatches += 1
            mismatches.append({
                "package_name": package_dir.name,
                "true_label": "malicious",
                "predicted_label": "benign",
                "pred_class": int(pred),
                "prob_benign": prob_benign,
                "prob_malicious": prob_malicious
            })

    print(f"  Tested {malicious_total} malicious packages, {malicious_mismatches} mismatches")

    # 测试良性包 (label=0, pred_class=0)
    print(f"\nTesting benign packages in {BENIGN_DIR}...")
    benign_dir = Path(BENIGN_DIR)
    for package_dir in benign_dir.iterdir():
        if not package_dir.is_dir():
            continue
        features = load_package_features(package_dir, feature_order)
        if features is None:
            print(f"  Warning: {package_dir.name} has no feature file, skipping")
            continue

        X = [features]
        pred = model.predict(X)[0]
        prob = model.predict_proba(X)[0]
        prob_benign = float(prob[0])
        prob_malicious = float(prob[1])

        benign_total += 1
        if pred == 1:  # 良性包被预测为恶意
            benign_mismatches += 1
            mismatches.append({
                "package_name": package_dir.name,
                "true_label": "benign",
                "predicted_label": "malicious",
                "pred_class": int(pred),
                "prob_benign": prob_benign,
                "prob_malicious": prob_malicious
            })

    print(f"  Tested {benign_total} benign packages, {benign_mismatches} mismatches")

    # 汇总
    total_packages = malicious_total + benign_total
    total_mismatches = malicious_mismatches + benign_mismatches
    accuracy = f"{(total_packages - total_mismatches) / total_packages * 100:.2f}%" if total_packages > 0 else "0.00%"

    # 计算恶意类（label=1）的 precision/recall/f1
    tp = malicious_total - malicious_mismatches  # 恶意包被正确预测为恶意
    fn = malicious_mismatches                     # 恶意包被错误预测为良性
    fp = benign_mismatches                        # 良性包被错误预测为恶意
    tn = benign_total - benign_mismatches          # 良性包被正确预测为良性

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    result = {
        "model_path": MODEL_PATH,
        "test_data": {
            "malicious": {
                "path": MALICIOUS_DIR,
                "total": malicious_total,
                "mismatches": malicious_mismatches
            },
            "benign": {
                "path": BENIGN_DIR,
                "total": benign_total,
                "mismatches": benign_mismatches
            }
        },
        "summary": {
            "total_packages": total_packages,
            "total_mismatches": total_mismatches,
            "accuracy": accuracy,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4)
        },
        "mismatches": mismatches
    }

    # 保存结果
    print(f"\nSaving misclassified packages to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # 打印摘要
    print(f"\n=== Summary ===")
    print(f"Total packages tested: {total_packages}")
    print(f"Total mismatches: {total_mismatches}")
    print(f"Accuracy: {accuracy}")
    print(f"Precision (malicious): {precision:.4f}")
    print(f"Recall (malicious): {recall:.4f}")
    print(f"F1 (malicious): {f1:.4f}")
    print(f"  - Malicious→Benign (False Positive): {malicious_mismatches}")
    print(f"  - Benign→Malicious (False Negative): {benign_mismatches}")


if __name__ == "__main__":
    test_model()