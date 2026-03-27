import os
import json
from utils.month_utils import generate_month_range


def convert_features_to_txt(pack_dir, output_txt_path, start_month='2022-01', end_month='2023-02', type_flag="malicious", feature_filename='closeness_feature_vector.json'):

    months = generate_month_range(start_month, end_month)

    total_count = 0

    # 新目录结构: {malicious,benign}/{月份}/{包}
    with open(output_txt_path, 'w', encoding='utf-8') as f_out:

        type_path = os.path.join(pack_dir, type_flag)

        for month in months:
            month_type_path = os.path.join(type_path, month)
            if not os.path.exists(month_type_path):
                continue

            for package_dir in os.listdir(month_type_path):
                package_path = os.path.join(month_type_path, package_dir)
                if not os.path.isdir(package_path):
                    continue

                feature_file = os.path.join(package_path, feature_filename)
                if not os.path.exists(feature_file):
                    continue

                try:
                    with open(feature_file, 'r', encoding='utf-8') as f:
                        feature_vector = json.load(f)

                    feature_list = list(feature_vector.values())
                    if type_flag == "malicious":
                        feature_list.append(1)  # 标签: 1 表示恶意
                    else:
                        feature_list.append(0)  # 标签: 0 表示良性

                    f_out.write(' '.join(map(str, feature_list)) + '\n')
                    total_count += 1

                except Exception as e:
                    print(f"process {package_path} error: {e}")
                    continue

    print(f"共转换 {total_count} 个 {type_flag} 包 (月份: {start_month} ~ {end_month})")


def clear_output_files(output_dir, start_month, end_month):
    """清除之前生成的 malware_features_*.txt 和 benign_features_*.txt 文件"""
    months = generate_month_range(start_month, end_month)
    cleared_count = 0
    for month in months:
        for prefix in ["malware_features_", "benign_features_"]:
            file_path = os.path.join(output_dir, f"{prefix}{month}.txt")
            if os.path.exists(file_path):
                os.remove(file_path)
                cleared_count += 1
    print(f"已清除 {cleared_count} 个输出文件")

def merge_features(pack_dir, output_dir, start_month, end_month, feature_filename='closeness_feature_vector.json'):
    """
    将指定月份范围内每个月的恶意和良性包特征分别合并，输出到指定目录。

    Args:
        pack_dir: 包目录路径，包含 malicious/ 和 benign/ 子目录
        output_dir: 输出目录路径
        start_month: 起始月份，格式 'yyyy-mm'
        end_month: 结束月份，格式 'yyyy-mm'
        feature_filename: 特征文件名，默认为 'closeness_feature_vector.json'
    """
    clear_output_files(output_dir, start_month, end_month)

    os.makedirs(output_dir, exist_ok=True)
    months = generate_month_range(start_month, end_month)

    for month in months:
        malicious_output_path = os.path.join(output_dir, f"malware_features_{month}.txt")
        benign_output_path = os.path.join(output_dir, f"benign_features_{month}.txt")

        convert_features_to_txt(pack_dir, malicious_output_path, start_month=month, end_month=month, type_flag="malicious", feature_filename=feature_filename)
        convert_features_to_txt(pack_dir, benign_output_path, start_month=month, end_month=month, type_flag="benign", feature_filename=feature_filename)


# 主程序入口
if __name__ == "__main__":

    pack_dir = r"/Data2/hxq/datasets/incremental_packages_dynamic_capping_subset"
    output_dir = r"/Data2/hxq/MalGuard/fea_ex/dataset"

    merge_features(pack_dir, output_dir, start_month='2022-01', end_month='2024-12')