import os
import json
import time
import pandas as pd
import numpy as np
from data_loader import load_train_data
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

from train_with_lime import train_with_progress_bar, load_sensitive_apis

def train():
    # 训练集：2022-01~2023-02
    X_trains, X_tests, y_trains, y_tests = [], [], [], []
    for month in [f"{year}-{str(m).zfill(2)}" for year in range(2022, 2024) for m in range(1, 13)]:
        if month >= "2023-03":
            break
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

    sensitive_api_file = r"/Data2/hxq/MalGuard/API-call-graph/gpt_prompt_result_closeness.json"
    with open(sensitive_api_file, "r") as f:
        sensitive_apis = json.load(f)
    sensitive_apis = load_sensitive_apis(sensitive_api_file) 

    model_save_path = r"./models"
    os.makedirs(model_save_path, exist_ok=True)

    # 记录训练时间
    training_times = []

    # NB
    nb_model = GaussianNB()
    start_time = time.time()
    train_with_progress_bar(nb_model, X_train, y_train, X_test, y_test, "Naive Bayes", model_save_path,
                            sensitive_apis, n_iter=100)
    nb_time = time.time() - start_time
    training_times.append({"Model": "Naive Bayes", "Training Time (s)": nb_time})

    # MLP
    mlp_model = MLPClassifier(hidden_layer_sizes=(100,), max_iter=1, warm_start=True, random_state=42)
    start_time = time.time()
    train_with_progress_bar(mlp_model, X_train, y_train, X_test, y_test, "Multi Layer Perceptron",
                            model_save_path, sensitive_apis, n_iter=500)
    mlp_time = time.time() - start_time
    training_times.append({"Model": "Multi Layer Perceptron", "Training Time (s)": mlp_time})

    # RF
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    start_time = time.time()
    train_with_progress_bar(rf_model, X_train, y_train, X_test, y_test, "Random Forest", model_save_path,
                            sensitive_apis, n_iter=100)
    rf_time = time.time() - start_time
    training_times.append({"Model": "Random Forest", "Training Time (s)": rf_time})

    # DT
    dt_model = DecisionTreeClassifier(random_state=42)
    start_time = time.time()
    train_with_progress_bar(dt_model, X_train, y_train, X_test, y_test, "Decision Tree", model_save_path,
                            sensitive_apis, n_iter=100)
    dt_time = time.time() - start_time
    training_times.append({"Model": "Decision Tree", "Training Time (s)": dt_time})

    # 保存训练时间到CSV
    times_df = pd.DataFrame(training_times)
    times_df.to_csv("/Data2/hxq/MalGuard/model_training/training_times.csv", index=False)
    print("\nTraining times saved to training_times.csv")
    print(times_df.to_string(index=False))

if __name__ == "__main__":
    train()