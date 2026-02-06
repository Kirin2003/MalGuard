"""
检查两个JSON文件中API的差异
"""
import json

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 读取两个文件
gpt_result = read_json(r"gpt_prompt_result_closeness.json")
top500 = read_json(r"output_top_500_closeness_centrality.json")

# 获取API名称集合
gpt_apis = set(api["api_name"] for api in gpt_result.get("apis", []))
top500_apis = set(top500.keys())

print(f"GPT结果中的API数量: {len(gpt_apis)}")
print(f"Top 500中的API数量: {len(top500_apis)}")

# 检查GPT结果中有但Top 500中没有的API
missing_from_top500 = gpt_apis - top500_apis
if missing_from_top500:
    print(f"\nGPT结果中有但Top 500中没有的API ({len(missing_from_top500)}个):")
    for api in sorted(missing_from_top500):
        print(f"  - {api}")
else:
    print("\n所有GPT结果中的API都存在于Top 500中")

# 检查Top 500中有但GPT结果中没有的API
missing_from_gpt = top500_apis - gpt_apis
if missing_from_gpt:
    print(f"\nTop 500中有但GPT结果中没有的API ({len(missing_from_gpt)}个):")
    for api in sorted(missing_from_gpt):
        print(f"  - {api}")
else:
    print("\nTop 500中的所有API都存在于GPT结果中")

# 共同API数量
common_apis = gpt_apis & top500_apis
print(f"\n共同API数量: {len(common_apis)}")
