"""
项目配置文件 - 集中管理月份范围等参数
"""
import os

# 基础月份范围 (用于训练基础模型)
BASE_START_MONTH = "2022-01"
BASE_END_MONTH = "2023-12"

# 增量月份范围 (用于增量训练/测试)
INCREMENTAL_START_MONTH = "2024-01"
INCREMENTAL_END_MONTH = "2024-12"

# 训练月份范围 (用于 upper.py 中的增量训练)
TRAIN_START_MONTH = "2023-12"
TRAIN_END_MONTH = "2024-11"

# 数据处理范围 (用于特征提取等)
DATA_START_MONTH = "2022-01"
DATA_END_MONTH = "2024-12"


# ============ 大模型配置 ============
# 支持多个模型配置，可通过命令行参数 --model 选择

LLM_CONFIGS = {
    "qwen": {
        "model_name": "qwen3.5-35b-a3b",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key_env": "OPENAI_API_KEY",  # 从环境变量读取
    },
    "deepseek": {
        "model_name": "deepseek-chat",
        "base_url": "https://api.deepseek.com/v1",
        "api_key_env": "DEEPSEEK_API_KEY",
    },
    "local": {
        "model_name": "deepseek",  # 本地 vllm 部署的模型
        "base_url": "http://localhost:8000/v1",
        "api_key_env": "LOCAL_LLM_API_KEY",  # 本地部署可以设为任意值或 "EMPTY"
    },
}

# 默认使用的模型
DEFAULT_LLM = "qwen"


def get_llm_config(model_name: str = None) -> dict:
    """
    获取大模型配置

    Args:
        model_name: 模型名称，对应 LLM_CONFIGS 中的 key。为 None 时使用 DEFAULT_LLM

    Returns:
        包含 model_name, base_url, api_key 的配置字典
    """
    model_name = model_name or DEFAULT_LLM

    if model_name not in LLM_CONFIGS:
        raise ValueError(f"未知的模型配置: {model_name}，可用配置: {list(LLM_CONFIGS.keys())}")

    config = LLM_CONFIGS[model_name].copy()
    # 从环境变量读取 api_key
    api_key = os.getenv(config.pop("api_key_env"), "")
    config["api_key"] = api_key

    if not config["api_key"]:
        print(f"警告: 未设置 API Key 环境变量，请检查配置")

    return config
