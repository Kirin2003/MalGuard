import json


def extract_top_n(input_path: str, output_path: str, n: int = 500) -> None:
    """Extract top N items from a JSON file.

    Args:
        input_path: Path to input JSON file
        output_path: Path to output JSON file
        n: Number of top items to extract
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    top_n_data = dict(list(data.items())[:n])

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(top_n_data, f, ensure_ascii=False, indent=2)

    print(f"前{n}条数据已保存到 {output_path}")


if __name__ == '__main__':
    input_file = r'/Data2/hxq/datasets/incremental_packages_dynamic_capping_subset/closeness_final_new.json'
    output_file = r'../results/output_top_500_closeness_centrality.json'
    extract_top_n(input_file, output_file)
