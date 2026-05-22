import json
from openai import OpenAI
import os
import time
import argparse
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_llm_config

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def write_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def gpt_prompt_top_apis(input_path, output_path, model_config, batch_size=50):
    """
    读取TOP API json文件，调用GPT评估恶意用途，输出结果文件。

    Args:
        input_path: 输入的TOP API json文件路径
        output_path: 输出的GPT评估结果文件路径
        model_config: 模型配置字典，包含 model_name, base_url, api_key
        batch_size: 每批评估的API数量，默认50
    """
    # 初始化OpenAI客户端
    client = OpenAI(
        api_key=model_config["api_key"],
        base_url=model_config["base_url"],
    )
    model_name = model_config["model_name"]

    # 读取输入文件
    feature_set = read_json(input_path)
    api_list = list(feature_set.keys())
    print(f"开始分批评估 {len(api_list)} 个 API (每批{batch_size}个)...")

    # 分批评估
    all_results = []
    total_batches = (len(api_list) + batch_size - 1) // batch_size

    for i in range(0, len(api_list), batch_size):
        batch = api_list[i:i + batch_size]
        batch_num = i // batch_size + 1
        print(f"  处理批次 {batch_num}/{total_batches} (API {i+1}-{min(i+batch_size, len(api_list))})...")

        prompt = f"""
feature_set={batch}
You are a security API auditor.
Your task is to determine whether following {len(batch)} Python APIs can potentially be used for malicious purposes.
Consider common attack techniques such as command execution, code obfuscation, data exfiltration, privilege escalation, etc.

For each API, identify potential malicious usage scenarios.

Output ONLY the malicious APIs and follow the required JSON format.

{{
  "apis": [
    {{
      "api_name": "The name of the API",
      "malicious_purposes": [
        "Potential malicious usage scenario 1",
        "Potential malicious usage scenario 2"
      ]
    }}
  ]
 }}
"""

        max_retries = 3
        for retry in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "You are a security expert."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                    max_tokens=8192,
                )
                text = response.choices[0].message.content

                text = text.strip()
                if text.startswith("```json"):
                    text = text.replace("```json", "").replace("```", "").strip()
                if text.startswith("```"):
                    text = text.replace("```", "").strip()

                batch_result = json.loads(text)
                all_results.extend(batch_result.get("apis", []))
                break
            except (json.decoder.JSONDecodeError, Exception) as e:
                if retry < max_retries - 1:
                    print(f"    批次 {batch_num} 解析失败，{5*(retry+1)}秒后重试...")
                    time.sleep(5 * (retry + 1))
                else:
                    print(f"    批次 {batch_num} 最终失败: {e}")
                    # 保存中间进度
                    final_output = {"apis": all_results}
                    write_json(final_output, output_path.replace(".json", "_progress.json"))
                    print(f"  已保存中间进度: {len(all_results)} 个API")

    # 统一添加api_id
    for idx, api in enumerate(all_results, start=1):
        api["api_id"] = idx

    # 保存结果
    final_output = {"apis": all_results}
    write_json(final_output, output_path)
    print(f"\n完成! 共评估 {len(all_results)} 个 API, 结果已保存到 {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="使用大模型评估API的恶意用途")
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="模型名称 (qwen/deepseek/local)，默认使用 config.py 中的 DEFAULT_LLM",
    )
    parser.add_argument(
        "--input",
        type=str,
        default="../results/output_top_500_closeness_centrality.json",
        help="输入的TOP API json文件路径",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="../results/gpt_prompt_result_closeness.json",
        help="输出的GPT评估结果文件路径",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="每批评估的API数量",
    )
    args = parser.parse_args()

    # 获取模型配置
    model_config = get_llm_config(args.model)
    print(f"使用模型: {model_config['model_name']}")
    print(f"API地址: {model_config['base_url']}")

    gpt_prompt_top_apis(
        input_path=args.input,
        output_path=args.output,
        model_config=model_config,
        batch_size=args.batch_size,
    )
