# MalGuard - 恶意软件包检测系统

MalGuard是一个基于API调用图中心性分析的恶意Python包检测系统，支持增量学习场景。

## 项目目录结构

```
MalGuard/
├── API-call-graph/        # API调用图构建与中心性分析
│   ├── cal_cen_new.py         # 构建API调用图并计算中心性
│   ├── cal_final_cen.py       # 计算所有包的平均中心性
│   ├── top500-ex.py           # 选取Top 500敏感API
│   ├── GPT-prompt.py          # 使用GPT分析敏感API的恶意用途
│   ├── output_top_500_closeness_centrality.json  # Top 500 API中心性值
│   ├── closeness_sensitive_api.json   # closeness中心性的敏感API
│   ├── degree_sensitive_api.json      # degree中心性的敏感API
│   ├── harmonic_sensitive_api.json    # harmonic中心性的敏感API
│   ├── katz_sensitive_api.json         # katz中心性的敏感API
│   └── gpt_prompt_result_closeness.json  # GPT分析结果(主用)
│
├── fea_ex/                # 特征提取与处理
│   ├── fea_vec_ex.py          # 从包中提取特征向量
│   ├── combine.py             # 合并特征向量为训练数据
│   └── dataset/               # 预处理后的特征数据集
│       ├── malware_features_{month}.txt   # 恶意样本特征(按月)
│       └── benign_features_{month}.txt    # 良性样本特征(按月)
│
├── model_training/        # 模型训练与测试
│   ├── train_with_lime.py    # 训练多个分类模型
│   ├── test_model.ipynb      # 增量测试与分析
│   ├── data_loader.py        # 数据加载工具
│   ├── monthly_results.csv   # 每月测试结果
│   └── models/               # 训练好的模型
│
└── requiremnets.txt      # 项目依赖
```

## 数据集目录结构

原始数据集位于: `/Data2/hxq/datasets/incremental_packages_dynamic_capping_subset/`

```
incremental_packages_dynamic_capping_subset/
├── benign/               # 良性包
│   ├── 2022-01/
│   │   ├── package-name-version/
│   │   │   ├── closeness_new.json      # API closeness中心性
│   │   │   ├── degree_new.json         # API degree中心性
│   │   │   ├── harmonic_new.json        # API harmonic中心性
│   │   │   ├── katz_new.json            # API katz中心性
│   │   │   ├── closeness_feature_vector.json  # 特征向量
│   │   │   └── ... (源代码文件)
│   │   └── ...
│   └── ...
│
├── malicious/            # 恶意包 (结构同benign)
│   ├── 2022-01/
│   └── ...
│
└── closeness_final_new.json  # 所有包的平均API中心性
```

---

## 完整流程

### Step 1: 构建API调用图并计算中心性

**脚本**: [API-call-graph/cal_cen_new.py](API-call-graph/cal_cen_new.py)

**输入**:
- 原始Python包目录: `/Data2/hxq/datasets/incremental_packages_dynamic_capping_subset/{benign,malicious}/{月份}/{包名}/`

**处理过程**:
1. 遍历每个包的所有`.py`文件
2. 使用AST解析提取API调用
3. 构建有向图(API调用关系)
4. 计算4种中心性指标:
   - `degree_centrality`: 度中心性
   - `closeness_centrality`: 接近中心性
   - `harmonic_centrality`: 调和中心性
   - `katz_centrality`: Katz中心性

**输出**:
- 每个包目录下生成:
  - `closeness_new.json`
  - `degree_new.json`
  - `harmonic_new.json`
  - `katz_new.json`

```bash
# 运行方式
cd API-call-graph
python cal_cen_new.py
```

---

### Step 2: 计算所有包的平均中心性

**脚本**: [API-call-graph/cal_final_cen.py](API-call-graph/cal_final_cen.py)

**输入**:
- 所有包的中心性文件(Step 1的输出)
- 指定月份范围(默认: 2022-01 ~ 2023-02)

