import os
import json
import time
# from cal_cen_new import process_package

def extract_features(fea_set_path, pack_dir, start_month='2022-01', end_month='2022-02'):

    # 生成月份列表
    from datetime import datetime
    start = datetime.strptime(start_month, '%Y-%m')
    end = datetime.strptime(end_month, '%Y-%m')
    months = []
    current = start
    while current <= end:
        months.append(current.strftime('%Y-%m'))
        current = (current.month == 12 and datetime(current.year + 1, 1, 1) or datetime(current.year, current.month + 1, 1))

    with open(fea_set_path, 'r', encoding='utf-8') as f:
        feature_set = json.load(f)

    api_feature_map = {api["api_name"]: 0 for api in feature_set["apis"]}

    # 新目录结构: {malicious,benign}/{月份}/{包}
    for type_name in ["malicious", "benign"]:
        type_path = os.path.join(pack_dir, type_name)

        for month in months:
            month_type_path = os.path.join(type_path, month)

            for package_dir in os.listdir(month_type_path):
                package_path = os.path.join(month_type_path, package_dir)
                if not os.path.isdir(package_path):
                    continue

                api_ex_file = os.path.join(package_path, "closeness_new.json")
                if not os.path.exists(api_ex_file):
                    missing_file = "missing_closeness.txt"
                    # process_package(package_path)
                    with open(missing_file, 'a', encoding='utf-8') as f:
                        f.write(package_dir + '\n')
                    continue

                try:
                    with open(api_ex_file, 'r', encoding='utf-8') as f:
                        api_ex_data = json.load(f)

                    feature_vector = {api: 0 for api in api_feature_map}

                    for api_name, feature_value in api_ex_data.items():
                        if api_name in api_feature_map:
                            feature_vector[api_name] = feature_value

                    output_file = os.path.join(package_path, "closeness_feature_vector.json")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(feature_vector, f, indent=4)
                except Exception as e:
                    print(f"process {package_path} error: {e}")

def extract_package_features(fea_set_path, package_path):

    with open(fea_set_path, 'r', encoding='utf-8') as f:
        feature_set = json.load(f)

    api_feature_map = {api["api_name"]: 0 for api in feature_set["apis"]}

    
    if not os.path.isdir(package_path):
        return

    api_ex_file = os.path.join(package_path, "closeness_new.json")
    if not os.path.exists(api_ex_file):
        print('missing closeness_new.json in ', package_path)

    try:
        with open(api_ex_file, 'r', encoding='utf-8') as f:
            api_ex_data = json.load(f)

        feature_vector = {api: 0 for api in api_feature_map}

        for api_name, feature_value in api_ex_data.items():
            if api_name in api_feature_map:
                feature_vector[api_name] = feature_value

        output_file = os.path.join(package_path, "closeness_feature_vector.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(feature_vector, f, indent=4)
    except Exception as e:
        print(f"process {package_path} error: {e}")

if __name__ == "__main__":

    starttime = time.time()
    print(f"The start time is: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

    fea_set_path = r"/Data2/hxq/MalGuard/API-call-graph/gpt_prompt_result_closeness.json" 
    pack_dir = r"/Data2/hxq/datasets/incremental_packages_dynamic_capping_subset" 

 
    extract_features(fea_set_path, pack_dir, start_month='2022-01', end_month='2024-12')


    endtime = time.time()
    totaltime = endtime - starttime
    print(f"The end time is: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    print(f"The total time is: {totaltime:.2f} 秒")

    # extract_package_features(fea_set_path, "/Data2/hxq/datasets/incremental_packages/2023-09/malicious/pytspeak-3.23")