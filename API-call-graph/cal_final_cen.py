import os
import json
from collections import defaultdict
import networkx as nx
import ast
import io



def load_centrality_values(package_path):
    centrality_values = {}
    for centrality_type in ['degree', 'closeness', 'harmonic', 'katz']:
        file_path = os.path.join(package_path, f"{centrality_type}_new.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                centrality_values[centrality_type] = json.load(f)
    return centrality_values

def calculate_final_centrality(all_packages):
    total_packages = len(all_packages)
    summed_values = defaultdict(lambda: defaultdict(float))

    for package in all_packages:
        centrality_values = load_centrality_values(package)
        for centrality_type, values in centrality_values.items():
            for api, value in values.items():
                summed_values[centrality_type][api] += value

    final_values = {
        centrality_type: {api: total / total_packages for api, total in apis.items()}
        for centrality_type, apis in summed_values.items()
    }

    return final_values

def save_final_results(final_results, output_folder):
    for centrality_type, values in final_results.items():
        sorted_values = dict(sorted(values.items(), key=lambda item: item[1], reverse=True))
        output_file = os.path.join(output_folder, f"{centrality_type}_final_new_0129.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sorted_values, f, ensure_ascii=False, indent=4)

def process_all_packages(base_folder, start_month='2022-01', end_month='2023-02'):
    # 生成月份范围
    from datetime import datetime
    start = datetime.strptime(start_month, '%Y-%m')
    end = datetime.strptime(end_month, '%Y-%m')
    months = []
    current = start
    while current <= end:
        months.append(current.strftime('%Y-%m'))
        current = (current.month == 12 and datetime(current.year + 1, 1, 1) or datetime(current.year, current.month + 1, 1))

    # 收集指定月份下的所有恶意包
    all_packages = []
    for month in months:
        month_path = os.path.join(base_folder, month, 'malicious')
        if os.path.exists(month_path):
            packages = [os.path.join(month_path, pkg) for pkg in os.listdir(month_path)
                       if os.path.isdir(os.path.join(month_path, pkg))]
            all_packages.extend(packages)

    print(f"共收集到 {len(all_packages)} 个恶意包 (月份: {start_month} ~ {end_month})")

    final_results = calculate_final_centrality(all_packages)

    save_final_results(final_results, base_folder)

if __name__ == '__main__':
    base_folder = r'/Data2/hxq/datasets/incremental_packages'
    process_all_packages(base_folder, start_month='2022-01', end_month='2023-02')