**处理过程**:
1. 收集指定月份范围内的所有恶意包
2. 对每个API,计算所有包的中心性平均值

**输出**:
- 数据集根目录下生成:
  - `closeness_final_new.json`
  - `degree_final_new.json`
  - `harmonic_final_new.json`
  - `katz_final_new.json`

```python
# 配置参数
base_folder = r'/Data2/hxq/datasets/incremental_packages_dynamic_capping_subset'
process_all_packages(base_folder, start_month='2022-01', end_month='2023-02')
```

---

### Step 3: 选取Top 500敏感API

**脚本**: [API-call-graph/top500-ex.py](API-call-graph/top500-ex.py)

**输入**:
- `closeness_final_new.json` (Step 2输出)

**处理过程**:
1. 按closeness中心性值降序排列
2. 选取前500个API

**输出**:
- `output_top_500_closeness_centrality.json`

```bash
# 运行
python top500-ex.py
```

---

### Step 4: 使用GPT分析敏感API的恶意用途

**脚本**: [API-call-graph/GPT-prompt.py](API-call-graph/GPT-prompt.py)

**输入**:
- `output_top_500_closeness_centrality.json` (Step 3输出)

**处理过程**:
1. 将500个API分成10批(每批50个)
2. 调用GPT API分析每个API的潜在恶意用途
3. 考虑攻击技术: 命令执行、代码混淆、数据外泄、权限提升等

**输出**:
- `gpt_prompt_result_closeness.json`

**JSON格式**:
```json
{
  "apis": [
    {
      "api_id": 1,
      "api_name": "os.system",
      "malicious_purposes": [
        "执行任意系统命令",
        "启动恶意进程"
      ]
    }
  ]
}
```

```bash
# 运行前设置环境变量
export OPENAI_API_KEY="your-api-key"

python GPT-prompt.py
```

**注意**: 项目已提供预处理结果，可直接使用:
- `gpt_prompt_result_closeness.json` (主用)
- `closeness_sensitive_api.json`
- `degree_sensitive_api.json`
- `harmonic_sensitive_api.json`
- `katz_sensitive_api.json`

---

### Step 5: 提取特征向量

**脚本**: [fea_ex/fea_vec_ex.py](fea_ex/fea_vec_ex.py)

**输入**:
- 敏感API列表: `API-call-graph/gpt_prompt_result_closeness.json`
- 原始包目录: `/Data2/hxq/datasets/incremental_packages_dynamic_capping_subset/{benign,malicious}/{月份}/{包名}/`
- 每个包必须有: `closeness_new.json`

**处理过程**:
1. 加载敏感API列表(500个)
2. 对每个包,将其`closeness_new.json`与敏感API列表匹配
3. 生成500维特征向量(敏感API的closeness中心性值)

**输出**:
- 每个包目录下生成: `closeness_feature_vector.json`

```python
# 配置参数
fea_set_path = r"/Data2/hxq/MalGuard/API-call-graph/gpt_prompt_result_closeness.json"
pack_dir = r"/Data2/hxq/datasets/incremental_packages_dynamic_capping_subset"

extract_features(fea_set_path, pack_dir, start_month='2022-01', end_month='2024-12')
```

---

### Step 6: 合并特征向量为训练数据

**脚本**: [fea_ex/combine.py](fea_ex/combine.py)

**输入**:
- 每个包的`closeness_feature_vector.json` (Step 5输出)

**处理过程**:
1. 按月份收集特征向量
2. 添加标签(恶意=1, 良性=0)
3. 转换为空格分隔的文本格式

**输出**:
- `fea_ex/dataset/malware_features_{month}.txt`
- `fea_ex/dataset/benign_features_{month}.txt`

**数据格式**:
```
feature1 feature2 ... feature500 label
0.123 0.456 ... 0.789 1
0.234 0.567 ... 0.890 0
```

```bash
# 运行 - 生成所有月份的特征文件
python combine.py

# 或指定月份范围
convert_features_to_txt(pack_dir, malicious_output_txt_path, start_month='2022-01', end_month='2023-02', type_flag="malicious")
```

