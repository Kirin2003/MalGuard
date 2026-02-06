import ast
import re
import os
import json
import networkx as nx
import time
from tqdm import tqdm
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count
def extract_api_calls(file_path):
    api_calls = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()

        try:
            tree = ast.parse(content, filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        api_calls.append(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        attr_name = f"{node.func.value.id}.{node.func.attr}" if isinstance(node.func.value, ast.Name) else node.func.attr
                        api_calls.append(attr_name)

        except (SyntaxError, ValueError):
            matches = re.finditer(r'\b(\w+)\s*\(', content)
            for match in matches:
                api_calls.append(match.group(1))

        return api_calls

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return []

def build_graph(api_calls):
    G = nx.DiGraph()
    for i, caller in enumerate(api_calls):
        G.add_node(caller)
        for callee in api_calls[i+1:]:
            if callee in G:
                G.add_edge(caller, callee)
    return G

def calculate_centrality(G):
    centralities = {}
    if G.number_of_nodes() > 0:
        try:
            centralities = {
                'degree': {k: v + 1 for k, v in nx.degree_centrality(G).items()},
                'closeness': {k: v + 1 for k, v in nx.closeness_centrality(G).items()},
                'harmonic': {k: v + 1 for k, v in nx.harmonic_centrality(G).items()},
                'katz': {k: v + 1 for k, v in nx.katz_centrality_numpy(G, alpha=0.01).items()}
            }
        except TypeError:
            centralities = {
                'degree': {k: v + 1 for k, v in nx.degree_centrality(G).items()},
                'closeness': {k: v + 1 for k, v in nx.closeness_centrality(G).items()},
                'harmonic': {k: v + 1 for k, v in nx.harmonic_centrality(G).items()},
            }
    return centralities

def process_file(file_path):
    api_calls = extract_api_calls(file_path)
    if api_calls:
        G = build_graph(api_calls)
        return G
    return None

def save_centralities(subdir_path, centralities):
    for measure, values in centralities.items():
        sorted_values = dict(sorted(values.items(), key=lambda item: item[1], reverse=True))
        output_file = os.path.join(subdir_path, f"{measure}_new.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sorted_values, f, ensure_ascii=False, indent=4)

def process_package(package_path):
    """处理单个包，构建API调用图并计算中心性"""
    # print(f"Start processing: {package_path}")

    all_api_calls = []
    future_to_file = {}

    with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        for dirpath, _, filenames in os.walk(package_path):
            for file in filenames:
                if file.endswith('.py'):
                    file_path = os.path.join(dirpath, file)
                    future_to_file[executor.submit(process_file, file_path)] = file_path

        # 收集所有文件的 API 调用图
        all_graphs = []
        for future in as_completed(future_to_file):
            G = future.result()
            if G:
                all_graphs.append(G)

    # 合并所有图的节点
    if all_graphs:
        # 创建合并的图
        merged_G = nx.DiGraph()
        for G in all_graphs:
            for node in G.nodes():
                merged_G.add_node(node)
            for edge in G.edges():
                merged_G.add_edge(*edge)

        # 只在合并后的图上计算一次中心性
        if merged_G.number_of_nodes() > 0:
            centralities = calculate_centrality(merged_G)
            save_centralities(package_path, centralities)

    # print(f"END PROCESSING {package_path}")

def main():
    base_path = r'/Data2/hxq/datasets/incremental_packages'

    # 生成 2022-01 到 2024-12 的月份列表
    from datetime import datetime
    start = datetime.strptime('2022-03', '%Y-%m')
    end = datetime.strptime('2024-12', '%Y-%m')
    months = []
    current = start
    while current <= end:
        months.append(current.strftime('%Y-%m'))
        current = (current.month == 12 and datetime(current.year + 1, 1, 1) or datetime(current.year, current.month + 1, 1))

    # 遍历所有月份和类型目录，处理每个包
    total_start_time = time.time()
    package_count = 0

    for month in months:
        month_path = os.path.join(base_path, month)

        for sub_type in ['benign', 'malicious']:
            type_path = os.path.join(month_path, sub_type)

            print(f"处理月份: {month}, 类型: {sub_type}")

            for package_name in os.listdir(type_path):
                package_path = os.path.join(type_path, package_name)
                if os.path.isdir(package_path):
                    process_package(package_path)
                    package_count += 1

    total_end_time = time.time()
    total_elapsed_time = total_end_time - total_start_time
    print(f"\n{'='*50}")
    print(f"全部处理完成! 共处理 {package_count} 个包, 总时间: {total_elapsed_time:.2f} second")
    print('='*50)

if __name__ == "__main__":
    main()
    # process_package("/Data2/hxq/datasets/incremental_packages/2023-09/malicious/pytspeak-3.23")