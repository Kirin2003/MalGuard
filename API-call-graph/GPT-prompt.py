import json
from openai import OpenAI
import os
import time

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def write_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 读取 top 500 API
feature_set = read_json(r"output_top_500_closeness_centrality.json")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def evaluate_all_apis(api_list, batch_size=50):
    """分批评估所有 API，避免响应过长截断"""
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
                    model="qwen3-max",
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
                    save_progress(all_results)

    return all_results

def add_api_ids(results):
    """为所有API添加递增的api_id"""
    for idx, api in enumerate(results, start=1):
        api["api_id"] = idx
    return results

def save_progress(results):
    """保存中间进度"""
    final_output = {"apis": results}
    write_json(final_output, r"gpt_prompt_result_closeness_progress.json")
    print(f"  已保存中间进度: {len(results)} 个API")

# 执行评估
api_list = list(feature_set.keys())
print(f"开始分批评估 {len(api_list)} 个 API (每批50个)...")

results = evaluate_all_apis(api_list, batch_size=50)

# 统一添加api_id
results = add_api_ids(results)

# 保存结果
final_output = {"apis": results}
write_json(final_output, r"gpt_prompt_result_closeness_0129.json")
print(f"\n完成! 共评估 {len(results)} 个 API, 结果已保存到 gpt_prompt_result_closeness_0129.json")
