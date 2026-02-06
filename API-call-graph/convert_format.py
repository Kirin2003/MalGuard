"""
将 gpt_prompt_result_closeness.json 转换为 closeness_sensitive_api.json 格式
添加 api_id 字段，malicious_purposes 转换为列表格式
"""
import json
import re

def convert_format(input_file, output_file):
    # 读取原始数据
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    converted_apis = []

    for idx, api in enumerate(data.get("apis", []), start=1):
        api_name = api.get("api_name", "")
        malicious_purposes_str = api.get("malicious_purposes", "")

        # 将字符串转换为列表格式
        purposes_list = split_purposes(malicious_purposes_str)

        converted_api = {
            "api_name": api_name,
            "malicious_purposes": purposes_list,
            "api_id": idx
        }
        converted_apis.append(converted_api)

    # 构建输出格式
    output_data = {
        "apis": converted_apis
    }

    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"转换完成! 共处理 {len(converted_apis)} 个 API")
    print(f"结果已保存到 {output_file}")

def split_purposes(text):
    """
    将描述性字符串拆分为多个用途列表
    常见分隔符: 句号+空格、逗号、分号等
    """
    if not text:
        return []

    # 按句号分隔（保留句号后的内容）
    parts = re.split(r'(?<=[.])\s+(?=[A-Z])', text)

    # 过滤空字符串并清理
    result = []
    for part in parts:
        part = part.strip().rstrip('.')
        if part and len(part) > 3:  # 过滤太短的片段
            # 首字母大写
            if part and part[0].islower():
                part = part[0].upper() + part[1:]
            result.append(part)

    # 如果拆分结果太少，直接返回原文本作为单元素列表
    if len(result) <= 1:
        result = [text.strip().rstrip('.')]

    return result

if __name__ == "__main__":
    input_file = "/Data2/hxq/MalGuard/API-call-graph/gpt_prompt_result_closeness.json"
    output_file = "/Data2/hxq/MalGuard/API-call-graph/closeness_sensitive_api.json"

    convert_format(input_file, output_file)
