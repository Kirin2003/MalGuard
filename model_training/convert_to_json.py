# -*- coding: utf-8 -*-
import pandas as pd
import json

# 读取CSV
df = pd.read_csv("/Data2/hxq/MalGuard/model_training/malicious_monthly_results.csv")

# 获取所有模型
models = df['Model'].unique()

# 为每个模型创建JSON文件
for model in models:
    model_df = df[df['Model'] == model]

    # 创建JSON格式
    result = {
        "month": model_df['Month'].tolist(),
        "f1": model_df['F1'].tolist(),
        "precision": model_df['Precision'].tolist(),
        "recall": model_df['Recall'].tolist()
    }

    # 保存JSON文件
    # 将模型名转为小写并用下划线连接
    model_key = model.lower().replace(" ", "_")
    output_path = f"/Data2/hxq/MalGuard/model_training/results/{model_key}.json"
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Saved: {output_path}")