---

### Step 7: 模型训练与增量测试

**脚本**: [model_training/test_model.ipynb](model_training/test_model.ipynb)

这是主要的训练和测试脚本，支持按月份的增量训练场景。

**输入**:
- 按月份的特征文件: `fea_ex/dataset/malware_features_{month}.txt`
- 按月份的特征文件: `fea_ex/dataset/benign_features_{month}.txt`
- 敏感API: `API-call-graph/gpt_prompt_result_closeness.json`

**增量训练场景**:
- 训练集: 2022-01 ~ 2023-02 (共14个月的数据合并)
- 测试集: 逐月测试 2023-03 ~ 2024-12

**处理流程**:

1. **数据加载与合并** (cell-1): 收集2022-01至2023-02的所有月份数据
```python
# 收集训练数据 - 2022-01 ~ 2023-02
X_trains, y_trains = [], []
for month in [f"{year}-{str(m).zfill(2)}" for year in range(2022, 2024) for m in range(1, 13)]:
    if month >= "2023-03":
        break
    X_train, X_test, y_train, y_test = load_train_data(
        f"malware_features_{month}.txt",
        f"benign_features_{month}.txt"
    )
    X_trains.append(X_train)
    y_trains.append(y_train)

# 合并为一个大训练集
X_train = np.vstack(X_trains)
y_train = np.hstack(y_trains)
```

**训练的模型** (cell-2):
| 模型 | 参数 |
|------|------|
| Naive Bayes | GaussianNB |
| Multi Layer Perceptron | hidden_layer_sizes=(100,), max_iter=500 |
| Random Forest | n_estimators=100 |
| Decision Tree | 默认参数 |

**结果示例**:
| Model | Month | Precision | Recall | F1 |
|-------|-------|-----------|--------|-----|
| Random Forest | 2023-03 | 0.9587 | 0.9612 | 0.9599 |
| Random Forest | 2023-04 | 0.9456 | 0.9501 | 0.9478 |
| ... | ... | ... | ... | ... |

**运行方式**:
```bash
cd model_training
jupyter notebook test_model.ipynb
```

---

## 完整使用示例

### 场景: 复现论文实验

1. **准备阶段** (如已有预处理数据可跳过):
   ```bash
   # Step 1-4: 已完成，结果在 API-call-graph/ 目录
   # Step 5-6: 提取并合并特征
   cd fea_ex
   python fea_vec_ex.py    # 生成特征向量
   python combine.py       # 合并为训练数据
   ```

2. **训练与增量测试**:
   ```bash
   cd model_training
   jupyter notebook test_model.ipynb
   ```

---

## 依赖安装

```bash
pip install -r requiremnets.txt
```

**主要依赖**:
- `openai`: GPT API调用
- `pandas`: 数据处理
- `tqdm`: 进度条
- `networkx`: 图计算
- `scipy`: 科学计算
- `scikit-learn`: 机器学习
- `xgboost`: XGBoost
- `lime`: 模型解释
- `joblib`: 模型序列化

---

## 注意事项

1. **数据集**: 需要PyPI恶意/良性包数据集，可从[PyPI](https://pypi.org/)或相关恶意软件数据集获取

2. **GPT API**: Step 4需要OpenAI API Key，可使用通义千问等兼容API

3. **增量学习**: 当前实现为"训练-测试"模式，真正的增量学习可使用`warm_start=True`或`partial_fit`

4. **特征维度**: 特征维度取决于敏感API数量(Top 500)，可根据需要调整

5. **月份范围**: 默认2022-01至2024-12，可根据实际数据调整

---

## 文件说明

| 文件 | 用途 |
|------|------|
| `fea_ex/combine.py` | 合并特征向量 |
| `fea_ex/fea_vec_ex.py` | 提取特征向量 |
| `model_training/test_model.ipynb` | 增量测试主流程 |
| `model_training/analyze_misclassified.py` | 误分类分析 |
| `API-call-graph/cal_cen_new.py` | 计算API中心性 |
