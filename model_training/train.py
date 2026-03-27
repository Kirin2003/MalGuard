import os
import time
import pandas as pd
import numpy as np
from data_loader import load_train_data
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

from train_with_lime import train_with_progress_bar, load_sensitive_apis
from utils.month_utils import generate_month_range


def prepare_dataset(start_month: str, end_month: str):
    """准备训练集和测试集

    Args:
        start_month: 起始月份，格式 'YYYY-mm'
        end_month: 结束月份，格式 'YYYY-mm'

    Returns:
        X_train, X_test, y_train, y_test
    """
    X_trains, X_tests, y_trains, y_tests = [], [], [], []
    for month in generate_month_range(start_month, end_month):
        malicious_output_txt_path = f"/Data2/hxq/MalGuard/fea_ex/dataset/malware_features_{month}.txt"
        benign_output_txt_path = f"/Data2/hxq/MalGuard/fea_ex/dataset/benign_features_{month}.txt"
        X_train, X_test, y_train, y_test = load_train_data(malicious_output_txt_path, benign_output_txt_path)
        X_trains.append(X_train)
        X_tests.append(X_test)
        y_trains.append(y_train)
        y_tests.append(y_test)
    X_train = np.vstack(X_trains)
    y_train = np.hstack(y_trains)
    X_test = np.vstack(X_tests)
    y_test = np.hstack(y_tests)
    return X_train, X_test, y_train, y_test


def clear_models(model_save_path):
    """清除上次训练的模型文件"""
    for f in os.listdir(model_save_path):
        file_path = os.path.join(model_save_path, f)
        if os.path.isfile(file_path):
            os.remove(file_path)


def train_nb(X_train, y_train, X_test, y_test, model_save_path, sensitive_apis):
    clear_models(model_save_path)
    nb_model = GaussianNB()
    start_time = time.time()
    train_with_progress_bar(nb_model, X_train, y_train, X_test, y_test, "Naive Bayes", model_save_path,
                            sensitive_apis, n_iter=100)
    return time.time() - start_time


def train_mlp(X_train, y_train, X_test, y_test, model_save_path, sensitive_apis):
    clear_models(model_save_path)
    mlp_model = MLPClassifier(hidden_layer_sizes=(100,), max_iter=1, warm_start=True, random_state=42)
    start_time = time.time()
    train_with_progress_bar(mlp_model, X_train, y_train, X_test, y_test, "Multi Layer Perceptron",
                            model_save_path, sensitive_apis, n_iter=500)
    return time.time() - start_time


def train_rf(X_train, y_train, X_test, y_test, model_save_path, sensitive_apis):
    clear_models(model_save_path)
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    start_time = time.time()
    train_with_progress_bar(rf_model, X_train, y_train, X_test, y_test, "Random Forest", model_save_path,
                            sensitive_apis, n_iter=100)
    return time.time() - start_time


def train_dt(X_train, y_train, X_test, y_test, model_save_path, sensitive_apis):
    clear_models(model_save_path)
    dt_model = DecisionTreeClassifier(random_state=42)
    start_time = time.time()
    train_with_progress_bar(dt_model, X_train, y_train, X_test, y_test, "Decision Tree", model_save_path,
                            sensitive_apis, n_iter=100)
    return time.time() - start_time


MODEL_NAME_MAP = {
    "nb": ("Naive Bayes", train_nb),
    "mlp": ("Multi Layer Perceptron", train_mlp),
    "rf": ("Random Forest", train_rf),
    "dt": ("Decision Tree", train_dt),
}


def train(X_train, X_test, y_train, y_test, model_name: str):
    """训练单个模型

    Args:
        X_train, X_test, y_train, y_test: 训练/测试数据
        model_name: 模型名称，支持 'nb', 'mlp', 'rf', 'dt'
    """
    if model_name not in MODEL_NAME_MAP:
        raise ValueError(f"Unknown model: {model_name}. Available: {list(MODEL_NAME_MAP.keys())}")

    sensitive_api_file = r"/Data2/hxq/MalGuard/API-call-graph/gpt_prompt_result_closeness.json"
    sensitive_apis = load_sensitive_apis(sensitive_api_file)

    model_save_path = r"./models"
    os.makedirs(model_save_path, exist_ok=True)

    display_name, train_func = MODEL_NAME_MAP[model_name]
    train_time = train_func(X_train, y_train, X_test, y_test, model_save_path, sensitive_apis)

    times_df = pd.DataFrame([{"Model": display_name, "Training Time (s)": train_time}])
    times_df.to_csv("/Data2/hxq/MalGuard/model_training/training_times.csv", index=False)
    print(f"\nTraining time saved to training_times.csv")
    print(times_df.to_string(index=False))

if __name__ == "__main__":
    X_train, X_test, y_train, y_test = prepare_dataset("2022-01", "2023-02")

    for model_name in ["nb", "mlp", "rf", "dt"]:
        train(X_train, X_test, y_train, y_test, model_name)