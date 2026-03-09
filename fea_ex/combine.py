import os
import json
from datetime import datetime


def convert_features_to_txt(pack_dir, output_txt_path, start_month='2022-01', end_month='2023-02', type_flag="malicious"):

    # 生成月份列表
    start = datetime.strptime(start_month, '%Y-%m')
    end = datetime.strptime(end_month, '%Y-%m')
    months = []
    current = start
    while current <= end:
        months.append(current.strftime('%Y-%m'))
        current = (current.month == 12 and datetime(current.year + 1, 1, 1) or datetime(current.year, current.month + 1, 1))

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

                feature_file = os.path.join(package_path, "closeness_feature_vector.json")
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


# 主程序入口
if __name__ == "__main__":

    pack_dir = r"/Data2/hxq/datasets/incremental_packages_dynamic_capping_subset"
    # malicious_output_txt_path = r"/Data2/hxq/MalGuard/fea_ex/malware_features_train.txt"
    # benign_output_txt_path = r"/Data2/hxq/MalGuard/fea_ex/benign_features_train.txt"

    # convert_features_to_txt(pack_dir, malicious_output_txt_path, start_month='2022-01', end_month='2023-02', type_flag="malicious")
    # convert_features_to_txt(pack_dir, benign_output_txt_path, start_month='2022-01', end_month='2023-02', type_flag="benign")

    # 将2303~2412每个月的特征向量各自合并成一个文件
    for month in [f"{year}-{str(m).zfill(2)}" for year in range(2022, 2025) for m in range(1, 13)]:
        malicious_output_txt_path = f"/Data2/hxq/MalGuard/fea_ex/dataset/malware_features_{month}.txt"
        benign_output_txt_path = f"/Data2/hxq/MalGuard/fea_ex/dataset/benign_features_{month}.txt"

        convert_features_to_txt(pack_dir, malicious_output_txt_path, start_month=month, end_month=month, type_flag="malicious")
        convert_features_to_txt(pack_dir, benign_output_txt_path, start_month=month, end_month=month, type_flag="benign")    